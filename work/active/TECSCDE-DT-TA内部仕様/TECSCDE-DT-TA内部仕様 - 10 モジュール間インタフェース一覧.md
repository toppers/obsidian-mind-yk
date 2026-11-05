---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第10章（モジュール間インタフェース一覧）— Cargoワークスペース構成（src-tauri/backend + frontend/wasm32）とTauri commandの一覧。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 10 of 11。

## 10. モジュール間インタフェース一覧

第2章の依存図・プロセス配置を、Cargoワークスペースの構成まで落とし込む。

```
Cargo.toml               [workspace] members = ["src-tauri", "frontend"]

src-tauri/                (backend、ネイティブターゲット)
  Cargo.toml
  tauri.conf.json           allowlist/capabilities設定
  src/
    file_service.rs           A: FileService（std::fs, dialogプラグイン、7章）
    tecsgen_runner.rs          I: TecsgenRunner（std::process、9章）
    commands.rs                #[tauri::command] 関数群
    main.rs                    起動処理・コマンドライン引数/open-fileの処理（7.4節）

frontend/                 (frontend、wasm32-unknown-unknown ターゲット)
  Cargo.toml
  src/
    model/                  (C) cell.rs, port.rs, join.rs, region.rs, document.rs — 3章と同一
    cdl/                    (B) lexer.rs, parser.rs, serializer.rs, tool_info.rs
    commands/               (D) command.rs（トレイト）, history.rs, ops/*.rs（clipboard連携含む、4章）
    render/                 (E) svg_renderer.rs（web-sys）, hit_test.rs, gesture.rs — 5章と同一
    view_state/             (F) view_state.rs, display_filters.rs — 6章と同一
    ui_shell/               (G) toolbar.rs, palette.rs, property_panel.rs, status_bar.rs, dialogs/
    diagnostics/            (H) collector.rs, tecsgen_result_parser.rs（9章）
    gateways/                  file_gateway.rs（7章）, tecsgen_gateway.rs（9章）, clipboard_gateway.rs（4章）
    tecsgen_link/           (I) command_builder.rs — TECSCDE-TS内部仕様9章と同一
    app/
      store.rs                 Store（C・F・Hを束ねる）
      main.rs                  #[wasm_bindgen(start)] エントリポイント
```

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-DT-EL内部仕様第10章]]（Electron版）と比較すると、`main/`・`preload/`・`renderer/`という3ディレクトリ構成が`src-tauri/`・`frontend/`という**2ディレクトリ構成**になる——preloadに相当する層がないという第2章の設計と対応する。

### 10.1 プロセス間の依存の機械的強制

- `frontend/`配下のいかなるファイルも、ネイティブOS API（`std::fs`・`std::process`等）に依存するクレートを直接使ってはならない——そもそも`wasm32-unknown-unknown`ターゲットでは大半のネイティブクレートがコンパイルエラーになるため、**Rustのターゲット分離がこの制約を言語・ビルドシステムのレベルで強制する**（Electron版がdependency-cruiserによる静的解析で強制していたのに対し、Tauri版はコンパイルの成否そのものが検証手段になる点が実質的な差分）。
- `src-tauri/`配下のファイルはDOM/SVGへアクセスしてはならない（`web-sys`のDOM系APIは`wasm32`ターゲット外では利用できないため、これもコンパイルエラーとして自然に検出される）。

### 10.2 モジュール間の主要インタフェース

| 提供モジュール | インタフェース | 利用モジュール |
|---|---|---|
| C | `TecscdeDocument`（読み取り専用メソッドのみ公開） | 全frontend側モジュール |
| D | `Command`トレイト／`History`／`store.dispatch(command)` | G, E |
| B | `CdlParser::parse(text)` ／ `CdlSerializer::serialize(doc)` | gateways（保存時）, app |
| F | `ViewState`（読み取り専用）、`store.view_state` | E, G |
| H | `DiagnosticsCollector::to_report()` | G |
| I（frontend側） | `TecsgenCommandBuilder::build(doc, refs)` | G, `TecsgenGateway` |
| **A（backend）** | `invoke("file_*", ...)`（`FileGateway`経由） | G |
| **I（backend）** | `invoke("tecsgen_*", ...)`（`TecsgenGateway`経由） | G |
| **backend（クリップボード）** | `invoke("clipboard_*", ...)`（`ClipboardGateway`経由） | D（Copy/Paste/Cutコマンド） |

Electron版の表（[[TECSCDE-DT-EL内部仕様]]10.2節）と異なり、**「preload直接ブリッジ」という行が存在しない**——クリップボードも他のbackend機能と同じ`invoke`の行に統一される（第2章2.3節）。

### 10.3 開発ツール方針

- `frontend/Cargo.toml`は`crate-type = ["cdylib"]`（WASM出力）、`src-tauri/Cargo.toml`はネイティブバイナリとして別々にビルドする。
- `wasm-pack`または`trunk`でfrontendをビルドし、Tauriの`tauri.conf.json`の`build.frontendDist`に出力先を指定する。
- `tauri.conf.json`の`app.security.csp`・`plugins`（`dialog`・`clipboard-manager`）で、frontendに公開するcommandの範囲を明示的に絞る——Electronの`contextIsolation`設定に相当する、Tauri側のケイパビリティ設定。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-TS内部仕様 第10章（frontendモジュールのディレクトリ構成の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 10 モジュール間インタフェース一覧|TECSCDE-DT-EL内部仕様 第10章（Electron版、対比対象）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-TA内部仕様 第2章（本章の依存図の一次情報源）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---
