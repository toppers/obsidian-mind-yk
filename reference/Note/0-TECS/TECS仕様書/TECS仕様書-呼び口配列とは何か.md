---
date: 2026-06-08
description: "呼び口配列（call port array）の概念。サイズ省略可（[]）・CDL宣言形式と呼び出し方式（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - cdl
---
● インデックスは確認済み（5記事一致）。「呼び口配列」に関連する記事を読みます。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● 実装モデルの呼び口配列に関する箇所も確認します。

  Searched for 1 pattern (ctrl+o to expand)

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "呼び口配列とは何か" → answered from 2 articles (standard)
      4  ## [2026-06-08] query | "結合とは何か" → answered from 1 article (standard)
      5  ## [2026-06-07] query | "呼び口とは何か" → answered from 2 articles (standard, same as TECS仕様書-呼び口とは何か)
      6  ## [2026-06-07] query | "TECS仕様書-シグニチャとは何か" → answered from 2 articles (standard)

● ---
  「呼び口配列」とは（tecs-0 wiki より）

  **呼び口配列（call port array）**とは、1つのセルタイプが複数の結合先（受け口）を持てるよう、呼び口を配列として宣言したものです。

  CDL での宣言構文

  call  sSignature cArray[];     # 呼び口配列（サイズ省略可）

  通常の呼び口（call sSignature cPortName;）が1つの受け口にしか結合できないのに対し、呼び口配列はインデックスごとに異なる受け口と結合で
  きます。サイズは省略でき、tecsgen が結合記述から自動決定します。

  結合時の BNF

  組上げ記述（セル記述）における結合の BNF は以下のとおりです：

  join: ca_name '=' expression ';'
      | ca_name '[' ']' '=' expression ';'
      | ca_name '[' array_index ']' '=' expression ';'
      | ca_name '=' initializer ';'

  呼び口配列への結合は ca_name '[]' = ... または ca_name '[array_index]' = ...
  の形式で記述します。インデックスを明示することも、省略（自動採番）することも可能です。

  呼び口配列を使う場面

  - 複数の同種コンポーネントを束ねて呼び出したい場合（例: 複数のモーターを同じセルタイプで制御する）
  - 組上げ記述によって動的にセル数が変わるシステム構成に対応する場合

  受け口配列との対比

  call  sSignature cArray[];     # 呼び口配列 — 呼び出す側、サイズ省略可
  entry sSignature eArray[N];    # 受け口配列 — 提供する側、サイズ N を明示

  受け口配列（eArray[N]）は、異なる呼び元を識別できる（どのインデックスから呼ばれたかをセルタイプコード内で判定できる）という特性があり
  ます。

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) — call sSignature cArray[];
  の構文と「サイズ省略可」の説明、受け口配列との対比
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — 結合の BNF（ca_name '[' ']' '=' / ca_name '[' array_index ']'
  '='）

  Knowledge gaps:
  - 呼び口配列のインデックスへのアクセス方法（セルタイプコード側での cArray_idx_ マクロ等）については tecs-0 wiki に記載なし
  - スルー結合と組み合わせた場合の動作は記載なし
