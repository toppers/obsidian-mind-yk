---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第10章（モジュール間インタフェース一覧）— main/preload/rendererのディレクトリ構成とIPCチャネル一覧。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 10 of 11。

## 10. モジュール間インタフェース一覧

第2章の依存図・プロセス配置を、実際のディレクトリ構成まで落とし込む。

```
src/
  main/                    (mainプロセス)
    file-service.ts          A: FileService（dialog + fs、7章）
    tecsgen-runner.ts         I: TecsgenRunner（child_process、9章）
    ipc.ts                    ipcMain.handleの登録一式
    index.ts                  起動処理・BrowserWindow生成・コマンドライン引数/open-fileの処理（7.4節）
  preload/
    index.ts                 contextBridge.exposeInMainWorld（2章2.4節）。clipboardもipcMain経由
  renderer/
    model/                 (C) types.ts, document.ts, invariants.ts — TECSCDE-TS内部仕様3章と同一
    cdl/                   (B) grammar.ts, builder.ts, serializer.ts, tool-info.ts, cdecl-extractor.ts — 同左
    commands/              (D) command.ts, history.ts, ops/*.ts（clipboard連携を含む、4章）
    render/                (E) svg-renderer.ts, hit-test.ts, gesture.ts — TECSCDE-TS内部仕様5章と同一
    view-state/            (F) view-state.ts, display-filters.ts — 同左
    ui-shell/              (G) toolbar.ts, palette.ts, property-panel.ts, status-bar.ts, dialogs/
    diagnostics/           (H) collector.ts, tecsgen-result-parser.ts（9章）
    gateways/                 file-gateway.ts（7章）, tecsgen-gateway.ts（9章）, clipboard-gateway.ts（4章）
    tecsgen-link/          (I) command-builder.ts — TECSCDE-TS内部仕様9章と同一
    app/
      store.ts                Store（C・F・Hを束ねる）
      main.ts                 起動・依存注入・イベント配線
```

[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様第10章]]のディレクトリ構成と比較すると、**`main/`・`preload/`という2つの新規ディレクトリが加わり、`renderer/`配下に`gateways/`が新設される**点のみが差分——`model/`・`cdl/`・`render/`等の既存モジュールはディレクトリ構成ごとrendererへそのまま持ち込める。

### 10.1 プロセス間の依存の機械的強制

第2章の依存図に加え、**プロセス境界の逸脱**を新たなルールとしてCIで検証する。

- `renderer/`配下のいかなるファイルも`electron`（`fs`・`child_process`・`dialog`等のNode/Electron API）を直接importしてはならない。すべて`gateways/`経由（`window.tecscde.*`）でアクセスする。
- `main/`配下のファイルはDOM/SVGへアクセスしてはならない（そもそもmainプロセスにDOMが存在しないため、実行時エラーとして自然に検出される）。
- 上記はdependency-cruiserの`allowed`/`forbidden`ルールとして`renderer/`から`electron`モジュールへのimportを禁止する形で機械的に強制する（[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様10.1節]]の方針を拡張）。

### 10.2 モジュール間の主要インタフェース

| 提供モジュール | インタフェース（クラス） | 利用モジュール |
|---|---|---|
| C | `TecscdeDocument`（読み取り専用メソッドのみ公開） | 全renderer側モジュール |
| D | `Command`／`History`／`store.dispatch(command)` | G, E |
| B | `CdlGrammar`（WASM初期化） ／ `CdlDocumentBuilder.build(text)` ／ `CdlSerializer.serializeSource(doc, sourceKey)`（主ファイルも定義元で選別。`serialize(doc)`も同じ契約、4C） ／ `CdeclExtractor.extract(text)` | gateways（保存・インポート解決時）, app |
| F | `ViewState`（読み取り専用）、`store.viewState` | E, G |
| H | `DiagnosticsCollector.toReport()` | G |
| I（renderer側） | `TecsgenCommandBuilder.build(doc, refs)` | G, `TecsgenGateway` |
| **A（main）** | `window.tecscde.file.*`（`FileGateway`経由、`resolveImports`含む） | G, B |
| **I（main）** | `window.tecscde.tecsgen.*`（`TecsgenGateway`経由、`generate`/`preprocess`/`version`） | G, B |
| **preload** | `window.tecscde.clipboard.*`（`ClipboardGateway`経由、ipcMainの`clipboard:writeText`／`clipboard:readText`を呼ぶ。Promiseを返す） | **Copyは例外**: `AppStore.copySelection`が`dispatch`を通さず`CopyCommand.apply()`を直接1回だけ呼び、その中でゲートウェイへ書き込む。Copyは履歴へ登録しない。カットの書き込みは`AppStore.cutSelection`、貼り付けの読み取りは`clipboard-actions`で事前に行い、`CutCommand.apply()`・`PasteCommand.apply()`はゲートウェイを直接呼ばない（第4章4.1節。2026-11-08、監査#27で統一） |

