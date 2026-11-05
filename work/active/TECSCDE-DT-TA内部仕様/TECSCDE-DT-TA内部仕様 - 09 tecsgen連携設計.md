---
date: 2026-09-05
description: "TECSCDE-DT-TA内部仕様書 第9章（tecsgen連携設計）— backendのTecsgenRunner構造体（std::process::Command）とfrontend側TecsgenGatewayによるRust/Tauri固有のサブプロセス実行実装。"
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

Domain note split from [[TECSCDE-DT-TA内部仕様]] (2026-09-05). Chapter 9 of 11. Rust/Tauri固有化の中心章の1つ。

## 9. tecsgen連携設計

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様第8章8.4節]]が採用した「tecsgenをサブプロセスとして直接実行する」を、Rustの`std::process::Command`（非同期版は`tokio::process::Command`）で実現する。コマンド文字列の組み立て（`TecsgenCommandBuilder`）は[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様第9章]]の設計を関数として**そのまま踏襲**——第2章2.2節のとおりこの部分は純粋な計算処理でありfrontendに残る。

### 9.1 `TecsgenRunner`構造体（backend）

```rust
// src-tauri/src/tecsgen_runner.rs
use tokio::process::Command;
use std::time::Duration;

pub struct TecsgenResult { pub stdout: String, pub stderr: String, pub exit_code: Option<i32>, pub executable_found: bool }

pub struct TecsgenRunner;

impl TecsgenRunner {
    pub async fn run(&self, args: &[String]) -> Result<TecsgenResult, std::io::Error> {
        let output = tokio::time::timeout(
            Duration::from_secs(30),
            Command::new("tecsgen").args(args).output(),
        ).await;

        match output {
            Ok(Ok(out)) => Ok(TecsgenResult {
                stdout: String::from_utf8_lossy(&out.stdout).into_owned(),
                stderr: String::from_utf8_lossy(&out.stderr).into_owned(),
                exit_code: out.status.code(),
                executable_found: true,
            }),
            Ok(Err(e)) if e.kind() == std::io::ErrorKind::NotFound => {
                // 実行ファイルが見つからない（第2章2.4節相当の新規制約）
                Ok(TecsgenResult { stdout: String::new(), stderr: String::new(), exit_code: None, executable_found: false })
            }
            Ok(Err(e)) => Err(e),
            Err(_timeout) => Err(std::io::Error::new(std::io::ErrorKind::TimedOut, "tecsgen timed out")),
        }
    }

    pub async fn version(&self) -> Result<Option<String>, std::io::Error> {
        let result = self.run(&["--version".to_string()]).await?;
        Ok(result.executable_found.then(|| result.stdout.trim().to_string()))
    }
}
```

`Result<TecsgenResult, std::io::Error>`という戻り値は、TypeScript版（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様第9章]]）の`try/catch`による`ENOENT`判定と同じ意図を、Rustの`match`によるエラー種別判定として表現する。`tecsgen`が非0で終了する場合（構文・意味エラーがある場合）は`Command::output()`自体はエラーにならず`ExitStatus`に反映される点はNode.jsの`execFile`（非0終了を例外として扱う）と異なる——Rustの標準ライブラリの挙動に合わせて`Ok(TecsgenResult { exit_code: Some(non_zero), .. })`として扱い、呼び出し側（診断への変換、9.4節）が`exit_code`を見て判断する設計とする。

### 9.2 Tauri commandの登録（backend）

```rust
// src-tauri/src/commands.rs
#[tauri::command]
async fn tecsgen_generate(args: Vec<String>) -> Result<TecsgenResult, String> {
    TecsgenRunner.run(&args).await.map_err(|e| e.to_string())
}

#[tauri::command]
async fn tecsgen_version() -> Result<Option<String>, String> {
    TecsgenRunner.version().await.map_err(|e| e.to_string())
}
```

### 9.3 `TecsgenGateway`構造体（frontend）

```rust
// src/gateways/tecsgen_gateway.rs
use tauri_sys::core::invoke;

pub struct TecsgenGateway;

impl TecsgenGateway {
    pub async fn generate(&self, args: &[String]) -> Result<TecsgenResult, JsValue> {
        invoke("tecsgen_generate", &GenerateArgs { args }).await
    }
    pub async fn version(&self) -> Result<Option<String>, JsValue> { invoke("tecsgen_version", &()).await }
}
```

### 9.4 実行結果の診断への変換

```rust
pub struct TecsgenResultParser;

impl TecsgenResultParser {
    // <ファイル名>:<行>:<列>: error|warning: <メッセージ> を解析する（TECSCDE外部仕様9.1.1の書式）
    pub fn parse(result: &TecsgenResult) -> Vec<Diagnostic> {
        if !result.executable_found {
            return vec![Diagnostic::error("E-TECSGEN-NOT-FOUND", "tecsgen実行ファイルが見つかりません。環境変数PATHを確認してください。")];
        }
        format!("{}{}", result.stdout, result.stderr)
            .lines()
            .filter_map(Self::parse_line)
            .collect()
    }

    fn parse_line(line: &str) -> Option<Diagnostic> {
        // 正規表現（`regex`クレート）で書式を解析し Diagnostic::error/warning を構築
        None
    }
}
```

解析結果は第8章の`DiagnosticsCollector::report()`へそのまま渡す。tecsgen実行結果由来の診断も、CDLインポート時の診断（第8章）と**同じ一覧・同じジャンプ機構**で提示する方針は[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|TECSCDE-DT外部仕様第9章]]・[[TECSCDE-DT-EL内部仕様]]第9章と同一。

### 9.5 実行の起点

「実行(Generate)」操作はモジュールG（UIシェル）から`TecsgenGateway::generate()`を呼ぶ。実行は利用者が明示的にトリガーする操作に限る方針は変更なし。

## Related

- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（本章が実装する外部仕様、8.4節）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 09 tecsgen連携設計|TECSCDE-TS内部仕様 第9章（TecsgenCommandBuilderの一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（Electron版、対比対象）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-DT-TA内部仕様 第8章（診断の集約先）]]
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様（目次）]]

---
