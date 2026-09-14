---
date: 2026-06-07
description: "TECSウィキ（tecs）クエリ回答 — 呼び口（Call Port）とは何か。セルが他セルの機能を要求する口で、受け口に結合して関数を呼び出す。CDLでの呼び口宣言"
tags:
  - reference
  - tecs
  - wiki-query
---

  呼び口とは何か（tecs wiki 版）

  呼び口（Call Port） はセルが他のセルの機能を要求するための口です。受け口（Entry
  Port）に結合することで、その受け口が提供する関数を呼び出せるようになります。

  CDL での呼び口宣言

  call sSignature  cCallPort;     // 単一呼び口
  call sSignature  cArray[];      // 呼び口配列（サイズ省略可）

  慣習として呼び口名の先頭は c（例: cTask, cKernel）。

  呼び口指定子

  ┌──────────┬──────────────────────────────────────────┐
  │  指定子  │                   意味                   │
  ├──────────┼──────────────────────────────────────────┤
  │ optional │ 未結合でも良い（通常は結合必須）         │
  ├──────────┼──────────────────────────────────────────┤
  │ omit     │ 出力コードから除外（スタブ・テスト用途） │
  └──────────┴──────────────────────────────────────────┘

  制約

  - 結合必須（optional なしの場合）
  - 分流不可（1つの呼び口が複数受け口に結合不可）
  - 合流は受け口側で受け入れ可

  C 言語での呼び口関数

  // 単一呼び口
  ER cCall_func1(int32_t inval, int32_t *outval);

  // 呼び口配列（第1引数に subscript）
  ER cCall_func1(int_t subscript, int32_t inval, int32_t *outval);

  - NCP_cCall — 呼び口配列のサイズ取得マクロ
  - TEST_OPTIONAL_CP_cCall() — optional 呼び口の結合確認マクロ

  through による結合変換

  cell tMyType MyCell {
      cCall = [through(RPCPlugin, "...")] RemoteCell.eEntry;
  };

  ---
  Sources used:
  - tecs-overview (wiki/topics/tecs-overview.md) (confidence: high) — 呼び口の基本定義（機能を要求するポート）
  - cdl-language (wiki/concepts/cdl-language.md) (confidence: high) — 呼び口宣言構文・optional/omit 指定子・through
  指定子
  - implementation-model (wiki/concepts/implementation-model.md) (confidence: high) — 呼び口関数の C
  言語形式・NCP_cCall・TEST_OPTIONAL_CP

  Related in other wikis:
  - tecs-0: TECSコンポーネントモデル (../tecs-0/wiki/concepts/tecs-component-model.md) —
  仕様書原文ベースの定義（分流不可・コールバック・RPC 分類）

  Knowledge gaps:
  - 動的結合（Descriptor 型）を使う呼び口の詳細は advanced-cdl-features (wiki/concepts/advanced-cdl-features.md) に記載
  - 呼び口最適化の詳細は implementation-patterns (wiki/concepts/implementation-patterns.md) に記載
