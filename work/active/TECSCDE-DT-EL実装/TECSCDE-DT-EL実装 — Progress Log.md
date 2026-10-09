---
date: 2026-09-10
description: "TECSCDE-DT-EL実装 の日付つき進捗ログ（2026-09-06〜）。[[TECSCDE-DT-EL実装]] の ## Notes が25KBを超えたため verbatim 分離。物理順を保持。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

Event-log satellite of [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] (2026-09-10, 25KB threshold split). 日付つきの実装エントリを元の物理順のまま保持する。要約とAction Itemsはコア側。

## Progress

- **2026-09-06、[[TECSCDE-DT-EL内部仕様]]第11章11.4節の提案どおりの順序で実装**:
  1. **モデル＋CDLパーサ/シリアライザのround trip** — [[TECSCDE-TS実装]]（`E:\Ccur\typescript\TECSCDE-TS`）の`src/model`・`src/cdl`・`src/diagnostics`を、第3・5・6・8章が「完全に同一、変更なし」と規定するとおり**そのままコピー**して`src/renderer/model`・`src/renderer/cdl`・`src/renderer/diagnostics`に配置。ポート元の8テストもそのまま移設し、パスのみ修正して全件pass。
  2. **UIより先にIPCゲートウェイの疎通を確認**（本書固有の新規リスク、11.4節#2） — 実際の`electron .`起動によるE2E確認ではなく、`vitest`で`electron`モジュールをモックした契約テストとして実施:
     - `FileService`（`dialog`+`fs`、7.1節）: ダイアログのキャンセル・複数ファイル選択時のeditable/references分離・アトミック書き込み（tmpファイル→rename）を実ファイルシステム相手に検証
     - `TecsgenRunner`（`child_process.execFile`、9.1節）: 成功・非0終了・ENOENT（実行ファイル未検出）の3パターンを検証
     - `ipc.ts`（7.2・9.2節）: 全6チャネル（`file:open`/`save`/`saveAs`/`export`、`tecsgen:generate`/`version`）が正しいメソッドに配線されていることを検証
     - `preload/index.ts`（2.4節）: `contextBridge.exposeInMainWorld`が公開するAPIが正しいIPCチャネルを呼ぶこと、`clipboard`がipcMainを介さず直接ブリッジされることを検証
     - `renderer/gateways/*`（2.4・7.3・9.3・4.1節）: 3ゲートウェイクラスが`window.tecscde.*`へ正しく委譲することを検証
  3. `.dependency-cruiser.cjs`（10.1節）でrenderer→electron・main→rendererの禁止importを機械的に強制。ルールが実際に違反を検知することを、一時的に違反コードを注入して確認済み（最初の実装では`to.path`のマッチ対象を誤り、無検知のまま素通りしていたバグを発見・修正）。
- **29テスト全pass**（新規21件＋移設8件）。`npm run check`（型チェック×2 + テスト + depcruise）が通ることを確認。
- **2026-09-08、実機`electron .`起動を確認（部分的にpass）**。この間にリポジトリ側でElectron 44 / Vitest 5 へのアップグレードが入っており（コミット`146c51f`・`3302bec`、本ノート未記録だった）、`electron`バイナリ（`node_modules/electron/dist/electron.exe`）も取得済みで以前のpostinstallブロックは解消していた。`npm run build:main` 後に `electron .` を実行:
  - **起動は成功**: main（ESM）がロードされ`app.whenReady()`が発火、`BrowserWindow`生成、4プロセス構成（main+GPU+renderer+utility）がConsoleセッション上に立ち上がった。Electron 44がESM mainをそのまま実行できることを確認。
  - **既知どおりの失敗**: `Failed to load URL: .../dist/renderer/index.html … ERR_FILE_NOT_FOUND`（renderer=モジュールG未ビルド、7.4節・main/index.tsのコメントどおり）。
  - **新規の不具合**: `Unable to load preload script … SyntaxError: Cannot use import statement outside a module`。preloadが`"type": "module"`配下の`.js`としてESM出力されているが、Electronのサンドボックス化されたpreloadはCommonJSコンテキストで実行されるため`import`を解釈できない。契約テスト（`tests/preload/index.test.ts`）はTSソースをvitestが変換して読むため、この出力形式の不整合を検出できていなかった——実機起動でのみ露見。
