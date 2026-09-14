---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第7章（ファイルI/O設計）— backendのFileService構造体（std::fs+dialogプラグイン、アトミック書き込み）とfrontend側FileGateway（invoke経由）。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 7 of 11. Rust/Tauri固有化の中心章の1つ。

## 7. ファイルI/O設計

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様第5章]]の規定（真の上書き保存、ファイル関連付け、複数ファイル対応）を実現する。

### 7.1 `FileService`構造体（backend）

```rust
// src-tauri/src/file_service.rs
use tauri_plugin_dialog::DialogExt;
use tokio::fs;

pub struct FileService { window: tauri::Window }

impl FileService {
    pub fn new(window: tauri::Window) -> FileService { FileService { window } }

    pub async fn open_dialog(&self) -> Result<Option<OpenResult>, std::io::Error> {
        let paths = self.window.dialog()
            .file()
            .add_filter("CDE files", &["cde", "cdl"])
            .blocking_pick_files(); // 複数選択可
        let Some(paths) = paths else { return Ok(None); };

        let mut contents = Vec::new();
        for p in &paths {
            contents.push(fs::read_to_string(p.as_path().unwrap()).await?);
        }
        let editable_path = paths.last().unwrap().clone(); // 最後に選択したファイルを編集対象とする
        let editable_content = contents.pop().unwrap();
        Ok(Some(OpenResult {
            editable: FileEntry { path: editable_path.to_string(), content: editable_content },
            references: paths[..paths.len()-1].iter().zip(contents)
                .map(|(p, c)| FileEntry { path: p.to_string(), content: c })
                .collect(),
        }))
    }

    pub async fn save(path: &str, content: &str) -> Result<(), std::io::Error> {
        Self::write_atomic(path, content).await
    }

    pub async fn save_as_dialog(&self, suggested_name: &str, content: &str) -> Result<Option<String>, std::io::Error> {
        let path = self.window.dialog()
            .file()
            .set_file_name(suggested_name)
            .add_filter("CDE files", &["cde"])
            .blocking_save_file();
        let Some(path) = path else { return Ok(None); };
        let path_str = path.to_string();
        Self::write_atomic(&path_str, content).await?;
        Ok(Some(path_str))
    }

    async fn write_atomic(path: &str, content: &str) -> Result<(), std::io::Error> {
        let tmp_path = format!("{path}.tmp-{}", std::process::id());
        fs::write(&tmp_path, content).await?;
        fs::rename(&tmp_path, path).await // 同一ファイルシステム内であればOSレベルでアトミック
    }
}
```

Electron版（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様第7章]]）と同じく、一時ファイル書き込み＋リネームでアトミックな上書き保存を実現する。`std::io::Error`をそのまま伝播させる設計は、Rustの`Result`型による標準的なエラーハンドリングであり、TypeScript版の`try/catch`より呼び出し側にエラー処理を強制する度合いが強い（第3章3.3節で述べた傾向と同じ）。

### 7.2 Tauri commandの登録（backend）

```rust
// src-tauri/src/commands.rs
#[tauri::command]
async fn file_open(window: tauri::Window) -> Result<Option<OpenResult>, String> {
    FileService::new(window).open_dialog().await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn file_save(path: String, content: String) -> Result<(), String> {
    FileService::save(&path, &content).await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn file_save_as(window: tauri::Window, content: String, suggested_name: String) -> Result<Option<String>, String> {
    FileService::new(window).save_as_dialog(&suggested_name, &content).await.map_err(|e| e.to_string())
}
```

`Result<T, String>`という戻り値型は、Tauri commandの標準的な慣習である——`invoke`側（frontend）は`Err`をJavaScript例外相当として受け取る。エラー型を`String`に落とすのは簡便だが、より厳密な型を保ちたい場合は`serde::Serialize`を実装したカスタムエラー型を使ってもよい(unverified／実装時の選択)。

### 7.3 `FileGateway`構造体（frontend）

```rust
// src/gateways/file_gateway.rs
use tauri_sys::core::invoke;

pub struct FileGateway;

impl FileGateway {
    pub async fn open(&self) -> Result<Option<OpenResult>, JsValue> { invoke("file_open", &()).await }
    pub async fn save(&self, path: &str, content: &str) -> Result<(), JsValue> {
        invoke("file_save", &SaveArgs { path, content }).await
    }
    pub async fn save_as(&self, content: &str, suggested_name: &str) -> Result<Option<String>, JsValue> {
        invoke("file_save_as", &SaveAsArgs { content, suggested_name }).await
    }
}
```

`DirtyTracker`構造体（未保存状態の管理、`History.past.len()`基準）は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]の設計を struct+impl として**そのまま踏襲**——プロセス境界とは無関係な純粋なfrontend側の状態である。

### 7.4 起動時のファイルオープン経路

[[TECSCDE-DT外部仕様]]5.3節が新設した2経路（コマンドライン引数・ファイル関連付け）は、backend側の起動処理で扱う。

```rust
// src-tauri/src/main.rs
fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // コマンドライン引数、または .cde/.cdl ファイルの「アプリで開く」
            let args: Vec<String> = std::env::args().collect();
            if let Some(path) = args.iter().find(|a| a.ends_with(".cde") || a.ends_with(".cdl")) {
                app.manage(PendingOpenPath(Some(path.clone())));
            }
            Ok(())
        })
        // macOS: Tauriの `tauri-plugin-single-instance` や `RunEvent::Opened` でファイル関連付けイベントを扱う
        .invoke_handler(tauri::generate_handler![file_open, file_save, file_save_as])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

`PendingOpenPath`（Tauriの`app.manage`で保持する共有状態）は、frontendの初期化完了後に専用のTauri command（`app_pending_open_path`）で取得し、`FileGateway`を介した通常のダイアログを開かず直接読み込む。

### 7.5 インポート参照先の解決

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.1・5.3節]]および同第8章8.1節が規定する参照先の自動追跡は、frontendのモジュールBが抽出したインポート要求をbackendのTauri commandへ渡して実現する。

```rust
pub enum ImportKind { Import, ImportC }
pub struct ImportRequest { pub kind: ImportKind, pub specifier: String }
pub struct ImportResolutionOptions {
    pub base_dir: Option<String>,
    pub import_paths: Vec<String>,
    pub cpp: Option<String>,
}
pub struct ResolvedImport {
    pub request: ImportRequest,
    pub canonical_path: Option<String>,
    pub content: Option<String>,
    pub error: Option<ImportResolutionError>,
}
```

`FileGateway::resolve_imports(editable_path, requests, options)`は`file_resolve_imports` commandを呼ぶ。backendは、編集対象ファイルのディレクトリ、`base_dir`、`import_path`の順に候補を`std::fs::canonicalize`で正規化して存在を検証し、実在したファイルをUTF-8として読み取って返す。frontendは返されたCDLを再びモジュールBへ渡し、追加の`import`／`import_C`を再帰的に解決する。循環参照と重複読み込みはbackendが返す正規化済み絶対パスをキーにfrontend側で抑止する。

`base_dir`・`import_path`・`cpp`の保存値は解決処理へ入力するだけで、正規化結果や現在の環境に合わせてモデル内の値を書き換えない。解決失敗は`ImportResolutionError`として返し、第8章の診断へ変換する。`import_C`で用いる`cpp`は第9章9.6節へ渡す起動候補であり、ファイルI/O command自身は外部プロセスを起動しない。

## Related

- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（本章が実装する外部仕様）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様 第7章（DirtyTrackerの一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（Electron版、対比対象）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-TA内部仕様 第2章（プロセス配置の根拠）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---