### 10.3 開発ツール方針

[[TECSCDE-TS内部仕様]]10.3節と同一の方針に加え、Electron固有の設定を追加する。

- `contextIsolation: true`・`nodeIntegration: false`を既定とする（rendererプロセスのセキュリティ標準構成）。
- `renderer/`のビルド出力とNode.js APIを要する`main/`・`preload/`のビルドは別のtsconfig（`tsconfig.renderer.json`／`tsconfig.main.json`）で分離し、`renderer/`側は`lib: ["DOM", "ES2020"]`のみを許可することで、Node APIの誤importをコンパイル時にも検出する。

### 10.4 V0.2.0の追加契約

以下は実装前の契約案です。既存の`TecscdeApi`へ追加・統合し、`src/shared/ipc-types.ts` → `src/main/ipc.ts` → `src/preload/index.mts` → rendererのゲートウェイの順に接続します。preloadは現在のESM構成を維持します。第2章のプロセス境界とdependency-cruiserの禁止規則は変更しません。

| 責務 | main | renderer | 契約 |
|---|---|---|---|
| 設定取得・保存 | `app-settings.ts`とパス解決 | 情報ダイアログ、設定ゲートウェイ | `settings:getToolSettings`、`settings:updateToolSettings` |
| tecsgen候補選択・確認 | ネイティブdialog、`TecsgenRunner` | 情報ダイアログ、`TecsgenGateway` | `settings:chooseTecsgenPath`、`tecsgen:checkPath` |
| 保存後の版確認 | 現在の実行設定で版を取得 | 9Cの診断更新、revision照合 | 既存`tecsgen:version`を再利用 |
| CDL一覧生成 | `CdlFileListService`案、fs | 情報ダイアログ、`FileGateway` | `file:planCdlFileLists`／`file:applyCdlFileLists`。計画・確認・変更前提の再検査は7Gを正とする |
| 定義ファイル表示 | 既存のテキスト読込処理 | `DefinitionFileView`案 | 既存API再利用を優先 |
| active・結合・リージョン表示 | なし | `AppStore`、`ViewState`、`DisplayFilters`、`SvgRenderer` | renderer内で完結 |
| active最上段配置 | なし | 純粋な配置計算`prepareMoveActiveToTop(doc)`→`ActiveTopPlan`と編集`MoveActiveCellsToTopCommand(plan)`（6C.4、2026-11-08） | `History`で再生。入口はツールバーのボタン`moveActiveToTop`（`canMoveActiveToTop(doc)`で有効・無効を判定。6C.4） |
| 仮想ファイル・プラグイン相当 | 設定`pluginTypeSource`は既存の設定API（`settings:getToolSettings`・`updateToolSettings`）で共用。IPCの新設なし | renderer内`PluginTypeProvider`の`InternalPluginTypeProvider`（Web Worker上の`InternalTecsgenProcessor`と`VirtualFileSystem`。9D.6、2026-11-08） | 併用方式（既定は外部）。対象は付表のプラグインのみ。自動の切り替えなし |

