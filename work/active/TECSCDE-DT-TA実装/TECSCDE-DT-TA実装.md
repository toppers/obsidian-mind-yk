---
date: 2026-09-07
description: "TECSCDE-DT-TA（Tauri・Rust）の実装進捗ノート。2026-09-07にローカルリポジトリを git init（初期化のみ、README＋.gitignore、実装は未着手）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

# TECSCDE-DT-TA実装

## Context

- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]]（Tauri・Rust、struct/impl/trait設計、backend/frontendの2層プロセス境界、全11章執筆完了 2026-09-05）に対応する実装。
- 対象ローカルリポジトリ: `E:\Ccur\typescript\TECSCDE-DT-TA`（[[TECSCDE-JS-TS実装]]の`E:\Ccur\typescript\TECSCDE`、[[TECSCDE-TS実装]]の`E:\Ccur\typescript\TECSCDE-TS`、[[TECSCDE-DT-EL実装]]の`E:\Ccur\typescript\TECSCDE-DT-EL`とは別リポジトリ）。**2026-09-07に`git init`（初期化のみ）**。
- 対象リモートリポジトリ: 未作成（ローカルのみ、2026-09-07時点）。

## Notes

- **2026-09-07、リポジトリ初期化のみ実施**（ユーザ指示によりスコープを初期化に限定）:
  - `git init`（default branch `main`）、初回コミット `chore: initialize repository`（`5c568f6`）。
  - `README.md` — [[TECSCDE-DT-TA内部仕様]]へのリンク、姉妹リポジトリとの関係、第10章のディレクトリ構成案、第11章11.4節の最初の実装単位、ツールチェーンの現状を記載。
  - `.gitignore` — Rust用（`/target`、`*.log`、wasm出力、`om_MCP.md`シンボリックリンク）。
  - `om_MCP.md` シンボリックリンク（`~/.agents/rules/om_MCP.md`宛、[[TECSCDE-DT-EL実装]]に倣う。gitには含めず）。
- **[[TECSCDE-DT-EL実装]]との違い**: EL版は初回コミットで`tecscde-ts`からmodel/CDL/diagnosticsを**そのままコピー**して移植できたが、本書は対応するRust実装が存在しないため、model/CDL層も`tecscde-ts`内部仕様からのRustへの**新規移植**になる（コピーではない）。
- **ツールチェーンの現状（as of 2026-09-07、この開発環境）**: Rust 1.97.1あり、ただし`x86_64-pc-windows-msvc`ターゲットのみ。`wasm32-unknown-unknown`ターゲット・`tauri-cli`・`trunk`/`wasm-pack`は未導入。
- **未決事項（[[TECSCDE-DT-TA内部仕様 - 11 未決事項と実装単位案|内部仕様11.2節]]）**: `tauri-sys`の成熟度、`im`クレートの採否、フロントエンドを完全にRustにする判断の妥当性、Rust/WASMのデバッグ体験。

## Action Items

- [x] ローカルリポジトリの`git init`（初期化のみ）
- [ ] Cargoワークスペース骨格の作成（root `Cargo.toml` + `src-tauri/` + `frontend/`、[[TECSCDE-DT-TA内部仕様 - 10 モジュール間インタフェース一覧|第10章]]）
- [ ] `rustup target add wasm32-unknown-unknown` ＋ `tauri-cli`/`trunk` 導入
- [ ] 第11章11.4節#1: model + CDLパーサ/シリアライザのround trip（`tecscde-ts`内部仕様からRustへ移植、`cargo test`）
- [ ] 第11章11.4節#2: `wasm32-unknown-unknown`ビルド・WebView上での実行確認
- [ ] 第11章11.4節#3: `invoke`の疎通確認（`FileGateway::open()`→`file_open` command→`invoke`→frontend受信）
- [ ] リモートリポジトリの作成（[[TECSCDE-TS実装]]に倣うなら`tecscde-dt-ta`）

## Related

- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様|TECSCDE-DT-TA内部仕様]] — 本実装が対応する内部仕様（全11章）
- [[TECSCDE-DT-EL実装]] — 姉妹実装（Electron・TypeScript）。リポジトリ構成・進め方の先例
- [[TECSCDE-TS実装]] — model/cdl/diagnosticsの移植元（設計の一次情報源）
- [[TECSCDE-JS-TS実装]] — 現行の関数ベース・ブラウザ版実装（比較対象）
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]] — 本実装が実現する外部仕様（デスクトップ版）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
- [[North Star]] — 🔴最優先はTECSCDE JS版実装（本実装はデスクトップ・Tauri版という別ラインの検証）
