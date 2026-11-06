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
| B | `CdlGrammar`（WASM初期化） ／ `CdlDocumentBuilder.build(text)` ／ `CdlSerializer.serialize(doc)` ／ `CdeclExtractor.extract(text)` | gateways（保存・インポート解決時）, app |
| F | `ViewState`（読み取り専用）、`store.viewState` | E, G |
| H | `DiagnosticsCollector.toReport()` | G |
| I（renderer側） | `TecsgenCommandBuilder.build(doc, refs)` | G, `TecsgenGateway` |
| **A（main）** | `window.tecscde.file.*`（`FileGateway`経由、`resolveImports`含む） | G, B |
| **I（main）** | `window.tecscde.tecsgen.*`（`TecsgenGateway`経由、`generate`/`preprocess`/`version`） | G, B |
| **preload** | `window.tecscde.clipboard.*`（`ClipboardGateway`経由、ipcMainの`clipboard:writeText`／`clipboard:readText`を呼ぶ。Promiseを返す） | `AppStore`（コピー・カット）、`clipboard-actions`（貼り付けの読み取り）。Copy／Paste／Cutコマンド（D）はゲートウェイを直接呼ばない（4章4.1節） |

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
| CDL一覧生成 | `CdlFileListService`案、fs | 情報ダイアログ、`FileGateway` | `file:createCdlFileLists` |
| 定義ファイル表示 | 既存のテキスト読込処理 | `DefinitionFileView`案 | 既存API再利用を優先 |
| active・結合・リージョン表示 | なし | `AppStore`、`ViewState`、`DisplayFilters`、`SvgRenderer` | renderer内で完結 |
| active最上段配置 | なし | 純粋な配置計算と編集`Command` | `History`で再生 |
| 仮想ファイル・プラグイン相当 | 配置先TBC | 配置先TBC | メモリ内の契約骨格のみ。IPC新設の要否もTBC |

データの項目・結果型と失敗処理は[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]・[[TECSCDE-DT-EL内部仕様 - 07G V0.2.0CDLファイル一覧生成]]、ビューの所有と寿命は[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、純粋計算と編集履歴の分離は[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]を参照します。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様 第10章（rendererモジュールのディレクトリ構成の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（本章の依存図の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09B CdeclExtractor設計|TECSCDE-DT-EL内部仕様 第9B章（10.2表・行Bの`CdeclExtractor.extract(text)`の設計本体）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
