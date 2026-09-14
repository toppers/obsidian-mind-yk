---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第11章（未決事項と実装単位案）— 外部仕様由来の未決事項に加え、Electron固有の未決事項（sandbox設定・配布方式）と、本書の採否という論点を整理。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 11 of 11（本書の最終章）。

## 11. 未決事項と実装単位案

### 11.1 未決事項（外部仕様由来、既存内部仕様と共通）

複合セルタイプの表現方法・OSクリップボード連携の詳細仕様（本書は往復のCDL断片化までを規定し、それ以上の高度な連携は範囲外）・図全体の自動レイアウトは、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 11 未決事項と実装単位案|TECSCDE-TS内部仕様11.1節]]・[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 10 制約・制限|TECSCDE-DT外部仕様第10章]]と同一であり、Electron固有化とは無関係に残る。

### 11.2 Electron固有の未決事項

| # | 事項 | 現状 |
|---|---|---|
| 1 | ~~`sandbox: true`の採否~~ → **決定済み（2026-09-08）: `sandbox: false`** | preloadをESM（`.mjs`）で書く方針を採ったため`sandbox: false`（Electronのサンドボックス化preloadはESM importを使えない）。`contextIsolation: true`・`nodeIntegration: false`は維持。経緯・トレードオフ: [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定\|preload ESM・sandbox決定]]。第2章2.4節のコードも`.mjs` + `createRequire`によるclipboard取得に更新済み |
| 2 | ~~配布ツールの選定~~ → **一部決定済み（2026-09-12）: パッケージング(package/make)はElectron Forge（`@electron-forge/maker-squirrel`）**。自動更新(publish)・コード署名・macOS/Linux向けMakerは範囲外のまま未決。詳細・導入時に見つかった3件の環境要因（gitフェッチ禁止によるoverrides、electron-winstallerの上流バグ、`@electron/packager`のNode 26非対応）は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]Action Items参照。コード署名の背景知識・設定箇所は[[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]]、選定時に比較したパッケージング・自動更新ツールの一覧は[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]参照 |
| 3 | `tecsgen`・Cプリプロセッサの検出方法 | 第9章9.1節の`TecsgenRunner`は`PATH`頼みの起動（`execFile('tecsgen', ...)`）としたが、複数バージョンの共存やパス設定不備への対応（設定画面での明示的なパス指定等）は未決 |
| 5 | tree-sitterバインディングの選択 | **2026-09-13追加**（[[work/active/TECSCDE内部仕様/TECSCDE内部仕様 - 04 CDLパーサ／シリアライザ設計\|TECSCDE内部仕様第4章]]の改訂に伴う本書固有の選択）。ブラウザ版と異なりElectronはネイティブバインディング（`node-tree-sitter`）を選べるが、**モジュールBはrendererに置かれ`nodeIntegration: false`・`contextIsolation: true`（第2章2.4節）のためrendererからは読み込めない**。したがって選択肢は①rendererで`web-tree-sitter`（WASM）を使う（プロセス配置を変えずに済む・ブラウザ版と同一コード）②CDL解析をmainへ移し`node-tree-sitter`を使う（速いがBの配置を第2章2.2節から変更することになり、解析結果をIPCで渡す設計が増える）。**①を既定とする**——②が要る性能要件は現時点で観測されておらず、プロセス境界を動かす代償に見合わない(unverified／大規模CDLでの実測が要る) |
| 4 | ファイルブラウザの再検討 | [[TECSCDE-DT外部仕様]]第10章10.4節は「技術的に実現可能だが見送り」としていたが、mainプロセスに`fs.readdir`（`FileService`の拡張）が既にあるため、実装コストは低い。採否は引き続き未決 |

### 11.3 Tauriではなくelectronを選ぶことの含意（参考）

本書はElectronに固有化したことで、[[TECSCDE-DT外部仕様]]が言語非依存を保つために避けていた前提を置けるようになった。1点だけ、Tauriとの比較で明らかになった留意点を記す——**ElectronはWebViewを自前でバンドルする（Chromium同梱）ため、TauriのようなOSごとのWebView実装差異（第2章2.4節、[[TECSCDE-DT外部仕様]]第2章2.4節）は生じない**。これはElectron選択の利点だが、その代わりアプリケーションの配布サイズが大きくなる（Chromium同梱のため）というトレードオフを伴う。本書はこのトレードオフの評価自体は行わない（配布方式は11.2節#2のとおり範囲外）。

### 11.4 最初の実装単位の提案

[[TECSCDE-TS内部仕様]]11.3節の提案（モデル＋CDLパーサ／シリアライザのround trip）を土台としつつ、本書固有の検証観点を1つ追加する。

1. **モデル＋CDLパーサのround trip**（[[TECSCDE-TS内部仕様]]11.3節と同一）——外部との唯一の契約点を最初に固める。
2. **IPCゲートウェイの疎通確認を、UIの実装より先に行う。** `FileGateway.open()`→`FileService.openDialog()`→IPC→レンダラでの受信、という一往復が、preloadの`contextBridge`設定を含めて正しく動作することを最初に確認する。これは本書固有の新しいリスク（`contextIsolation`・`sandbox`設定の誤りはUI実装が進んだ後に発覚すると手戻りが大きい）に対する検証観点であり、[[TECSCDE-TS内部仕様]]にはなかった項目である。
3. 次点として`History`のUndo/Redoをヘッドレスでテストする単位（[[TECSCDE-TS内部仕様]]11.3節と同一の優先順位）。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 11 未決事項と実装単位案|TECSCDE-TS内部仕様 第11章（対応する既存設計、外部仕様由来の未決事項の一次情報源）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 10 制約・制限|TECSCDE-DT外部仕様 第10章（ファイルブラウザ見送りの一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]