- **2026-09-08、preloadをESM化して修正**（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|preload ESM・sandbox決定]]、11.2節#1をユーザー判断で確定）:
  - `src/preload/index.ts` → `src/preload/index.mts`（`.mts`はpackage typeに関わらずESM `.mjs`を出力）。`main/index.ts`の`webPreferences`を`preload: "../preload/index.mjs"` + `sandbox: false`に。`contextIsolation: true`・`nodeIntegration: false`は維持。
  - ESMの`electron`はpreload向けに`clipboard`を名前付きエクスポートしないため、`clipboard`だけ`createRequire(import.meta.url)("electron")`でCJS版から取得（`contextBridge`/`ipcRenderer`は名前付きimportのまま）。この2回目のエラー（`does not provide an export named 'clipboard'`）も実機`electron .`で発見。
  - `tests/preload/index.test.ts`: `node:module`の`createRequire`をモックしてclipboard経路を検証。`tsconfig.main.json`のincludeを`src/preload/**/*.mts`に。
  - **再度`electron .`で確認**: `Unable to load preload script`エラーが消え、preloadがESMでロード・`contextBridge.exposeInMainWorld("tecscde", ...)`実行を確認。残るログはrenderer未ビルドの`ERR_FILE_NOT_FOUND`とCSP警告（実装が進めば解消）のみ。`npm run check`（build + 47テスト + depcruise）green。
  - `contextBridge`分離の実挙動そのもの（`window.tecscde.*`がrendererから呼べるか）は、rendererが存在して初めて検証可能なため引き続き未確認。
- **2026-09-07、11.4節#3の実装単位（第4章 編集コマンドとUndo-Redo）をクラスベースで新規実装**（コミット`0b753e7`）:
  - `commands/command.ts`: `Command`抽象クラス（`apply`のみ、`invert()`なし——[[work/active/tecs/TECSCDE Undo-Redo設計決定|Undo-Redo設計決定]]どおり非対称バグの余地をクラス階層から排除）
  - `commands/history.ts`: `History`クラス。`canUndo`/`canRedo`/`current`/`commit`/`undo`/`redo`のみを公開し、replay計算とpast/future配列操作を内側にカプセル化。replayベースのため外部仕様6.6.1の現行版2不具合（初回コミットUndo不可・Redo恒久無効）は構造的に再発しない。`undo`/`redo`は不能時に`InvariantViolation`を投げる（呼び出し側が`canUndo`/`canRedo`で事前判定する前提）
  - `commands/support.ts`: カスケード削除・結合の経路再計算（`autoRouteBars`）・セル名の自動導出（セルタイプ名の先頭`t`除去＋連番）・`nextJoinId`をモデル公開APIのみ経由で実装
  - セルコマンド: `AddCellCommand`・`MoveCellCommand`（絶対）・`MoveCellsCommand`（相対・複数）・`DeleteCommand`（カスケード）・`RenameCellCommand`・`EditAttrCommand`・`ChangeRegionCommand`・`AlignTopCommand`/`AlignLeftCommand`
  - 結合コマンド: `CreateJoinCommand`（シグニチャ不一致・結合済み呼び口を静かにキャンセル）・`DeleteJoinCommand`・`MoveJoinBarCommand`
  - ポートコマンド: `MovePortCommand`・`ChangePortEdgeCommand`（移動先辺の長さでオフセット再クランプ）
  - モデル層への最小追加: `Join.withBars()`（経路差し替えプリミティブ、`moveBar`と同じ不変更新ファミリー）1メソッドのみ
  - **Copy/Paste/Cutは今回の範囲外**: 第2章の`ClipboardGateway`（`window.tecscde.clipboard`直接ブリッジ）配線＋CDLの`cell`ブロック断片のシリアライズ／パース（未実装）に依存するため。Action Items参照
  - **新規18テスト**（`History`7件＋コマンド11件、すべてヘッドレス`vitest`）。サンプルフィクスチャ（cell 3・join 2・celltype 3）に対し各コマンドが`assertInvariants`を保つことを確認。**47テスト全pass**、`npm run check`green

