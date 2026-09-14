---
date: 2026-06-12T00:00:00.000Z
description: "TECSウィキ（tecs ReadTheDocs版）クエリ回答 — 多段リレーモデルの書き方"
tags:
  - reference
  - tecs
  - wiki-query
---

● 多段リレーモデル関連を検索します。

  Searched for 4 patterns, read 2 files (ctrl+o to expand)

● 実装パターン記事の多段リレー関連も確認します。

  Searched for 2 patterns (ctrl+o to expand)

● Update(C:/Users/ykomi/wiki/topics/tecs/log.md)
  ⎿  Added 1 line
      2
      3  ## [2026-06-12] query | "RPCの書き方を教えて" → partial answer — RPC plugins undocumented, framework + CDL through 構文のみ (standard)
      4  ## [2026-06-12] query | "アロケータの書き方を教えて" → answered from 4 wiki articles + 1 raw (standard)
      5 +## [2026-06-12] query | "多段リレーモデルの書き方を教えて" → partial answer — TCD 概念記述 + リレーアロケータ CDL 例のみ (standard)
      6
      7  ## [2026-06-11] query | "RPCの書き方を教えて" → partial answer — RPC plugins all undocumented, framework only (standard)
      8  ## [2026-06-11] query | "複合セルの書き方を教えて" → answered from 3 articles + 1 raw (standard)

● ---
  TECS における多段リレーモデルの書き方

  1. 多段リレーモデルとは

  メモリ領域が受け口で確保・受け取られ、その後呼び口への send
  引数として渡されるモデルです。中継コンポーネント（スルーコンポーネント）がデータを次へ転送する構成で、各段のアロケータを tecsgen が自動生成します。

  [受信元] ─ receive ─▶ [中継セル] ─ send ─▶ [送信先]
                           ↑
                     アロケータをリレー（<=）

  ---
  2. CDL の組上げ記述での指定ルール

  ┌────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │       ルール       │                                                   内容                                                   │
  ├────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ アロケータ指定箇所 │ 最右辺の受け口（最終送り先側）で [allocator(...)] を指定する                                             │
  ├────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ 自動生成           │ tecsgen が送り元・受け元それぞれの send / receive パラメータに対応するアロケータ呼び口を内部的に生成する │
  └────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ---
  3. リレーアロケータの書き方（CDL）

  中継コンポーネントのセルタイプ定義で <= 演算子を使い、受け口アロケータを呼び口アロケータへ転送します。

  // セルタイプ定義 — リレーアロケータの宣言
  celltype tThroughComponent {
      [allocator(
          snd.buf <= cSR.snd.buf,   // 受け口 → 呼び口へリレー
          rcv.buf <= cSR.rcv.buf
      )]
      entry  sSendRecv eS;
      call   sSendRecv cSR;
  };

  セル定義（組上げ記述）側では allocator 指定不要です。<= が「受け口のアロケータを呼び口のアロケータへ転送」を意味します。

  ---
  4. 実装パターンの別記法

  呼び口が受け取った receive 引数をさらに別の呼び口に渡す場合：

  entry sBuffer eInput {
      cOutput.receive_pData <= eInput.receive_pData;  // アロケータのリレー
  };

  ---
  5. TCD 図での表記

  - CDL の組上げ記述では最右辺の受け口でアロケータ（▼ シンボル）を指定
  - tecsgen が各段の send / receive パラメータに対応するアロケータ呼び口を内部的に生成するため、中間の段には ▼ を描かない

  ---
  Sources used:
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) — 多段リレーモデルの概念・CDL 指定ルール（最右辺受け口）・TCD 図の描き方
  - 実装パターン (wiki/concepts/implementation-patterns.md) (confidence: high) — <= 演算子によるリレーアロケータの別記法
  - raw: TECS アロケータ (raw/articles/2026-05-19-imp-allocator.md) (confidence: high) — リレーアロケータの完全な CDL 例（tThroughComponent パターン）
  - raw: TCD リファレンス (raw/articles/2026-05-06-tecs-component-diagram.md) (confidence: medium) — 多段リレーモデルの元ドキュメント記述

  Knowledge gaps:
  - 3段以上の多段構成での具体的な CDL 例がウィキにありません
  - send + receive が混在する場合（双方向転送）の記述例が不足しています
  - 多段リレーモデルの仕様書レベルの定義は tecs-0 ウィキ（第2章・第3章）にある可能性があります — /wiki:query --wiki tecs-0 多段リレー
  で確認を推奨します
