---
date: 2026-08-30
description: TECSCDE-JS-TS実装の実装進捗ログ（モジュールA〜I全9モジュール、dependency-cruiser境界強制、tree-sitter移行、2026-08-30〜2026-09-14）。TECSCDE-JS-TS実装.mdから分割（25KB閾値、2026-09-14）。
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-JS-TS実装 — 実装進捗ログ

[[TECSCDE-JS-TS実装]]の実装進捗を日付順に記録するログ。本体が25KB閾値を超えたため分割（2026-09-14）。

## 実装進捗
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
2. ~~CDL文法・メッセージカタログは簡易実装: tecsgen本来の文法ではなく、検証に必要な範囲のサブセットです(コード内コメントに明記済み)。~~ → **2026-09-13、記述が誤りだったと判明し訂正**: 実態は「サブセット」ではなく**別方言**で、保存した`.cde`はtecsgenに入力できなかった（外部仕様2.2違反）。tree-sitter移行で解消（下記2026-09-13の項）。メッセージカタログの簡易実装は継続。
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

### 2026-09-14 — モジュールG（UIシェル / UI Components & Shell）実装完了

TECSCDE内部仕様 第2章・第3章・第6章・第9章および外部仕様 第3章・第6.5節・第9.3節に基づくプロパティパネル詳細、セルタイプパレット、各種ダイアログ/モーダル、ステータスバー表示（モジュールG）の実装を完了。

1. **プロパティパネルの拡充（外部仕様3.4 / 内部仕様3.4）**:
   - **未選択時**: ドキュメント統計（セル数、結合数、セルタイプ数、編集対象CDLファイル名）および用紙サイズ（A4/A3/B5/B4/Letter）・用紙向き（縦/横）ドロップダウンを表示。用紙変更時は Undo/Redo 可能な `changePaper` コマンドをディスパッチ。
   - **単一セル選択時**: 名前（読み込み専用時は色のみに頼らず `🔒 読み込み専用` テキスト明記）、セルタイプ、所属リージョンドロップダウン、属性キー・値リスト、ポート設定一覧（呼び口/受け口/配列/シグニチャ）を表示。
   - **複数セル選択時**: 選択セル総数・編集可能セル数表示、上端揃え・左端揃えボタン、一括リージョン変更、共通属性一括編集を提供。
   - **結合選択時**: 始点セル・ポート・シグニチャ、終点セル・ポート・シグニチャ、セグメント数表示、および結合削除ボタンを提供。
2. **セルタイプパレット（外部仕様3.3 / 内部仕様3.3）**:
   - セルタイプ一覧（名称、受け口・呼び口数）を表示。クリックで新規セル作成モードへ移行。
   - 各セルタイプ行に詳細情報ボタン（`ℹ`）を設置し、クリックで定義メタデータ、呼び口・受け口一覧（シグニチャ・配列長）、属性一覧を表示する詳細モーダル（`showCelltypeDetailModal`）を展開。
3. **各種ダイアログ・モーダル（外部仕様3.8 / 9.3 / 内部仕様9.3）**:
   - `showCelltypeDetailModal`: セルタイプ詳細（ポート、シグニチャ、属性定義）の閲覧モーダル。
   - `renderDiagnosticsList`: 診断メッセージ一覧（深刻度アイコン、対象セル/位置、メッセージ内容）のテーブル表示と対象セルへのジャンプナビゲーション。
   - 未保存破棄確認（`confirmDiscard`）および tecsgen コマンド実行設定ダイアログ（`showTecsgenCommandDialog`）。
4. **ステータスバーの拡充（外部仕様3.6 / 内部仕様3.6）**:
   - 現在の操作モード表示（新規セル作成時は選択セルタイプ名表示: `モード: セル新規作成 (tLogger)`）。
   - マウスモデル座標表示（`X: 12.5, Y: 34.0 mm`）、未保存変更インジケータ（`● 未保存の変更があります`）。
   - クリック可能なエラー/警告バッジ（`❌ 1件 ⚠️ 2件`）を配置し、クリックで診断メッセージ一覧モーダルを直接トグル展開。
