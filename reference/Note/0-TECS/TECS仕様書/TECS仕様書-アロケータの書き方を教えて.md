---
date: 2026-06-12T00:00:00.000Z
description: "TECSウィキ（tecs-0/仕様書ベース）クエリ回答 — アロケータの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● tecs-0 ウィキのアロケータ関連を検索します。

  Searched for 4 patterns, read 1 file (ctrl+o to expand)

● celltype-implementation.md のアロケータセクションをもっと読みます。

  Searched for 4 patterns, read 1 file (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs-0/log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3  ## [2026-06-12] query | "RPCの書き方を教えて" → answered from 3 wiki articles + 2 raw (standard)
      4 +## [2026-06-12] query | "アロケータの書き方を教えて" → answered from 2 wiki articles + 3 raw (standard)
      5
      6  ## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles (2 wiki + 1 raw) (standard)
      7  ## [2026-06-11] query | "アクティブの書き方を教えて" → answered from 4 articles + 2 raw (standard)

● ---
  TECS におけるアロケータの書き方（tecs-0 ウィキ — 仕様書ベース）

  1. アロケータとは

  send / receive 指定子のある引数に対して、tecsgen がアロケータ呼び口と結合を自動挿入する仕組みです。

  ┌────────────────────┬───────────────────────┬──────────────┬──────────────────────┐
  │       指定子       │         方向          │      型      │  alloc/dealloc 責任  │
  ├────────────────────┼───────────────────────┼──────────────┼──────────────────────┤
  │ send(allocator)    │ 入力（呼び元→呼び先） │ 単一ポインタ │ 呼び出し先が dealloc │
  ├────────────────────┼───────────────────────┼──────────────┼──────────────────────┤
  │ receive(allocator) │ 出力（呼び先→呼び元） │ 二重ポインタ │ 呼び出し先が alloc   │
  └────────────────────┴───────────────────────┴──────────────┴──────────────────────┘

  ---
  2. アロケータシグニチャの書き方

  アロケータとして使うシグニチャは alloc / dealloc 関数を持つ必要があります。

  signature sAlloc {
      ER  alloc( [in] size_t size, [out] void **p_buf );
      ER  dealloc( [in] void *buf );
  };

  ---
  3. send/receive を使うシグニチャの書き方

  send(cAlloc) の cAlloc はアロケータシグニチャの呼び口名です。size_is と組み合わせます。

  signature sPacketTransfer {
      ER  send(    [send(cAlloc), size_is(len)]       uint8_t *packet,    [in]  uint32_t len );
      ER  receive( [receive(cAlloc), size_is(*p_len)] uint8_t **p_packet, [out] uint32_t *p_len );
  };

  ---
  4. tecsgen が自動生成するアロケータ呼び口

  send/receive 引数に対してtecsgenがアロケータ呼び口と結合を自動挿入します。開発者が CDL に明示的に書く必要はありません。

  /* tecsgen 自動生成 — アロケータ呼び口 */
  ER alloc( size_t len, void *p );
  ER dealloc( void *p );

  ---
  5. セル指定子 [allocator]

  CDL 仕様の指定子キーワードとして allocator が存在します。セルタイプの受け口宣言で使います（受け口からアロケータをリレーするパターン）。

  指定子キーワード: active allocator count_is idx_is_id in in_through inout omit
                    out out_through receive send singleton size_is string through to_through

  ---
  6. 注意事項（仕様書 writeme より）

  cell の allocator 指定 は仕様書の「未記述課題」 として明記されています。cell 側（組上げ記述）でのアロケータ指定方法の詳細は、tecs-0
  ウィキの仕様書からは読み取れません。

  ---
  Sources used:
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — send/receive 引数の定義・allocator 指定子キーワード・sPacketTransfer 例
  - celltype-implementation (wiki/topics/celltype-implementation.md) (confidence: high) — tecsgen のアロケータ自動挿入・sAlloc シグニチャ形式
  - raw: 第3章CDL後半 (raw/articles/2026-05-17-tecs-spec-chap3-cdl-part2.md) (confidence: high) — 引数指定子表・writeme.txt 未記述課題の確認
  - raw: 第4章実装モデル (raw/articles/2026-05-17-tecs-spec-chap4-implementation-model.md) (confidence: high) — アロケータコード自動挿入の原文記述
  - raw: CDLシグニチャ記述例 (raw/articles/2026-06-08-cdl-signature-examples.md) (confidence: high) — send/receive を含む完全なシグニチャ例

  Knowledge gaps:
  - cell の allocator 指定（組上げ記述でのアロケータ結合方法）が未記述課題 として仕様書自体に明記されており、tecs-0 ウィキではカバーできていません
  - → tecs ウィキ（wiki/concepts/implementation-patterns.md）には [allocator(eS.snd.buf=alloc.eA)] の CDL 組上げ例があります。補完には --with tecs
  または /wiki:query --wiki tecs が有効です
