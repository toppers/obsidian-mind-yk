---
date: 2026-09-13
description: TECSCDE-JS-TS実装の実装進捗ログ後半（2026-09-13〜09-14、モジュールG・F・E・D、tree-sitter移行）。実装進捗ログから分割（25KB閾値、2026-09-14）。
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-JS-TS実装 — 実装進捗ログ 後半

[[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ|実装進捗ログ]]から分割（物理順を保持）。[[TECSCDE-JS-TS実装]]が本体、前半は[[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ — 前半|実装進捗ログ 前半]]。

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

**最大の発見: 出力が有効なCDLでなかった**（詳細と一般化は[[Patterns - 検証と調査 Archive#自前パーサと自前シリアライザのround-tripは、方言が外界の仕様から外れていても永久に緑になる（2026-09-13）|Patterns]]）。tree-sitter文法で検証したところ`public/samples/celltypes.cdl`は全体が1個の`ERROR`、`main.cde`は`cell`ブロック終端の`;`欠落で`MISSING`が3件。serializerが`;`を出すよう修正し、fixtureを本物のCDLへ書き換え、**出力が文法で解析できることをテストで固定**した。既存の`.cde`は終端`;`が無くてもtree-sitterの`MISSING`回復で読めるため読み込み互換は維持。

あわせて、CDL本体の`import`/`import_C`文が解析はされるが保存時に消えていた欠落も修正（`TecscdeDocument.preservedImports`として原文のまま往復、回帰テスト追加）。

検証: 32テストpass、`tsc --noEmit`＋`vite build`成功。**実機ブラウザでdev/build両方を確認**——サンプル読込で3セル・2結合の描画とセルタイプ一覧、コンソールエラーなし、wasm 2件とも200。**WASMのロードはnavigation startから約120ms**（DOMContentLoaded 80ms）で完了。バンドルは408.70 kB（gzip 148.20 kB）。

未追随: [[TECSCDE-TS実装]]・[[TECSCDE-DT-EL実装]]の`lexer.ts`/`parser.ts`は手書きのまま（内部仕様4.7の移行メモ）。

### 2026-09-01
- `/om-standup`の提案を受け、`MoveJoinBarCommand`の実装に着手しようとしたところ、**モデル層からUI配線・プレビュー描画・テスト8件まで一気通貫で既に実装済み**（2026-08-30 07:18〜07:24、この進捗ノート自身が書かれるより前の時間帯）と判明。誰が書いたか・どのセッションの作業かは特定できないが、`npm run build`グリーン・Vitest 30/30全パス（旧11件から19件増、後述のportOps.ts分含む）で動作確認済みだったため、そのままコミット（`8b86f8a`）。あわせて同じタイミングで書かれていた`portOps.ts`（`movePort`/`changePortEdge`、テスト済みだがUI未配線）・`cutCells`の独立Cutコマンド化も同じコミットに含めた。上記3・5の記載を実態に合わせて訂正。

## Related
- [[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ|実装進捗ログ]] — 索引
- [[work/active/TECSCDE-JS-TS実装/TECSCDE-JS-TS実装 — 実装進捗ログ — 前半|実装進捗ログ 前半]]
- [[TECSCDE-JS-TS実装]]
