---
date: 2026-09-05
description: "TECSCDE-DT外部仕様書 第1章（概要）— 目的、ツールチェーン内の位置付け、想定実装（Electron/Tauri）、対象読者、関連文書。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE-DT外部仕様]] (2026-09-05). Chapter 1 of 11（[[TECSCDE外部仕様]]と同一の章構成）。

## 1. 概要

### 1.1 目的

本書は、[[TECSCDE外部仕様]]（TECS Component Diagram Editor、ブラウザ単体・フレームワーク非依存のJS版）を出発点に、**デスクトップアプリケーションとして実装する場合の外部仕様**を定める。CDL で手書きしていたセルタイプ定義・組み上げ記述を図的な操作に置き換え、CDL ファイルとの双方向変換を提供するという目的自体は[[TECSCDE外部仕様]]1.1節と同一であり、変わらない。

本書が新たに扱うのは、**ブラウザという実行環境の制約が外れることで可能になる機能**である。詳細は第2章以降で規定するが、要点は「ネイティブなファイルシステムアクセス」「tecsgenのサブプロセス実行」「OSクリップボード連携」の3点に集約される。

### 1.2 ツールチェーンにおける位置付け

```
.cdl ファイル
    ↕ TECSCDE-DT（読み込み・書き出し）
コンポーネント図（TCD）
    ↓ エクスポート
.cdl ファイル / 画像（SVG・PNG）
    ↓ tecsgen（本書では直接実行も可能、第8章）
生成コード
```

[[TECSCDE外部仕様]]1.2節と異なり、本書の実行環境はtecsgenを**サブプロセスとして直接呼び出せる**（第8章）。ただし、これはTECSCDEの位置付け自体を「設計環境」から「ビルドツール」へ変えるものではない——コード生成の実行は利用者が明示的にトリガーする操作であり、TECSCDEが自動的・暗黙的にコード生成を行うことはない。この境界の詳細は第8章8.4節で規定する。

### 1.3 想定する実装方法（言語非依存の要件）

本書は特定の言語・フレームワークに依存しない外部仕様として書く。想定する実装方法は次の2系統であり、**両方で同一の挙動になること**を本書の要件とする。

| 系統 | UI層 | バックエンド | プロセス起動・ファイルI/O |
|---|---|---|---|
| Electron | Chromium（HTML/SVG/DOM） | Node.js | `child_process`、`fs`モジュール |
| Tauri | OSネイティブWebView（Windows: WebView2／macOS: WKWebView／Linux: WebKitGTK） | Rust | `std::process::Command`、`fs`クレートまたは公式プラグイン |

本書の各章は、上表のいずれの組み合わせでも実現可能な挙動のみを規定する。**両方で実現できる機能は積極的に採用し**、逆に一方でしか実現できない機能（例: Tauriの各OS依存WebViewに固有の挙動）は規定に含めない。

### 1.4 対象読者

- TECSCDEをデスクトップアプリとして実装することを検討する開発者（Electron/TypeScript または Tauri/Rust）
- [[TECSCDE外部仕様]]（ブラウザ版）と比較し、デスクトップ化による差分を把握したい設計者

### 1.5 関連文書

| 文書 | 内容 |
|------|------|
| [[TECSCDE外部仕様]] | 本書の一次情報源（ブラウザ単体版）。行動仕様の大半を共有し、本書は差分のみを詳述する |
| [[reference/03-Resources/my-topic/wiki/tecs--cdlref-index\|CDL リファレンスマニュアル]] | CDL 言語仕様 |
| [[reference/03-Resources/my-topic/wiki/tecs--tcdref\|TECS コンポーネント図（TCD）リファレンスマニュアル]] | 図の記法・要素定義 |
| [[tecsgen外部仕様]] | CDL コンパイラ（本書ではサブプロセスとして直接連携する、第8章） |

---
