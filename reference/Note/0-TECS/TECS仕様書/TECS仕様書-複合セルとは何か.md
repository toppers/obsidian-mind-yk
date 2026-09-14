---
date: 2026-06-08
description: "複合セルタイプ（composite celltype）の定義。CDL記述・内部セル構成・外部結合（export）（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - cdl
---
 tecs-0 wiki のインデックスは確認済み（5記事一致）。複合セルに関連するコンテンツを検索します。

  Searched for 1 pattern, read 2 files (ctrl+o to expand)

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "複合セルとは何か" → answered from 2 articles (standard)
      4  ## [2026-06-08] query | "アクティブセルとは何か" → answered from 2 articles (standard)
      5  ## [2026-06-08] query | "コンテキストとは何か" → partial answer from 1 article (standard; limited coverage)
      6  ## [2026-06-08] query | "受け口配列とは何か" → answered from 3 articles (standard)

● ---
  「複合セル（複合セルタイプ）」とは（tecs-0 wiki より）

  **複合セルタイプ（composite celltype）**とは、複数のセルを組み合わせて新しいセルを生成する機能です。内部に複数のセル（内部セル）を持
  ち、それらを束ねて外部から単一のコンポーネントとして見せます。

  CDL での記述

  composite tCompositeName {
    entry sSig eOuter;           # 外部受け口（外部から呼ばれる口）
    attribute { ... };           # 属性
    cell tInner inner1 { ... };  # 内部セル
    eOuter = inner1.eInner;      # 外部結合（内部→外部の公開）
  };

  BNF（構文規則）

  composite composite_celltype_name '{' composite_celltype_statement_list '}' ';'

  複合セルタイプ文として記述できるもの：

  ┌─────────────────────┬────────────────────────────────────────┐
  │        種類         │                  内容                  │
  ├─────────────────────┼────────────────────────────────────────┤
  │ port                │ 外部ポート（entry/call）宣言           │
  ├─────────────────────┼────────────────────────────────────────┤
  │ composite_attribute │ 属性宣言                               │
  ├─────────────────────┼────────────────────────────────────────┤
  │ internal_cell       │ 内部セルの定義                         │
  ├─────────────────────┼────────────────────────────────────────┤
  │ export_join         │ 外部結合（内部受け口を外部に公開する） │
  └─────────────────────┴────────────────────────────────────────┘

  外部結合（export_join）

  内部セルの受け口を外部に公開する仕組みです：

  export_name '=' internal_ref_cell_name '.' internal_cell_elem_name ';'
  # 例: eOuter = inner1.eInner;

  プロトタイプ宣言

  内部セルが相互参照し合う場合（A が B を参照し、B が A を参照する等）、前方参照のためにプロトタイプ宣言が使えます：

  cell internal_namespace_celltype_name internal_cell_name ';'

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) — 複合セルタイプの定義・CDL
  記述例・「複数のセルを組み合わせて新しいセルを生成する」という概念説明
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — composite の BNF
  構文、複合セルタイプ文の4種類（port/composite_attribute/internal_cell/export_join）、プロトタイプ宣言・外部結合の形式

  Related in other wikis:
  - tecs wiki: CDL 高度機能 (wiki/concepts/advanced-cdl-features.md) — composite の詳細実装（composite.cExtCall / composite.myAttr
  等の参照方法、$id$ の解決先）

  Knowledge gaps:
  - 複合セルタイプのセルタイプコードから内部セルにアクセスする方法は tecs-0 wiki には記載なし
  - 複合セルタイプの call ポート（外部からの呼び出し用）の宣言方法の具体例がない
  - composite_attribute の詳細な文法は記載なし
