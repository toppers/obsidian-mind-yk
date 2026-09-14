---
date: 2026-06-08
description: "TECSの合流（Convergence）の概念と書き方。TCD3本線表記・CDL組上げ記述（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - tcd
---
● 今セッションで tcd-notation.md を全文読み済みです。ログ更新して回答します。

● Update(~\wiki\topics\tecs\log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-08] query | "合流の書き方" → answered from 1 article (standard)
      4  ## [2026-06-08] query | "基本的なコンポーネント図の書き方" → answered from 1 article (standard)
      5  ## [2026-06-08] query | "TECSコンポーネント図の書き方" → answered from 1 article (standard)
      6  ## [2026-06-08] query | "複合セルとは何か" → answered from 3 articles (standard)

● ---
  TCD における「合流」の書き方（tecs wiki より）

  ルール

  **合流（Convergence）**とは、複数の呼び口が1つの受け口に接続される接続形態です。

  - 可能: 複数の呼び口 → 1つの受け口（多対一）
  - 不可: 1つの呼び口 → 複数の受け口（分流）

  描き方

  合流点は3本の線が1点に集まる形で描きます：

  CellA.cService ─────┐
                      ├──► SharedServer.eService
  CellB.cService ─────┘

  交差との区別（重要）

  ▎ 4本の線が交わる場合は別々の接続の交差（合流ではない）。

            ─────×─────   ← 4本の線が交わる点は「交差」（合流ではない）
                 │

  合流は必ず3本が集まる形です。図上で線が4本交差している箇所は「たまたま線が重なっているだけ」であり、合流とは別物です。

  対応する CDL

  合流は CDL では複数のセルが同じ受け口を指定することで実現します：

  cell tCellA CellA {
      cService = SharedServer.eService;
  };
  cell tCellB CellB {
      cService = SharedServer.eService;   // 同じ受け口を指定 = 合流
  };

  ---
  Sources used:
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) — 合流の定義・「合流点は3本の線が集まる形」・4本交差との区別ルール

  Knowledge gaps:
  - 合流の最大接続数（2つ以上なら何個でも可能か）についての明示的な記述なし
