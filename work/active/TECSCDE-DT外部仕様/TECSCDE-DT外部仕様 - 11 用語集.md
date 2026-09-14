---
date: 2026-09-05
description: "TECSCDE-DT外部仕様書 第11章（用語集）— TECSCDE外部仕様の用語集を継承し、デスクトップ版固有の4用語（Electron/Tauri/サブプロセス実行/OSクリップボード連携）を追加。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE-DT外部仕様]] (2026-09-05). Chapter 11 of 11（[[TECSCDE外部仕様]]と同一の章構成、最終章）。

## 11. 用語集

TCD・TECSCDE・CDL・CDE・セル・セルタイプ・呼び口・受け口・シグニチャ・結合・結合バー・複合セルタイプ・リージョン・ネームスペース・属性・配列ポート・グリッド・locale・編集可能／編集不可・参照専用ファイル・`__tool_info__`・`direct_import`・整合性チェックの各用語は、[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 11 用語集|TECSCDE外部仕様第11章]]の定義と**完全に同一**。CDL言語一般の用語は同章の方針どおり[[tecsgen外部仕様]]の用語集を正とする。

本書固有の追加用語は次のとおり。

| 用語 | 定義 |
|------|------|
| Electron | TypeScriptによるデスクトップアプリ実装の想定フレームワークの1つ。Chromium＋Node.jsで構成（第1章1.3） |
| Tauri | Rustによるデスクトップアプリ実装の想定フレームワークの1つ。OSネイティブWebView＋Rustで構成（第1章1.3） |
| サブプロセス実行 | 本アプリケーションが外部プロセス（tecsgen本体・Cプリプロセッサ）をOSのプロセスとして起動し、標準出力・標準エラー出力・終了コードを取得する機構。Electron・Tauri両方で実現可能なため採用（第2章2.3、第8章8.4） |
| OSクリップボード連携 | コピーした要素をCDL断片としてOSネイティブのクリップボードへ書き込み、アプリ間・ウィンドウ間で貼り付けを可能にする機能。[[TECSCDE外部仕様]]では範囲外だったが、両フレームワークで実現可能なため本書で新規採用（第6章6.7） |

## Related

- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 11 用語集|TECSCDE外部仕様 第11章（一次情報源）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様（目次）]]
