---
date: 2026-06-11T00:00:00.000Z
description: "TECSウィキ（tecs-0/仕様書ベース）クエリ回答 — 複合セルの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● tecs-0 wiki の複合セルタイプ情報を grep で確認します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● cdl-language-spec.md の複合セルタイプ部分を詳しく読みます。

  Read 2 files (ctrl+o to expand)

● 必要な情報が揃いました。回答を合成します。

  ---
  複合セルタイプ（composite）の書き方（tecs-0 wiki）

  概要

  複数のセルをひとまとまりにして、外部から単一コンポーネントとして扱えるようにする仕組みです。

  ---
  1. CDL 構文

  composite composite_celltype_name { composite_celltype_statement_list };

  複合セルタイプの本体に書けるもの（4種類）：

  ┌─────────────────────┬────────────────────────────────────────────┐
  │        記述         │                    説明                    │
  ├─────────────────────┼────────────────────────────────────────────┤
  │ port                │ 外部公開する呼び口・受け口                 │
  ├─────────────────────┼────────────────────────────────────────────┤
  │ composite_attribute │ 外部公開する属性                           │
  ├─────────────────────┼────────────────────────────────────────────┤
  │ internal_cell       │ 内部に配置するセル                         │
  ├─────────────────────┼────────────────────────────────────────────┤
  │ export_join         │ 外部名と内部セルの要素を結びつける外部結合 │
  └─────────────────────┴────────────────────────────────────────────┘

  ---
  2. 具体的な CDL 例

  composite tMyComposite {
      /* 外部受け口・呼び口 */
      entry sSig eOuter;
      call  sSig cOuter;
      attribute {
          int32_t myVal = 0;
      };

      /* 内部セル */
      cell tInner Inner1 {
          /* 内部セルの結合 */
          cInnerCall = Inner2.eEntry;
          val = myVal;        /* composite の属性を使用 */
      };
      cell tInner Inner2 { };

      /* 外部結合（外部名 = 内部セル名.要素名） */
      eOuter = Inner2.eInner;   /* 受け口エクスポート */
      cOuter = Inner1.cInner;   /* 呼び口エクスポート */
  };

  ---
  3. 外部結合の構文

  export_name '=' internal_ref_cell_name '.' internal_cell_elem_name ';'

  外部名（ポート名や属性名）と内部セルの要素を = で結びつけます。

  ---
  4. プロトタイプ宣言（循環参照対策）

  内部セルが互いに受け口を参照し合う場合、前方参照のためのプロトタイプ宣言が必要です：

  cell internal_namespace_celltype_name internal_cell_name ';'

  結合リストなしの宣言のみ。実際の結合はその後の完全なセル記述で行います。

  ---
  5. 指定子の伝播ルール

  ┌───────────┬──────────────────────────────────────────────────────────────────────┐
  │  指定子   │                                 条件                                 │
  ├───────────┼──────────────────────────────────────────────────────────────────────┤
  │ active    │ 内部セルのセルタイプが1つでも active なら、複合セルタイプでも必要    │
  ├───────────┼──────────────────────────────────────────────────────────────────────┤
  │ singleton │ 内部セルのセルタイプが1つでも singleton なら、複合セルタイプでも必要 │
  └───────────┴──────────────────────────────────────────────────────────────────────┘

  [active]
  composite tActiveComposite {
      cell tActiveTask InnerTask { };  /* active なセルを内包 */
  };

  ---
  6. 複合セルタイプ属性の構文

  attribute '{' composite_attribute_declaration_list '}' ';'

  複合セル全体の属性として、内部セルから参照できます。

  ---
  Sources used:
  - wiki/concepts/cdl-language-spec.md (confidence: high) — composite BNF・外部結合構文・プロトタイプ宣言
  - wiki/concepts/tecs-component-model.md (confidence: high) — 複合セルタイプの概念定義・CDL例
  - raw/articles/2026-05-17-tecs-spec-chap3-cdl-part2.md (confidence: high) — 複合セルタイプの詳細BNF・active/singleton
  伝播ルール

  Knowledge gaps:
  - tecs-0 wiki には外部結合の composite.eXxx => 記法（呼び口と受け口で別々の方向性を持つパターン）の明示的な説明がない
  - アロケータ付き複合セルタイプの記述方法（writeme.txt に未記述課題として列挙）
  - through 指定子との組み合わせ（同じく未記述）
  - → 詳細な実例は /wiki:query --wiki tecs 複合セルの書き方 で補完可能

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles (2 wiki + 1 raw) (standard
        +)
      4  ## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 4 articles + 2 raw (standard)
      5  ## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 2 articles + 1 raw (standard)
      6  ## [2026-06-08] query | "受け口配列の書き方を教えて (2)" → answered from 4 articles (standard; raw used)

● tecs-0 wiki での複合セル回答を完了しました。

  tecs-0 の外部結合は export_name = inner_cell.elem_name; という = 記法で説明されており、tecs wiki の composite.eXxx =>
  InnerCell.eXxx という => 記法と表現が異なります。どちらも同じ構造を表していますが、仕様書ベースの tecs-0
  はより抽象的な BNF 形式で記述されています。