データの項目・結果型と失敗処理は[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]・[[TECSCDE-DT-EL内部仕様 - 07G V0.2.0CDLファイル一覧生成]]、ビューの所有と寿命は[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、純粋計算と編集履歴の分離は[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]を参照します。

### 10.5 セッション保存・復元の追加契約（2026-11-07、監査#9）

[[TECSCDE-DT-EL内部仕様 - 07H セッション保存と復元|7H]]の`SessionSnapshot`を`src/shared/ipc-types.ts`の共有型とする。`FileGateway.saveSession(snapshot)`、preloadの`file.saveSession`、mainの`file:saveSession`は、主ファイル・追加CDL・オプションファイル・追加探索パスの4項目を同じ値として受け渡す。mainは`settings.json`の`lastSession`だけを部分更新する。

起動時の復元結果を供給する`app:bootstrap`にも、ソース群に加えて`optionsFilePath`・採用した`extraImportPaths`・再解析した`systemDirs`を含める。再解析成功時は同じ解析結果の`importPaths`・`systemDirs`を使い、空配列も保存値より優先する。失敗時だけ保存済み探索パスと`systemDirs`空を使う。rendererはこの組を解決用contextとしてimport前に渡し、先にライブストアへ適用しない。採用表と再保存は7H.3.1を正とし、現行コードは未対応（三者監査#8、2026-11-09）。型・欠落項目の正規化・保存失敗・復元中の保存抑止は7Hに従う。復元の分岐は主パスの真偽ではなく7H.0の有効セッション判定に従う。主なしは7Iのnullable primary、空状態はfiles空の成功batchで渡し、失敗nullへ変換しない。shared型・main初期供給・rendererでこの区別を共用する。現行`5cf2d85`は主なしをsamplesへ置換するため未対応（2026-11-09）。

### 10.6 複数ファイルの一括読み込みAPI（2026-11-07、監査#16）

[[TECSCDE-DT-EL内部仕様 - 07I 複数ファイルの一括読み込み契約|7I]]の`OpenPathsRequest`・`OpenPathsBatch`・`OpenPathsResult`を共有型として定義し、`FileGateway.openPaths(request)` → preloadの`file.openPaths(request)` → `file:openPaths` → `FileService.openPaths(request)`を同じ契約へ統一する。主ファイル・参照の役割と`sourceOrder`を明示し、配列の逆順や位置から推定しない。

一括成功結果だけをストアへ適用する。起動時の`app:bootstrap`と7Hのセッションにも、4項目に加えて`sourceOrder`を渡す。解決後は通常のimport追加分を含む実解析順を保存する。役割を持つ`primaryPath`を同じ通常ソースの`primarySourceKey`へ対応付け、basenameや最後のeditableソースから推定しない。`null`と省略は7I.3の異なる契約とし、存在しない明示主は失敗とする。新規セッション保存では`sourceOrder`を必須とし、省略互換は旧設定読取だけに限定する。これらは確定契約であり、現行`5cf2d85`は未対応（三者監査#5、2026-11-09、7I.0）。

rendererの非同期採用は7I.7の`OpenReadGuard`（要求世代・文書世代・revision）で統一する。guardはrenderer内の状態であり、mainの`OpenPathsRequest`や7Kの配送requestIdと混同しない。適用前の照合、同期commitと固定session登録、採用後の通知、busy所有権を分ける。`file-actions`・ストア・起動bootstrap・各読込入口への実装が必要で、現行`5cf2d85`には未反映（三者監査#6、2026-11-09）。

### 10.7 診断ソースジャンプの契約（2026-11-08、監査#18）

[[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ|8B]]の`DiagnosticSourceRef`・`DiagnosticCoordinateKind`（案）を診断の補助情報とする。mainのtecsgen結果には実際の実行cwdと必要なソース本文を関連付け、生成一時ファイルは本文を結果へ保持してから削除する。rendererのRegistry・ナビゲータ・読み取り専用ビューはその値から移動先を決める。位置の原値と、表示座標への変換は分ける。

ディスク本文の取得には既存の副作用のないテキスト読込APIを優先する。必要なら`FileGateway.readTextForView(absolutePath)` → preloadの`file.readTextForView` → `file:readTextForView` → mainの`FileService`を追加し、成功時の本文・パス、失敗時の理由を判別できる結果型にする。図を開く・セッションを保存する処理は起動しない。解析時のスナップショット表示にはファイルI/Oを要求せず、UI側で保持した本文を使う。実装適合は未確認。

通常ファイルから取得した本文には取得時点と解析入力との一致確認有無も関連付ける。外部tecsgenの結果取得時にファイルを読めたことだけで、実行中に解析した版との一致を保証しない。未確認の場合は8Bの表示文言で区別する。

### 10.8 保存結果と未保存状態の契約（2026-11-08、監査#21）

[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定|7J]]の文書保存は`SourceSaveRequest`・`SourceSaveResult`（案）を共有し、`FileGateway.saveSource` → preloadの`file.saveSource` → `file:saveSource` → mainの`FileService.saveSource`で要求と成功／失敗を対応付ける。保存先選択だけの`chooseSavePath`（案）と書き込みを分離し、取消ではソースやbaselineを変更しない。mainは同じ正規化済み保存先への書き込みを直列化し、成功した書込順を返す。

