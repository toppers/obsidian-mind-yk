---
date: 2026-06-07
description: "TECSウィキ（tecs）クエリ回答 — 受け口とは何か。冒頭にwiki logの更新出力を含む生ログ形式のまま整形されていない"
tags:
  - reference
  - tecs
  - wiki-query
---

● 受け口に関する情報はすでに読み込んだ記事に揃っています。ログを更新して回答します。

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-07] query | "受け口とは何か" → answered from 3 articles (standard)
      4  ## [2026-06-07] query | "セルタイプとは何か" → answered from 3 articles (standard)
      5  ## [2026-06-07] query | "セルとは何か" → answered from 3 articles (standard)
      6  ## [2026-06-07] query | "コンポーネントとは何か" → answered from 2 articles (standard)

● 受け口とは何か（tecs wiki 版）

  受け口（Entry Port / Receptacle） はセルが外部に提供する機能の口です。受け口を通して、他のセルが呼び口（Call
  Port）を結合し、そのセルの機能を呼び出せるようになります。

  CDL での受け口宣言

  entry sSignature  eEntryPort;     // 単一受け口
  entry sSignature  eArray[N];      // 受け口配列（N 個の口）

  慣習として受け口名の先頭は e（例: eTask, eKernel）。対応するシグニチャ名は先頭が s（例: sTask）。

  受け口指定子

  ┌───────────┬───────────────────────────────────────────────────────────┐
  │  指定子   │                           意味                            │
  ├───────────┼───────────────────────────────────────────────────────────┤
  │ allocator │ リレーアロケータを指定（send/receive 引数がある場合）     │
  ├───────────┼───────────────────────────────────────────────────────────┤
  │ inline    │ インライン関数として実装（nNS_tCelltype_inline.h に記述） │
  └───────────┴───────────────────────────────────────────────────────────┘

  受け口と呼び口の関係

  - 合流（多対一）可: 複数の呼び口が1つの受け口に結合できる
  - 分流（一対多）不可: 1つの呼び口が複数の受け口に結合することはできない
  - コールバック: 受け口側のセルが逆向きに呼び口を持ち、双方向に接続する補助的パターン

  C 言語実装での受け口関数

  受け口に対応する関数（セルタイプコード内に実装）の形式：

  // 非シングルトン・単一受け口
  ER eEntry_func(CELLIDX idx, int32_t inval, int32_t *outval)
  {
      CELLCB *p_cellcb;
      if (VALID_IDX(idx)) { p_cellcb = GET_CELLCB(idx); }
      else { return E_ID; }
      ...
  }

  // 受け口配列（添数 subscript が第2引数に追加）
  ER eEntry_func(CELLIDX idx, int_t subscript, int32_t inval, int32_t *outval)

  // シングルトン（idx 引数なし）
  ER eEntry_func(int32_t inval, int32_t *outval)

  - CELLIDX idx — セルを識別する第1引数（非シングルトン必須）
  - int_t subscript — 受け口配列の場合のみ、第2引数として追加
  - シングルトンセルでは idx 引数・CB 取得が不要

  受け口とシグニチャの関係

  受け口はシグニチャ（関数ヘッダの集合）に対応付けられ、構文的な型整合性を保証します。意味的整合性は各シグニチャの仕様が
  担います。シグニチャに [oneway] が指定された関数では、パラメータ方向は in または send のみ使用可能です。

  ---
  Sources used:
  - tecs-overview (wiki/topics/tecs-overview.md) (confidence: high) — 受け口の基本定義（機能を提供するポート）
  - cdl-language (wiki/concepts/cdl-language.md) (confidence: high) —
  受け口宣言構文・指定子（allocator/inline）・合流/分流ルール
  - implementation-model (wiki/concepts/implementation-model.md) (confidence: high) — 受け口関数の C
  言語形式（CELLIDX/subscript/シングルトン差異）

  Related in other wikis:
  - tecs-0: TECSコンポーネントモデル (../tecs-0/wiki/concepts/tecs-component-model.md) —
  受け口の仕様書原文定義（合流・コールバック・リージョン越え結合の制約）

  Knowledge gaps:
  - 受け口に対する VMT（Virtual Method Table）最適化の詳細は implementation-patterns
  (wiki/concepts/implementation-patterns.md) に記載
  - inline 受け口の実装ファイル（nNS_tCelltype_inline.h）の具体的な記述例は未収録

