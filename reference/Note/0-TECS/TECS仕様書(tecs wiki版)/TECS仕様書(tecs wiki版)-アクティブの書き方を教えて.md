---
date: 2026-06-11T00:00:00.000Z
description: "TECSウィキ（tecs ReadTheDocs版）クエリ回答 — アクティブセルの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● tecs wiki のインデックスを確認します。

  Read 1 file (ctrl+o to expand)

● 「アクティブ」に関連する記事を特定しました。cdl-language.md、implementation-model.md、asp3-kernel-objects.md
  を並行して読みます。

  Read 2 files (ctrl+o to expand)

● active の具体的な例を asp3-kernel-objects.md と implementation-patterns.md で確認します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● TCD記法の詳細を確認します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● rawソースもアクティブセルを検索します。

  Searched for 1 pattern (ctrl+o to expand)

● 十分な情報が集まりました。回答を合成します。

  ---
  アクティブセルの書き方（TECS CDL）

  概要

  アクティブセルとは、受け口関数が外から呼ばれなくても動作するセル（タスク・ハンドラ等）です。CDL では active
  指定子をセルタイプに付けます。TCD では二重線の矩形で描きます。

  ---
  1. セルタイプの定義

  [active] 指定子を celltype の前に付けます：

  [active]
  celltype tMyTask {
      /* 外から呼ばれる受け口（オプション） */
      entry sTask eTask;
      /* 他のセルの機能を呼ぶ呼び口 */
      call sSomeService cService;
      /* タスクのスタックサイズ等の属性 */
      attr {
          uint32_t stackSize = 1024;
      };
  };

  ---
  2. ASP3+TECS でのタスク定義（実用例）

  ASP3 では tTask が既定義のアクティブセルタイプです。アプリケーションのタスク本体は eTaskBody
  受け口として別のセルタイプに実装し、cTaskBody 呼び口で接続します：

  /* アプリケーション側 — タスク本体を実装する */
  celltype tMyApp {
      entry sTaskBody eTaskBody;  /* タスク本体の受け口 */
      call sSemaphore cSemaphore; /* 使いたいカーネルオブジェクト */
  };
  cell tMyApp MyApp { };

  /* タスクの生成と結合 */
  cell tTask MyTask {
      attribute = C_EXP("TA_ACT"); /* 起動直後から実行 */
      stackSize = 1024;
      priority  = 10;
      cTaskBody = MyApp.eTaskBody; /* タスク本体を接続 */
  };

  タスク本体の C 実装：

  /* tMyApp.c */
  void eTaskBody_main(CELLIDX idx)
  {
      CELLCB *p_cellcb = GET_CELLCB(idx);
      /* タスクのメインループ */
      for (;;) {
          cSemaphore_wait();  /* 呼び口関数の呼び出し */
          /* 処理 */
      }
  }

  内部的には tTask_start(intptr_t exinf) が cTaskBody_main() を呼び出します。

  ---
  3. require との組み合わせ

  アクティブセルタイプで require を使う例：

  [active]
  celltype tRequire {
      require Kernel.eSc;              /* セル指定 */
      require tKernel.eSc;             /* セルタイプ指定（シングルトン限定） */
      require cReqCall = Kernel.eSc;   /* 呼び口名あり */
  };

  ---
  4. TCD 表記

  ┌────────────────┬────────────────────┬───────────────────┐
  │      要素      │        TCD         │        CDL        │
  ├────────────────┼────────────────────┼───────────────────┤
  │ アクティブセル │ 矩形の輪郭が二重線 │ [active] celltype │
  ├────────────────┼────────────────────┼───────────────────┤
  │ 通常セル       │ 矩形の輪郭が細線   │ celltype          │
  └────────────────┴────────────────────┴───────────────────┘

  ---
  5. 注意事項

  - INITIALIZE_TECS() はアクティブセルを持つシステムでも必ず呼ぶこと（未呼出は未定義動作）
  - ファクトリで CRE_TSK 等の静的 API を tecsgen.cfg に出力する（ASP3 の tTask はファクトリ内蔵）
  - tecsflow コマンドでアクティブセルを起点とする呼び出しフローを解析できる（V1.7.0 追加）

  ---
  Sources used:
  - wiki/concepts/cdl-language.md (confidence: high) — active 指定子の定義と一覧
  - wiki/topics/tcd-notation.md (confidence: high) — アクティブセルの TCD 表記（二重線）
  - wiki/topics/asp3-kernel-objects.md (confidence: high) — tTask の CDL 使用例・cTaskBody/eTaskBody パターン
  - raw/articles/2026-05-19-asp3-task.md (confidence: high) — tTask の完全な CDL + C 実装例
  - raw/articles/2026-05-19-cdl-celltype-detail.md (confidence: high) — require との組み合わせ
  - wiki/concepts/implementation-patterns.md (confidence: medium) — INITIALIZE_TECS() の必須性

  Knowledge gaps:
  - 独自アクティブセルタイプにファクトリを書く詳細例（tTask 以外で CRE_TSK 相当を自作する場合）
  - ATK2 のアクティブセル（tTask 相当）の構造

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 5 articles + 2 raw (standard)
      4  ## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 4 articles (standard)
      5  ## [2026-06-11] query | "呼び口配列の書き方を教えて" → answered from 4 articles (standard)
      6  ## [2026-06-11] query | "合流の書き方を教えて" → answered from 2 articles (standard)

● アクティブセルの書き方を回答しました。

  要点：[active] celltype tMyTask { ... }; で定義し、TCD では二重線の矩形で描きます。ASP3 では tTask
  が既定義で、タスク本体は cTaskBody = MyApp.eTaskBody; の接続パターンで分離します。

✻ Cogitated for 1m 29s
