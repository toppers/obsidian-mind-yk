---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第3章（モデル設計）— TECSCDE-TS内部仕様を基本とし、複合セルタイプは3B章で拡張。rendererプロセスで動作。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 3 of 11。

## 3. モデル設計

`Cell`・`Port`（`CPort`/`EPort`）・`Join`・`Region`・`RegionTree`・`TecscdeDocument`のクラス設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様第3章]]と**複合セルタイプを除き同一**。第2章2.3節で述べたとおり本モジュール（C）はrendererプロセスで動作し、Node.js APIへの依存を一切持たない——これはブラウザ版（TECSCDE-TS内部仕様）から変更する理由がないことの裏付けでもある。

複合セルタイプのモデル、未対応構文フラグ、外側セルへの適用は[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B章]]で定める。

その他の詳細は[[TECSCDE-TS内部仕様]]第3章を参照。

### 3.1 TECS CDL組込型の解析

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.1節]]に従い、署名の関数の戻り値・引数とCDL内の`typedef`に現れるTECS CDL組込型を、Cヘッダの定義に依存せず解析する。対象は`void`、`bool_t`、`char_t`、`schar_t`、`uchar_t`、`int8_t`、`int16_t`、`int32_t`、`int64_t`、`int128_t`、`uint8_t`、`uint16_t`、`uint32_t`、`uint64_t`、`uint128_t`、`float32_t`、`double64_t`の17種類とする。

`cdl/signature-types.ts`はこれらを`CType`の`primitive`として生成し、型名を`primitive.name`に保持する。幅や符号の異なる型を別の型として扱い、ヘッダ由来の`typedef`がなくても`CTypeRegistry`で解決できるようにする。`defined`（未解決の型名参照）へ変換して`W-C-TYPE-UNRESOLVED`を出してはならない。

`int_t`、`uint_t`、`long_t`、`ulong_t`、`short_t`、`ushort_t`は組込型に含めない。これらはCDL内の`typedef`または`import_C`の定義を用いて通常の型名として解決し、定義が見つからない場合にのみ未解決型として診断する。

### 3.2 セルの区別属性（`editable`と`systemDefined`、2026-10-21。2026-10-22に実装）

`Cell`は、編集可否の`editable`に加えて、**`systemDefined: boolean`**（システム定義CDLで定義されたセルか）を`readonly`フィールドとして持つ。`Cell.create()`は両方を引数で受け取り、保持するだけで、判定はしない（TS内部仕様第3章3.3節#5と同じ分担）。

| フィールド | 意味 | 決まり方 |
|---|---|---|
| `editable` | 編集・削除・保存の対象にできるか | 通常CDLは`true`。Plugin生成セルは`false`。`systemDefined`かつ`allowEditSystemDefined=false`なら`false`（**ソース単位**で決める。下記） |
| `systemDefined` | `-S`で指定されたディレクトリ配下のCDLで定義されたか | 定義元パス（`locale`のファイル）が`systemDirs`のいずれかの配下か。主ファイルか追加読み込みファイルかとは独立 |

- **判定の置き場所**（2026-10-22実装）: `CdlDocumentLoader.loadSources()`（第7C章7.7.4節）が、`LoadOptions.systemDirs`と各`CdlSource.sourcePath`から`systemDefined`を決め、セルの生成時に渡す。パス比較の`isUnderAny(path, dirs)`は、依存の無い純粋関数として`shared/path-under.ts`に置き、main・rendererの両方から使える（当初案の「mainで比較して結果をrendererへ渡す」は採らなかった。`OpenFileEntry`に判定結果を載せる変更が要らず、`import`自動追跡など開く経路がいくつあってもローダーの1か所で済むため）。Windows形式のパス（ドライブ文字、UNC）は大文字小文字を区別せずに比べる。
- **編集可否はソース単位で決める**（2026-10-22）: `systemDefined`かつ`allowEditSystemDefined=false`のソースは、`CdlSource.editable`ごと`false`にする。セル単位で`editable=false`にしない理由は、編集可能なソースはテンプレートを持ち、保存時（`serializeFromTemplate`）にテンプレートのセルをすべて削除して編集可能なセルだけを書き戻すため、編集不可のセルが混ざると、そのセルが保存で消えるから。編集不可のソースはテンプレートを持たないので、書き戻しの対象にならない。主ファイルが閲覧のみのときは、保存を行わない（`AppStore.isEditingFileReadOnlySystemDefined()`）。
- **設定**（2026-10-22実装）: `allowEditSystemDefined`は`settings.json`（`AppSettings`）の真偽値で、既定は`false`。rendererは起動時にIPC `settings:get`で一度読み、`AppStore`に保持する。設定画面は無い（外部仕様2.5節）。
- **表示**（2026-10-22）: `systemDefined`のセルのSVG要素に`system-defined`クラスを付ける。編集不可のため、既存の`readonly`の見た目になる。形状や記号による追加の区別は未決。
- **`editable`の算出**: `editable = 通常の規則 && !(systemDefined && !allowEditSystemDefined)`。`allowEditSystemDefined`は`AppSettings`の真偽値で、既定は`false`（名前・置き場所は提案、未確定）。`true`にすると`systemDefined`のセルも通常CDLと同じ`editable`になる。
- **コマンド・保存との関係**: `editable=false`のセルは、既存の編集コマンドの前提条件（編集不可セルは対象外）と`CdlSerializer.serializeSource()`の書き戻し対象外に、そのまま従う。`systemDefined`自体は編集可否を直接参照せず、`editable`の算出にだけ使う。表示上の区別は第5章の描画仕様で別途定める。
- **テスト（実装時）**: 配下・入れ子・兄弟ディレクトリの接頭辞一致（`/sys`と`/sysx`）・Windowsの大文字小文字・相対`-S`・`-S`なし・主ファイルが配下にある場合・`allowEditSystemDefined`の切り替え。

