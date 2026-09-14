---
date: 2026-06-11T00:00:00.000Z
description: "TECSウィキ（tecs ReadTheDocs版）クエリ回答 — 複合セルの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● インデックスは既読です。複合セルタイプに最も関連する advanced-cdl-features.md を読みます。

  Read 1 file (ctrl+o to expand)

● advanced-cdl-features.md で基本構文を確認しました。rawソースでより詳細な情報を確認します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● 複合セルタイプ内のプロトタイプ宣言についても確認します。

  Searched for 1 pattern (ctrl+o to expand)

● 必要な情報が揃いました。回答を合成します。

  ---
  複合セルタイプ（composite）の書き方

  概要

  composite は複数のセルをひとまとまりにして、外部から単一コンポーネントとして見せる機能です。TCD
  では通常セルと同じ矩形（特別なマーキングなし）で描きます。

  ---
  1. 基本構文

  composite tMyComposite {
      /* --- 外部に公開するポート・属性 --- */
      entry  sSignature  eExtEntry;       // 外部受け口
      call   sSignature  cExtCall;        // 外部呼び口
      attr {
          int32_t myAttr = 10;
      };

      /* --- 内部セル --- */
      cell tCelltype Cell1 {
          cInnerCall = Cell2.eEntry;
          val = composite.myAttr;          // 属性をエクスポート（内部セル内）
      };
      cell tCelltype Cell2 {
          cExtPortInCell => composite.cExtCall;  // 呼び口エクスポート（内部セル内）
      };

      /* --- 受け口のエクスポート（内部セル外、複合セルタイプ直下） --- */
      composite.eExtEntry => Cell2.eEntry;
  };

  ---
  2. エクスポート構文の3パターン

  ┌────────┬────────────────────┬──────────────────────────────────────────┐
  │  対象  │      記述場所      │                   構文                   │
  ├────────┼────────────────────┼──────────────────────────────────────────┤
  │ 呼び口 │ 内部セル内         │ cPort => composite.cExtCall;             │
  ├────────┼────────────────────┼──────────────────────────────────────────┤
  │ 受け口 │ 複合セルタイプ直下 │ composite.eExtEntry => InnerCell.eEntry; │
  ├────────┼────────────────────┼──────────────────────────────────────────┤
  │ 属性   │ 内部セル内         │ attr = composite.myAttr;                 │
  └────────┴────────────────────┴──────────────────────────────────────────┘

  ▎ 配列全体のエクスポートは可能ですが、特定の添数（インデックス）のみのエクスポートは不可です。

  ---
  3. 指定子（active / singleton）

  ┌─────────────┬──────────────────────────────────────────────────────┐
  │   指定子    │                      付ける条件                      │
  ├─────────────┼──────────────────────────────────────────────────────┤
  │ [active]    │ 内部セルのセルタイプが1つでも active な場合に必要    │
  ├─────────────┼──────────────────────────────────────────────────────┤
  │ [singleton] │ 内部セルのセルタイプが1つでも singleton な場合に必要 │
  └─────────────┴──────────────────────────────────────────────────────┘

  [active, singleton]
  composite tActiveComposite {
      cell tActiveTask inner { };  /* active なセルを内包 */
  };

  ---
  4. C_EXP での名前置換ルール（composite 特有）

  複合セルタイプの attr に現れる C_EXP:

  ┌────────────────────┬───────────────────────────────────────────────┐
  │       マクロ       │                    解決先                     │
  ├────────────────────┼───────────────────────────────────────────────┤
  │ $id$, $ct$, $cell$ │ 複合セルの名前（複合セルタイプ名_複合セル名） │
  ├────────────────────┼───────────────────────────────────────────────┤
  │ 内部セルの $id$    │ 展開後の内部セル名                            │
  └────────────────────┴───────────────────────────────────────────────┘

  例: CompositeCell.Cell1 の B_$id$ → B_CompositeCell_Cell1

  ---
  5. 使用不可の指定子

  ┌──────────┬─────────────────────┐
  │   対象   │   使えない指定子    │
  ├──────────┼─────────────────────┤
  │ 受け口   │ inline 指定子       │
  ├──────────┼─────────────────────┤
  │ 属性     │ omit 指定子         │
  ├──────────┼─────────────────────┤
  │ 内部セル │ omit, inline 指定子 │
  └──────────┴─────────────────────┘

  ---
  6. プロトタイプ宣言（内部セルの相互参照）

  内部セルが互いに参照し合う場合（循環依存）はプロトタイプ宣言で前方参照します：

  ┌──────────────────┬────────────────────────────────────────┐
  │       種類       │                  説明                  │
  ├──────────────────┼────────────────────────────────────────┤
  │ 純粋プロトタイプ │ 結合リストなし。前方参照のみ           │
  ├──────────────────┼────────────────────────────────────────┤
  │ 指定プロトタイプ │ 結合・属性を部分的または完全に事前指定 │
  └──────────────────┴────────────────────────────────────────┘

  ---
  7. TCD 表記

  複合セルは外部からは通常セルと同じ矩形で描きます。内部構造は通常のコンポーネント図には記載しません。

  ---
  Sources used:
  - wiki/concepts/advanced-cdl-features.md (confidence: high) — composite の基本構文・エクスポートパターン
  - raw/articles/2026-05-19-cdl-composite.md (confidence: high) — active/singleton
  伝播ルール・C_EXP名前置換・使用不可指定子
  - wiki/concepts/cdl-language.md (confidence: high) — プロトタイプ宣言の種類
  - wiki/topics/tcd-notation.md (confidence: high) — 複合セルの TCD 表記（特別マーキングなし）

  Knowledge gaps:
  - composite に generate(Plugin, ...) を適用する場合の詳細（複合セルタイププラグイン）
  - 複合セルタイプのアロケータ（リレーアロケータ・内部アロケータ）の具体的な記述例

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles + 1 raw (standard)
      4  ## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 5 articles + 2 raw (standard)
      5  ## [2026-06-11] query | "コールバックの書き方を教えて" → answered from 4 articles (standard)
      6  ## [2026-06-11] query | "呼び口配列の書き方を教えて" → answered from 4 articles (standard)

● 複合セルタイプの書き方を回答しました。

  エクスポート方向が左右非対称（呼び口は内部セル内に =>、受け口は複合セルタイプ直下に
  composite.e...）という点が最も重要な構文上の特徴です。

✻ Worked for 1m 13s

※ recap: TECS CDL wiki queries via /wiki:query (tecs and tecs-0). Answered callbacks, active cells, and composite cells.
  Next: continue with more wiki queries or wrap up the session.
