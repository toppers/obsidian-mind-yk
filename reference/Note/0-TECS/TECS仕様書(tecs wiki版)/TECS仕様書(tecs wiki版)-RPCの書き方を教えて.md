---
date: 2026-06-12T00:00:00.000Z
description: "TECSウィキ（tecs ReadTheDocs版）クエリ回答 — RPCの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● TECSウィキの設定を確認し、インデックスを読みます。

  Searched for 1 pattern, read 2 files (ctrl+o to expand)

● RPCに関連する記事を検索します。

  Searched for 4 patterns, read 4 files (ctrl+o to expand)

● ログを更新して回答を生成します。

● Bash(echo "## [2026-06-12] query | \"RPCの書き方を教えて\" → answered from 4 articles (standard)" >> "C:/Users/ykomi/wiki/topics/tecs/log.md" 2>&1)
  ⎿  cygpath: can't convert empty path
     cygpath: can't convert empty path
  ⎿  Allowed by auto mode classifier

  Read 1 file (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 2 lines
      1  # Wiki Activity Log
      2
      3 +## [2026-06-12] query | "RPCの書き方を教えて" → partial answer — RPC plugins undocumented, framework + CDL through 構文のみ (standard)
      4 +
      5  ## [2026-06-11] query | "RPCの書き方を教えて" → partial answer — RPC plugins all undocumented, framework only (standard)
      6  ## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles + 1 raw (standard)
      7  ## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 5 articles + 2 raw (standard)

● ---
  TECS における RPC の書き方

  ウィキの正直な評価: RPC プラグイン 4
  種はすべて「ドキュメント未記載」状態です。ウィキが持つ情報は「どんな仕組みがある」という分類レベルに留まり、具体的な CDL
  記述の完全な例はありません。以下はウィキが提供できる範囲です。

  ---
  1. RPC とは（概念）

  TECS の RPC は 異なるアドレス空間・プロセッサ間でセル間呼び出しを行う仕組みです。TCD（コンポーネント図）では通常の接続線が一重線なのに対して、RPC
  接続は二重線で表記します。CDL 上では実際には RPC プラグインが「チャネルコンポーネント」を自動生成して間に挿入されます。

  ---
  2. 4 種の RPC プラグイン

  ┌───────────────────────┬──────────────────────────────────────────────┐
  │      プラグイン       │                     説明                     │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ TransparentRPCPlugin  │ 透過的 RPC。呼び出し元・先のコードに変更不要 │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ OpaqueRPCPlugin       │ 不透過 RPC                                   │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ SharedRPCPlugin       │ 共有メモリ経由 RPC                           │
  ├───────────────────────┼──────────────────────────────────────────────┤
  │ SharedOpaqueRPCPlugin │ 共有メモリ経由・不透過 RPC                   │
  └───────────────────────┴──────────────────────────────────────────────┘

  ---
  3. CDL での基本的な使い方（ウィキの例）

  プラグインは [generate] 指定子でセルの呼び口に適用します:

  cell tMyType MyCell {
      [generate(TransparentRPCPlugin, "...")]
      cCall = RemoteCell.eEntry;
  };

  ---
  4. region + through ポートによる RPC（ウィキに記述あり）

  リージョン境界を越える通信では in_through / out_through で RPC プラグインを指定できます:

  region rSecure {
      [in_through( "RPCPlugin" )]
      entry sSecure eSecure;  // 外部からこのリージョンへの入り口
  };

  ┌──────────────┬─────────────────────────────────┐
  │ through 種別 │              方向               │
  ├──────────────┼─────────────────────────────────┤
  │ in_through   │ 外 → リージョン内               │
  ├──────────────┼─────────────────────────────────┤
  │ out_through  │ リージョン内 → 外               │
  ├──────────────┼─────────────────────────────────┤
  │ to_through   │ 任意 → 特定セル直接ルーティング │
  └──────────────┴─────────────────────────────────┘

  through 文字列内では置換変数 $source$ / $destination$ / $start_region$ / $end_region$ が使用できます。

  ---
  5. TCD での表記

  - 通常接続 → 一重線
  - RPC 接続 → 二重線（RPC チャネルコンポーネントに置き換えられることを示す）
  - RPC には SysLog が必要

  ---
  Sources used:
  - tecsgen プラグインリファレンス (wiki/references/plugins.md) (confidence: high) — RPCプラグイン4種の一覧・[generate] 構文例
  - CDL 高度機能 (wiki/concepts/advanced-cdl-features.md) (confidence: high) — in_through/out_through 構文
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) — TCD での RPC 二重線表記
  - raw: TECS プラグインリファレンス (raw/articles/2026-05-06-tecs-plugin-reference.md) (confidence: medium) — 元ソースの補足

  Knowledge gaps:
  - RPC プラグイン 4 種はすべてドキュメント未記載。TransparentRPC / OpaqueRPC / SharedRPC それぞれの具体的な CDL
  記述例・プラグイン引数・動作の違いはウィキにありません。
  - 推奨: TECS ソースコード中の RPC 使用例（E:\Crepo\ykominami-svn-2\tecsgen\trunk）や TOPPERS 公式ドキュメントを /wiki:ingest
  してコンパイルすると情報が補完されます。
