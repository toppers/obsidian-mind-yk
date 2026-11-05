---
date: 2026-10-21
description: "TECSCDE-DT-EL内部仕様 4B。CDLパーサ（モジュールB）の実装構造——文法のロード、tool_info抽出、CST走査、モデル組み立て、保存時の直列化、診断を、src/renderer/cdl/ の読解に基づいてまとめる。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

# 4B. CDLパーサ設計（モジュールB）

Domain note of [[TECSCDE-DT-EL内部仕様]]。モジュールB（CDLパーサ／シリアライザ）の**実装の構造**を、`E:\Ccur\typescript\TECSCDE-DT-EL\src\renderer\cdl\` のソースを読んでまとめる（2026-10-21、as of 実装のコミット時点）。設計の出発点は[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計|TECSCDE内部仕様第4章]]（構文解析をtree-sitter文法へ委ねる改訂を含む）と[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様第2章]]で、本章はそれらをDT-ELの実装に対応づけた記録である。配置（rendererプロセス、WASM版tree-sitter）は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|第2章]]で定める。

> [!note] この章の根拠
> 各節の記述は、実装ファイルの読解によるもの。テスト（`tests/`）は読んでいないため、挙動の保証としては扱わない。実装を見て気づいた点は4B.10節に分けて記す（仕様と実装のずれの候補を含む）。

## 4B.1 構成要素

| ファイル | 主な型・関数 | 役割 |
|---|---|---|
| `grammar.ts` | `CdlGrammar` | tree-sitterのWASMをロードし、初期化済みパーサを保持する薄い層 |
| `tool-info.ts` | `ToolInfoValidator` | `__tool_info__("name") { … }`ブロックの抽出（本体から空白置換で除去）、JSONの検証・直列化 |
| `cst.ts` | `CdlDocumentBuilder`、`ParsedCdl`と各`*Decl` | tree-sitterのCST（構文木）を走査して、中間表現`ParsedCdl`を作る |
| `signature-types.ts` | `signatureFunctions`、`localTypedefs`、`TypeUse` | シグニチャの関数の戻り値・引数の型と、CDL内`typedef`の抽出（組込型17種は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|3.1節]]） |
| `document-builder.ts` | `CdlDocumentLoader`、`CdlSource`、`LoadResult` | 複数ファイル分の`ParsedCdl`と`tool_info`を、`TecscdeDocument`へ組み立てる |
| `port-type-index.ts` | `PortTypeIndex`、`portTypeKey` | ポートの型の解決結果をモデルとは別に保持する索引 |
| `serializer.ts` | `CdlSerializer` | `TecscdeDocument`をCDLテキストへ書き戻す |
| `fragment.ts` | `serializeCellsAsCdl`、`tryParseCdlFragment` | Copy/Cut/Pasteが使う、`cell`ブロックだけの断片 |
| `messages.ts` | `syntaxError`ほか | 診断メッセージの生成（コード体系は4B.7） |

> [!warning] 名前と置き場所のずれ
> クラス`CdlDocumentBuilder`は`cst.ts`にあり、`document-builder.ts`にあるのは`CdlDocumentLoader`である。ファイル名だけを頼りに探すと取り違える（歴史的経緯: 旧`CdlLexer`／`CdlParser`の置き換えで、`cst.ts`にビルダーが入った）。

## 4B.2 読み込みの流れ

```
CdlSource[]（text・fileName・sourcePath・editable・generated）
  │  ① 各ソースごとに
  ├─ ToolInfoValidator.extractBlocks(text)      → blocks と sourceWithBlanks（tool_info を空白に置換、改行は保つ）
  ├─ CdlDocumentBuilder.build(sourceWithBlanks)  → ParsedCdl（signatures・typedefs・celltypes・cells・imports・generates・composites・scopes・diagnostics）
  ├─ ToolInfoValidator.parseTecsgen / parseTecscde（ブロックごと）→ ToolInfoTecsgen・レイアウト（cellList・joinList・paper）
  │  ② 全ソースがそろってから
  ├─ CTypeRegistry で型を解決 → シグニチャ型・ポート型の索引
  ├─ セルタイプ登録（ポートの既定配置）・Mrubyブリッジ補完
  ├─ セル（1周目）: 重複選択・配置・リージョン・ポート
  ├─ 結合（2周目）: 全セルが揃ってから解決
  └─ TecscdeDocument.build(...)  → LoadResult（document・diagnostics・portTypeIndex）