- **2026-09-09、第5章（描画・インタラクション設計）をクラスベースで新規実装**。[[TECSCDE-DT-EL内部仕様]]第5章＝[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 05 描画・インタラクション設計|TECSCDE-TS内部仕様第5章]]（verbatim）、挙動の正典は[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 06 描画・インタラクション設計|TECSCDE内部仕様第6章]]。[[TECSCDE-JS-TS実装]]の`render/svgRenderer.ts`・`hitTest.ts`・`gesture.ts`（関数ベース）を、DT-ELのクラスベース・モデルAPI（`TecscdeDocument.getCell/withCell`等・不変クラス）へ写した:
  - `src/renderer/render/` に8ファイル: `view.ts`（`CanvasView` interface＋`SelectionState`値クラス。完全な`ViewState`は第6章。5.4節）、`element-renderer.ts`（`ElementRenderer<TModel,TContext>`抽象＋SVGヘルパー、5.1節）、`cell-renderer.ts`／`join-renderer.ts`（種別ごとの下位クラス。片方の変更が他方に波及しないことを型で表現）、`svg-path.ts`（`joinPolyline` 純粋関数）、`svg-renderer.ts`（`Map<Id,SVGGElement>`対応表による差分更新。前回描画との identity 比較で「図全体の再描画」を構造的に排除、5.1節）、`hit-tester.ts`（優先順位ポート＞セル＞結合バー、結合バー探索をピクセル半径内に限定＝外部仕様6.2.2の改善、5.2節）、`gesture-controller.ts`（`DragState` Union＋`GestureHost`。遷移の終端でのみ第4章コマンドを発行、5.3節）、`index.ts`。
  - **仕様スケッチからの逸脱2点（ヘッダコメントに理由明記）**: ①`HitTester`は`renderer`ではなく`CanvasView`を受け取る（要素位置はモデルから一意、必要なのはpx→mm換算のズームのみ）。②`GestureController`はコンストラクタでDOMリスナを張らず、`pointerDown/Move/Up`・`keyDown`を公開メソッドに、DOM結線を`attach(svg)`に分離（状態機械をヘッドレス検証可能にする。本リポジトリの契約テスト方針に合わせた）。仕様書自身が第5章の設計を「スケッチ」と明記。
  - **SVG描画クラス（`SvgRenderer`/`CellRenderer`/`JoinRenderer`）は`build:renderer`の型チェックのみ**。DOM生成の実挙動検証はモジュールG（rendererのHTMLシェル）が存在して初めて可能——preloadの`contextBridge`分離が未検証なのと同じ理由（jsdomは追加しない方針を踏襲）。
  - **新規20テスト**（`hit-tester.test.ts` 8件・`gesture-controller.test.ts` 12件、すべてヘッドレス`vitest`）。サンプルフィクスチャに対し優先順位・半径限定・ドラッグFSMの各遷移（セル移動→`MoveCellsCommand`／結合作成→`CreateJoinCommand`／バー移動→`MoveJoinBarCommand`／Delete・矢印キー／矩形選択／Escapeキャンセル）を確認。**67テスト全pass**、`npm run check`（build×2 + test + depcruise）green。
  - **第6章（表示制御）は未着手**: `ViewState`／`DisplayFilters`クラス（ズーム/パン/グリッド/フィルタ/検索の集約）。第5章は暫定の`CanvasView` interfaceで先行し、第6章の`ViewState`がこれを満たすアダプタを提供する設計。

