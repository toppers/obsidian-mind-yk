---
date: 2026-09-12
description: "Electronアプリのパッケージング・自動更新ツールの比較参考ノート（electron-builder、Forge、Squirrel、update-electron-app等）。DT-EL・DT-TA内部仕様の背景知識。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - reference
---

# Electronアプリの配布・自動更新ツール

## Context

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様11.2節#2]]の「配布・自動更新・コード署名の実現手段」という未決事項の検討過程でのツール比較。[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]は2026-09-12にこのうちパッケージング(package/make)部分を**Electron Forge**（`@electron-forge/maker-squirrel`）で解決したが、自動更新(publish)は未着手。本ノートは選定時に比較した候補群の記録。

## パッケージング（配布物の生成）

| ツール | 特徴 |
|--------|------|
| **electron-builder** | 単一の設定ファイル（`package.json`内または`electron-builder.yml`）からWindows/macOS/Linux向け配布物を生成。コード署名（Windows Authenticode・macOS notarization）を統合的に扱える。`electron-updater`（同作者）と組み合わせて自動更新まで一気通貫 |
| **Electron Forge**（採用） | Electron公式が推奨する統合CLIツール。パッケージング・署名・配布メーカー（Squirrel/DMG/deb/rpm等）・自動更新（`update-electron-app`等と連携）までプラグイン形式で一括管理。事実上の公式デファクト |
| **electron-packager** | 最小限のパッケージング専用ツール（署名・インストーラ生成・自動更新は含まない、より低レベル。Electron ForgeやTECSCDE-DT-ELが検証で直接叩いたのもこの層） |
| **@electron/osx-sign / @electron/notarize** | macOSの署名・notarizationのみを担う単機能パッケージ（electron-builder内部でも利用） |

## 自動更新

| ツール/方式 | 特徴 |
|------|------|
| **electron-updater** | electron-builder前提（`latest.yml`等のビルド時生成メタデータを参照）。GitHub Releases/S3/Generic HTTPサーバ等へ更新チェック→差分ダウンロード→次回起動時に自動適用。macOSでは署名・notarizationが実質必須 |
| **Squirrel.Windows / Squirrel.Mac** | Electron初期からある自動更新の基盤技術。electron-updaterも内部でSquirrel.Macを利用。Forgeの`@electron-forge/maker-squirrel`と組み合わせて使うことが多い |
| **update-electron-app** | Electron公式の薄いラッパー。内部的にGitHub ReleasesとSquirrelを使い、数行のコードで自動更新を有効化 |
| **Nucleus** | セルフホスト型の更新サーバ実装（OSS）。自前インフラで配信を完結させたい場合の選択肢 |
| **独自実装** | `net`モジュールで更新確認APIを叩き、差分ファイルをダウンロードして`app.relaunch()`する等のフルスクラッチ方式。保守コストは高いが自由度も高い |

## OSネイティブの配布チャネル（自前の自動更新実装が不要になる代替）

| 方式 | 特徴 |
|------|------|
| Mac App Store / Microsoft Store | OS標準のストア配布。更新はストア側に委ねられるが審査・サンドボックス制約を受ける |
| Homebrew Cask（macOS）/ winget・Chocolatey（Windows）/ Snap・Flatpak（Linux） | パッケージマネージャ経由の配布。ユーザー側の`brew upgrade`等が更新手段になる |

## TECSCDE-DT-ELでの選定状況（2026-09-23時点）

パッケージング（package/make）は**Electron Forge**を採用・動作確認済み（実装詳細は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]Action Items参照）。自動更新(publish)は**決定済み**: `update-electron-app` + GitHub Releasesを採用。push先の`origin`（`toppers/tecscde-dt-el`）が当時非公開リポジトリであったため一時的に配布専用の公開ミラーリポジトリ案を検討したが、同日中にユーザーがoriginをpublicへ変更したため撤回——**origin自身へ直接publish**する構成で確定した。決定の経緯は[[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|TECSCDE-DT-EL 配布アーキテクチャ決定]]参照。

## Related

- [[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|TECSCDE-DT-EL 配布アーキテクチャ決定]] — 本ノートの比較検討をもとに確定した自動更新方式の決定記録（2026-09-23）
- [[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]] — 採用したForgeの具体的な使い方（インストール・コマンド・forge.config.js構造）
- [[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]] — 同じ未決事項のうちコード署名の仕組み（OV/EV証明書・Authenticode）を扱う姉妹ノート
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — Electron Forge導入の実装ノート
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章11.2節#2]] — 対応する未決事項
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-TA内部仕様 第11章11.2節#5]] — Tauri版の同種の未決事項（`tauri-plugin-updater`は別エコシステムのため本ノートの対象外）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体

