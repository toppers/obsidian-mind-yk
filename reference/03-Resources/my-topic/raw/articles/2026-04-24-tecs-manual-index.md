---
date: 2026-04-24
source-type: article
source-url: e:\Crepo\github-toppers\tecs-docs\docs\_build\html\index.html
title: TECS マニュアル
compiled: true
tags: [tecs, toppers, rtos, documentation]
description: "TOPPERS プロジェクトの組込みコンポーネントシステム TECS 公式マニュアルの目次。CDL仕様・実装モデル・ASP3/ATK2連携・プラグイン等を網羅。"
---

# TECS マニュアル

© Copyright 2016-2018, TOPPERS Project.
Sphinx で構築、Read the Docs テーマ使用。

## 目次

### TECS コア仕様

- TECS マニュアルのライセンス
  - TECS WG --- TECS の開発母体
- 組込みコンポーネントシステム TECS 仕様
- TECS V1.4.0 ～ V1.7.0 の新機能
  - TECS V1.7.0 の新機能
  - TECS V1.6.1 の新機能
  - TECS V1.5.0 の新機能
  - TECS V1.4.0 の新機能

### TECS コンポーネント図 (TCD)

- TECS コンポーネント図
  - 概要
  - TECS コンポーネント図の書き方

### TECS コンポーネント記述言語 (CDL)

- TECS コンポーネント記述言語 (TECS CDL)
  - 概要
  - 対応バージョン
  - 共通事項
  - TECS CDL の記述内容
  - 未記載事項
  - 字句
  - 型
  - 式
  - 名前有効範囲
  - 名前付けの慣習
  - 前置部
  - シグニチャ記述
  - セルタイプ記述
  - 複合セルタイプ記述
  - 組上げ記述 (セル記述)
  - ネームスペース
  - リージョン

### TECS コンポーネント実装モデル

- TECS コンポーネント実装モデル
  - ユーザー実装モデルとシステム実装モデル
  - セルタイプコード
  - 初期化コード
  - ファクトリ
  - FOREACH_CELL マクロ
  - セルタイプコードでのアロケータ
  - マクロ
  - ファイルの一覧

### RTOS 連携

- ASP3+TECS
  - ASP3+TECSについて
  - タスク (tTask)
  - イベントフラグ (tEventflag)
  - データキュー (tDataqueue)
  - タイムイベント通知
  - セマフォ (tSemaphore)
  - 優先度データキュー (tPriorityDataqueue)
  - 固定長メモリプール (tFixedSizeMemoryPool)
  - 初期化ルーチン (tInitializeRoutine)
  - 終了処理ルーチン (tTerminateRoutine)
  - 割込みサブルーチン (tISR)
- ATK2+TECS
  - ATK2+TECS について
  - カーネル (tKernel)
  - タスク (tTask)
  - 割込み管理 (tISR)
  - カウンタ (tCounter)
  - アラーム (tAlarm)
  - リソース (tResource)

### mruby 連携

- mruby on ev3rt+tecs
  - mruby on ev3rt+tecs について
  - バッテリ (Battery)
  - ボタン (Battery)
  - LEDライト (LED)
  - スピーカ (Speaker)
  - LCD (LCD)
  - モータ (Motor)
  - RTOS機能 (RTOS)
  - カラーセンサ (Color)
  - ジャイロセンサ (Gyro)
  - 超音波センサ (Ultrasonic)
  - タッチセンサ (Touch)
  - 共有変数 (SharedMemory)
  - バランサ (Balancer)
- mruby on GR-PEACH+TECS
  - ビルド方法
  - アプリケーションの開発方法
  - RTOS機能 (RTOS)
  - LED (LED)

### ネットワーク・メモリ

- TINET+TECS
- TLSF+TECS

### ツールリファレンス

- プラグインリファレンスマニュアル
  - 各種カーネル対応プラグイン
  - mruby ブリッジプラグイン
  - トレースプラグイン
  - RPC プラグイン
  - C 言語インタフェースプラグイン
- コマンドリファレンスマニュアル
- 参考リンク

---

Source: [[index]]