ソース別の保存状態・履歴位置・dirtyの導出はrendererの責務とする。`window:setDirty`と終了確認への回答は、保存結果を反映した現在の統一判定を使い、保存成功だけで無条件にfalseを送らない。画像export・セッション保存はCDL本文の保存checkpointを更新しない。旧7.1〜7.3の簡便な保存API例だけでは文書保存の完了処理を構成せず、7Jの要求・結果管理を通す。rendererの`SaveTicket`は1ソース・1書き込みの固定状態を保持し、mainへ渡す`SourceSaveRequest`との対応と応答照合を7J.4・7J.7に従わせる。旧API等の同じ保存先への書込も共通キューを通し、失敗後も後続要求を処理する。現行`5cf2d85`はこの契約に未対応（三者監査#3、2026-11-08）。

保存完了の照合ではSourceIdと文書世代に加え、保存先世代と現在パスも使い、SaveAs後の旧保存先への完了で現在のcheckpointを戻さない。書込順は同じ保存先内だけで比較する。終了時は7J.9の`CloseStateRequest`／`CloseStateResponse`をsharedで共有し、main→rendererの`window:requestCloseState`、renderer→mainの`window:closeState`、取消時のmain→rendererの`window:cancelCloseState`をpreload・`WindowGateway`へ接続する。mainは通常closeを同期中断し、送信元とqueryIdを照合する。rendererは新規編集等を止めても開始済み保存の完了・checkpoint反映を続け、最新dirtyを返す。mainは新規書込受付を閉じて受理済み保存の完了も確認する。rendererタイムアウトで書込待機を打ち切らず、応答不明はcleanにしない。取消で停止を解除し、成功済みcheckpointは維持する。型・一度限りの閉じる許可・遅延応答除外・受入条件は7J.9を正とし、現行`5cf2d85`は未対応（三者監査#4、2026-11-09）。

### 10.9 エクスポートのバイト列型（2026-11-08、監査#28）

sharedの`ExportData = string | Uint8Array`を、`FileGateway.export`・preloadの`file.export`・`file:export`受信・`FileService.exportFile`の共通型とする。preloadは値を変換せず中継し、mainだけがUint8Arrayのビュー範囲を`Buffer.from(data)`でコピーして、内部の原子的書き込みへ渡す。renderer側APIにBufferを要求しない。詳細は[[TECSCDE-DT-EL内部仕様 - 07F エクスポート設計（たたき台）|7F.7.10.7]]を正とし、PDFのBufferはmain内に留める。実装適合は未確認。

### 10.10 OS関連付け入力の入口（2026-11-08、監査#22）

[[TECSCDE-DT-EL内部仕様 - 07K 関連付け入力の収集と一括オープン|7K]]の`LaunchOpenRequest`（案）は入力元・requestId・順序付きパス列・送信元cwdを持つ。mainのOSアダプタと収集キューがバッチを確定し、7Iの要求へ変換する。macOSはネイティブ配列通知の受信アダプタを追加し、既存open-fileの単数変数上書きで代用しない。Windows/Linuxは関連付けモードを明示して受信し、既起動instanceへ確定済みコンテキストを値として転送する。

起動時の一括結果は`app:bootstrap`で1回供給し、その後の入力は`app:openRequest`（案）と`onOpenRequest`購読でrendererへ渡す。main・preloadはUIのストアを更新せず、rendererが7I・7Jの確認・一括適用・保存を行う。新しいOSアダプタ・ランチャー登録と受信APIの実装適合は未確認。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様 第10章（rendererモジュールのディレクトリ構成の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（本章の依存図の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章（10.2表・行Bの`CdeclExtractor.extract(text)`の設計本体）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
