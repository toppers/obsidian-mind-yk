---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第2章（モジュール構成とプロセス境界）— 9モジュールをbackend/frontendへ配置し、Tauri commandとGatewayによるinvoke契約を設計する。本書の中心章。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 2 of 11. **本書の中心章**。

## 2. モジュール構成とプロセス境界

### 2.1 モジュール一覧・依存方向は既存と同一

9モジュール（A〜I）の責務・依存方向は[[TECSCDE内部仕様]]第2章・[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様第2章]]と**同一であり、本章では再掲しない**。本章が決めるのは、これらをTauriのbackend／frontendにどう配置するかという軸である。

### 2.2 モジュール別プロセス配置

| # | モジュール | 配置 | 理由 |
|---|---|---|---|
| A | ファイルI/O | **backend**（`FileService`構造体） | `std::fs`・Tauriの`dialog`プラグインはbackend専用 |
| B | CDLパーサ／シリアライザ | **frontend** | 純粋な計算処理。OSリソースへのアクセスを要しない。**2026-09-13追記**: 構文解析をtree-sitter文法へ委ねる改訂（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]）を受けても配置は変わらないが、本書はfrontendもRust（`wasm32-unknown-unknown`）であるため、backendの`tree-sitter`クレートを使う選択肢が別に生じる。11.2節#6 |
| C | モデル | **frontend** | UIから直接操作されるため |
| D | 編集コマンド／Undo-Redo | **frontend** | UI操作に同期的に応答する必要がある |
| E | 描画（SVGレンダリング） | **frontend** | DOM/SVGへのアクセスはWebView内（frontend）でのみ可能 |
| F | 表示制御（View State） | **frontend** | UI状態そのもの |
| G | UIシェル | **frontend** | 同上 |
| H | 整合性チェック／診断 | **frontend** | B（frontend）とI（backendの実行結果をinvoke経由で受け取る）の両方から集約 |
| I | tecsgen連携 | **backend**（`TecsgenRunner`構造体）＋**frontend**（コマンド文字列組み立て） | サブプロセス起動（`std::process::Command`）はbackend専用。文字列組み立て自体は純粋な計算処理でありfrontendに残せる |

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様第2章]]（Electron版）と**配置の結論は同一**（backend必須はA・Iのみ）——プロセス境界という軸自体はフレームワークに依存せず、OSリソースへのアクセス要否という同じ基準で決まるためである。

### 2.3 invokeによる統一されたゲートウェイ

Electron版はファイルI/O・tecsgen実行をIPC経由、クリップボードをpreloadからの直接ブリッジ、という**2種類の経路**を使い分けていた（[[TECSCDE-DT-EL内部仕様]]第2章2.4節）。Tauriには preload に相当する層がなく、**クリップボードを含む全てのネイティブ操作を`invoke`という単一の経路で統一する。**

```
┌──────────────── backend (Rust native) ────────────────┐
│  FileService       TecsgenRunner       ClipboardService │
│  (std::fs, dialog)  (std::process)      (tauri-plugin-   │
│                                          clipboard-manager)│
└───────────────────────┬─────────────────────────────────┘
                         │ #[tauri::command] + generate_handler!
┌────────────────────────┴─────────────────────────────────┐
│                  frontend (Rust + WASM)                     │
│  FileGateway   TecsgenGateway   ClipboardGateway            │
│  (invoke経由)  (invoke経由)     (invoke経由。Electron版と    │
│                                 異なり直接ブリッジではない)   │
│         ↓             ↓                ↓                    │
│              G (UIシェル) が呼び出す                          │
└──────────────────────────────────────────────────────────┘
```

```rust
// src-tauri/src/commands.rs（backend）
#[tauri::command]
async fn file_open(window: tauri::Window) -> Result<Option<OpenResult>, String> {
    FileService::new(window).open_dialog().await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn file_save(path: String, content: String) -> Result<(), String> {
    FileService::write_atomic(&path, &content).await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn tecsgen_generate(args: Vec<String>) -> Result<TecsgenResult, String> {
    TecsgenRunner::new().run(&args).await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn clipboard_write_text(text: String, app: tauri::AppHandle) -> Result<(), String> {
    app.clipboard().write_text(text).map_err(|e| e.to_string())
}

#[tauri::command]
async fn clipboard_read_text(app: tauri::AppHandle) -> Result<String, String> {
    app.clipboard().read_text().map_err(|e| e.to_string())
}
```

```rust
// src-tauri/src/main.rs
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .invoke_handler(tauri::generate_handler![
            file_open, file_save, file_save_as, file_export,
            tecsgen_generate, tecsgen_version,
            clipboard_write_text, clipboard_read_text,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

```rust
// src/gateways/file_gateway.rs（frontend、wasm32ターゲット）
use tauri_sys::core::invoke;

pub struct FileGateway;

impl FileGateway {
    pub async fn open(&self) -> Result<Option<OpenResult>, JsValue> {
        invoke("file_open", &()).await
    }
    pub async fn save(&self, path: &str, content: &str) -> Result<(), JsValue> {
        invoke("file_save", &SaveArgs { path, content }).await
    }
}

pub struct ClipboardGateway;

impl ClipboardGateway {
    pub async fn write_text(&self, text: &str) -> Result<(), JsValue> {
        invoke("clipboard_write_text", &ClipboardArgs { text }).await
    }
    pub async fn read_text(&self) -> Result<String, JsValue> {
        invoke("clipboard_read_text", &()).await
    }
}
```

`invoke`は`tauri-sys`クレート（Tauri公式ではないが広く使われるRust向けラッパー）が提供する関数で、内部的には`window.__TAURI__.core.invoke`へ橋渡しする。`serde`による型付きの引数・戻り値のシリアライズ／デシリアライズが標準で効く点は、TypeScript版の`JSON`シリアライズと同等だが、Rust側は`serde::Serialize`/`Deserialize`導出によりコンパイル時に型が検証される。

### 2.4 Electron版との対比のまとめ

| 観点 | [[TECSCDE-DT-EL内部仕様]]（Electron） | 本書（Tauri） |
|---|---|---|
| プロセス層 | main／preload／renderer の3層 | backend／frontend の2層 |
| クリップボードのアクセス経路 | preloadから直接ブリッジ（IPC不使用） | 他のネイティブ操作と同じ`invoke`経路（backend経由） |
| ゲートウェイの実装言語 | TypeScript（`ipcRenderer.invoke`のラップ） | Rust（`tauri_sys::core::invoke`のラップ） |
| 型の受け渡し | `JSON.stringify`相当、型はTypeScriptの構造的型付けに依存 | `serde`による導出、コンパイル時によりコンパイル時に検証される |

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 02 モジュール構成と責務境界|TECSCDE-TS内部仕様 第2章（モジュール分割・依存方向の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（Electron版のプロセス境界設計、対比対象）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-TA内部仕様 第7章（FileService/FileGatewayの詳細）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-TA内部仕様 第9章（TecsgenRunner/TecsgenGatewayの詳細）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---
