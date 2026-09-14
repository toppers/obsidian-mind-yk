---
date: 2026-06-09
description: "呼び口配列のCDL宣言・TCD表記・C実装（subscript第1引数・NCP_マクロ）（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - cdl
---
● tecs wiki の関連記事を読んで回答します。

  Searched for 1 pattern, read 2 files (ctrl+o to expand)

● implementation-model.md も確認します。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● implementation-model.md の該当部分を確認します。

  Searched for 3 patterns, read 1 file (ctrl+o to expand)

● これで十分な情報が集まりました。回答します。

  ---
  呼び口配列の書き方

  1. セルタイプでの宣言（CDL）

  呼び口配列は「配列形式で複数セルへの結合が可能」なポートとして宣言します（cdl-language.md）。サイズは省略するのが一般的で、tecsgen
  が結合数から自動決定します。

  celltype tMyType {
      call sSignature cArray[];   /* サイズ省略 — tecsgenが自動決定 */
      /* サイズ明示も可能: call sSignature cArray[3]; */
  };

  2. 組上げ記述での結合（CDL）

  インデックスを付加して各要素を個別に結合します（plugins.md の RepeatJoinPlugin 説明から確認）：

  cell tMyType MyCell {
      cArray[0] = TargetCellA.eFunc;
      cArray[1] = TargetCellB.eFunc;
      cArray[2] = TargetCellC.eFunc;
  };

  RepeatJoinPlugin を使うと、同一パターンの配列結合を N 個自動展開できます。

  3. TCD（コンポーネント図）での表記

  tcd-notation.md より：

  ▎ 配列インデックスをポート名に付加して表記。
  ▎ 呼び口配列と受け口配列のインデックスを対応させると、複数の呼び元にわたるコールバック機能を実現できる。

  つまり cArray[0]、cArray[1]、cArray[2] のように、各インデックスを接続線のラベルとして図に記載します。

  4. C実装側の呼び出し方法

  implementation-model.md より：

  /* 非配列の場合 */
  ER cCall_func1(int32_t inval, int32_t *outval);

  /* 配列の場合 — subscript が第1引数 */
  ER cCall_func1(int_t subscript, int32_t inval, int32_t *outval);

  subscript に配列インデックスを渡して各要素を呼び分けます。

  配列サイズの取得マクロ：

  ┌────────────┬─────────────────────────────────────────────┐
  │   マクロ   │                    用途                     │
  ├────────────┼─────────────────────────────────────────────┤
  │ NCP_cCall  │ 呼び口配列のサイズ（短縮形、p_cellcb 前提） │
  ├────────────┼─────────────────────────────────────────────┤
  │ N_CP_cCall │ 呼び口配列のサイズ（通常形）                │
  └────────────┴─────────────────────────────────────────────┘

  全要素への反復呼び出しの例（Cコード）：

  for (int_t i = 0; i < NCP_cArray; i++) {
      cArray_func1(i, inval);
  }

  ---
  Sources used:
  - CDL（コンポーネント記述言語） (wiki/concepts/cdl-language.md) (confidence: high) — 呼び口ポートの配列形式説明
  - TCD（TECS コンポーネント図）記法 (wiki/topics/tcd-notation.md) (confidence: high) — TCD
  での呼び口配列表記（インデックスをポート名に付加）
  - セルタイプコード実装モデル (wiki/concepts/implementation-model.md) (confidence: high) — subscript引数、NCP_/N_CP_ マクロ
  - プラグインリファレンス (wiki/references/plugins.md) (confidence: high) — cArray[0] = ... の結合記法、RepeatJoinPlugin

  Knowledge gaps:
  - CDL 宣言構文（call sSignature cArray[];）の明示的な例がこの wiki にない（tecs-0 wiki の cdl-language-spec.md に BNF と宣言例あり）
  - 呼び口配列に optional や omit を組み合わせた場合の挙動の詳細

● Update(~\wiki\topics\tecs\log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-08] query | "呼び口配列の書き方を教えて" → answered from 4 articles (standard)
      4  ## [2026-06-08] query | "合流の書き方" → answered from 1 article (standard)
      5  ## [2026-06-08] query | "基本的なコンポーネント図の書き方" → answered from 1 article (standard)
      6  ## [2026-06-08] query | "TECSコンポーネント図の書き方" → answered from 1 article (standard)

● ログ更新完了。次のクエリをどうぞ。