```

- **同期性**: 非同期なのはWASMのロード（`CdlGrammar.init()`）だけで、以降の`parse`・`build`・`loadSources`はすべて同期。
- **行番号の保存**: `extractBlocks`は`tool_info`の範囲を空白で潰すが改行は残すので、診断の行・桁は元テキストと一致する。
- **未初期化時の扱い**: `CdlGrammar.parserInstance`は、未初期化なら例外を投げる。利用者の入力に由来しない起動順序の不具合なので、診断には倒さない。

## 4B.3 文法のロード（`CdlGrammar`）

- WASMは2つ: tree-sitterのランタイムと、CDL文法（tecsgenの`bnf.y.rb`由来の移植文法）。ブラウザでは`/wasm/tree-sitter.wasm`・`/wasm/tree-sitter-cdl.wasm`を既定のURLとし、テストでは実体のバイト列を注入する（`CdlGrammarAssets`）。
- `init()`は多重呼び出しで同じPromiseを返す（呼び出し側の排他は不要）。文法パッケージ同梱の`lib/index.ts`は`__dirname`に依存して動かないため使わず、`.wasm`を`public/wasm/`に取り込んで直接ロードする。
- 構文解析の範囲は絞らない（tecsgen自身の構文定義の移植文法を使うため）。

## 4B.4 CST走査（`CdlDocumentBuilder.build`）

`build(sourceWithBlanks)`が返す`ParsedCdl`の中身:

| フィールド | 要素 | 持つ情報 |
|---|---|---|
| `signatures` | `SignatureDecl` | 修飾名、関数本体の有無、関数の型情報、位置 |
| `typedefs` | `LocalTypedefDecl` | CDL内`typedef` |
| `celltypes` | `CelltypeDecl` | 名前、修飾名、ポート、属性名 |
| `composites` | `CompositeDecl` | 名前、ポート、属性、内部構造`CompositeStructure`、`hasUnsupportedSyntax` |
| `cells` | `CellDecl` | セルタイプ名、セル名、結合代入、属性代入、位置、`regionPath`、`startIndex`／`endIndex` |
| `imports` | `ImportDecl` | `import`／`import_C`の種別、パス、**原文**（保存時の書き戻し用） |
| `generates` | `GenerateDecl` | プラグイン名、シグニチャ名、引数、スコープ、原文 |
| `scopes` | `CdlScope` | `namespace`／`region`のパス、本体末尾の位置`bodyEndIndex`（保存時の挿入位置） |
| `diagnostics` | `Diagnostic` | 構文エラー（4B.7） |

- **スコープの表現**: ルートは`"::"`、入れ子は`"::A::B"`。`namespace`と`region`は`visitNested`が再帰的に降り、`scopes`に追加して、中の`cell`・`celltype`・`signature`・`generate`・`import`などに親のパスを引き渡す。
- **セルの属性と結合の判別**（`collectCell`）: 代入文の右辺が`field_expression`（`target.ePort`）なら結合、それ以外は属性代入として**値を元テキストのまま**保持する。`initializer`の包みは剥がす。配列添字（`cport[n]`）は`cportIndex`に入れる。添字を省いた結合（`cport[]`）は`cportIndex`を持たない（外部仕様4.6.x。tecsgenの構文規則では添字`-1`）。ローダーが、同じセルの同じ呼び口の中で、書かれた順に0, 1, 2…を割り当てる。添字を書いた結合と省いた結合が混ざったときは`W-JOIN-INDEX-INCONSISTENT`を出す。実装済み（2026-11-02、実装リポジトリPR #23、マージコミット`1a5cc4e`。`cst.ts`の`assignOmittedSubscripts`、保存は`serializer.ts`の`omittedFormPorts`）。
- **セルタイプ**（`collectCelltype`）: `port`（`call`／`entry`、シグニチャ、名前、配列サイズ）、`attribute`の名前、`require`を拾う。`var`・`factory`はモデルに反映しない。`require`は独立の`celltype_statement`なので、`collectPort`の`isRequire`は`false`のままで、`collectRequire`が別に拾う（2026-10-22実装）。**名前つき**（`require 名前 = 要求先.受け口;`）は、利用者が結合できる通常の呼び口（`isRequire=false`）で、シグニチャはローダーが要求先（セルタイプ名、またはセル名のセルタイプ）の受け口から解決する（解決できないときは`W-PORT-SIGNATURE-UNRESOLVED`）。**名前なし**（`require 要求先.受け口;`）は図に出ない呼び口（`isRequire=true`）で、4B.5節の`hiddenRequirePortCount`に数える。
- **複合セルタイプ**（`collectComposite`）: 外部ポート、属性、内部セル（束縛`join`／`external_join`）、ポートの公開（`export_join`）を集める。認識できない節、ポートの欠損、`hasError`のいずれかで`hasUnsupportedSyntax`を立てる。定義の**原文**を`structure.rawText`に保持する（無編集保存で完全一致させるため。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B]]）。
- **保持するだけの構文**: `generate`、`import`／`import_C`は原文を保持する。モデルへは反映しない。
- **トップレベルとネストの走査**: 2026-10-22に、トップレベルも`visitNested(top, "::")`で走査する形に統合した（以前は別々の`switch`で同じ分岐を持っていた。4B.10節の3）。名前の修飾は、トップレベルの`signature`は修飾なし、ネスト内は`A::B`形式（親のパスが`::`なら修飾なしになるだけで、規則は1つ）。

## 4B.5 モデルの組み立て（`CdlDocumentLoader.loadSources`）

入力`CdlSource`は、`text`・`fileName`・`sourcePath?`・`editable`・`generated?`を持つ。`editable`は**呼び出し側が決めて渡す**（クラス自体は判定しない。TS内部仕様3.3節#5と同じ分担）。`generated`はPlugin生成CDL（読み取り専用、保存対象と参照先に含めない）。

1. **ソースごとの解析**（4B.2の①）。`editable`なソースのスコープは`editableRegionPaths`にも登録する。`editable`かつ非`generated`なら、保存用の`sourceTemplate`（元テキスト、各セルの位置、直前コメントを含む先頭位置`leadingText`、結合の原文、複合定義の原文、スコープ末尾、`tool_info`ブロックの範囲）を作る。`import`／`import_C`の原文は、`editable`なソース（複数あれば最後）のものを`preservedImports`に持つ。
2. **`tool_info`の解釈**: `tecsgen`ブロックは版を検査して保持するだけ。`tecscde`ブロックは検証し、用紙・セルの配置（`cellList`）・結合のバー（`joinList`）を**ソースごと**に覚える。自分宛てでないツール名のブロックは読み飛ばす（外部仕様5.1.1）。
3. **型の解決**: `CTypeRegistry`（`cdeclResults`と、CDL内`typedef`）で、シグニチャの戻り値・引数を解決する。解決できない型は警告`W-C-TYPE-UNRESOLVED`。ポートのシグニチャが解決できなければ`W-PORT-SIGNATURE-UNRESOLVED`。結果は`PortTypeIndex`に入れ、モデルとは別に返す。
4. **セルタイプの登録**: ポートに既定配置を割り当てる——呼び口は左辺、受け口は右辺、辺の長さ15mmを個数で均等割り（`assignDefaultPortLayout`）。`MrubyBridgePlugin`の`generate`からは、外側のセルタイプ（`nMruby::t…`と`…_Initializer`）を補う。
5. **セル（1周目）**: 全ソース分をまとめて処理する。
   - **重複**: 同名セルは、最初に採用された定義のみモデル化し、後続は`W-DUP-CELL`。ただしPlugin生成どうしの重複は、結合と属性の多い方を採る（tecsgenが前方宣言を先に出す場合があるため）。
   - **配置**: `tool_info`にレイアウトがあればそれを使い、無ければ自動配置（外部仕様5.3.xの規定〔2026-11-03採用〕。従来の格子の順に、既存のセル〔保存済みの位置を持つセルを含む〕と重ならない最初の候補へ置き、用紙の内に収まらないセルは先頭から走査し直して横8mm・縦6mmずつずらして置き、数を`W-AUTO-LAYOUT-OVERFLOW`で知らせる）。幅25×高さ15mm。※実装は未対応（2026-11-03時点。現行は外部仕様5.3.1のとおり、横に55mm進め、用紙幅−30mmを超えたら次の行、高さ−15mmを超えたら先頭へ戻して重ねる）。
   - **リージョン**: CDLのスコープを優先する。ルート直下のセルは、`tool_info`の所属が（`editable`なソースなら`editableRegionPaths`、そうでなければ`regionPaths`の）スコープに存在すれば使い、食い違えば`W-REGION-MISMATCH`。詳細と外部仕様との差は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.3節]]。
   - **セルタイプ未解決**: `celltypeUnresolved: true`のセルを作り、ポートは空。`W-UNRESOLVED-CELLTYPE`。
   - **隠れ`require`**: 名前なしの`require`があるセルタイプのセルごとに、その個数を示す`W-REQUIRE-PORT-HIDDEN`（2026-10-22に実際に出るようにした）。名前つきの`require`は対象外。
   - **ポートの配置**: 保存された辺とオフセットで上書きする。
6. **結合（2周目）**: 全セルが揃ってから解決する。結合先（セルまたは受け口）が無ければ`W-MISSING-JOIN-TARGET`で飛ばす。バーは、保存されたものがあればそれ、無ければ`autoRouteBars`で自動経路にする。
7. **仕上げ**: 保存テンプレートの各セルの`joins`から、モデルに取り込まれた結合を除く（モデルに反映できなかった結合の原文だけを残す）。編集対象は`editable`なソースの**最後**で、それ以外（かつ非`generated`）が`referenceFiles`。`TecscdeDocument.build`に渡して`LoadResult`を返す。

`loadSingle(text, fileName, editable = true)`は、テストと新規作成直後の1ファイル読み込み用の簡便な呼び出し。

## 4B.6 保存時の直列化（`CdlSerializer`）

- **`serializeSource(doc, sourceKey)`**: 編集対象ファイルなら`serialize`へ。それ以外は、そのファイルの`sourceTemplate`を使い、`cell.editable && cell.locale === sourceKey`のセルだけを書く。`tecscde`ブロックのレイアウト（セル・ポート・結合のバー）を作り直し、`tecsgen`ブロックは変えない。
- **`serialize(doc, now)`**: 編集可能なセルを名前順に並べ（決定性のため）、`tecsgen`ブロック（版・保存時刻・`directImport`＝参照ファイルを更新）、`import`の原文、`cell`ブロック、`tecscde`ブロックの3つを出力する。`sourceTemplate`があれば次のテンプレート方式、無ければ上の新規形式。
- **テンプレート方式**（`serializeFromTemplate`）: 元テキストのセル範囲を削除し、各リージョン（スコープ）の末尾へセルを挿入する。コメントは`leadingText`としてセルについていく。`tool_info`は既存の位置で置換し、無ければ先頭（`tecsgen`）または末尾（`tecscde`）に足す。編集は位置の降順に適用する。
- **保存後の検査**: 書いた結果をもう一度`build`して検証し、不整合なら**例外**を投げる（診断ではない）: 複合定義の名前・原文が変わった、構文エラーが出た、セル数が変わった、セルの所属リージョンが復元できない。保存前にも、リージョン所属の不整合、同名セル、保存先リージョンが編集ファイルに無いことを例外にする。
- **結合の書き出し**: `編集可能なセル由来の結合のみ`を`joinList`に出す（外部仕様5.4.1）。

## 4B.7 診断

`messages.ts`が生成する診断:

| コード | 内容 | 出どころ |
|---|---|---|
| `G1015` | 予期しないファイル終端 | `ERROR`ノードの内容が空のとき |
| `G1016` | 構文エラー（`syntax error near`） | `MISSING`ノード、または`ERROR`ノード。対応先が定まらなければこれに倒す |
| `W-DUP-CELL` | セル重複 | 4B.5節 |
| `W-UNRESOLVED-CELLTYPE` | セルタイプ未解決 | 4B.5節（整合性チェックの`diagnostics/integrity.ts`も同名を出す） |
| `W-MISSING-JOIN-TARGET` | 結合先が無い | 4B.5節 |
| `W-COMPOSITE-UNSUPPORTED` | 複合セルタイプの未対応構文 | **DT-ELでは使わない仕様**（第8章、3B.5）。生成関数`compositeUnsupported`は、呼び出しが無いため2026-10-22に削除した（4B.10節の5）。コード`W_CODES.COMPOSITE_UNSUPPORTED`は、「出ない」ことを確かめるテストが参照するため残す。未対応構文の通知はプロパティ欄のみ |
| `W-REQUIRE-PORT-HIDDEN` | 隠れ`require`ポート | 4B.5節 |
| `W-LAYOUT-DISCARDED`、`W-LAYOUT-PARSE-ERROR`、`W-NEWER-FORMAT` | `tool_info`の検証 | `ToolInfoValidator`（`tool-info.ts`が直接出す） |
| `W-UNRESOLVED-REF-FILE`、`W-CPP-FALLBACK`、`W-CDECL-PARSE` | 参照ファイル・cpp・Cヘッダ解析 | `app/import-resolution.ts`（7.5節、9B）と`diagnostics/integrity.ts`。ローダーは出さない |
| `W-C-TYPE-UNRESOLVED`、`W-PORT-SIGNATURE-UNRESOLVED`、`W-REGION-MISMATCH` | 型・ポート・リージョン | `document-builder.ts`。コードは`messages.ts`の`W_CODES`に集約した（2026-10-22。`tool-info.ts`の`W-NEWER-FORMAT`・`W-LAYOUT-*`も同様） |
| `W-PLUGIN-TYPE-LOAD`、`E-TECSGEN-NOT-FOUND` | tecsgenの起動失敗 | それぞれ`app/file-actions.ts`、`diagnostics/tecsgen-result-parser.ts`（パーサーの外。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|9.7節]]） |

- tree-sitterはエラーの位置と構造しか返さず、メッセージ文言を持たない（移植したのは構文定義だけで、メッセージカタログは含まれない）。そのため構文エラーは大半を`G1016`にまとめる（tecsgen自身も大半をこの1コードで報告する）。`messages.ts`のコード体系は、外部仕様が引用する範囲の再現で、tecsgenのカタログ全体の網羅ではない。
- 診断の`location.file`は、`CdlDocumentBuilder`の段階では空で、`loadSources`が`withLocation`でファイル名を埋める。

## 4B.8 クリップボード用の断片（`fragment.ts`）

`serializeCellsAsCdl`は、選択中のセルを`cell`ブロックだけに直列化する（位置・リージョン・結合は含めない。外部仕様6.7節）。`tryParseCdlFragment`は、`CdlDocumentBuilder.build`の結果を使い、構文エラーがあるか、`cell`が1つも無ければ`undefined`を返す（貼り付けは「何もしない」）。

## 4B.9 システム定義CDLへの拡張点（設計）

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|3.2節]]のとおり、`CdlSource`に`systemDefined`を加え、`loadSources`が`Cell`へ`systemDefined`を渡し、`editable`を算出する。判定そのものは`CdlDocumentLoader`の外（main側の`isUnderAny`）で行い、ここではソースの属性として受け取る。実装は未着手。

## 4B.10 実装を読んで気づいた点

仕様と実装のずれの候補。いずれも、読解のみで、動作は確認していない。

1. ~~**`isRequire`が常に`false`**~~ → **解消（2026-10-22）**。`require`を拾う処理を足した（4B.2節の「セルタイプ」）。経緯: `collectPort`は`isRequire: false`固定（`require`は独立した`celltype_statement`のため）。一方、`loadSources`は`isRequire`のポート数を`hiddenRequirePortCount`にするので、この経路では**常に0**となり、`W-REQUIRE-PORT-HIDDEN`は出ない可能性が高い。`celltype_statement`の`require`を拾う処理が`collectCelltype`に無いことが原因（`var`／`require`／`factory`は無視する、とコメントがある）。
2. ~~**古いドキュメントコメント**~~ → **解消（2026-10-22）**（`loadSources`のコメントを更新）。経緯: `loadSources`の説明は「編集対象ファイルのcellのみeditable=trueとなり」と書くが、現行の仕様（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|7C]]）は呼び出し側が決める`editable`で、通常CDLは全て編集可能。`CdlSource.editable`のコメントも「読み込んだCDLは編集可能」となっていて、こちらは現行どおり。
3. ~~**トップレベルとネストの重複**~~ → **解消（2026-10-22）**（`visitNested`に統合。統合前も`signature`の名前の修飾に実際の差は無かった）。経緯: `build`のトップレベル`switch`と`visitNested`の`switch`が別々に同じ分岐を持ち、片方だけ直す事故が起きうる。`signature`の名前の修飾規則も、片方（トップレベル）は常に修飾なし。
4. ~~**メッセージの二重管理**~~ → **解消（2026-10-22）**（`W_CODES`に集約）。経緯: `W-C-TYPE-UNRESOLVED`などは`document-builder.ts`に直書きされ、`messages.ts`の`W_CODES`にない。
5. ~~**`compositeUnsupported`の呼び出しが無い**~~ → **解消（2026-10-22）**（関数を削除。コード定数はテスト用に残す）。経緯: `messages.ts`の`W-COMPOSITE-UNSUPPORTED`と生成関数は、`src`内に呼び出しが見当たらない（2026-10-21の検索）。DT-ELの仕様（第8章、3B.5。DT外部仕様4.7節・第9章と一致）は、複合型の存在や未対応構文を警告にしないので、仕様と実装は整合しており、残るのは未使用の定義だけ（削除してよい）。
6. ~~**ファイル名ヘッダの参照番号**~~ → **解消（2026-10-22）**（`cdl/`の主要なファイルの先頭コメントに、DT-EL内部仕様04Bへの参照を足した）。経緯: ソース先頭のコメントは「TECSCDE-TS内部仕様 2.2」「11.3」など、TS版の章番号を指す。DT-ELで章番号が違う場合に追跡しにくい（本章がDT-ELの対応表になる）。

## 関連

- [[TECSCDE-DT-EL内部仕様]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章 モデル設計]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B 複合セルタイプ設計]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|7C 読み込み経路の統合]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|9B CdeclExtractor設計]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計|TECSCDE内部仕様第4章]]
- [[TECSCDE-DT-EL実装]]
