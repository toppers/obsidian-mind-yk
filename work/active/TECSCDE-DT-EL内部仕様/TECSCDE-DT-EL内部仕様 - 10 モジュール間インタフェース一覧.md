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
    index.ts                 contextBridge.exposeInMainWorld（2章2.4節）。clipboard直接ブリッジ含む
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
| B | `CdlGrammar`（WASM初期化） ／ `CdlDocumentBuilder.build(cst)` ／ `CdlSerializer.serialize(doc)` ／ `CdeclExtractor.extract(cst)` | gateways（保存・インポート解決時）, app |
| F | `ViewState`（読み取り専用）、`store.viewState` | E, G |
| H | `DiagnosticsCollector.toReport()` | G |
| I（renderer側） | `TecsgenCommandBuilder.build(doc, refs)` | G, `TecsgenGateway` |
| **A（main）** | `window.tecscde.file.*`（`FileGateway`経由、`resolveImports`含む） | G, B |
| **I（main）** | `window.tecscde.tecsgen.*`（`TecsgenGateway`経由、`generate`/`preprocess`/`version`） | G, B |
| **preload** | `window.tecscde.clipboard.*`（`ClipboardGateway`経由、ipcMain不使用） | D（Copy/Paste/Cutコマンド） |

### 10.3 開発ツール方針

[[TECSCDE-TS内部仕様]]10.3節と同一の方針に加え、Electron固有の設定を追加する。

- `contextIsolation: true`・`nodeIntegration: false`を既定とする（rendererプロセスのセキュリティ標準構成）。
- `renderer/`のビルド出力とNode.js APIを要する`main/`・`preload/`のビルドは別のtsconfig（`tsconfig.renderer.json`／`tsconfig.main.json`）で分離し、`renderer/`側は`lib: ["DOM", "ES2020"]`のみを許可することで、Node APIの誤importをコンパイル時にも検出する。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様 第10章（rendererモジュールのディレクトリ構成の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（本章の依存図の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