- **2026-09-09、第6章（表示制御設計）をクラスベースで新規実装**。[[TECSCDE-DT-EL内部仕様]]第6章＝[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様第6章]]（verbatim）、挙動の正典は[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 07 表示制御設計|TECSCDE内部仕様第7章]]。新モジュール`src/renderer/view-state/`（[[TECSCDE-JS-TS実装]]の`src/view-state/`に対応。モジュールF＝表示制御、モデルCへの参照を持たない）に5ファイル:
  - `view-state.ts`（`ViewState`不変クラス。`zoom`/`panCenter`/`gridVisible`/`filters`/`searchQuery`を集約。`initial`/`zoomAt`/`resetZoom`/`panBy`/`panTo`/`toggleGrid`/`withFilters`/`withSearchQuery`、`ZOOM_MIN/MAX/STEP`・`clampZoom`。6.1節）
  - `display-filters.ts`（`DisplayFilters`不変クラス＝`regionFilter`/`namespaceFilter`/`colorByRegion`/`showSignatureNames`、6.5節。＋`resolveHiddenRegionIds(filters, RegionTree)`純関数——モデル非参照を保つため、フィルタは`RegionId`生値で保持し非表示集合への解決はアダプタ側で行う）
  - `navigator.ts`（6.3節。`computeNavigator(view, PaperSpec, viewport)`純関数。用紙全体が収まる縮小率での自動非表示＝7.3.2、可視モデル矩形の算出。実DOMはモジュールG待ち）
  - `search.ts`（6.4節。`searchDocument(doc, query, hiddenRegionIds?)`純関数。セル名/セルタイプ名/ポート名・シグニチャ名/結合端点/名前空間パスをマッチ。非表示リージョンのヒットを`revealed`で返す＝フィルタ一時緩和の材料、7.4.2。巡回カーソル保持はモジュールG）
  - `index.ts`（公開面）
  - **`zoomAt`/`panBy`の座標系の逸脱（ヘッダコメントに明記）**: `panCenter`はモデル座標系の表示中心。描画層（`CanvasView`）はpanをSVG変換ではなくシェル（モジュールG）のスクロールで実現するため`panCenter`を読まない——`panCenter`はナビゲータとスクロール位置復元用。`zoomAt`は固定点不変条件`(anchor − panCenter)·zoom`を保つ定式化とし、ビューポート寸法に非依存（7.1.2の「左上基準でずれる」欠落の解消）。
  - **第5章の暫定`CanvasView`との接続**: `ViewState.toCanvasView(regions)`が`{zoom, gridVisible, showSignatureNames, hiddenRegionIds}`へ射影。`ViewState.initial().toCanvasView(空doc)`＝`defaultCanvasView()`をテストで固定。`GestureHost.getView(): CanvasView`はそのまま——モジュールG実装時に`this.viewState.toCanvasView(this.doc.regions)`を返す配線になる（ch5コードの変更不要）。
  - **新規23テスト**（`view-state.test.ts`。zoomAt固定点・クランプ・不変wither・toCanvasViewパリティ・`resolveHiddenRegionIds`のリージョン/ネームスペース/AND合成・ナビゲータ自動非表示・検索）。**90テスト全pass**、`npm run check`（build×2 + test + depcruise）green。

