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
| `fragment.ts` | `serializeClipboardAsCdl`（更新後の契約案）、`tryParseCdlFragment` | Copy/Cut/Pasteが使うセル群のCDL断片。複数セルでは選択セル間の結合代入も含める（第4章4.1節） |
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
- **セルの属性と結合の判別**（`collectCell`）: 代入文の右辺が`field_expression`（`target.ePort`）なら結合、それ以外は属性代入として**値を元テキストのまま**保持する。`initializer`の包みは剥がす。配列添字（`cport[n]`）は`cportIndex`に入れる。添字を省いた結合（`cport[]`）は`cportIndex`を持たない（外部仕様4.6.x。tecsgenの構文規則では添字`-1`）。ローダーが、同じセルの同じ呼び口の中で、書かれた順に0, 1, 2…を割り当てる。添字を書いた結合と省いた結合が混ざったときは`W-JOIN-INDEX-INCONSISTENT`を出す。別の実装時点では実装済み（2026-11-02、実装リポジトリPR #23、マージコミット`1a5cc4e`。`cst.ts`の`assignOmittedSubscripts`、保存は`serializer.ts`の`omittedFormPorts`）。今回基準`5cf2d85`にはこの採番・混在警告・保存契約が未反映であり、PR履歴だけで現checkoutの適合を示すものではない（監査#19）。
- **セルタイプ**（`collectCelltype`）: `port`（`call`／`entry`、シグニチャ、名前、配列サイズ）、`attribute`の名前、`require`を拾う。`var`・`factory`はモデルに反映しない。`require`は独立の`celltype_statement`なので、`collectPort`の`isRequire`は`false`のままで、`collectRequire`が別に拾う（2026-10-22実装）。**名前つき**（`require 名前 = 要求先.受け口;`）は、利用者が結合できる通常の呼び口（`isRequire=false`）で、シグニチャはローダーが要求先（セルタイプ名、またはセル名のセルタイプ）の受け口から解決する（解決できないときは`W-PORT-SIGNATURE-UNRESOLVED`）。**名前なし**（`require 要求先.受け口;`）は図に出ない呼び口（`isRequire=true`）で、4B.5節の`hiddenRequirePortCount`に数える。
- **複合セルタイプ**（`collectComposite`）: 外部ポート、属性、内部セル（束縛`join`／`external_join`）、ポートの公開（`export_join`）を集める。認識できない節、ポートの欠損、`hasError`のいずれかで`hasUnsupportedSyntax`を立てる。定義の**原文**を`structure.rawText`に保持する（無編集保存で完全一致させるため。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B]]）。
- **保持するだけの構文**: `generate`、`import`／`import_C`は原文を保持する。モデルへは反映しない。
- **トップレベルとネストの走査**: 2026-10-22に、トップレベルも`visitNested(top, "::")`で走査する形に統合した（以前は別々の`switch`で同じ分岐を持っていた。4B.10節の3）。名前の修飾は、トップレベルの`signature`は修飾なし、ネスト内は`A::B`形式（親のパスが`::`なら修飾なしになるだけで、規則は1つ）。

## 4B.5 モデルの組み立て（`CdlDocumentLoader.loadSources`）

入力`CdlSource`は、`text`・`fileName`・`sourcePath?`・`editable`・`generated?`を持つ。`editable`は**呼び出し側が決めて渡す**（クラス自体は判定しない。TS内部仕様3.3節#5と同じ分担）。`generated`はPlugin生成CDL（読み取り専用、保存対象と参照先に含めない）。