### 3.3 リージョン木とセル所属の反映（2026-10-21、ソースの確認に基づく）

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05A 開く（読み込み）|DT外部仕様5.3節]]の「リージョンの読み込み」「所属変更と保存」に対応する実装の構造と規則。クラス設計（`Region`・`RegionTree`・`Cell.regionId`）は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様第3章]]と同一で、DT-ELは構築・復元・変更・保存の規則を加える。根拠は`model/region.ts`、`cdl/cst.ts`、`cdl/document-builder.ts`、`cdl/serializer.ts`、`commands/cell-commands.ts`、`commands/clipboard-commands.ts`、`app/property-panel.ts`の読解（テストは読んでいない）。

**表現**: `Region.id`と`namespacePath`は同じ文字列（ルートは`"::"`、入れ子は`"::A::B"`）。`Cell.regionId`はその文字列。`RegionTree`は、各`Region.cellIds`を`Cell.regionId`の逆引き索引として持ち、`TecscdeDocument.withCell`が`assignCell`、削除が`removeCell`で同期する。`namespace`と`region`は、CDL上は別の構文だが、どちらも入れ子の**スコープ**として同じように木に載せる（外部仕様4.8でネームスペースをリージョンの識別子に統合している）。

**木の構築**（`CdlDocumentBuilder`が`scopes`を返し、`CdlDocumentLoader`が合成する）:
1. 読み込んだ**全ソース**の`scopes`から、各スコープのパスとその祖先をすべて`regionPaths`に集める。`editable`なソース由来のものは`editableRegionPaths`にも集める。ルート`"::"`は常にある。
2. `regionPaths`の親子関係から木を作る（`buildRegionTree`。子はパスの辞書順）。各`Region.cellIds`は、`regionId`が自分のパスのセルとする。**リージョン宣言はファイル別ではなく、全ファイル分を1本の木にまとめる**。

**セルの所属の決定**（`loadSources`の1周目、セルごと）: 優先順位は次のとおり。
1. **CDLのスコープ**: セルが`namespace`／`region`の中に書かれていれば、そのスコープのパス（`CellDecl.regionPath`）。外部仕様の「セルの所属はCDLのスコープを優先する」に対応する。
2. **`tool_info`の所属情報**: セルがCDLのルート直下に書かれている場合に限り、`__tool_info__("tecscde")`の`cellList[セル名].region`を見る。その値が、**`editable`なソースなら`editableRegionPaths`**、そうでなければ`regionPaths`に存在すれば採用する。
3. それ以外はルート。
4. `tool_info`の所属情報があって、採用した所属と違うときは、警告`W-REGION-MISMATCH`を出す。

> [!note] 外部仕様との整合（2026-10-22、実装を正として外部仕様5.3節を改めた）
> 外部仕様は以前「`tool_info`の所属情報を、セルの定義元ファイルに存在するリージョンに限って復元する」と書いていたが、実装は定義元ファイルではなく、上の2.のとおり**`editable`なソースなら`editable`なソース全体のスコープの和集合、そうでなければ全ソースのスコープ**に対して存在を確認する。外部仕様をこの実装の規則に改めた（単一ファイルの読み込みでは両者の結果は同じ）。別ファイルにだけあるリージョンを`tool_info`が指していても復元する。その状態で保存すると、下の「保存」の2.の検査で例外になりうる点は、実装の既知の振る舞いとして残る（動作は未確認）。`tool_info`の所属情報（`cellList`）は、まずそのセルの定義元ファイルの`tecscde`ブロック（`layoutsBySource`）から読む。そのファイルが自前の`tecscde`ブロックを持たないときは、`?? tecscdeParsed`により**最後に読んだ他ファイルの`tecscde`ブロック**の値を使う。同名セルがあると他ファイルの所属情報が混じりうるが、これも外部仕様5.3節に実装どおり記載した（読解のみ、動作は未確認）。

