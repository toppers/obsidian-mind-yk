---
date: 2026-06-08
description: "アクティブセルの定義。active指定子・タスク/ハンドラ内包・TCD二重線表記・CDL宣言（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - cdl
---
● tecs wiki のインデックスは確認済み（16記事一致）。アクティブセルに関連するコンテンツを検索します。

  Searched for 2 patterns (ctrl+o to expand)

● ASP3 の tTask（アクティブセルの代表例）の実装を確認します。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● tTask の詳細を確認します。

  Read 1 file (ctrl+o to expand)

● Update(~\wiki\topics\tecs\log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-08] query | "アクティブセルとは何か" → answered from 4 articles (standard)
      4  ## [2026-06-08] query | "コンテキストとは何か" → answered from 4 articles (standard)
      5  ## [2026-06-08] query | "受け口配列とは何か" → answered from 3 articles (standard)
      6  ## [2026-06-08] query | "結合とは何か" → answered from 3 articles (standard)

● ---
  「アクティブセル」とは（tecs wiki より）

  **アクティブセル（Active Cell）**とは、受け口関数が呼ばれなくても自律的に動作するセルです。タスクや割り込みハンドラ等、実行を自ら開始
  できるコンポーネントがこれに該当します。

  CDL での宣言

  セルタイプに [active] 指定子を付けて宣言します：

  [active] celltype tMyTask {
      entry sTaskBody eTaskBody;   # タスク本体を提供する受け口
      call  sTask     cTask;       # タスク制御サービスへの呼び口
      ...
  };

  CDL 言語のセルタイプ指定子一覧における active の定義：

  ▎ タスク・ハンドラ等、受け口関数が呼ばれなくても動作する

  TCD（コンポーネント図）での表記

  アクティブセルは矩形の輪郭を二重線で描きます。通常のパッシブセルとの視覚的な区別です。

  ┌────────────────────┬───────────────────┐
  │      TCD 表記      │     CDL 記述      │
  ├────────────────────┼───────────────────┤
  │ セル（二重線矩形） │ [active] celltype │
  ├────────────────────┼───────────────────┤
  │ セル（単線矩形）   │ 通常のセルタイプ  │
  └────────────────────┴───────────────────┘

  具体例：ASP3+TECS の tTask

  ASP3+TECS ではタスクが典型的なアクティブセルです：

  cell tTask MyTask {
      attribute = C_EXP("TA_ACT");  // 生成直後に起動
      priority  = 10;
      stackSize = 512;
      cTaskBody = MyApp.eTaskBody;   // タスク本体を別セルに委譲
  };

  tTask は cTaskBody 呼び口でアプリケーションセルの eTaskBody 受け口を呼び出すことでタスク本体を実行します。タスクは RTOS
  によって自律的にスケジューリングされるため「アクティブ」です。

  初期化との関係

  active セルタイプを持つシステムでも、INITIALIZE_TECS() の呼び出しは必須です。呼ばないと未定義動作になります。

  tecsflow によるフロー解析

  V1.7.0 で追加された tecsflow コマンドはアクティブセルを起点とする関数呼出しフローを解析します：

  # (1) アクティブセルを起点とするフロー
  [active cell] ::AVR_CyclicAVR (path 46)
      ciBody.main => AVR_AVRBody.eiCyclicBody.main (gen/tmp_tAVRBody.c 482)

  これにより、システム全体のアクティブセルから始まる処理フローを可視化できます。

  ---
  Sources used:
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) — アクティブセルの定義（二重線矩形）、CDL active 指定子との対応
  - CDL 言語 (wiki/concepts/cdl-language.md) (confidence: high) — セルタイプ指定子 active の意味
  - 実装パターン (wiki/concepts/implementation-patterns.md) (confidence: high) — active セルタイプでも INITIALIZE_TECS()
  が必須であること
  - ASP3 カーネルオブジェクト (wiki/topics/asp3-kernel-objects.md) (confidence: high) — tTask を具体例として、アクティブセルの実際の
  CDL 記述
  - TECS 概要 (wiki/topics/tecs-overview.md) / tecsgen コマンド (wiki/references/tecsgen-commands.md) (confidence: high) — tecsflow
  がアクティブセル起点のフロー解析ツールであること

  Knowledge gaps:
  - アクティブセルタイプに対して tecsgen が生成するコードの具体的な違い（パッシブセルとの生成コード差分）は wiki に記載なし
  - [active] と [singleton] の組み合わせ可否については記載なし