1. **ソースごとの解析**（4B.2の①）。`editable`なソースのスコープは`editableRegionPaths`にも登録する。`editable`かつ非`generated`なら、保存用の`sourceTemplate`（元テキスト、各セルの位置、直前コメントを含む先頭位置`leadingText`、結合の原文、複合定義の原文、スコープ末尾、`tool_info`ブロックの範囲）を作る。`import`／`import_C`の原文は、明示された主ファイル`primarySourceKey`のものを`preservedImports`に持つ。主ファイル指定を省略した旧補助呼び出しだけ、従来の最後の`editable`ソースを使う（2026-11-07、監査#16、7I.3）。
2. **`tool_info`の解釈**: `tecsgen`ブロックは版を検査して保持するだけ。`tecscde`ブロックは検証し、用紙・セルの配置（`cellList`）・結合のバー（`joinList`）を**ソースごと**に覚える。用紙の未指定を既定値で潰さず、最小用紙選択までは明示指定と区別する（[[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択|4D.1]]）。複数ソースの用紙の採用元（開いた順に最初に有効な`paper`を宣言するファイル）の決定は、外部仕様5.3.x項目8に従う（2026-11-08）。自分宛てでないツール名のブロックは読み飛ばす（外部仕様5.1.1）。
3. **型の解決**: `CTypeRegistry`（`cdeclResults`と、CDL内`typedef`）で、シグニチャの戻り値・引数を解決する。解決できない型は警告`W-C-TYPE-UNRESOLVED`。ポートのシグニチャが解決できなければ`W-PORT-SIGNATURE-UNRESOLVED`。結果は`PortTypeIndex`に入れ、モデルとは別に返す。
4. **セルタイプの登録**: ポートに既定配置を割り当てる——呼び口は左辺、受け口は右辺、辺の長さ15mmを個数で均等割り（`assignDefaultPortLayout`）。`MrubyBridgePlugin`の`generate`からは、外側のセルタイプ（`nMruby::t…`と`…_Initializer`）を補う。
   - **配列種別の保持（2026-11-07、監査#12の追加契約）**: 宣言の非配列・`[N]`・`[]`・未解決を区別して配列グループへ渡す。現在の結合数や`subscript`だけから可変長を推定しない。[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入|4E]]の挿入で添字が変わった結合は、元の結合原文を無変更扱いで再利用せず、現在の添字で出力する。個数は外部5.1.x・4E.5で復元・保存する。
5. **セル（1周目）**: 全ソース分をまとめて処理する。
   - **重複**: 同名セルは、最初に採用された定義のみモデル化し、後続は`W-DUP-CELL`。ただしPlugin生成どうしの重複は、結合と属性の多い方を採る（tecsgenが前方宣言を先に出す場合があるため）。
   - **配置と用紙選択**: 全ソースの採用セルを確定し、保存済み位置を持つセルと自動配置対象を分けてから、[[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択|4D]]の計算を行う（2026-11-07、監査#10）。用紙未指定ならA4横→A3横→A2横を同じ初期条件で試し、重ならず収まる最小用紙を採用する。全候補で失敗した場合だけA2横でずらし配置と`W-AUTO-LAYOUT-OVERFLOW`へ進む。指定用紙は自動拡大せず尊重し、固定セルの位置も動かさない。既定のセル寸法は幅25×高さ15mm。これは2026-11-03採用の外部仕様5.3.xを具体化した契約であり、実装適合は未確認。
   - **リージョン**: CDLのスコープを優先する。ルート直下のセルは、`tool_info`の所属が（`editable`なソースなら`editableRegionPaths`、そうでなければ`regionPaths`の）スコープに存在すれば使い、食い違えば`W-REGION-MISMATCH`。詳細と外部仕様との差は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.3節]]。
   - **セルタイプ未解決**: `celltypeUnresolved: true`のセルを作り、ポートは空。`W-UNRESOLVED-CELLTYPE`。
   - **隠れ`require`**: 名前なしの`require`があるセルタイプのセルごとに、その個数を示す`W-REQUIRE-PORT-HIDDEN`（2026-10-22に実際に出るようにした）。名前つきの`require`は対象外。
   - **ポートの配置**: 保存された辺とオフセットで上書きする。
