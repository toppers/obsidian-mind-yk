---
date: 2026-06-18
description: "/wiki:query「シグニチャの引数方向」--wiki tecs-0-md の実行記録（整形前の生ログ）"
tags:
  - reference
  - tecs
  - wiki-query
---

❯ /wiki:query "シグニチャの引数方向" --wiki tecs-0-md — 記事への質問

関連記事を読んで回答します。

  Read 2 files

● Update(~\wiki\topics\tecs-0-md\log.md)
Added 1 line

## [2026-06-18] init | Wiki initialized
## [2026-06-18] ingest | TECS仕様書 V1.3.0.1 (PDF→MD変換) (raw/notes/2026-06-18-tecs-spec-v1-3-0-1.md)
## [2026-06-18] query | "シグニチャの引数方向" → answered from 2 articles (standard)
## [2026-06-18] compile | 1 source → 16 new articles (tecs-overview, tecs-component-model, tecs-cdl, tec
s-component-implementation, tecs-cell, tecs-signature, tecs-celltype, tecs-port, tecs-join, tecs-composi
te-celltype, tecs-region, tecs-allocator, tecs-factory, tecs-rpc, tecs-plugin, tecs-naming-conventions)

シグニチャの引数方向

TECS CDLのシグニチャでは、関数の各引数に入出力方向を明示的に指定することが必須です。C言語の関数インタフェースよりも厳密で、ポインタが「入力か出力か」「アロケータ管理メモリか否か」まで明確化します。

指定子の一覧

┌─────────┬──────────────────┬──────────────────────────────────────────┐
│ 指定子  │       方向       │                メモリ管理                │
├─────────┼──────────────────┼──────────────────────────────────────────┤
│ in      │ 呼び先への入力   │ 通常メモリ（呼び元管理）                 │
├─────────┼──────────────────┼──────────────────────────────────────────┤
│ out     │ 呼び先からの出力 │ 通常メモリ（呼び元管理）                 │
├─────────┼──────────────────┼──────────────────────────────────────────┤
│ inout   │ 入出力           │ 通常メモリ                               │
├─────────┼──────────────────┼──────────────────────────────────────────┤
│ send    │ 呼び先への入力   │ アロケータ確保メモリ（受け取り側が解放） │
├─────────┼──────────────────┼──────────────────────────────────────────┤
│ receive │ 呼び先からの出力 │ アロケータ確保メモリ（受け取り側が解放） │
└─────────┴──────────────────┴──────────────────────────────────────────┘

in/out vs send/receive の違い

- in/out/inout — ポインタが指すメモリ領域は呼び元が確保・管理。呼び先は借りるだけ
- send/receive — アロケータで確保されたメモリを渡す。受け取った側が解放義務を負う

send/receive を使う場合、シグニチャ定義時にどのアロケータを使うか（アロケータシグニチャ）を指定する必要があります。具体的なアロケータは受け口側のセルタイプで定義します（合流してくる複数の呼び元が必ず同一アロケータを使う必要があるため）。

oneway 関数

引数方向とは別に、戻り値なし・出力引数なしの関数は oneway として指定できます。RPC（リモート呼び出し）時に非同期呼び出し（呼び出し完了を待たずに呼び元が処理を再開）が可能になります。

データ型の逸脱（deviate）

TECSはポインタの多重度を引数の入出力方向ごとに制限しています。この制限を満たさない場合（C言語由来の曖昧なポインタ型等）は「逸脱」となり、シグニチャ内で明示的に deviate 宣言が必要です。逸脱したシグニチャはプラグインによるセル自動生成が原則できません。

---
Sources used:
- シグニチャ（signature） (C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-signature.md) (confidence: high) — 引数方向指定子の全定義・oneway・deviate
- アロケータ（allocator） (C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-allocator.md) (confidence: high) — send/receiveとアロケータの関係

Knowledge gaps:
- CDLでの実際の引数方向記法（[in]ブラケット記法か否か）の詳細は仕様書本文§4章を直接参照要
- size is/count is/string による配列の明示記法の詳細は未コンパイル（仕様書内に記述あり）
