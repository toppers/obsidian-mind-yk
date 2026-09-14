---
date: 2026-06-09
description: "受け口配列のCDL宣言（entry sSignature eArray[N]）・TCD表記・CDL結合BNF。サイズN必須（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - cdl
---
● tecs-0 wiki の celltype-implementation.md と関連記事を検索します。

  Searched for 8 patterns, read 3 files (ctrl+o to expand)

● これで十分な情報が集まりました。回答します。

  ---
  受け口配列の書き方

  1. セルタイプでの宣言（CDL）

  tecs-component-model.md より：

  entry sSignature eArray[N];    /* 受け口配列 — サイズ N は必須 */

  ▎ 呼び口配列との違い: 呼び口配列は cArray[] とサイズ省略可能ですが、受け口配列は N を明示する必要があります。

  2. 受け口配列の特性

  tecs-component-model.md と rawソース（第2章）より：

  - 呼び元を識別できる — 合流（複数の呼び口が1つの受け口に結合）とは異なり、受け口配列は呼び元のインデックスを受け取って識別が可能
  - 用途: 複数の呼び元セルそれぞれに対して個別の応答が必要な場合に使用

  3. 組上げ記述での結合（CDL）

  呼び口配列と受け口配列を対応させて結合します（cdl-language-spec.md BNF より）：

  cell tCallerType CallerA {
      cCall[] = Provider.eArray[0];   /* インデックス明示 */
  };

  cell tCallerType CallerB {
      cCall[] = Provider.eArray[1];
  };

  または呼び口配列から一括結合：

  cell tDispatcher Dispatcher {
      cArray[0] = CellA.eFunc;
      cArray[1] = CellB.eFunc;
      /* eArray は提供側に宣言 — 呼び口配列と1対1で対応 */
  };

  rawソース（第3章後半）の記述: 「呼び口配列は全添数を記述する」。

  4. 実装側への影響

  celltype-implementation.md の最適化テーブルより：

  ┌──────────────────────────┬────────────────────────────────────────────────────────┬────────────────────────────────┐
  │          最適化          │                          条件                          │              効果              │
  ├──────────────────────────┼────────────────────────────────────────────────────────┼────────────────────────────────┤
  │ 受け口ディスクリプタ不要 │ 全受け口が同じセルタイプの受け口かつ受け口が配列でない │ 受け口ディスクリプタ→IDXに置換 │
  └──────────────────────────┴────────────────────────────────────────────────────────┴────────────────────────────────┘

  受け口が配列の場合はこの最適化が適用されず、受け口ディスクリプタが必要になります。

  TCD図記法について

  TCD（コンポーネント図）での受け口配列の描き方は このwiki（tecs-0）ではカバーされていません。tecs wiki の wiki/topics/tcd-notation.md
  を参照してください。

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) — entry sSignature eArray[N];
  宣言構文、受け口配列の呼び元識別特性
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — 結合BNF
  - セルタイプ実装モデル (wiki/topics/celltype-implementation.md) (confidence: high) — 受け口ディスクリプタ不要最適化の条件
  - raw 2026-05-17-tecs-spec-chap2-component-model.md (confidence: high) — 呼び口配列と受け口配列の違い（合流との対比）

  Knowledge gaps:
  - C実装側での受け口関数の引数形式（int_t subscript が第2引数に追加される）がこのwikiに未収録 → tecs wiki の implementation-model.md
  に詳細あり
  - TCD図での受け口配列表記（インデックスをポート名に付加）がこのwikiに未収録

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "受け口配列の書き方を教えて" → answered from 4 articles (standard; raw used)
      4  ## [2026-06-08] query | "呼び口配列の書き方を教えて" → answered from 2 articles (standard)
      5  ## [2026-06-08] query | "合流の書き方 (2)" → concept only, no diagram notation (standard)
      6  ## [2026-06-08] query | "合流の書き方" → concept only, no diagram notation (standard)

● ログ更新完了。次のクエリをどうぞ。
