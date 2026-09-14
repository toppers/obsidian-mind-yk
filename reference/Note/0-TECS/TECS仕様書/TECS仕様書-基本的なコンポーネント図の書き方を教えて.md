---
date: 2026-06-08
description: "TECSコンポーネント図（TCD）の基本的な書き方。セル矩形・受け口三角・呼び口線分の記法（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - tcd
---
● tecs-0 wiki のインデックスは確認済み（5記事一致）。前回クエリで TCD 記法記事が存在しないことを確認済み。今回は「基本的なコンポーネン
  ト図の書き方」として、CDL/コンポーネントモデルから描ける情報がないか全文検索します。

  Searched for 1 pattern (ctrl+o to expand)

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "基本的なコンポーネント図の書き方" → no coverage in this wiki (standard)
      4  ## [2026-06-08] query | "TECSコンポーネント図の書き方" → no coverage in this wiki (standard)
      5  ## [2026-06-08] query | "TECSコンポーネント図とは何か" → partial answer from 1 article (standard; limited coverage)
      6  ## [2026-06-08] query | "複合セルとは何か" → answered from 2 articles (standard)

● tecs-0 wiki にはコンポーネント図の書き方に関する記載がありません。

  ---
  「基本的なコンポーネント図の書き方」について（tecs-0 wiki）

  tecs-0 wiki には、コンポーネント図（TCD）の書き方・記法に関する記事が存在しません。

  TCD は TECS の4要素の一つとして「コンポーネント構造の視覚的記法」と位置づけられているとだけ言及されており、具体的なシンボル・描画ルー
  ルの解説は収録されていません。

  tecs-0 wiki が持っている関連知識は以下のとおりです（直接の「書き方」ではありませんが、図を理解・描くための基礎概念）：

  ┌──────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
  │                   概念                   │                               記事                               │
  ├──────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ セル・セルタイプ・シグニチャ・結合の定義 │ TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) │
  ├──────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ CDL の組上げ記述（図と1対1対応する）     │ CDL言語仕様 (wiki/concepts/cdl-language-spec.md)                 │
  └──────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘

  ---
  Sources used:
  - TECS概要 (wiki/topics/tecs-overview.md) (confidence: high) — TCD が「コンポーネント構造の視覚的記法」という言及のみ

  Related in other wikis:
  - tecs wiki: TCD 記法 (wiki/topics/tcd-notation.md) — 完全な書き方ガイド。セル（矩形）・受け口（内向き塗りつぶし三角形）・呼び口（線
  分）・接続線・アクティブセル（二重線）・合流・配列・コールバック・RPC・アロケータ・多段リレーモデルの全記法と CDL 対応表を収録

  Knowledge gaps:
  - TCD の記法を解説したソースを tecs-0 wiki に /wiki:ingest → /wiki:compile することで対応できます
