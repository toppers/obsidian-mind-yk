---
date: 2026-06-07
description: "TECSウィキ（tecs-0・仕様書原文ベース）クエリ回答 — 呼び口とは何か。冒頭にwiki logの更新出力を含む生ログ形式のまま整形されていない"
tags:
  - reference
  - tecs
  - wiki-query
---

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-07] query | "呼び口とは何か" → answered from 2 articles (standard, same as TECS仕様書-呼び口
        +とは何か)
      4  ## [2026-06-07] query | "TECS仕様書-シグニチャとは何か" → answered from 2 articles (standard)
      5  ## [2026-06-07] query | "TECS仕様書-受け口とは何か" → answered from 2 articles (standard)
      6  ## [2026-06-07] query | "TECS仕様書-呼び口とは何か" → answered from 2 articles (standard)

● 呼び口とは何か（tecs-0 wiki 版 — 仕様書原文ベース）

  呼び口（call port） はセルが他のセルの機能を要求するための口です。シグニチャに対応付けられ、必ず受け口（entry
  port）と結合されます。

  CDL での呼び口宣言

  call sSignature cPortName;    // 単一呼び口
  call sSignature cArray[];     // 呼び口配列（サイズ省略可）

  慣習として呼び口名の先頭は c（例: cTask, cKernel）。

  呼び口の特性

  ┌──────────┬─────────────────────────────────────────────────────┐
  │   特性   │                        内容                         │
  ├──────────┼─────────────────────────────────────────────────────┤
  │ 機能要求 │ 他のセルへ関数呼出しを行う。呼び元の役割            │
  ├──────────┼─────────────────────────────────────────────────────┤
  │ 結合必須 │ 必ず受け口と結合しなければならない                  │
  ├──────────┼─────────────────────────────────────────────────────┤
  │ 分流不可 │ 1つの呼び口が複数の受け口に結合することはできない   │
  ├──────────┼─────────────────────────────────────────────────────┤
  │ 配列形式 │ cArray[] 形式で複数セルへの呼び口を配列で表現できる │
  └──────────┴─────────────────────────────────────────────────────┘

  組上げ記述（結合）

  cell tCellType CellName {
      cCallPort = TargetCell.eEntryPort;   // 呼び口 → 受け口の結合
      attr = 42;
  };

  [through(plugin, arg)] 指定子でスルーセル（RPC チャネル等）を挿入：

  cCallPort = [through(RPCPlugin, "arg")] RemoteCell.eEntryPort;

  コールバックパターン

  呼び口を持つセルが逆向きに受け口も持ち、2つのセルが相互に接続する補助的な結合です。

  RPC による分散

  呼び口・受け口の結合を RPC チャネルに置き換えることで分散処理が実現します：

  ┌────────────────────────────────────┬────────────────────────────────────────┐
  │              接続分類              │                  説明                  │
  ├────────────────────────────────────┼────────────────────────────────────────┤
  │ トランスペアレント（直接）         │ 通常の関数呼出し。同一アドレス空間     │
  ├────────────────────────────────────┼────────────────────────────────────────┤
  │ トランスペアレント（アウトタスク） │ 同一 CPU・異なるタスク。メモリ共有あり │
  ├────────────────────────────────────┼────────────────────────────────────────┤
  │ オペイク（クローズドネットワーク） │ 静的接続。引数をコピー渡し             │
  ├────────────────────────────────────┼────────────────────────────────────────┤
  │ オペイク（オープンネットワーク）   │ 動的接続。認証・存在保証なし           │
  └────────────────────────────────────┴────────────────────────────────────────┘

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) —
  呼び口の定義・結合必須・分流不可・through 指定子・コールバック・RPC 分類
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — call キーワード・BNF

  Related in other wikis:
  - tecs: cdl-language (../tecs/wiki/concepts/cdl-language.md) — optional/omit 指定子・NCP_cCall マクロ
  - tecs: implementation-model (../tecs/wiki/concepts/implementation-model.md) — 呼び口関数の C
  言語形式・TEST_OPTIONAL_CP マクロ

  Knowledge gaps:
  - optional/omit 呼び口指定子は tecs-0 wiki に未収録（TECS 仕様書原文には非記載または未コンパイル）
  - 呼び口の最適化（単一セル最適化・VMT 削除）は tecs-0 wiki の セルタイプ実装モデル
  (wiki/topics/celltype-implementation.md) に部分記載