**所属変更**（外部仕様の「所属変更」）:
- **UI**（`property-panel.ts`）: `region`の選択肢は木全体（ルートと全スコープ）。ただし、ルート以外で、**そのセルの定義元ファイルの`sourceTemplate.scopes`に無いスコープは選択不可（`disabled`）**。セルが`editable`でなければ、セレクト全体が無効。外部仕様の「ルートまたはそのセルの定義元CDLファイルに存在するリージョンから選択する。別ファイルにのみ存在するリージョンは変更先にしない」に対応する。
- **コマンド**（`ChangeRegionCommand.apply`）: セルが無い、`editable`でない、所属が同じ、移動先のリージョンが木に無い、のいずれかなら何もしない。移動先がルート以外で、定義元ファイルの`sourceTemplate.scopes`に無い場合も何もしない（UIの無効化と同じ検査を二重に持つ）。定義元のテンプレートが無い場合（新規作成など）は、木にあれば許す。
- **提供しない操作**: リージョンの新規作成・改名・削除・移動のコマンドは存在しない（外部仕様と一致）。

**セルの新規作成と貼り付け**: 新規セルの所属はルート。貼り付けたセルは、コピー元の所属を引き継ぐが、貼り付け先のファイルの`sourceTemplate.scopes`にそのスコープが無ければルートにする（`clipboard-commands.ts`）。

**保存**（`CdlSerializer`、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計|4B.6]]）:
1. 各セルの`regionId`が木の`cellIds`に含まれていることを確かめる。食い違いは例外「リージョン所属が不整合です」。
2. セルの移動先スコープが、保存先ファイルの`sourceTemplate.scopes`（ルートを除く）に無ければ例外「保存先リージョンが編集ファイルにありません」。
3. 元のセル範囲を削除し、**移動先スコープの本体末尾（`bodyEndIndex`）に挿入**する（ルートはファイル末尾）。セルの直前のコメントはセルについていく（`leadingText`）。リージョン宣言とそれ以外の原文には手を触れない（往復保持）。
4. `tecscde`ブロックの`cellList`には、各セルの`regionId`を`region`として書く（CDLのスコープと重複して持つ。読み込みではCDLのスコープが優先）。
5. 書き出した結果を再解析し、構文エラー、セル数、**各セルの所属の復元**（`expected`と`regionPath`の一致）を検査して、不一致なら例外にする。

> [!note] 既知の限界
> 保存時の失敗は例外（診断ではない）で、利用者へどう提示するかは、呼び出し側に依存する。上の「外部仕様との差」にある状態（別ファイルにしかないリージョンへの復元）が、保存時にどう失敗するかは確認していない。

### 3.4 C型抽出結果の接続とポート型解決（2026-10-21、ソースの確認に基づく）

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|DT外部仕様8.1節]]は、`import_C`のCヘッダを**型情報の入力**とし（編集対象のセルは生成しない）、Cプリプロセッサがあれば展開結果から、無ければ`typedef`／`struct`の抽出へフォールバックして取り込み、**どちらでも解決できなかった型は未解決として警告する**、と定める。結合の可否はシグニチャの一致で判定する（TECSCDE外部仕様4.5節）。本節は、抽出結果（`CdeclResult`）が読み込みへどう接続され、ポートの型にどう使われるかの構造を示す。根拠は`app/import-resolution.ts`、`app/file-actions.ts`、`cdecl/type-registry.ts`、`cdl/document-builder.ts`、`cdl/port-type-index.ts`、`commands/join-commands.ts`、リポジトリの設計メモ`docs/design/import-c-port-type-resolution.md`の読解（テストは読んでいない）。

**データの流れ**:
```
resolveImportClosure（7E）──import_C──▶ ingestImportC
    cpp実行（成功: 展開後 / 失敗・無: 生テキスト＝フォールバック→W-CPP-FALLBACK）
    └▶ CdeclExtractor.extract（9B）→ CdeclResult（typedefs・structs・hasErrors・usedFallback）
        hasErrorsなら W-CDECL-PARSE。抽出できた宣言は捨てない
    └▶ Map<正規化ヘッダパス, CdeclResult>（cdeclResults）
file-actions（applyOpenResult・addAsReference）──{ cdeclResults }──▶ CdlDocumentLoader.loadSources
    ① 全ソースを解析し、署名と CDL内typedef を集める
    ② CTypeRegistry（全ヘッダの typedef・struct ＋ CDL内typedef を先に集約）
    ③ 署名ごとに関数の戻り値・引数を解決 → ResolvedSignatureType
    ④ セルタイプのポートの署名参照を解決 → PortTemplate.signature を正規化、ResolvedPortType
    ▶ LoadResult.portTypeIndex ──▶ AppStore（loadDocument の引数）
```

