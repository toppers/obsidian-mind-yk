---
date: 2026-06-11T00:00:00.000Z
description: "TECSウィキ（tecs-0/仕様書ベース）クエリ回答 — コールバックの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● まず tecs-0 ウィキの場所を特定します。

  Read 3 files (ctrl+o to expand)

● インデックス確認：5記事、5行（一致）。コールバック関連として cdl-language-spec.md と tecs-component-model.md
  を読みます。

  Searched for 1 pattern, read 2 files (ctrl+o to expand)

● コールバックへの直接言及が少ないため、rawソースを検索します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● rawソースにコールバック例があります。全文を読みます。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● rawソースのCDL後半（結合部分）もコールバック記述を確認します。

  Searched for 2 patterns (ctrl+o to expand)

● tecs-0 wiki内の情報で回答を合成します。

  ---
  コールバックの書き方（tecs-0 wiki）

  概念定義

  tecs-0 wiki の定義：

  ▎ コールバック: 2つのセルが相互に呼び口・受け口を持ち接続し合う補助的な結合。

  通常の結合（A の呼び口 → B の受け口）とは別に、B 側も A の受け口を呼べるよう双方向に接続する構造です。

  ---
  1. [callback] シグニチャの定義

  コールバック用シグニチャには [callback] 指定子を付けます。

  [callback] signature siEventHandler {
      void  onDataReady( [in] uint32_t dataSize );
      void  onError( [in] int32_t errorCode );
  };

  命名規則として非タスクコンテキスト（割り込み・コールバック）には si プレフィックスを使います：

  ┌──────────────────────────────────────────────────┬──────────┬───────────────────────┐
  │                   コンテキスト                   │ 接頭文字 │          例           │
  ├──────────────────────────────────────────────────┼──────────┼───────────────────────┤
  │ タスクコンテキスト                               │ s        │ sMotor, sTask         │
  ├──────────────────────────────────────────────────┼──────────┼───────────────────────┤
  │ 非タスクコンテキスト（割り込み・コールバック等） │ si       │ siEventHandler, siISR │
  ├──────────────────────────────────────────────────┼──────────┼───────────────────────┤
  │ カーネル外                                       │ sn       │ snInit                │
  └──────────────────────────────────────────────────┴──────────┴───────────────────────┘

  ---
  2. セルタイプへの組み込み

  コールバックを通知する側（ドライバ等）：
  celltype tDriver {
      call siEventHandler cHandler;  /* コールバック先の受け口を呼ぶ */
  };

  コールバックを受け取る側（アプリ等）：
  celltype tApp {
      entry siEventHandler eHandler;  /* コールバックが届く受け口 */
  };

  ---
  3. アセンブリ（結合記述）

  2つのセルが相互に接続し合う構造になります：

  cell tDriver Driver { };
  cell tApp App {
      /* ここでは通常結合の逆方向 — App の受け口を Driver の呼び口に接続 */
  };

  ▎ 注意: tecs-0 wiki には逆結合の <= 構文の具体的な記述はありません。CDL 結合の標準構文は cCallPort =
  ▎ TargetCell.eEntryPort; ですが、コールバックの場合は双方向に結合を書く形になります。

  ---
  Sources used:
  - wiki/concepts/tecs-component-model.md (confidence: high) — コールバックの概念定義（相互呼び口・受け口結合）
  - raw/articles/2026-06-08-cdl-signature-examples.md (confidence: high) — [callback] シグニチャ構文例・si 命名規則
  - wiki/concepts/cdl-language-spec.md (confidence: medium) — si 命名規則（非タスクコンテキスト）

  Knowledge gaps:
  - tecs-0 wiki には <= 逆結合演算子の構文詳細が未コンパイル（raw章2にも記述なし）
  - [prototype] 指定子との関係（逆結合の有効条件）が未収録
  - コールバック付きアセンブリの完全な CDL スニペット例がない
  - → より詳細な逆結合構文は /wiki:query --wiki tecs コールバックの書き方 で補完可能

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  File must be read first

  Read 1 file (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 2 articles + 1 raw (standard)
      4  ## [2026-06-08] query | "受け口配列の書き方を教えて (2)" → answered from 4 articles (standard; raw used)
      5  ## [2026-06-08] query | "受け口配列の書き方を教えて" → answered from 4 articles (standard; raw used)
      6  ## [2026-06-08] query | "呼び口配列の書き方を教えて" → answered from 2 articles (standard)

● tecs-0 wiki でのコールバック回答を完了しました。

  tecs と tecs-0 の違いのまとめ：
  - tecs-0（仕様書ベース）: [callback] シグニチャ構文と「相互結合」という概念定義まで
  - tecs（実践知識ベース）: <= 逆結合演算子・[prototype] 条件・アセンブリ完全例まで網羅

  tecs-0 wiki に逆結合構文の記事を追加するには /wiki:ingest --wiki tecs-0 でCDL結合詳細ソースを取り込む必要があります。

✻ Cooked for 1m 16s

※ recap: TECSウィキへのクエリ対応中。tecs と tecs-0
  両ウィキでコールバックの書き方の回答を完了しログ記録済み。次のアクションはありません。
