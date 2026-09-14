---
date: 2026-06-08
description: "アクティブセルの定義。active指定子・タスク/ハンドラ内包・TCD二重線表記・CDL宣言（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - cdl
---

● tecs-0 wiki のインデックスは確認済み（5記事一致）。アクティブセルに関連するコンテンツを検索します。

  Searched for 1 pattern (ctrl+o to expand)

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "アクティブセルとは何か" → answered from 2 articles (standard)
      4  ## [2026-06-08] query | "コンテキストとは何か" → partial answer from 1 article (standard; limited coverage)
      5  ## [2026-06-08] query | "受け口配列とは何か" → answered from 3 articles (standard)
      6  ## [2026-06-08] query | "呼び口配列とは何か" → answered from 2 articles (standard)

● ---
  「アクティブセル」とは（tecs-0 wiki より）

  **アクティブセル（Active Cell）**とは、タスク等の CPU 資源割付けを伴うセルです。CDL ではセルタイプに active
  指定子を付けて宣言します。

  CDL での宣言

  セルタイプ指定子テーブルより：

  ┌────────┬───────────────────────────────────────────────┐
  │ 指定子 │                     意味                      │
  ├────────┼───────────────────────────────────────────────┤
  │ active │ タスク等の CPU 資源割付けを伴うアクティブセル │
  └────────┴───────────────────────────────────────────────┘

  CDL 言語仕様の定義では、さらに具体的に：

  ▎ active — アクティブセル（タスクセル or タスク内包セル）

  すなわちアクティブセルには2種類の形態があります：
  - タスクセル: セル自体がタスクを持つ
  - タスク内包セル: 内部にタスクを持つ複合セル

  位置づけ

  active はセルタイプ指定子キーワードの一つであり、CDL の celltype
  宣言ブロック内で使用します。他の指定子（singleton、idx_is_id）と同様に、セルタイプの性質を tecsgen に伝えるためのものです。

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) — active 指定子の意味「タスク等の CPU
  資源割付けを伴うアクティブセル」
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — active が指定子キーワードであること、「タスクセル or
  タスク内包セル」の定義

  Related in other wikis:
  - tecs wiki: TCD 記法 (wiki/topics/tcd-notation.md) — アクティブセルは TCD
  図上で二重線矩形として表記、受け口が呼ばれなくても動作するセルという定義
  - tecs wiki: ASP3 カーネルオブジェクト (wiki/topics/asp3-kernel-objects.md) — tTask が具体的なアクティブセルの実例

  Knowledge gaps:
  - tecs-0 wiki には active 指定子の具体的な CDL コード例がない
  - active 指定子が tecsgen の生成コードにどう影響するか（生成されるファクトリや初期化コードの違い）は記載なし
  - タスクセルとタスク内包セルの具体的な違い・使い分けは記載なし