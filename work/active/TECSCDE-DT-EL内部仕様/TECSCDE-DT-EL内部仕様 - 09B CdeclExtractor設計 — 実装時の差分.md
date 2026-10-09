---
date: 2026-09-23
description: "[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|第9B章]]（CdeclExtractor設計）の9B.7節を分離したイベントログ的サテライト。設計案から実装時に判明した8件の差分（クラス設計・API形状・グローバル初期化の競合・文法の実際の挙動等）。9B章から分離（25KB閾値）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章]] (2026-09-23、25KB閾値)。9B.1〜9B.6の設計本体はverbatimで元ファイルに残置、本節（9B.7）のみ分離。

### 9B.7 実装時の差分（2026-09-23、`E:\Ccur\typescript\TECSCDE-DT-EL`）

上記9B.3〜9B.6の設計案から、実装時に実際のリポジトリ・文法の挙動を確認して変更した点。

| #   | 設計案                                                                      | 実装での実際                                                                                                                                                                                                                                                                                | 理由                                                                                                                                                                                                             |
| --- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `initCdeclParser()`等の関数スタイル（JS-TS実装を参考）                                  | `CdeclGrammar`静的クラス（`init`/`isReady`/`parserInstance`/`resetForTest`）                                                                                                                                                                                                                 | DT-EL実装の実際の`CdlGrammar`（`src/renderer/cdl/grammar.ts`）が既に静的クラスだった。9B.3は参照元を取り違えていた                                                                                                                             |
| 2   | `CdeclExtractor.extract(tree: Tree)`                                     | `CdeclExtractor.extract(text: string)`（内部で`CdeclGrammar.parserInstance.parse()`）                                                                                                                                                                                                      | `CdlDocumentBuilder.build(text)`が同じ「テキストを受け取り内部でparseする」慣習だったため合わせた                                                                                                                                            |
| 3   | `Diagnostic`をクラスとして`Diagnostic.warning(code, message)`で生成                | `Diagnostic`はプレーンなinterface。生成は`cdl/messages.ts`のファクトリ関数（`cppFallback()`・`cdeclParseError()`、`W_CODES.CPP_FALLBACK`/`W_CODES.CDECL_PARSE_ERROR`）に委ねる                                                                                                                                  | 実装のDiagnostic型がそもそもクラスではなかった。extractor.ts自体はヘッダパスを知らないため、診断生成はヘッダパスを持つ呼び出し側（`import-resolution.ts`）に置き、`CdeclExtractor.extract()`は`hasErrors: boolean`だけを返す                                                    |
| 4   | WASM資産を`/wasm/tree-sitter-tecs_cdecl.wasm`へ直接fetch                       | main→IPC（既存`cdl:grammar-assets`チャネルを拡張、`CdlGrammarAssetBytes.cdeclWasm`追加）でバイト列を受け取る                                                                                                                                                                                                  | 第11章11.5節#7で確定済みの実装差分（rendererの`file://` fetchがCORSで塞がれる）と同じ理由。既存のCDL文法と同じ起動シーケンスに乗せた                                                                                                                          |
| 5   | （未検討）`CdlGrammar.init()`と`CdeclGrammar.init()`を並列実行                      | 両方を**逐次**awaitする（`Promise.all`禁止）                                                                                                                                                                                                                                                     | web-tree-sitterの`Parser.init()`はEmscriptenランタイムをグローバルに初期化するため、2つのinit()を並列実行すると競合し、後段の`Language.load()`が「Incompatible language version 0」で失敗することを実測で発見（`tests/setup.ts`・`main.ts`の両方で修正）                       |
| 6   | `struct_declarator.childForFieldName("declarator")`で子の`declarator`ノードを取得 | フィールド名に頼らず`namedChildren.find(c => c.type === "declarator")`で取得                                                                                                                                                                                                                       | 実際の`tree-sitter-tecs_cdecl.wasm`では、bitfieldを伴わない`struct_declarator`の`declarator`子に**フィールド名が付与されていない**（`fieldNameForChild(0)`が`null`）ことを実測で発見。node-types.jsonの`fields.declarator`（`required: false`）は誤解を招く記載だった |
| 7   | `resolveStructSpecifier`はタグ無し（無名struct）に対し`undefined`を返す                 | タグとmembersを別々に返す`resolveStructSpecifierMembers()`へ分割。無名structでも`members`は返し、レジストリ登録（タグ必須）は呼び出し側で判断                                                                                                                                                                                    | `typedef struct { ... } Name;`（無名structのtypedef）で`resolveDeclarationSpecifiers`が呼ぶ際にmembersが失われるバグとして発覚（テストで検出）                                                                                                |
| 8   | `import-resolution.ts`の関数群への影響を明示せず                                      | `resolveImportClosure`/`resolveAllImports`/`resolveAddedReference`に`tecsgenGateway: TecsgenGateway`パラメータを追加、戻り値に`cdeclResults: Map<string, CdeclResult>`を追加。`file-actions.ts`（`applyOpenResult`/`openFromPath`/`addAsReference`/`loadOptionsFile`）・`main.ts`・`shell.ts`まで連鎖的にパラメータを追加 | `TecsgenGateway.preprocess()`を呼ぶには、IPCゲートウェイをrenderer側のオーケストレーション層まで橋渡しする必要があった。既存の`AppShell`が既に`this.tecsgen`を保持していたため、末端の橋渡しは1行追加ずつで済んだ                                                                      |

すべて[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]の該当箇所にも反映済み。実装は279テストpass・`npm run check` green（2026-09-23）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章（設計本体、本ノートの分離元）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（統合先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]
