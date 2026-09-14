---
date: 2026-06-09
description: "呼び口配列のCDL宣言（call sSignature cArray[]）・CDL結合BNF。サイズ省略可（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - cdl
---
 tecs-0 wiki の cdl-language-spec.md はすでに読み込まれているため、そこから直接回答します。

  ---
  呼び口配列の書き方

  1. セルタイプでの宣言（CDL）

  セルタイプ定義内で呼び口配列を宣言します。サイズは省略可能で、tecsgen が結合数から自動決定します。

  celltype tMyType {
      call sSignature cArray[];   /* サイズ省略 — tecsgenが自動決定 */
  };

  サイズを明示したい場合は：

  celltype tMyType {
      call sSignature cArray[3];  /* サイズ明示 */
  };

  2. 組上げ記述での結合（CDL）

  セル記述内での結合方法は3通りあります（cdl-language-spec.md BNF より）：

  join: ca_name '[' ']' '=' expression ';'          /* インデックス省略形 */
      | ca_name '[' array_index ']' '=' expression ';'  /* インデックス明示 */

  インデックス省略（配列順に自動割当て）：

  cell tMyType MyCell {
      cArray[] = TargetCellA.eFunc;
      cArray[] = TargetCellB.eFunc;
      cArray[] = TargetCellC.eFunc;
  };

  インデックス明示：

  cell tMyType MyCell {
      cArray[0] = TargetCellA.eFunc;
      cArray[1] = TargetCellB.eFunc;
      cArray[2] = TargetCellC.eFunc;
  };

  3. 命名規則

  呼び口名は c 接頭文字 + キャメルケース（cArray、cMotorList 等）。

  TCD図記法について

  TCD（コンポーネント図）での呼び口配列の描き方は このwiki（tecs-0）ではカバーされていません。tecs wiki の wiki/topics/tcd-notation.md
  に記法ガイドがあります。

  ---
  Sources used:
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — セル結合BNF（ca_name '[' ']' '='形式）、セルタイプ port
  宣言構文
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) — call sSignature cArray[]; サイズ省略の仕様

  Knowledge gaps:
  - TCD図での呼び口配列表記（インデックスをポート名に付加する記法）はこのwikiに未収録。tecs wiki tcd-notation.md を参照
  - [] と [N] の動作の違いについての詳細説明が不足（仕様書 第3章に詳細あり）

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "呼び口配列の書き方を教えて" → answered from 2 articles (standard)
      4  ## [2026-06-08] query | "合流の書き方 (2)" → concept only, no diagram notation (standard)
      5  ## [2026-06-08] query | "合流の書き方" → concept only, no diagram notation (standard)
      6  ## [2026-06-08] query | "基本的なコンポーネント図の書き方" → no coverage in this wiki (standard)

● ログ更新完了。次のクエリを続けてください。
