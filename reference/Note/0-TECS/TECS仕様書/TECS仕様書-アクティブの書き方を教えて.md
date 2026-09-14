---
date: 2026-06-11T00:00:00.000Z
description: "TECSウィキ（tecs-0/仕様書ベース）クエリ回答 — アクティブセルの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● tecs-0 wiki の インデックスは既読です。celltype-implementation.md を読み、アクティブ関連をgrepします。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● rawソースで active の具体的な CDL 構文を確認します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● 十分な情報が集まりました。

  ---
  アクティブセルの書き方（tecs-0 wiki）

  概念定義

  tecs-0 wiki（TECS仕様書ベース）の定義：

  ▎ アクティブセル: タスク・ハンドラなど CPU 資源割付けを伴うセル、またはそれらを内包したセル

  ---
  1. CDL 構文

  セルタイプ指定子 active を celltype の前に付けます：

  [celltype_specifier_list] celltype celltype_name { ... };

  具体的には：

  [active] celltype tMyTask {
      call   sSomeSignature cSomePort;
      entry  sSomeSignature eSomePort;
      attr {
          uint32_t stackSize = 1024;
      };
      var {
          bool_t running;
      };
      factory {
          write( "tecsgen.cfg", "CRE_TSK(%s, { ... });", $id$ );
      };
  };

  複数指定子の例：

  [active, singleton] celltype tSystemTask {
      call sKernel cKernel;
  };

  ---
  2. 指定子の意味

  セルタイプ指定子一覧（tecs-0 wiki）：

  ┌───────────┬────────────────────────────────────────────────┐
  │  指定子   │                      意味                      │
  ├───────────┼────────────────────────────────────────────────┤
  │ active    │ アクティブセル（タスクセル or タスク内包セル） │
  ├───────────┼────────────────────────────────────────────────┤
  │ singleton │ セルがシステム中に1つだけ存在                  │
  ├───────────┼────────────────────────────────────────────────┤
  │ idx_is_id │ 実行時識別に整数値を使用（有効性検査あり）     │
  └───────────┴────────────────────────────────────────────────┘

  ---
  3. 複合セルタイプへの伝播

  内部セルが active を持つ複合セルタイプは、複合セルタイプ側にも active 指定が必要です：

  [active] composite tActiveComposite {
      /* 内部にアクティブセルを内包 */
      cell tActiveInner inner { };
  };

  ▎ セルタイプ指定子（active/singleton）は、内部セルで指定されていれば複合セルタイプでも指定必要。（仕様書第3章後半）

  ---
  4. セルタイプコードの構成

  アクティブセルも通常のセルタイプコードと同じファイル構成で実装します：

  ┌───────────────────┬──────────────────────────────────────┐
  │     ファイル      │                 内容                 │
  ├───────────────────┼──────────────────────────────────────┤
  │ tMyTask.c         │ セルタイプコード（タスク本体の実装） │
  ├───────────────────┼──────────────────────────────────────┤
  │ tMyTask_tecsgen.h │ tecsgen 自動生成ヘッダ               │
  ├───────────────────┼──────────────────────────────────────┤
  │ tMyTask_tecsgen.c │ tecsgen 自動生成コード               │
  └───────────────────┴──────────────────────────────────────┘

  属性・変数へのアクセスは通常マクロ（ATTR_xxx, VAR_xxx）を使います。

  ---
  Sources used:
  - wiki/concepts/cdl-language-spec.md (confidence: high) — active 指定子の定義・BNF構文
  - wiki/concepts/tecs-component-model.md (confidence: high) — アクティブセルの概念定義
  - raw/articles/2026-05-17-tecs-spec-chap2-component-model.md (confidence: high) —
  アクティブセルの詳細定義（CPU資源割付け）
  - raw/articles/2026-05-17-tecs-spec-chap3-cdl-part1.md (confidence: high) — CDL 構文 BNF
  - raw/articles/2026-05-17-tecs-spec-chap3-cdl-part2.md (confidence: high) — 複合セルへの active 伝播ルール
  - wiki/topics/celltype-implementation.md (confidence: medium) — セルタイプコードのファイル構成

  Knowledge gaps:
  - tecs-0 wiki には具体的な CDL コード例（[active] celltype ... { ... }; の完全なサンプル）が未収録
  - タスク本体の接続パターン（cTaskBody = MyApp.eTaskBody; 等）は未収録
  - → 実践例は /wiki:query --wiki tecs アクティブの書き方 で補完可能

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 4 articles + 2 raw (standard)
      4  ## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 2 articles + 1 raw (standard)
      5  ## [2026-06-08] query | "受け口配列の書き方を教えて (2)" → answered from 4 articles (standard; raw used)
      6  ## [2026-06-08] query | "受け口配列の書き方を教えて" → answered from 4 articles (standard; raw used)

● tecs-0 wiki でのアクティブセル回答を完了しました。

  tecs-0 の追加ポイント：複合セルタイプが active な内部セルを内包する場合、複合セルタイプ側にも [active]
  指定が必要という仕様書ルールが確認できました。これは tecs wiki では明示されていなかった情報です。