6. **結合（2周目）**: 全セルが揃ってから解決する。結合先（セルまたは受け口）が無ければ`W-MISSING-JOIN-TARGET`で飛ばす。保存バーは要素スキーマ・本数・呼び口辺との向き・現在の受け口端点との幾何整合を検証し、妥当な経路だけ採用する。不正な経路だけを破棄して`autoRouteBars`へ戻し、破棄件数を警告する。保存バーが無い場合も自動経路を使う（監査#32）。
7. **仕上げ**: 保存テンプレートの各セルの`joins`から、モデルに取り込まれた結合を除く（モデルに反映できなかった結合の原文だけを残す）。主ファイルはオプションの`primarySourceKey`で明示した通常ソースとし、保存テンプレートはそのソースが編集可能な場合だけ採用する。編集不可主のimports・元情報は主から取得し、別の編集可能ソースのテンプレートで代用しない。それ以外（かつ非`generated`）を`referenceFiles`とする。一括読み込みは[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I]]の`sourceOrder`順で解析し、主ファイルを配列末尾へ移さない。主ファイルは読み取り専用でも役割を保持する。指定省略の旧補助呼び出しだけ従来の最後の`editable`ソースへフォールバックする。`TecscdeDocument.build`に渡して`LoadResult`を返す（2026-11-07、監査#16の契約更新）。

`loadSingle(text, fileName, editable = true)`は、テストと新規作成直後の1ファイル読み込み用の簡便な呼び出し。対象ソースのキーを`primarySourceKey`として渡す。

`primarySourceKey`の型は`string | null | undefined`とし、`undefined`だけを旧推定の互換経路に使う。 明示キーが通常ソースに存在しなければ構築を失敗させ、別ソースへ代替しない。現行`5cf2d85`にはこの追加項目と順序の契約は未反映（三者監査#5、2026-11-09、7I.0）。7Hの主ファイルなし復元は明示的な`null`として扱い、参照ソースを主ファイルに昇格させない（7I.3）。

## 4B.6 保存時の直列化（`CdlSerializer`）

詳細は[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約|4C ファイル別保存契約]]へ分離した（2026-11-07、25KB閾値による）。主ファイルも追加読み込みファイルも、`cell.editable && cell.locale === sourceKey`で定義元を選別する。`serialize(doc)`もこの契約に従う。結合・レイアウト・テンプレート・保存後検査の範囲と検証条件は4Cで定める。

## 4B.7〜4B.10 診断・断片・拡張点・気づいた点

[[TECSCDE-DT-EL内部仕様 - 04H CDLパーサの診断・断片・拡張点|4H]]へ分離した（2026-11-08、25KB閾値、逐語。節番号は変わらない）。

- **4B.7 診断** — 診断コード表（`G1015`・`G1016`・`W-*`・`E-TECSGEN-NOT-FOUND`）と、`location.file`の埋め方。
- **4B.8 クリップボード用の断片（`fragment.ts`）** — `serializeCellsAsCdl`の契約更新（2026-11-07）と`tryParseCdlFragment`。
- **4B.9 システム定義CDLの判定（実装済み）** — rendererのローダーが`systemDirs`と定義元パスからソース単位の編集可否を確定し、`Cell`へ渡す。
- **4B.10 実装を読んで気づいた点** — 仕様と実装のずれの候補6件（いずれも2026-10-22に解消済み）。

## 関連

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT-EL内部仕様 - 04H CDLパーサの診断・断片・拡張点|4H CDLパーサの診断・断片・拡張点]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章 モデル設計]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B 複合セルタイプ設計]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|7C 読み込み経路の統合]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|9B CdeclExtractor設計]]
- [[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計|TECSCDE内部仕様第4章]]
- [[TECSCDE-DT-EL実装]]

- [[TECSCDE-DT-EL内部仕様 - 監査対応 19-28 配列と配置]] — 該当する監査項目の契約補足（2026-11-09）。

- [[TECSCDE-DT-EL内部仕様 - 監査対応 29-38 保存と画面]] — 該当する監査項目の契約補足（2026-11-09）。
