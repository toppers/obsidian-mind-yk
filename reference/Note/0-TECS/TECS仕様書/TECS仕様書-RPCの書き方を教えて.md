---
date: 2026-06-12T00:00:00.000Z
description: "TECSウィキ（tecs-0/仕様書ベース）クエリ回答 — RPCの書き方。接続4分類・TransparentRPC・OpaqueRPC CDL設定"
tags:
  - reference
  - tecs
  - wiki-query
---

● tecs-0 ウィキのインデックスを確認します。

  Searched for 5 patterns, read 1 file (ctrl+o to expand)

● 豊富な情報があります。CDL言語仕様とRaw記事も確認します。

  Searched for 5 patterns, read 1 file (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  File must be read first

  Read 1 file (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 2 lines
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-12] query | "RPCの書き方を教えて" → answered from 3 wiki articles + 2 raw (standard)
      4 +
      5  ## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles (2 wiki + 1 raw) (standard)
      6  ## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 4 articles + 2 raw (standard)
      7  ## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 2 articles + 1 raw (standard)

● ---
  TECS における RPC の書き方（tecs-0 ウィキ — 仕様書ベース）

  1. RPC とは

  TECS の RPC は 結合を「RPC チャネルコンポーネント」に置き換えることで、呼び元と呼び先を異なる CPU
  に配置する仕組みです。設計方針として「コンポーネント間通信は関数呼出しが基本、RPC により分散環境にも対応」と明記されています。

  ---
  2. 接続の 4 分類

  ┌───────────────────────────────────────┬──────────────────────────────────────────────────┐
  │                 分類                  │                       特徴                       │
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ トランスペアレント - 直接接続         │ 通常の関数呼び出し。同一アドレス空間             │
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ トランスペアレント - アウトタスク接続 │ 同一 CPU・異なるタスク。メモリ空間は共有あり     │
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ オペイク - クローズドネットワーク     │ 静的接続。ポインタ参照不可のためコピー渡しが必要 │
  ├───────────────────────────────────────┼──────────────────────────────────────────────────┤
  │ オペイク - オープンネットワーク       │ 動的接続。認証手続きが必要                       │
  └───────────────────────────────────────┴──────────────────────────────────────────────────┘

  ---
  3. RPC チャネルモデル

  RPC チャネル = マーシャラ + アンマーシャラ + チャネルコンポーネント

  - チャネルコンポーネントはシグニチャ次第で置換可能
  - tecsgen が CDL の through 指定子や region の in_through/out_through に基づいて自動生成する

  ---
  4. CDL での記述方法

  4-a. through 指定子（呼び口の結合時に直接指定）

  cell tMyCell myCell {
      [through( RPCPlugin, "arg" )] cCall = RemoteCell.eEntry;
  };

  BNF:
  '[' 'through' '(' plugin_name ',' plugin_arg ')' ']' join

  4-b. region + in_through / out_through（リージョン境界での RPC）

  [in_through(RPCPlugin, "arg"), out_through()] region rTrusted {
      cell tSecureCell sc { ... };
  };

  ┌──────────────────────────────────────┬────────────────┬──────────────────────────────────────────────────────┐
  │                指定子                │      方向      │                         意味                         │
  ├──────────────────────────────────────┼────────────────┼──────────────────────────────────────────────────────┤
  │ in_through(plugin, arg)              │ 外部 → 内部    │ 外からこのリージョンへの結合を許可（スルーセル生成） │
  ├──────────────────────────────────────┼────────────────┼──────────────────────────────────────────────────────┤
  │ out_through(plugin, arg)             │ 内部 → 外部    │ このリージョンから外への結合を許可                   │
  ├──────────────────────────────────────┼────────────────┼──────────────────────────────────────────────────────┤
  │ to_through(region_name, plugin, arg) │ 兄弟リージョン │ 特定の兄弟リージョンへの結合を許可                   │
  └──────────────────────────────────────┴────────────────┴──────────────────────────────────────────────────────┘

  デフォルトでリージョン間の結合は禁止。in_through/out_through で明示した方向のみ許可されます。

  ---
  5. TCD（コンポーネント図）での表記

  RPC 接続は通常の接続線（一重線）に対して 二重線 で描きます。これが「RPC チャネルコンポーネントへの置き換え」を示します。SysLog が必要です。

  ---
  6. まとめ：使い分け

  ┌─────────────────────────────────────────────────────────┬──────────────────────────────────────────┐
  │                      やりたいこと                       │                   方法                   │
  ├─────────────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ 個々の結合を RPC にしたい                               │ [through(RPCPlugin, "arg")] を結合に付与 │
  ├─────────────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ リージョン内のセルへのアクセスをすべて RPC 経由にしたい │ region に in_through/out_through を指定  │
  └─────────────────────────────────────────────────────────┴──────────────────────────────────────────┘

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) — RPC 4分類・region + in_through 構文
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — through BNF 構文・region 指定子の BNF
  - raw: TECS仕様書 第2章 (raw/articles/2026-05-17-tecs-spec-chap2-component-model.md) (confidence: high) — RPC
  チャネルモデル（マーシャラ＋アンマーシャラ）の定義
  - raw: TECS仕様書 第3章後半 (raw/articles/2026-05-17-tecs-spec-chap3-cdl-part2.md) (confidence: high) — through/region 構文の補足

  Knowledge gaps:
  - 具体的な plugin_name に何を渡すか（TransparentRPCPlugin 等の引数の詳細）は tecs-0 ウィキに記述なし → tecs ウィキの plugins.md に一覧あり
  - through 指定子の詳細（writeme.txt に「未記述課題」として明記）
  - 動的結合を伴う RPC の記述方法も「未記述」とされている

✻ Brewed for 1m 20s

※ recap:
  TECSウィキでRPCの書き方を調査中。tecs-0ウィキの仕様書ベース情報（4分類・through構文・region指定子）を回答済み。次はRPCプラグインの具体的な引数詳細を
  tecs ウィキから補完するか、別の質問に進む。 (disable recaps in /config)