**`CTypeRegistry`**（`cdecl/type-registry.ts`）: 型の優先順位が読み込み順で決まらないよう、**全ヘッダの`typedef`・`struct`と、CDL内の`typedef`を、解決の前にすべて集約する**。同名で内容（JSON表現）が異なれば競合として記録し、解決時に競合した名前だけを未解決にする（両方の由来ヘッダを理由に表示）。完全に同一の定義の重複は許す。解決は、プリミティブ（CDL組込型17種を含む。3.1節）はそのまま、`defined`はtypedefを再帰展開、ポインタ・配列・関数・`struct`は要素を再帰して解決し、**未定義の名前、競合、循環、未対応のC型**のいずれかで`reason`を返して未解決にする。`TypeResolution`は、解決後の型、由来ヘッダ一覧、フォールバック由来かどうか、未解決の理由を持つ。

**署名とポートの解決**（`loadSources`）:
- **署名**: 関数本体を持つ`signature`だけを署名表（完全修飾名）に入れる。各関数の戻り値・引数を`CTypeRegistry`で解決し、未解決の使用箇所ごとに警告`W-C-TYPE-UNRESOLVED`（位置は型の使用箇所）を出す。`ResolvedSignatureType.valid`は、全関数の戻り値・引数が解決できたときだけ真。
- **ポート**: 署名名を、ポートを宣言したスコープから外側へ探索して完全修飾名（署名ID）に解決する（`::`で始まる名前はルートから）。解決できなければ警告`W-PORT-SIGNATURE-UNRESOLVED`を出し、**ポートは原文の署名名のまま図に残す**。解決できたら`PortTemplate.signature`を`::`付きの署名IDに正規化し、`PortTypeIndex.ports`に「セルタイプ名・方向・ポート名」をキーとして署名IDと`valid`を記録する。
- **失敗しても読み込みは止めない**: 未解決の型・署名があってもセル、ポート、既存の結合は表示し、問題は診断にだけ出る。`CType`自体は`CPort`／`EPort`にもシリアライザの保存形式にも複写しない。

**結合の可否との関係**: 結合の可否は、`cport.signature === eport.signature`の**文字列比較**（`commands/join-commands.ts`の結合コマンド、`render/gesture-controller.ts`の結合候補判定）のままである。署名名がポートの宣言時に完全修飾IDへ正規化されているため、同じ署名を指す両側はIDで一致し、異なる名前空間の同名署名は区別される。解決できなかった側は原文の文字列で比較される（移行規則）。**C型の構造は結合の可否に使わない**——C型の解決結果は、警告の発生と`PortTypeIndex`の`valid`にだけ反映される。

> [!note] 外部仕様との整合と、読解で気づいた点
> - 外部仕様の「どちらの経路でも解決できなかった型は未解決として警告する」「組込型には未解決の警告を出さない」「結合はシグニチャの一致で判定する」は、実装と一致している。
> - **`PortTypeIndex`の読み手が`src`に無い**（2026-10-22に「将来の利用を見込んだ予約」と決めた。削除しない。データの流れ=ローダー→`file-actions`→`AppStore`は維持し、読み手は未実装のまま。読むのはテストだけ）: `AppStore.getPortTypeIndex()`は定義だけで、呼び出しが見当たらない。C型の解決状態（`valid`・由来ヘッダ）は、結合の可否にも画面にも使われておらず、可視の効果は読み込み時の警告だけである。
> - **フォールバック由来の伝達**（2026-10-22に「`CTypeRegistry`内部の伝播のみ」と決めた。利用者への伝達は、別の`W-CPP-FALLBACK`が担うので、`TypeResolution.fallback`を読む処理は足さない）: 設計メモは「利用したポート型にもフォールバック由来の状態を伝える」としているが、`TypeResolution.fallback`は`CTypeRegistry`の内部で伝播するだけで、ローダー（`document-builder.ts`）を含め、`src`に読む箇所が無い（利用者には伝わらない）。
> - **第8章の整合性チェックへの接続**: `diagnostics/integrity.ts`は`PortTypeIndex`を使わない。第9B章が「未設計」としていた第8章への接続は、読み込み時の警告として実現しており、整合性チェックの独立した項目はない。
## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様 第3章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（本モジュールのプロセス配置根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
