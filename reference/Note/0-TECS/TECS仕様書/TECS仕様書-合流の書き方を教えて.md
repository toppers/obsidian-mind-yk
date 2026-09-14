---
date: 2026-06-08
description: "TECSの合流（Convergence）の概念と書き方。複数呼び口→1受け口の多対一結合（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - tcd
---
● tecs-0 wiki のインデックスは確認済み（5記事一致）。合流に関連するコンテンツを検索します。

  Searched for 1 pattern (ctrl+o to expand)

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "合流の書き方" → concept only, no diagram notation (standard)
      4  ## [2026-06-08] query | "基本的なコンポーネント図の書き方" → no coverage in this wiki (standard)
      5  ## [2026-06-08] query | "TECSコンポーネント図の書き方" → no coverage in this wiki (standard)
      6  ## [2026-06-08] query | "TECSコンポーネント図とは何か" → partial answer from 1 article (standard; limited coverage)

● ---
  「合流の書き方」について（tecs-0 wiki より）

  tecs-0 wiki には合流の概念定義は存在しますが、図としての書き方（描画方法）は記載されていません。

  tecs-0 wiki の定義

  ▎ 合流: 複数の呼び口が1つの受け口に結合（多対一）。逆の分流は不可。

  つまり：
  - 合流（多対一）: 複数のセルの呼び口 → 1つの受け口、これは可能
  - 分流（一対多）: 1つの呼び口 → 複数の受け口、これは不可

  CDL での記述（合流の実現方法）

  合流は組上げ記述で複数のセルが同じ受け口を結合先に指定することで実現します：

  cell tCellA CellA {
      cService = SharedServer.eService;   # 合流: CellA から
  };
  cell tCellB CellB {
      cService = SharedServer.eService;   # 合流: CellB も同じ受け口へ
  };

  ---
  Sources used:
  - TECSコンポーネントモデル (wiki/concepts/tecs-component-model.md) (confidence: high) —
  合流の概念定義「複数の呼び口が1つの受け口に結合（多対一）。逆の分流は不可。」

  Related in other wikis:
  - tecs wiki: TCD 記法 (wiki/topics/tcd-notation.md) —
  合流の図としての書き方を記載。「合流点は3本の線が集まる形。4本の線が交わる場合は別々の接続の交差（合流ではない）」という区別も含む

  Knowledge gaps:
  - tecs-0 wiki には合流の TCD 記法（図の描き方）が存在しない。詳細は tecs wiki を参照してください
