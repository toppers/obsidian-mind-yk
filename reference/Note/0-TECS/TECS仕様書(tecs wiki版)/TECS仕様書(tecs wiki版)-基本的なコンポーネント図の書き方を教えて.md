---
date: 2026-06-08
description: "TECSコンポーネント図（TCD）の基本的な書き方。セル矩形・受け口三角・呼び口線分の記法（tecs wiki版）"
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
      3 +## [2026-06-08] query | "基本的なコンポーネント図の書き方" → answered from 1 article (standard)
      4  ## [2026-06-08] query | "TECSコンポーネント図の書き方" → answered from 1 article (standard)
      5  ## [2026-06-08] query | "複合セルとは何か" → answered from 3 articles (standard)
      6  ## [2026-06-08] query | "TECSコンポーネント図とは何か" → answered from 2 articles (standard)

● ---
  基本的なコンポーネント図（TCD）の書き方（tecs wiki より）

  TCD は CDL の組上げ記述（属性値を除く）と1対1に対応します。CDL が書ければ図に変換でき、図が読めれば CDL に変換できます。

  ---
  配置の原則（まず決める）

  ▎ 上位レイヤ（アプリケーション）を上または左、下位レイヤ（デバイスドライバ・OS カーネル）を下または右に配置する。

  ---
  基本の4要素

  1. セル（コンポーネントインスタンス）

  ┌──────────────────┐
  │  tCelltypeName   │  ← セルタイプ名
  │  InstanceName    │  ← インスタンス名
  └──────────────────┘
  矩形で描きます。内部にセルタイプ名とインスタンス名を記載します。

  2. 受け口（提供するポート）

  矩形辺に内向きの塗りつぶし三角形を付け、ポート名を添えます。

  ▎ CDL: entry sSignature ePortName;

  3. 呼び口（要求するポート）

  矩形から線分を伸ばし、ポート名を添えます。

  ▎ CDL: call sSignature cPortName;

  4. 接続線

  呼び口から受け口へ線を引きます。線の上にシグニチャ名を記載します。

  ▎ CDL: cPortName = OtherCell.ePortName;

  ---
  最小限の図の例

  アプリ側（上）              ドライバ側（下）
  ┌──────────┐               ┌──────────────┐
  │  tApp    │               │   tDriver    │
  │  MyApp   │               │   HW         │
  │          │──[cDrv]──►◀──[eDrv]          │
  └──────────┘               └──────────────┘
           シグニチャ名

  - MyApp の呼び口 cDrv が HW の受け口 eDrv に接続

  対応する CDL：
  cell tApp MyApp {
      cDrv = HW.eDrv;
  };
  cell tDriver HW { };

  ---
  アクティブセル（タスク等）の識別

  タスクやハンドラ等、受け口が呼ばれなくても動作するセルは矩形を二重線で描きます。

  ▎ CDL: [active] celltype tMyTask { ... };

  ---
  合流（多対一接続）

  複数の呼び口を1つの受け口につなぐことができます。接続線が1点に集まる形で描きます（逆の「1つの呼び口が複数の受け口」は不可）。

  ---
  Sources used:
  - TCD 記法 (wiki/topics/tcd-notation.md) (confidence: high) —
  基本要素（セル・受け口・呼び口・接続線）の定義・描画原則・アクティブセルの二重線表記・合流のルール・CDL との対応表

  Knowledge gaps:
  - 実際の描画ツール（どのソフトウェアで TCD を描くか）は wiki に記載なし
  - 図の具体的なサンプル画像は収録なし（テキスト記述のみ）
