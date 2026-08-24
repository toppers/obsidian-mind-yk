---
date: 2026-08-16
description: "tecsgen外部仕様書 第2章（動作環境）— tecsgenの実行環境。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 2 of 10.

## 2. 動作環境

| 項目 | 内容 |
|------|------|
| 実装言語 | Ruby |
| 最小 Ruby バージョン | 1.9.2 以降（動作確認済みバージョン: 2.2.2p95） |
| 動作確認 OS | Linux (Ubuntu, Fedora)、macOS X、Windows (Cygwin)、Windows コマンドプロンプト（exerb 版） |
| 依存ライブラリ | 標準ライブラリのみ（`optparse`, `kconv`, `pp`）。構文解析器（`bnf.tab.rb`）は同梱 |
| ツールバージョン（trunk） | 1.9.0 |

---

