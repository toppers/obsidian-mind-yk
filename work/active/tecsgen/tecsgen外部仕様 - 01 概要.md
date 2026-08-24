---
date: 2026-08-16
description: "tecsgen外部仕様書 第1章（概要）— 目的、ビルドシステムにおける位置付け、対象読者、関連文書。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 1 of 10.

## 1. 概要

### 1.1 目的

tecsgen は TECS（TOPPERS Embedded Component System）のコンポーネント記述コンパイラである。CDL（Component Description Language）で記述されたコンポーネント構成を入力として受け取り、C 言語のセルタイプ実装用コードおよびカーネル設定コードを生成する。

### 1.2 ビルドシステムにおける位置付け

```
.cdl ファイル
    ↓ tecsgen
生成コード（_tecsgen.h, _factory.h, tecsgen.cfg, テンプレート .c/.h）
    ↓ tecsmerge（手書きコードへのマージ）
セルタイプ実装コード
    ↓ C コンパイラ
実行ファイル
```

### 1.3 対象読者

- TECS を利用して組込みシステムを開発するアプリケーション開発者
- tecsgen を利用する TECS ユーザー
- TECS カーネルライブラリ（ASP3 等）の組み込み担当者

### 1.4 関連文書

| 文書 | 内容 |
|------|------|
| CDL リファレンスマニュアル | CDL 言語仕様の詳細 |
| TECS コンポーネント実装モデルリファレンスマニュアル | 生成コードの詳細 |
| TECS コンポーネント図（TCD）リファレンスマニュアル | コンポーネント図の記法 |
| tecsmerge コマンドリファレンス | tecsmerge の使い方 |
| tecsflow コマンドリファレンス | tecsflow の使い方 |

---

