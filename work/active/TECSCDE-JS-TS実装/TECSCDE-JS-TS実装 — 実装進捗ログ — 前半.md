---
date: 2026-08-30
description: TECSCDE-JS-TS実装の実装進捗ログ前半（2026-08-30〜09-01、モジュールI・A・H）。実装進捗ログから分割（25KB閾値、2026-09-14）。
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-JS-TS実装 — 実装進捗ログ 前半

[[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ|実装進捗ログ]]から分割（物理順を保持）。[[TECSCDE-JS-TS実装]]が本体。

### 026-08-30
- ブラウザでの動作確認が完了しました。開発サーバー(http://localhost:5183/)上で以下を実機確認しています(コンソールエラーなし)。

確認できたこと
- 起動時のUI(ツールバー、SVGキャンバス、セルタイプ一覧、プロパティパネル、ステータスバー)が正しく描画される
- 「サンプルを開く」→ public/samples/celltypes.cdl + main.cde を読み込み、3セル(cLogger1/cSensor1/cController1)・2結線がSVG上に正しくレイアウトされる
- セルクリック選択 → プロパティパネルに name/celltype/region が反映される
- セルのドラッグ移動 → 結線(join)が追従して再ルーティングされ、タイトルバーに未保存マーク●、ステータスバーに「未保存の変更があります」が出る
- 「元に戻す」(Undo)クリック → 位置・結線が完全に元通りになり、ボタンの活性/非活性が正しく切り替わる
- 「やり直す」(Redo)クリック → 移動後の状態に正しく復元される

これで npm run build のグリーン、Vitest 11件全パスに加えて、実ブラウザでの読み込み・編集・Undo/Redoの一連の動作も確認できました。

一方で、実装にあたり正直にお伝えしておきたい差分・スコープカットが何点かあります。

1. Undo/Redo設計の変更: 内部仕様書(すでにコミット済み)の5章は Command{apply, invert()} 方式を記載していましたが、実装では「初期状態 + 実行済みコマンド列を先頭から再生する」replay方式に簡素化しました。Ruby版6.6.1の既知の2バグ(初回Undo不可・Redo恒久無効)をテストで固定する狙いも兼ねています。ノート側は5章(コミット`800d601`)で更新済み。決定の経緯・検討した選択肢は[[work/active/tecs/TECSCDE Undo-Redo設計決定|Decision Record]]に記録しました。
2. ~~CDL文法・メッセージカタログは簡易実装: tecsgen本来の文法ではなく、検証に必要な範囲のサブセットです(コード内コメントに明記済み)。~~ → **2026-09-13、記述が誤りだったと判明し訂正**: 実態は「サブセット」ではなく**別方言**で、保存した`.cde`はtecsgenに入力できなかった（外部仕様2.2違反）。tree-sitter移行で解消（実装進捗ログ 後半の2026-09-13の項）。メッセージカタログの簡易実装は継続。
3. 未実装/簡略化した機能（2026-09-01時点）:
   - ~~MoveJoinBarCommand(結線の中間点を直接ドラッグして経路変更)は未実装~~ → **2026-09-01実装完了**。モデル層(`moveBar`, geometry.ts)・コマンド層(`moveJoinBar`, joinOps.ts)・ドラッグジェスチャー(gesture.ts)・プレビュー描画(svgRenderer.ts)まで一気通貫で配線し、テスト8件追加。コミット`8b86f8a`
   - ChangePortEdgeCommand（`movePort`/`changePortEdge`、portOps.ts）はモデル/コマンド層のみ実装・テスト済みで、UIからの操作導線は依然未配線（この点は変わらず）
   - プロパティパネルでの複数セル一括編集は未対応
   - OSクリップボード連携(コピー&ペーストは内部クリップボードのみ)、PDFエクスポート、複合セルタイプの本格対応(検出はするが「非対応」警告のみ)は対象外
4. ~~内部仕様11章のdependency-cruiserによるモジュール境界強制は未実装~~ → **2026-09-14、モジュールH実装にて完了**（`.dependency-cruiser.cjs`で2章の依存グラフを機械的強制、`npm run depcruise` 52モジュール・148依存で0違反）。
5. ~~E:\Ccur\typescript\TECSCDE はまだgit初期化していません~~ → **誤り、訂正**: 実際には初回コミット`3f7ecd9`（初期実装一式）が既に存在しており、git初期化・初回コミットは完了済みだった。2026-09-01、MoveJoinBarCommand一式を`8b86f8a`としてコミット。

### 2026-09-14 — モジュールI（tecsgen連携 / tecsgen-link）実装完了

TECSCDE内部仕様 第10章および外部仕様 第8.4節に基づくtecsgen実行コマンド文字列組み立て、空白クォート処理、免責事項表示（モジュールI: 葉ノード・副作用なし・非実行）の実装を完了。

1. **コマンド文字列組み立て（`src/tecsgen-link/commandBuilder.ts`、外部仕様8.4.2 / 内部仕様10.1）**:
   - `TecsgenCommandBuilder.buildArgs`: ~~`baseDir`（`-I <base_dir>`）~~、`importPath`（`-I <import_path>...`）、`defineMacro`（`-D <macro>...`）、`referenceFilePaths`（`direct_import` 相当の参照専用ファイル群）、および `editingFilePath`（編集対象ファイル）を正規の引数配列として構築。→ **2026-09-14 訂正**: `baseDir`を`-I`で渡すのは誤りだった（`-I`は`--import-path`用であり、`base_dir`に対応するCLIオプションは存在しない、[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 08 CDL 連携#8.4.2 JS 版の規定]]参照）。同日中に`baseDir`をCLI引数から除外し、代わりに`cpp`（`-c <cpp>`）を追加、`baseDirHint()`で文脈情報としてのみ提示するよう修正（経緯: [[work/archive/2026/TECSCDE-TS モジュールI 二重実装の保留|TECSCDE-TS モジュールI 二重実装の保留]]）。
   - `TecsgenCommandBuilder.buildCommandLine`: 空白を含むパスを適切にダブルクォート（`quoteIfNeeded`）で囲み、利用者が端末でそのまま実行可能な完全なコマンドライン文字列を生成。
   - `buildTecsgenCommand`: `TecscdeDocument` からワンショットでコマンド文字列を組み立てるラッパー関数。
2. **免責事項の明記（`TECSGEN_DISCLAIMER`、外部仕様8.4.2）**:
   - 「このコマンドはローカル環境でtecsgenを実行するための提示のみです（実行はしません）。本ツールはCDLの構文的・参照的な整合性のみを確認しており、tecsgenが実際にこのCDLを受理するかどうかは保証しません。実行結果はtecsgen自身のエラー出力を確認してください。」の定型文言を提示。
3. **公開API構成（`src/tecsgen-link/index.ts`）**:
   - モジュールIの全公開関数・型・定数を `src/tecsgen-link/index.ts` から一元エクスポート。
4. **テスト追加・検証**:
   - `tests/tecsgenLink.commandBuilder.test.ts` (4テスト) を追加。
   - Vitest 全26テストスイート（105テスト）オールグリーン、`npm run check`（型チェック・Viteビルド・テスト・depcruise 55モジュール0違反）正常終了（0エラー）。

### 2026-09-14 — モジュールA（ファイルI/O / File I/O & Export）実装完了

TECSCDE内部仕様 第8章および外部仕様 第5章（5.1〜5.7）に基づくファイル読み込み・UTF-8/旧形式検証、保存（File System Access API & フォールバック）、SVG/PNGエクスポート（用紙/内容範囲選択・高解像度倍率）、印刷用CSS（@media print）の実装を完了。

1. **ファイル読み込み・入力検証（`src/io/fileOpen.ts`、外部仕様5.1.2 / 5.3.2 / 8.1.2 / 内部仕様8.1）**:
   - `validateCdlSourceText`: UTF-8以外の不正文字（Unicode置換文字 `\uFFFD`）や旧世代のサイドカー構文 `__location_information__` を検出して明確なエラーメッセージを提示。
   - `readFilesAsSources` / `readFileText`: `file.text()` および `FileReader.readAsText` フォールバックによる複数ファイル読み込み。最後の1ファイルを編集対象（`editable: true`）、それ以前を参照専用（`editable: false`）として確定。
   - `setupFileInput` / `setupDropTarget`: `<input type="file" multiple>` およびキャンバスへのドラッグ＆ドロップイベント処理。
2. **保存・名前を付けて保存（`src/io/fileSave.ts`、外部仕様5.4.2 / 内部仕様8.2）**:
   - `canUseFileSystemAccess`: `showOpenFilePicker` / `showSaveFilePicker` の有無を判定。
   - `saveDocumentFile`: 取得済みハンドルがあれば上書き保存、なければ（または名前を付けて保存時は）Pickerでの保存またはブラウザダウンロードへ安全にフォールバック。書き込み完了まで既存データを破壊しない。
3. **エクスポート（`src/io/exporter.ts` / `src/style.css`、外部仕様5.6.2 / 内部仕様8.3）**:
   - `exportSvg`: SVG（第一形式）のダウンロード。不要な選択枠・プレビューを除去し、「用紙に合わせる（`scope: "paper"`）」または「図の内容に合わせる（`scope: "content"`、`computeContentBBox`）」による矩形調整に対応。
   - `exportPng`: SVGをCanvas経由で高解像度ラスタライズ（出力倍率 `scale: 2` 等対応）し、PNG Blobとしてダウンロード。
   - `@media print`: ブラウザ標準の印刷機能で図全体を1ページに収めてPDF出力可能にする印刷専用CSSスタイルシートを追加。
4. **公開API構成（`src/io/index.ts`）**:
   - モジュールA（`fileOpen` / `fileSave` / `exporter`）の全公開関数・型を `src/io/index.ts` から一元エクスポート。
5. **テスト追加・検証**:
   - `tests/io.fileOpen.test.ts` (4テスト), `tests/io.fileSave.test.ts` (4テスト), `tests/io.exporter.test.ts` (3テスト) を追加。
   - Vitest 全25テストスイート（101テスト）オールグリーン、`npm run check`（型チェック・Viteビルド・テスト・depcruise 54モジュール0違反）正常終了（0エラー）。

### 2026-09-14 — モジュールH（整合性チェック・診断 / dependency-cruiserモジュール境界強制）実装完了

TECSCDE内部仕様 第2章・第9章・第10章・第11章および外部仕様 第8.3節・第9章に基づく診断集約層、オンデマンド整合性チェック（8項目）、tecsgen結果パーサ、および `dependency-cruiser` によるモジュール境界の機械的強制（モジュールH）の実装を完了。

1. **整合性チェック（`src/diagnostics/integrity.ts`、外部仕様8.3.2 / 9.2.2 / 内部仕様9.1）**:
   - `checkIntegrity(doc: TecscdeDocument)`: ドキュメントの現在状態から再導出可能な不整合を全走査:
     - `W-UNRESOLVED-CELLTYPE`: 未解決セルタイプの残存
     - `W-UNRESOLVED-REF-FILE`: `__tool_info__("tecsgen").direct_import` 参照専用ファイルの未読込
     - `W-DUP-CELL`: セル名の重複
     - `W-CELL-OUT-OF-BOUNDS`: 用紙描画領域（余白除く実効領域）外へのセル配置
     - `W-MISSING-JOIN-TARGET` / `W-JOIN-PORT-NOT-FOUND`: 結合先セル・ポートの不在
     - `W-SIGNATURE-MISMATCH`: 結合ポート間のシグニチャ不一致
     - `W-DUPLICATE-JOIN`: 同一呼び口・受け口間の重複結合
     - `W-REQUIRE-PORT-HIDDEN`: require指定呼び口の非表示
2. **診断集約層（`src/diagnostics/collector.ts` / `src/diagnostics/index.ts`、内部仕様9.1 / 9.2）**:
   - `DiagnosticsCollector`: 複数発生源からの診断を随時集約する可変コレクタ。
   - `buildReport` / `DiagnosticReport`: error を warning より前に安定ソートし、1件の集約レポート（外部仕様8.3.2要件）として提供。
3. **tecsgen結果パーサ（`src/diagnostics/tecsgenResultParser.ts`、外部仕様9.1.1 / 9.3.1）**:
   - `TecsgenResultParser.parse`: tecsgen の標準出力・標準エラー出力を解析し、位置情報（`file:line:col`）およびメッセージ先頭のコード（`G1016`, `S1109`等）を分離して `Diagnostic[]` を生成。
4. **UIジャンプナビゲーション連携（`src/ui-shell/dialogs.ts` / `src/app/main.ts`）**:
   - 診断一覧モーダルからセルへのジャンプ（選択＋ビューポート中央フォーカス）および結合（Join）へのジャンプ選択を完全配線。
5. **モジュール境界の機械的強制（`.dependency-cruiser.cjs`、内部仕様第2章2.2 / 第10章10.2 / 第11章11.1）**:
   - C(model) の完全孤立・中核性、D(commands) のモデル限定操作、H(diagnostics) の読み取り専用オブザーバ性、F(view-state) の独立性、I(tecsgen-link) の葉ノード性、E(render) / G(ui-shell) / A(io) の依存制約を8つの厳格ルールとして定義。
   - `npm run check`（`build` + `test` + `depcruise`）で52モジュール・148依存の境界違反0件を検証。
6. **テスト追加・検証**:
   - `tests/diagnostics.collector.test.ts` (2テスト), `tests/diagnostics.integrity.test.ts` (5テスト), `tests/diagnostics.tecsgenResultParser.test.ts` (3テスト) を追加。
   - Vitest 全22テストスイート（90テスト）オールグリーン、`npm run check`（型チェック・Viteビルド・テスト・depcruise）正常終了（0エラー）。

## Related
- [[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ|実装進捗ログ]] — 索引
- [[TECSCDE-JS-TS実装]]
