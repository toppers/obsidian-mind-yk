---
date: 2026-08-16
description: "tecsgen内部仕様書 第1章（概要）— 目的、対象バージョン、関連文書。2026-08-23、対象バージョンを1.9.0→1.9.1に訂正。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 1 of 12.

## 1. 概要

### 1.1 目的

本文書は tecsgen の実装内部を記述する。tecsgen のコード読解・改修・テスト仕様作成を行う TECS WG メンバを対象読者とする。

### 1.2 対象バージョン

`tecslib/version.rb` で管理。現在のトランクバージョン: **1.9.1**（2026-08-23確認。旧版は1.9.0としていたが実測と不一致）。

### 1.3 関連文書

| 文書 | 内容 |
|------|------|
| [[tecsgen外部仕様]] | CLI・入出力・エラー形式 |
| TECS CDL リファレンスマニュアル | CDL 言語仕様 |
| TECS コンポーネント実装モデルリファレンスマニュアル | 生成コードの仕様 |

---

