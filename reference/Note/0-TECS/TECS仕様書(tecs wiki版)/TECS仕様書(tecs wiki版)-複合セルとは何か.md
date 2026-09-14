---
date: 2026-06-08
description: "複合セルタイプ（composite celltype）の定義。CDL記述・内部セル構成・外部結合（export）（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - cdl
---
● tecs wiki のインデックスは確認済み（16記事一致）。複合セルについては今セッションで advanced-cdl-features.md と tcd-notation.md
  を既読です。確認のため全文検索を実施します。

  Searched for 2 patterns (ctrl+o to expand)

● Update(~\wiki\topics\tecs\log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-08] query | "複合セルとは何か" → answered from 3 articles (standard)
      4  ## [2026-06-08] query | "TECSコンポーネント図とは何か" → answered from 2 articles (standard)
      5  ## [2026-06-08] query | "アクティブセルとは何か" → answered from 4 articles (standard)
      6  ## [2026-06-08] query | "コンテキストとは何か" → answered from 4 articles (standard)

● ---
  「複合セル（複合セルタイプ）」とは（tecs wiki より）

  **複合セルタイプ（composite celltype）**とは、複数のセルをひとまとまりにして外部から単一コンポーネントとして見せる機能です。CDL では
  composite キーワードで宣言します。

  CDL での記述

  composite tMyComposite {
      call   sEntry cExtCall;        // 外部への呼び口をエクスポート
      entry  sEntry eExtEntry;       // 外部への受け口をエクスポート
      attr   int32_t myAttr = 0;     // 属性のエクスポート

      cell tInner Inner1 {
          cInnerCall => composite.cExtCall;  // 呼び口を外部に繋げる
          attr = composite.myAttr;
      };
      composite.eExtEntry => Inner1.eInnerEntry;  // 受け口を内部セルへ
  };

  エクスポート構文の2方向

  ┌──────────────────────┬──────────────────────────────────────────────────┬─────────────────────────────────────────────────┐
  │         種類         │                       構文                       │                      意味                       │
  ├──────────────────────┼──────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ 呼び口のエクスポート │ cPort => composite.cExternalCall                 │ 内部の呼び口を composite の外部呼び口として露出 │
  ├──────────────────────┼──────────────────────────────────────────────────┼─────────────────────────────────────────────────┤
  │ 受け口のエクスポート │ composite.eExternalEntry => inner.eInternalEntry │ 外部からの受け口を内部セルへ転送                │
  └──────────────────────┴──────────────────────────────────────────────────┴─────────────────────────────────────────────────┘

  $id$ の解決

  composite 内の内部セルでは、ファクトリ内の $id$ は（内部セル名ではなく）composite セル名に展開されます。

  TCD（コンポーネント図）での表記

  複合セルには特別なマーキングなし（通常セルと同一の矩形）。内部構造は通常コンポーネント図には記載しません。

  属性の $id$ の注意点

  複合セルタイプ内のセルの $id$ は composite セル名に解決されます（内部セルの $id$ ではありません）。これは factory
  を使う際の重要な挙動です。

  ---
  Sources used:
  - CDL 高度機能 (wiki/concepts/advanced-cdl-features.md) (confidence: high) — composite の CDL
  構文全体、エクスポート構文（呼び口/受け口/属性）、$id$ の解決先
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) — 複合セルの TCD 表記（特別なマーキングなし、内部構造は図に記載しない）
  - 実装パターン (wiki/concepts/implementation-patterns.md) (confidence: high) — composite 内の $id$ が composite
  セル名に展開されるという実装上の挙動

  Knowledge gaps:
  - composite 内に別の composite を入れ子にする場合の挙動は記載なし
  - composite と active 指定子の組み合わせ可否（タスクを内包する複合セルタイプ）は記載なし