- **2026-09-10、モジュールG（rendererのHTMLシェル）を最小スコープで新規実装**。内部仕様第2章2.3節「G: UIシェル」（renderer プロセス）。これで `SvgRenderer`／`GestureController`／`ViewState` が初めて実DOM上で動いた（従来はすべて型チェック＋ヘッドレス契約テストのみ）。スコープはユーザー確認済み（最小シェル: キャンバス＋open/save/saveAs＋Undo/Redo＋ズーム＋グリッド＋モード切替＋ステータスバー＋キーボード。パレット／プロパティパネル／検索ボックス／ナビゲータパネルは次段）。
  - **バンドル方式 = esbuild**（[[TECSCDE-実装アーキテクチャ案]]7項「単一HTML＋単一JSバンドル、esbuildはビルド時限定」に一致。devDep、配布物のランタイム依存ゼロ規定と矛盾しない）。`scripts/build-renderer.mjs` が `src/renderer/main.ts` → `dist/renderer/renderer.js` にバンドル、`index.html`・`public/samples` を `dist/renderer/` へコピー。`build:renderer` = 型チェック（`tsc --noEmit`）→ esbuild。`start` = `build`→`electron .`。
  - `src/renderer/app/` に5ファイル: `store.ts`（`AppStore`＝`History`＋`ViewState`＋`SelectionState`＋mode＋filePath＋DirtyTracker[7.3節]を束ねる pub/sub ストア）、`gesture-host.ts`（`AppGestureHost implements GestureHost`。`getView()` で `ViewState.toCanvasView(doc.regions)` を射影）、`pan-scroll.ts`（`panCenter`(mm) ⇔ `scrollLeft/Top`(px) の純関数ペア＝第6章が「シェルが持つ」とした対応づけの実体）、`file-actions.ts`（`FileGateway`＋`CdlDocumentLoader`／`CdlSerializer` を繋ぐ open/save/saveAs）、`shell.ts`（`AppShell`＝DOM取得・`SvgRenderer`/`GestureController` 生成・ツールバー/キーボード/ホイール/スクロール配線・描画ループ）。＋`src/renderer/main.ts`（エントリ）、`src/renderer/index.html`（単一HTML＋CSP＋全描画クラスの最小CSS）。
  - **起動ドキュメントの供給（7.4節 pendingOpenPath 経路）**: renderer は `file://` fetch がCORSで塞がるため、main が `did-finish-load` 後に `app:bootstrap` IPC で1回だけ送る（引数に `.cde`/`.cdl` があればそのファイル、無ければ `public/samples/{celltypes.cdl,main.cde}`）。preload に `onBootstrap(listener)` を追加、`src/main/file-service.ts` に `openPaths()` を追加、`main/index.ts` の握りつぶし `catch` を除去。
  - **実DOM検証 = happy-dom（配線テスト）＋手動 `electron .`（幾何・スクロール連動）**。新規テスト18件: `app-store.test.ts`（dispatch/undo/redo一致・DirtyTracker遷移・購読）、`pan-scroll.test.ts`（往復一致・クランプ・ズーム比例）、`shell.dom.test.ts`（`@vitest-environment happy-dom`。`#cells` に cellCount 個の `<g>`・celltype select 生成・グリッド切替・Undoボタン配線・モード切替・`GestureController` のpointer列でセル移動が1コマンド）。＋preload の `onBootstrap` テスト1件。
  - **手動 `electron .` スモーク（2026-09-10）**: 起動クリーン（renderer読込・preload橋渡し・`app:bootstrap` 経由で samples をパース）。診断ログで `cells=3 joins=2` を確認（[[TECSCDE内部仕様]]/roundtripテストの期待値と一致）。CSP を `index.html` に設定して Electron の CSP 警告も消えた。Console エラーなし。SVG幾何・ズーム/パンのスクロール連動の実挙動は happy-dom がレイアウトを持たないため手動確認に委ねた（今回は起動と描画ツリー生成まで確認、対話的な目視は未実施）。
  - **109テスト全pass**（既存90＋新規19）。`npm run check`（typecheck:renderer + esbuild + build:main + test + depcruise）green。
  - **ツール注意（[[Gotchas - Tooling & Config]]）**: RTK 経由の `tsc` は型エラーを握りつぶすだけでなく、`tsc -p tsconfig.main.json` の **emit 自体をスキップする**ことがある（`dist/` が古いまま）。`rtk proxy npx tsc …` で回避。今回 preload の `onBootstrap` 追加が dist に反映されず「`onBootstrap is not a function`」で1回転んだ。

