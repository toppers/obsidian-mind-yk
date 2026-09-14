---
date: 2026-06-12T00:00:00.000Z
description: "TECSウィキ（tecs ReadTheDocs版）クエリ回答 — アロケータの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● アロケータ関連の記事を検索します。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● アロケータ専用のraw記事があります。並行して読みます。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● implementation-patterns と TCD記法のアロケータ部分も確認します。

  Searched for 2 patterns (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3  ## [2026-06-12] query | "RPCの書き方を教えて" → partial answer — RPC plugins undocumented, framework + CDL through 構文のみ (standard)
      4 +## [2026-06-12] query | "アロケータの書き方を教えて" → answered from 4 wiki articles + 1 raw (standard)
      5
      6  ## [2026-06-11] query | "RPCの書き方を教えて" → partial answer — RPC plugins all undocumented, framework only (standard)
      7  ## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles + 1 raw (standard)

● ---
  TECS におけるアロケータの書き方

  1. アロケータとは

  シグニチャ関数の引数に send または receive 指定子を付けると、呼び元と呼び先の間でメモリ領域をアロケータ経由で受け渡す仕組みです。tecsgen
  がアロケータ用の呼び口を自動生成します。

  ┌─────────┬────────────────────┬──────────────────────┐
  │ 指定子  │ アロケート（確保） │ デアロケート（解放） │
  ├─────────┼────────────────────┼──────────────────────┤
  │ send    │ 呼び元が確保       │ 呼び先が解放         │
  ├─────────┼────────────────────┼──────────────────────┤
  │ receive │ 呼び先が確保       │ 呼び元が解放         │
  └─────────┴────────────────────┴──────────────────────┘

  ---
  2. シグニチャの書き方

  send / receive は size_is または count_is と組み合わせて使います。

  // アロケータシグニチャ（メモリ確保・解放を提供）
  signature sAlloc {
      ER  alloc( [in] size_t size, [out] void **p_buf );
      ER  dealloc( [in] void *buf );
  };

  // send/receive を使うシグニチャ
  signature sPacketTransfer {
      ER  send(    [send(cAlloc), size_is(len)]   uint8_t *packet,  [in]  uint32_t len );
      ER  receive( [receive(cAlloc), size_is(*p_len)] uint8_t **p_packet, [out] uint32_t *p_len );
  };

  ---
  3. セル（組上げ記述）の書き方

  重要: アロケータ指定は受け口側のセルに書く。呼び口側（送信元）は不要。

  signature sSendRecv {
      ER snd( [send(sAlloc), size_is(sz)] int8_t *buf, [in]int32_t sz );
      ER rcv( [receive(sAlloc), size_is(*sz)] int8_t **buf, [out]int32_t *sz );
  };

  // 受け口側: [allocator(受け口名.関数名.引数名 = アロケータセル.受け口名)]
  [allocator(eS.snd.buf=alloc.eA, eS.rcv.buf=alloc.eA)]
  cell tTestComponent comp {};

  // 呼び口側: allocator 指定不要
  cell tTestClient cl {
      cS = comp.eS;
  };

  ---
  4. 自動生成されるアロケータ呼び口

  tecsgen がアロケータ用の C 関数を自動生成します。命名規則：

  (呼び口名) + '_' + (関数名) + '_' + (引数名) + '_alloc'

  // 呼び口 cS の snd 関数 buf 引数に対して自動生成される
  ER cS_snd_buf_alloc( int32_t size, void** p );
  ER cS_snd_buf_dealloc( const void* p );

  // 呼び口 cS の rcv 関数 buf 引数
  ER cS_rcv_buf_alloc( int32_t size, void** p );
  ER cS_rcv_buf_dealloc( const void* p );

  // 呼び口配列の場合は subscript が第1引数に追加される
  ER cA_snd_buf_alloc( subscript, int32_t size, void** p );

  ---
  5. リレーアロケータ（スルーコンポーネント用）

  中継コンポーネントが受け口から呼び口へアロケータを転送するパターン。<= 演算子を使います。

  // セルタイプ定義側で <= でリレーを宣言
  celltype tThroughComponent {
      [allocator(
          snd.buf <= cSR.snd.buf,   // 受け口のアロケータ → 呼び口へ転送
          rcv.buf <= cSR.rcv.buf
      )]
      entry  sSendRecv eS;
      call   sSendRecv cSR;
  };

  セル定義側では allocator 指定不要（<= が転送を意味します）。

  ---
  6. TCD 図での表記

  - アロケータ接続は ▼ シンボル を接続線の近傍に配置し、アロケータセルの受け口に繋げます
  - 多段リレーモデルでは最右辺の受け口でアロケータを指定し、tecsgen が各段の呼び口を自動生成します

  ---
  Sources used:
  - TECS アロケータ raw 記事 (raw/articles/2026-05-19-imp-allocator.md) (confidence: high) — CDL 記述例・命名規則・リレーアロケータの <= 構文
  - 実装パターン (wiki/concepts/implementation-patterns.md) (confidence: high) — アロケータ呼び口命名規則・C 関数シグニチャ
  - CDL 言語 (wiki/concepts/cdl-language.md) (confidence: high) — send/receive 引数の方向・size_is との組み合わせ・allocator 指定子キーワード
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) — ▼ シンボルと多段リレーモデルの図解記法

  Knowledge gaps:
  - alloc / dealloc 関数の C 言語での実装例（セルタイプコードの書き方）はウィキに記載なし
  - CDL 仕様書でもアロケータは「実装済み・未文書化」として明記されているため、tecsgen ソースコードの確認が推奨されます
