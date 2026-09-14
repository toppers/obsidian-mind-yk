---
date: 2026-06-11T00:00:00.000Z
description: "TECSウィキ（tecs ReadTheDocs版）クエリ回答 — コールバックの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● 前回のセッションで収集済みの情報を基に回答を合成します。

  Read 1 file (ctrl+o to expand)

● ログを確認しました。コールバッククエリはまだ記録されていないので、今から回答を合成してログに追記します。

  ---
  コールバックの書き方（TECS CDL）

  概要

  TECSでは「コールバック」を、[callback] シグニチャ指定子を使った逆結合（Reverse
  Binding）パターンで表現します。通常の結合（呼び口→受け口）とは逆に、受け口から呼び口への結合が可能になります。

  ---
  1. シグニチャの定義

  コールバック用シグニチャには [callback] 指定子を付けます。命名慣習として si プレフィックスを使います。

  [callback] signature siEventHandler {
      void onDataReady( [in] uint32_t dataSize );
      void onError( [in] int32_t errorCode );
  };

  [callback] を付けることで、このシグニチャを介した受け口→呼び口の逆結合が許可されます。

  ---
  2. セルタイプの定義

  コールバックを受け取る側（イベントを通知するドライバ等）：
  celltype tDriver {
      /* コールバック先への呼び口（通知する相手の受け口を呼ぶ） */
      call siEventHandler cHandler;
  };

  コールバックを実装する側（上位アプリ等）：
  celltype tMain {
      /* 自分の受け口にコールバックが届く */
      entry siEventHandler eHandler;
  };

  ---
  3. アセンブリ記述（逆結合）

  逆結合は <= 演算子で記述します。左辺が受け口、右辺が呼び口です。

  cell tDriver Driver { };
  cell tMain Main { };

  [prototype]
  region rApp {
      cell tMain Main {
          /* 逆結合: Main.eHandler <= Driver.cHandler */
          eHandler <= Driver.cHandler;
      };
  };

  逆結合の条件（いずれか一方が必要）：
  4. シグニチャに [callback] 指定子がある
  5. セルタイプに [prototype] 指定子がある

  ---
  6. TCD表記（コンポーネント図）

  TCDでは矢印の向きが逆になります：

  [Main] →eHandler ... cHandler← [Driver]

  - 通常結合: 呼び口 → 受け口（左→右）
  - コールバック（逆結合）: 受け口 → 呼び口（矢印は受け口側から呼び口側へ）

  ---
  5. 実装側（C言語）

  コールバック受け口のC関数は通常の受け口と同様：

  /* tMain の実装 */
  void eHandler_onDataReady( CELLIDX idx, uint32_t dataSize )
  {
      /* データ受信処理 */
  }

  void eHandler_onError( CELLIDX idx, int32_t errorCode )
  {
      /* エラー処理 */
  }

  ドライバ側からの呼び出し（呼び口経由）：

  /* tDriver の実装 — コールバックを起動する */
  cHandler_onDataReady( receivedSize );

  ---
  まとめ

  ┌──────────────────────┬─────────────────────────────────────────────────┐
  │         要素         │                      記述                       │
  ├──────────────────────┼─────────────────────────────────────────────────┤
  │ シグニチャ           │ [callback] signature siXxx { ... };             │
  ├──────────────────────┼─────────────────────────────────────────────────┤
  │ 通知側（ドライバ等） │ call siXxx cHandler;                            │
  ├──────────────────────┼─────────────────────────────────────────────────┤
  │ 受信側（アプリ等）   │ entry siXxx eHandler;                           │
  ├──────────────────────┼─────────────────────────────────────────────────┤
  │ アセンブリ           │ eHandler <= Driver.cHandler;                    │
  ├──────────────────────┼─────────────────────────────────────────────────┤
  │ 条件                 │ [callback] シグニチャ OR [prototype] セルタイプ │
  └──────────────────────┴─────────────────────────────────────────────────┘

  ---
  Sources used:
  - wiki/references/cdl-signature-examples.md (confidence: high) — [callback] 構文例
  - wiki/concepts/cdl-language.md (confidence: high) — callback 指定子の説明、si 命名規則
  - wiki/topics/tcd-notation.md (confidence: high) — 逆結合のTCD表記
  - raw/articles/2026-05-19-cdl-cell-binding-detail.md (confidence: high) — <= 逆結合構文、条件（[prototype] OR
  callback）

  Knowledge gaps:
  - [prototype] セルタイプとコールバックの組み合わせ制約の詳細
  - 複数セルへのコールバック（呼び口配列+逆結合）の具体例

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 3 lines
      1  # Wiki Activity Log
      2
      3 +## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 4 articles (standard)
      4 +## [2026-06-11] query | "呼び口配列の書き方を教えて" → answered from 4 articles (standard)
      5 +## [2026-06-11] query | "合流の書き方を教えて" → answered from 2 articles (standard)
      6  ## [2026-06-08] query | "受け口配列の書き方を教えて" → answered from 2 articles (standard)
      7  ## [2026-06-08] query | "呼び口配列の書き方を教えて" → answered from 4 articles (standard)
      8  ## [2026-06-08] query | "合流の書き方" → answered from 1 article (standard)

● ログ更新完了。コールバックの書き方の回答を合成しました。

  [callback] シグニチャ + <= 逆結合演算子が核心で、逆結合の有効条件は「[callback] シグニチャ」または「[prototype]
  セルタイプ」のいずれかです。
