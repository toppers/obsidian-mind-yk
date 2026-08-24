---
date: 2026-08-16
description: "TECSCDE外部仕様書 第1章（概要）— 目的、ツールチェーン内の位置付け、対象読者、関連文書。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE外部仕様]] (2026-08-16, 141KB threshold). Chapter 1 of 11.
## 1. 概要

### 1.1 目的

TECSCDE（TECS Component Diagram Editor）は、TECS のコンポーネント構成をコンポーネント図（TCD: TECS Component Diagram）として視覚的に作成・編集するための設計環境である。CDL（Component Description Language）で手書きしていたセルタイプ定義・組み上げ記述を、図的な操作（セルの配置・呼び口/受け口の結合）に置き換え、CDL ファイルとの双方向変換（インポート／エクスポート）を提供する。

これにより、CDL の構文を直接記述せずにコンポーネント構成を設計・レビューできるようにし、TECS 採用時の学習コストと記述ミスを削減することを目的とする。

### 1.2 ツールチェーンにおける位置付け

```
.cdl ファイル
    ↕ TECSCDE（読み込み・書き出し）
コンポーネント図（TCD）
    ↓ エクスポート
.cdl ファイル / 画像（SVG・PNG）
    ↓ tecsgen
生成コード（実装は [[tecsgen外部仕様]] を参照）
```

TECSCDE は tecsgen の**前段**に位置する設計ツールである。TECSCDE 自体はコード生成を行わず、CDL ファイルの生成・編集までを担当する。生成された `.cdl` は tecsgen にそのまま入力できる。

### 1.3 対象読者

- TECS を用いてコンポーネントベースの組込みシステムを設計するアプリケーション開発者
- CDL を手書きせず、図によるコンポーネント設計を行いたい設計者
- 既存の `.cdl` ファイルを可視化し、レビュー・仕様確認したい担当者
- TECS を初めて学ぶ開発者（図による構造理解の補助）

### 1.4 関連文書

| 文書 | 内容 |
|------|------|
| [[reference/03-Resources/my-topic/wiki/tecs--cdlref-index\|CDL リファレンスマニュアル]] | CDL 言語仕様 |
| [[reference/03-Resources/my-topic/wiki/tecs--tcdref\|TECS コンポーネント図（TCD）リファレンスマニュアル]] | 図の記法・要素定義 |
| [[tecsgen外部仕様]] | CDL コンパイラ（TECSCDE の後段ツール） |

---