5. **テスト追加・検証**:
   - `tests/commands.paper.test.ts` (1テスト), `tests/uiShell.propertyPanel.test.ts` (4テスト), `tests/uiShell.palette.test.ts` (2テスト), `tests/uiShell.statusBar.test.ts` (2テスト), `tests/uiShell.dialogs.test.ts` (2テスト) を追加。
   - Vitest 全19テストスイート（80テスト）オールグリーン、`tsc --noEmit` & `vite build` 正常終了（0エラー）。

### 2026-09-13 — モジュールF（表示制御 / View State）実装完了

TECSCDE内部仕様 第7章および外部仕様 第7章に基づく表示制御・ビューポート・検索・リージョン色分け・表示フィルタ（モジュールF）の実装を完了。

1. **ビューポート（ズーム・パン・中心維持）（外部仕様7.1.2 / 内部仕様7.1）**:
   - `src/view-state/viewport.ts`: 倍率変更時に中央モデル座標を維持する `calculateZoomCenter`、ポインタ位置固定ホイールズーム用 `calculateZoomAtPointer`、パンスクロール計算 `calculatePanScroll`、ナビゲータ自動判定 `shouldShowNavigator` を実装。
   - `src/app/main.ts`: スライダー・キーボード（`Ctrl+0`, `Ctrl++`, `Ctrl+-`）・ズームボタンでの中央維持ズーム、`Ctrl+Wheel` でのポインタ固定ズーム、およびスペースキー+ドラッグによるキャンバスパンを配線。
2. **ナビゲータ（ミニマップ）（外部仕様3.5 / 7.1.2 / 内部仕様7.3）**:
   - `src/ui-shell/navigator.ts`: 用紙・セル（色分け対応）・現在ビューポート矩形（`nav-viewport`）を表示する `NavigatorComponent` を新設。クリック・ドラッグで該当モデル座標へジャンプ。
   - 用紙全体がビューポート内に収まる場合は自動非表示（手動トグルで強制表示可能）。
3. **検索・ハイライト・一時可視化（外部仕様7.4.2 / 内部仕様7.4）**:
   - `src/view-state/search.ts` & `src/app/store.ts`: セル名・セルタイプ名・シグニチャ名を対象とした検索（`searchDocument`）。
   - 検索一致セルが属する非表示リージョンを一時的に可視化（`getEffectiveHiddenRegions`）。
   - ツールバーに一致件数表示（`1/3件`など）、次へ（↓/Enter）・前へ（↑/Shift+Enter）・クリア（Esc）による巡回・センタリングジャンプを配線。
4. **表示フィルタ・リージョン色分け・スタブ結合（外部仕様7.5.2 / 内部仕様7.5）**:
   - `src/view-state/regionColor.ts`: 決定論的（再現性のある）リージョン色割り当て（`getRegionColor`）および凡例生成（`getRegionLegend`）。
   - `src/render/svgRenderer.ts`: `colorByRegion` 有効時のセル背景塗り分け、および非表示リージョンへの結合を境界スタブ記号（`.join-stub` 破線＋端点マーカー）として描画（両端非表示のみ完全非表示）。
5. **テスト追加・検証**:
   - `tests/viewState.viewport.test.ts` (4テスト), `tests/viewState.regionColor.test.ts` (2テスト), `tests/viewState.search.test.ts` (2テスト), `tests/render.viewFilters.test.ts` (5テスト) を追加。
   - Vitest 全14テストスイート（69テスト）オールグリーン、`tsc --noEmit` & `vite build` 正常終了（0エラー）。

### 2026-09-13 — モジュールE（描画・キャンバス・SVG / インタラクション層）実装完了

TECSCDE内部仕様 第6章および外部仕様 第3章・第4章に基づくSVG描画・ヒットテスト・視覚フィードバック（モジュールE）の実装を完了。

1. **SVG階層構造の完全準拠（内部仕様6.1）**:
   - `<svg>` 直下の階層順を仕様に準拠して構成: `<g id="grid">`, `<g id="regions-underlay">`, `<g id="joins">`, `<g id="cells">`, `<g id="join-preview">`, `<g id="selection-overlay">`。
