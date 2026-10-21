---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第1章（概要）— Electron固有化の位置づけ、想定するプロセスモデル、対象読者、関連文書。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 1 of 11（[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]と同一の11章構成）。

## 1. 概要

### 1.1 目的

本書は、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様|TECSCDE-DT外部仕様]]（TECSCDEのデスクトップアプリ版外部仕様、Electron/Tauri言語非依存）を実現するための内部設計のうち、**TypeScriptクラスベースで、かつElectronに固有化した設計**を提案するものである。

[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様|TECSCDE-TS内部仕様]]は同じクラスベース設計をブラウザ単体版（[[TECSCDE外部仕様]]）向けに提案していた。本書はそのクラス設計（`Cell`・`Command`・`History`等）を可能な限りそのまま踏襲しつつ、[[TECSCDE-DT外部仕様]]が新規に採用したデスクトップ機能（ネイティブファイルI/O・tecsgenのサブプロセス実行・OSクリップボード連携）をElectronのAPIで具体化する。

### 1.2 Electronに固有化するとはどういうことか

[[TECSCDE-DT外部仕様]]は「Electron・Tauriのどちらでも同一の挙動になること」を要件としていた（言語非依存）。本書はこの制約を外し、**Electronの実装詳細を直接使ってよいものとする**。

| 観点 | 比較元の仕様・設計 | 本書の立場 |
|---|---|---|
| ファイルI/O | [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 07 ファイルI-O設計|TECSCDE-TS内部仕様第7章]]が`FileIOStrategy`を定義し、ブラウザのFile System Access APIとダウンロードによる保存を切り替える | **Node.jsの`fs`・Electronの`dialog`モジュールを直接使う**（第7章） |
| プロセス実行 | Electron `child_process`・Tauri `Command`のどちらでも可、という前提のみ規定 | **Electronの`child_process.execFile`を直接使う**（第9章） |
| クリップボード | OSクリップボード連携を採用（実現手段は未指定） | **Electronの`clipboard`モジュールを直接使う**（第4章、[[TECSCDE-TS内部仕様]]の設計を継承） |

### 1.3 本書固有の中心的な設計課題: プロセス境界

Electronは、Node.js APIへの完全なアクセスを持つ**mainプロセス**と、Webページに相当し既定ではNode.js APIを持たない**rendererプロセス**の2つに分かれる。[[TECSCDE外部仕様]]・[[TECSCDE-DT外部仕様]]・[[TECSCDE-TS内部仕様]]のいずれも、この区別が存在しない前提（単一のブラウザページ、あるいは単一のプロセス）で書かれていた。

本書が新たに決定しなければならないのは、**9モジュール（A〜I）のうちどれがmainプロセスで動き、どれがrendererプロセスで動くか**、そして両者をつなぐ**IPC（プロセス間通信）の契約**である。この設計は第2章で行う。原則は次の2点である。

1. **UIとモデル・コマンド・描画（C・D・E・F・G）はrendererプロセスに置く。** これらは既存のクラス設計（[[TECSCDE-TS内部仕様]]）をそのまま使い、DOM/SVGへのアクセスを必要とするため、rendererプロセスから動かす理由がない。
2. **OSリソースに直接アクセスするモジュール（A・I、および一部のH）はmainプロセスに置く。** ファイルシステム・外部プロセス起動はNode.js APIを要し、セキュリティ上（`contextIsolation: true`）rendererプロセスから直接呼べない。rendererプロセスからは、`preload`スクリプトが`contextBridge`で公開する薄いゲートウェイクラス経由でのみアクセスする。

### 1.4 対象読者

- TECSCDEをElectron・TypeScriptクラスベースで実装することを検討する開発者
- [[TECSCDE-TS内部仕様]]（ブラウザ版のクラス設計）からの差分を把握したい設計者

### 1.5 関連文書

| 文書 | 内容 |
|------|------|
| [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様\|TECSCDE-DT外部仕様]] | 本書が実装する外部仕様（デスクトップ版） |
| [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様\|TECSCDE-TS内部仕様]] | 本書が踏襲するクラス設計の一次情報源（ブラウザ版） |
| [[TECSCDE内部仕様]] | さらに元となる関数/インタフェースベースの内部仕様 |

---