- **2026-09-10、第8章（整合性チェックとメッセージ設計＝モジュールH）を実装**。[[TECSCDE-DT-EL内部仕様]]第8章＝[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様第8章]]（verbatim）。診断の**型**（`interface Diagnostic`）は既存（`diagnostics/types.ts`、B が生成）で、今回は**集約層**を追加:
  - `src/renderer/diagnostics/` に3ファイル: `collector.ts`（`DiagnosticsCollector`＝可変。`report`/`reportAll`/`clear`/`toReport`。イミュータブル方針の対象外＝8.2節 note ＝ `GestureController.state` と同格。＋`DiagnosticReport` 不変値クラス＝severity 昇順の安定ソート・`errorCount`/`warningCount`/`isEmpty`/`static empty()`）、`integrity.ts`（`checkIntegrity(doc)` 純関数＝[[TECSCDE-JS-TS実装]] `src/diagnostics/collector.ts` の関数版を DT-EL の不変モデルAPI `doc.cellValues()` へ写す。未解決セルタイプの残存＋`direct_import` の未読込ファイル＝`W-UNRESOLVED-REF-FILE`〈8.3表で唯一のH生成コード〉）、`index.ts`（公開面）
  - `cdl/messages.ts`: `W_CODES.UNRESOLVED_REF_FILE` と `unresolvedReferenceFile(name)` ファクトリを追加（JS-TS の同名関数を写す）
  - **モジュールGへの配線＝ステータスバーに件数のみ**（ユーザー確認）: `AppStore` に `loadDiagnostics`（B のロード時診断）を保持、`getReport(): DiagnosticReport` が `loadDiagnostics ＋ checkIntegrity(現doc)` を都度集約（派生値、購読通知なし）。`file-actions.ts` の `applyOpenResult` が `loadSources` の戻り `diagnostics` を `store.loadDocument` へ渡すよう変更。`shell.ts` の `refreshStatus()` が `#status-diag` に `⚠ N エラー / M 警告`（ゼロなら空）。`index.html` にスパン追加。**一覧パネル＋ジャンプ機構（8.4節）は G の次段**。
- **2026-09-11、第4章4.1節（Copy/Cut/Paste・断片シリアライズ）、モジュールGへのキーボード配線、モジュールG次段（パレット/プロパティパネル/検索/ナビゲータ）、第9章9.4節（TecsgenResultParser）、第9章9.5節（Generate操作配線・TecsgenCommandBuilder）を実装**（コミット`0e79b3e`, `e4e7484`, `67ad15f`, `9933003`, `5c04939`）。183テスト全pass。
- **2026-09-12、第8章8.4節（診断パネルUI配線・DiagnosticsPanelView）とElectron Forge導入を実装**。185テスト全pass、`electron-forge make`によるWindows Setup.exe生成成功。
- **2026-09-13、外部仕様・内部仕様の改訂（`import_C`プリプロセス・フォールバック対応）に追随し、第9章9.6節のプリプロセス実行基盤を実装**:
  - `src/shared/ipc-types.ts`: `CppResult`（`stdout`, `stderr`, `exitCode`, `executableFound`）および `TecscdeApi.tecsgen.preprocess(headerPath, cppCommand)` を追加。
  - `src/main/tecsgen-runner.ts`: `preprocess(headerPath: string, cppCommand?: string): Promise<CppResult>` メソッドを追加。`gcc -E -DTECSGEN` または `cppCommand` の実行、ENOENTハンドリング（`executableFound: false`）、異常終了時の安全な返却を実装。
  - `src/main/ipc.ts`: `tecsgen:preprocess` IPCチャネルをハンドラ登録。
  - `src/preload/index.mts`: `contextBridge`に`tecsgen.preprocess`を公開。
  - `src/renderer/gateways/tecsgen-gateway.ts`: `preprocess`メソッドを実装（`window.tecscde.tecsgen.preprocess`へ委譲）。
  - **テスト**: `tests/main/tecsgen-runner.test.ts`（2件）、`tests/preload/index.test.ts`（1件）、`tests/main/ipc.test.ts`（1件）、`tests/renderer/gateways.test.ts`（1件）を追加・検証。**188テスト全pass**、`npm run check`（typecheck:renderer + esbuild + build:main + test + depcruise）green。

## 2026-09-16以降

2026-09-16〜の日付つき実装エントリ（tree-sitter移行・`-I`誤り訂正・未コミット作業の整理）は
[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜|TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜]]
に分離（2026-09-20、25KB閾値）。

## Related

- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — コア（要約・Action Items・Related）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様]] — 対応する内部仕様（全11章）