2. **セルの二重矩形選択と状態視覚表現（外部仕様4.1.1/4.1.2）**:
   - セル選択時に外側1mm（`GapActive = 1mm`）の破線矩形 `<rect class="cell-selection-outline">` を描画し、色覚特性によらず形状で選択状態を識別可能に。
   - 編集可能（通常塗り）、読み込み専用（`.readonly`）、未解決セルタイプ（`.unresolved`）、検索一致（`.search-match`）のクラス別SVG属性・スタイルを適用。
3. **結合可能性の視覚フィードバック（外部仕様3.7/4.6.2）**:
   - `src/render/hitTest.ts`: `canJoinPorts` を追加し、同一セル禁止およびシグニチャ完全一致を検証。
   - 結合ドラッグ（`joining`）操作中、接続可能な受け口に `.selectable-target`（緑色ハイライト＋カーソル変化）を付与し、操作開始元の呼び口に `.joining-source` を付与。
4. **ヒットテスト・幾何計算の検証（内部仕様6.3）**:
   - ヒット優先順位: ポート（2.5mm以内）＞ セル矩形 ＞ 結合バー（2mm以内）＞ 空白。
   - ラバーバンド選択（`cellsFullyInside`）: 矩形内部完全包含判定。
5. **テスト追加・検証**:
   - `tests/render.hitTest.test.ts`（8テスト）、`tests/render.svgRenderer.test.ts`（5テスト）を追加。
   - Vitest 全10テストスイート（56テスト）オールグリーン、`tsc --noEmit` & `vite build` 正常終了（0エラー）。

### 2026-09-13 — モジュールD（編集操作・コマンド / インタラクション連携）実装完了

TECSCDE内部仕様 第5章・第6章・第7章に基づく編集操作・コマンドおよびUI連携の残項目（モジュールD）を一気通貫で実装完了。

1. **OSクリップボード連携（CDL断片シリアライズ／パース）**:
   - `src/cdl/fragment.ts`: `serializeCellsAsCdl`（選択セルをCDL構文 `cell Celltype Name { ... };` 形式で出力）および `tryParseCdlFragment`（tree-sitterパーサ `parseCdl` を用いた安全な構文解析）を実装。
   - `src/commands/ops/clipboardOps.ts`: `copyCells`、`pasteCells`、`cutCells` に加え、アプリ内クリップボードとOSクリップボードフォールバック（`pasteFromAppClipboard`, `pasteFromCdlFragment`）を統合。
   - `src/app/store.ts` & `src/app/main.ts`: `Ctrl+C` / `Ctrl+X` / `Ctrl+V` に `navigator.clipboard.writeText` / `readText` を非同期連携。
2. **ポート位置・所属辺変更UIジェスチャ配線（ChangePortEdgeCommand / MovePortCommand）**:
   - `src/model/geometry.ts`: マウスポインタから最近傍辺と所属オフセットを計算する純粋関数 `closestPortEdgeAndOffset` を追加。
   - `src/render/gesture.ts`: `movingPort` ドラッグ状態を新設。EPortクリック、または結合済みCPort／Alt+CPortドラッグでポート移動を開始。ドロップ時に同辺内なら `movePort`、別辺なら `changePortEdge` をディスパッチ。
   - `src/render/svgRenderer.ts`: ドラッグ中のポート仮位置を示すプレビュー三角印表示（`setPortDragPreview` / `clearPortDragPreview`）を追加。
3. **複数セル整列コマンド（Align）UI配線**:
   - `src/ui-shell/toolbar.ts` & `src/ui-shell/propertyPanel.ts`: 複数セル選択（2個以上）時に活性化する「上端揃え」「左端揃え」ボタンを配置。
4. **プロパティパネルでの複数セル一括編集**:
   - `src/commands/ops/cellOps.ts`: `changeRegions`（一括リージョン変更）および `editAttrs`（共通属性一括変更）コマンドを追加。
   - `src/ui-shell/propertyPanel.ts`: 複数セル選択時に選択数・編集可能数表示、一括リージョン変更ドロップダウン、共通属性の一括編集フィールドを表示。
