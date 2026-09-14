---
date: 2026-06-08
description: "TECSの結合（join）の定義・種類（静的/動的/スルー）・CDL組上げ記述の構文（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - cdl
---
● WikiのHUB設定を読み込みます。

  Searched for 1 pattern, read 3 files (ctrl+o to expand)

● 「結合」に関連する記事を特定します。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● 結合に関する詳細を追加で読みます。

  Searched for 2 patterns, read 1 file (ctrl+o to expand)

● 組上げ記述の詳細も確認します。

  Read 1 file (ctrl+o to expand)

● ログに追記して回答を生成します。

  Read 1 file (ctrl+o to expand)

● Update(~\wiki\topics\tecs\log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-08] query | "結合とは何か" → answered from 3 articles (standard)
      4  ## [2026-06-07] query | "TECS仕様書-呼び口とは何か" → answered from 3 articles (standard)
      5  ## [2026-06-07] query | "受け口とは何か" → answered from 3 articles (standard)
      6  ## [2026-06-07] query | "セルタイプとは何か" → answered from 3 articles (standard)

● ---
  TECS における「結合」とは

  **結合（Join）とは、あるセルの呼び口（Call Port）を別のセルの受け口（Entry
  Port）**に接続する操作・その接続関係そのものです。コンポーネント間の通信路を CDL の組上げ記述で宣言的に定義します。

  基本的な結合（静的結合）

  組上げ記述（セル記述）の中で、以下のように記述します：

  cell tMyType MyCell {
      cCall = AnotherCell.eEntry;  // 結合
      myAttr = 42;
  };

  - 左辺: 自セルの呼び口名（cXxx）
  - 右辺: 結合先のセル名とその受け口名（セル名.eXxx）

  ビルド時に固定される静的結合で、tecsgen が呼び口の関数ポインタを受け口の実装関数に解決します。

  呼び口の結合オプション

  ┌──────────┬───────────────────────────────────────────────────┐
  │  指定子  │                       意味                        │
  ├──────────┼───────────────────────────────────────────────────┤
  │ optional │ 未結合でも良い呼び口（NULL チェックが必要になる） │
  ├──────────┼───────────────────────────────────────────────────┤
  │ omit     │ 出力コードから除外                                │
  ├──────────┼───────────────────────────────────────────────────┤
  │ 配列形式 │ cCall[N] — 複数の受け口への結合が可能             │
  └──────────┴───────────────────────────────────────────────────┘

  動的結合（Dynamic Join）

  V1.4.0 で追加された、実行時に結合先を切り替える機能。

  celltype tSwitchable {
      [dynamic]
      call sEntry cDynamic;        // 動的呼び口（初期値なし可）

      [ref_desc]
      call sEntry cDescriptor;     // Descriptor を受け取る呼び口
  };

  セルタイプコード側で操作：

  // 結合先を切り替える
  Descriptor(sEntry) desc = cDescriptor_refer_to_descriptor();
  cDynamic_set_descriptor(desc);

  // 結合を解除する
  cDynamic_unjoin();

  Descriptor(sSignature) 型が受け口への参照（ポインタ相当）を保持します。

  リージョン境界越えの結合

  セルが異なる region（アドレス空間・セキュリティドメイン等）に属する場合、in_through / out_through
  を使って境界越えの結合を実現します。through-cell（プラグインが生成する中継コンポーネント）が自動挿入されます：

  region rNormal {
      cell tUser UserCell {
          cSecure = SecretCell.eSecure; // リージョン境界越えの結合
      };
  };

  ---
  Sources used:
  - CDL 高度機能 (wiki/concepts/advanced-cdl-features.md) (confidence: high) —
  動的結合・Descriptor型・リージョン境界越えの詳細
  - CDL 言語 (wiki/concepts/cdl-language.md) (confidence: high) —
  組上げ記述・結合構文・呼び口指定子（optional/omit/配列）
  - TECS 概要 (wiki/topics/tecs-overview.md) (confidence: high) — 動的結合が V1.4.0 追加機能であることの確認

  Knowledge gaps:
  - 結合が解決される詳細なタイミング（tecsgen の内部処理）については wiki に記載なし
  - optional 呼び口における実行時の NULL チェック方法の具体的コード例なし
