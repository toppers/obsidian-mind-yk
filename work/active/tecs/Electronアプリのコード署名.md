---
date: 2026-09-12
description: "コード署名（Authenticode方式・OV/EV証明書・macOS notarization）の仕組みと、Electron Forge/electron-builder/electron-winstallerでの設定方法の参考ノート。TECSCDE-DT-EL内部仕様第11章11.2節#2・TECSCDE-DT-TA内部仕様第11章11.2節#5の未決事項（配布・自動更新・コード署名）の背景知識。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - reference
---

# Electronアプリのコード署名

## Context

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様11.2節#2]]・[[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-TA内部仕様11.2節#5]]がともに「配布・自動更新・コード署名」を未決事項としている。[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]が2026-09-12にElectron Forge（`@electron-forge/maker-squirrel`）を導入しパッケージング自体は解決したが、**コード署名は未設定のまま**（生成される`Setup.exe`は未署名）。本ノートはその背景知識と、実装時に必要になる設定の参考。

## コード署名とは

実行ファイル/インストーラに、開発者の身元を証明するデジタル署名を付与する仕組み。OSは署名を検証し、①署名者本人が作成したこと、②署名後に改ざんされていないこと、を保証する。

未署名の場合の挙動:

| OS | 挙動 |
|----|------|
| Windows | SmartScreenが「発行元不明のアプリ」警告を出す。「詳細情報」→「実行」を能動的にクリックしないと起動できない |
| macOS | Gatekeeperが起動をブロック。署名に加えて**Apple公証(notarization)**も無いと「壊れている」とすら表示される |

## 仕組み（Windows/Authenticode方式）

1. 認証局（CA）からコード署名証明書を取得
2. `signtool.exe`（Windows SDK付属）や`electron-builder`/`electron-winstaller`内包ツールで、証明書の秘密鍵を使い実行ファイルのハッシュに署名
3. 署名情報とタイムスタンプ（証明書失効後も有効性を保つため）が実行ファイルに埋め込まれる
4. OSが証明書チェーンをルートCAまで検証し、発行元を表示

## 証明書の種類

| 種類 | 特徴 |
|------|------|
| OV（Organization Validation） | 法人確認が必要。年間数万円〜。SmartScreenの「評価」蓄積が必要なため、発行直後もしばらく警告が出ることがある |
| EV（Extended Validation） | 厳格な審査、USBトークン等のハードウェア保管必須。年間数万円〜十数万円。SmartScreen警告が即座に出ないのが利点 |
| macOS Developer ID | Apple Developer Program（年額$99）加入で取得可能。個人開発でも比較的安価 |

個人・小規模開発ではWindows証明書のコスト（特にEVのハードウェアトークン運用）がハードルになりやすい。

## Electronツールチェーンでの設定箇所

- **electron-builder**: `certificateFile`/`certificatePassword`（Windows）、`identity`（macOS）等の設定で署名・notarizationまで自動化
- **electron-winstaller**（`@electron-forge/maker-squirrel`が内部で使用）: `signWithParams`オプションで`signtool.exe`相当の署名パラメータを渡す
- **Electron Forge**: `packagerConfig.osxSign`（macOS）／`packagerConfig.win32metadata`＋外部署名フックで対応

## TECSCDE-DT-ELの現状（2026-09-12時点）

Electron Forge導入は完了したが`forge.config.js`に署名設定は追加していない。現状のビルドを配布するとWindows SmartScreenの警告が出る。個人配布・検証目的であれば当面許容範囲だが、広く配布するなら証明書取得（OV/EV）と`forge.config.js`への`certificateFile`等の追加が必要。

## Related

- [[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]] — 採用したForgeの具体的な使い方（署名設定を追加する際の設定箇所もここ）
- [[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]] — 同じ未決事項のうちパッケージング・自動更新ツールの比較を扱う姉妹ノート
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — Electron Forge導入の実装ノート（本ノートの直接のきっかけ）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章11.2節#2]] — 対応する未決事項
- [[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-TA内部仕様 第11章11.2節#5]] — Tauri版の同種の未決事項（`tauri-plugin-updater`等は別途検討要）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体