5. **テスト追加・検証**:
   - `tests/cdl-fragment.test.ts`, `tests/commands.align.test.ts`, `tests/commands.clipboard.test.ts`, `tests/commands.ports.test.ts` を追加・更新。
   - Vitest 全8テストスイート（43テスト）オールグリーン、`tsc --noEmit` & `vite build` 正常終了（0エラー）。

### 2026-09-13 — CDLパーサをtree-sitterへ移行（コミット`353853a`）

[[TECSCDE外部仕様]]2.2節の改訂（CDL解析系のみを外部依存の例外として認める）と[[TECSCDE内部仕様]]第4章の全面改訂を受けた実装側の追随。手書きの`src/cdl/lexer.ts`・`parser.ts`を削除し、`grammar.ts`（文法ロード）＋`cst.ts`（CST走査）へ置き換えた。用いた文法は[[CDLParser(tree-sitter利用-JS版)]]（`bnf.y.rb`からの移植）。

- 中間表現`ParsedCdl`の形を保ったため`document-builder.ts`はimport先の差し替え1行のみ。`store.ts`・`io`・`diagnostics`の契約は無変更。
- 非同期は`initCdlParser()`の1点に閉じ込め、`parse()`は同期のまま（内部仕様4.3）。
- `.wasm`は`public/wasm/`へvendor（出所・サイズ・ABIは同ディレクトリのREADMEに記録）。ランタイム依存は`web-tree-sitter`のみで、**本プロジェクト初のランタイム依存**。

**最大の発見: 出力が有効なCDLでなかった**（詳細と一般化は[[Patterns - 検証と調査#自前パーサと自前シリアライザのround-tripは、方言が外界の仕様から外れていても永久に緑になる（2026-09-13）|Patterns]]）。tree-sitter文法で検証したところ`public/samples/celltypes.cdl`は全体が1個の`ERROR`、`main.cde`は`cell`ブロック終端の`;`欠落で`MISSING`が3件。serializerが`;`を出すよう修正し、fixtureを本物のCDLへ書き換え、**出力が文法で解析できることをテストで固定**した。既存の`.cde`は終端`;`が無くてもtree-sitterの`MISSING`回復で読めるため読み込み互換は維持。

あわせて、CDL本体の`import`/`import_C`文が解析はされるが保存時に消えていた欠落も修正（`TecscdeDocument.preservedImports`として原文のまま往復、回帰テスト追加）。

検証: 32テストpass、`tsc --noEmit`＋`vite build`成功。**実機ブラウザでdev/build両方を確認**——サンプル読込で3セル・2結合の描画とセルタイプ一覧、コンソールエラーなし、wasm 2件とも200。**WASMのロードはnavigation startから約120ms**（DOMContentLoaded 80ms）で完了。バンドルは408.70 kB（gzip 148.20 kB）。

未追随: [[TECSCDE-TS実装]]・[[TECSCDE-DT-EL実装]]の`lexer.ts`/`parser.ts`は手書きのまま（内部仕様4.7の移行メモ）。

### 2026-09-01
- `/om-standup`の提案を受け、`MoveJoinBarCommand`の実装に着手しようとしたところ、**モデル層からUI配線・プレビュー描画・テスト8件まで一気通貫で既に実装済み**（2026-08-30 07:18〜07:24、この進捗ノート自身が書かれるより前の時間帯）と判明。誰が書いたか・どのセッションの作業かは特定できないが、`npm run build`グリーン・Vitest 30/30全パス（旧11件から19件増、後述のportOps.ts分含む）で動作確認済みだったため、そのままコミット（`8b86f8a`）。あわせて同じタイミングで書かれていた`portOps.ts`（`movePort`/`changePortEdge`、テスト済みだがUI未配線）・`cutCells`の独立Cutコマンド化も同じコミットに含めた。上記3・5の記載を実態に合わせて訂正。

## Related
- [[TECSCDE-JS-TS実装]] — 本ログのコアノート
