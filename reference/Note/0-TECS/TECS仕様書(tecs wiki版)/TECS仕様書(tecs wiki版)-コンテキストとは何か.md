---
date: 2026-06-08
description: "TECSのコンテキスト（タスク/非タスク）。シグニチャ接頭文字（s/si）との対応とITRON OSでの適用（tecs wiki版）"
tags:
  - tecs
  - reference
  - tecs-wiki
  - cdl
---
 tecs wiki のインデックスは確認済み（16記事一致）。コンテキストに関連する記事を検索します。

  Searched for 1 pattern, read 1 file (ctrl+o to expand)

● シグニチャ記述例の context 節全体と、命名規則の si 接頭文字部分を読みます。

  Read 2 files (ctrl+o to expand)

● Update(~\wiki\topics\tecs\log.md)
  ⎿  Added 1 line
      1  # Wiki Activity Log
      2
      3 +## [2026-06-08] query | "コンテキストとは何か" → answered from 4 articles (standard)
      4  ## [2026-06-08] query | "受け口配列とは何か" → answered from 3 articles (standard)
      5  ## [2026-06-08] query | "結合とは何か" → answered from 3 articles (standard)
      6  ## [2026-06-07] query | "TECS仕様書-呼び口とは何か" → answered from 3 articles (standard)

● ---
  TECS における「コンテキスト」とは（tecs wiki より）

  TECSにおけるコンテキスト（context）とは、受け口（関数）が呼び出される実行環境の種別を指します。主に「タスクコンテキスト」と「非タスク
  コンテキスト」の2種類があります。

  2種類のコンテキスト

  ┌──────────────────────┬───────────────────────────┬─────────────────────────────────────────────────────┐
  │     コンテキスト     │        呼び出し元         │                        特徴                         │
  ├──────────────────────┼───────────────────────────┼─────────────────────────────────────────────────────┤
  │ タスクコンテキスト   │ 通常のタスク処理中        │ 待ちを伴う操作が可能                                │
  ├──────────────────────┼───────────────────────────┼─────────────────────────────────────────────────────┤
  │ 非タスクコンテキスト │ 割り込みハンドラ (ISR) 等 │ 待ちを伴わない操作のみ可能（ポーリング・signal 等） │
  └──────────────────────┴───────────────────────────┴─────────────────────────────────────────────────────┘

  CDL での表現：context 指定子

  シグニチャに [context("...")] 指定子を付けることで、そのシグニチャが想定する実行コンテキストを設計ドキュメントとして宣言できます：

  [context("non-task")] signature siISRService {
      ER  notifyFromISR( [in] uint32_t event );
  };

  指定できる値: "task" | "non-task" | "any"

  ▎ 注意: この指定子はあくまで設計ドキュメント用であり、tecsgen によるコンパイル時チェックには使用されません。

  命名規則との対応

  コンテキストはシグニチャの接頭文字規則にも反映されています：

  ┌──────────┬──────────────────────┬─────────────────────┐
  │ 接頭文字 │     コンテキスト     │         例          │
  ├──────────┼──────────────────────┼─────────────────────┤
  │ s        │ タスクコンテキスト   │ sTask, sSemaphore   │
  ├──────────┼──────────────────────┼─────────────────────┤
  │ si       │ 非タスクコンテキスト │ siTask, siSemaphore │
  ├──────────┼──────────────────────┼─────────────────────┤
  │ sn       │ カーネル外           │ snInit              │
  └──────────┴──────────────────────┴─────────────────────┘

  ASP3+TECS における実例

  すべてのカーネルオブジェクトは2種類の受け口を持ちます：

  - eXxx（s-プレフィックスのシグニチャ）— タスクコンテキスト用。待ちを伴う全操作が可能
  - eiXxx（si-プレフィックスのシグニチャ）— 非タスクコンテキスト用（ei プレフィックスの受け口）。待ちを伴わない操作のみ

  例：
  - siTask（非タスクコンテキスト）: activate / wakeUp / cancelWakeUp のみ
  - siSemaphore（非タスクコンテキスト）: signal のみ
  - siEventflag（非タスクコンテキスト）: set のみ

  ---
  Sources used:
  - CDL シグニチャ記述例 (wiki/references/cdl-signature-examples.md) (confidence: high) — context 指定子の CDL 構文と si
  接頭文字との組み合わせ例
  - CDL 言語 (wiki/concepts/cdl-language.md) (confidence: high) — context("task"|"non-task"|"any") が設計ドキュメント用であることの明記
  - CDL 命名規則 (wiki/references/cdl-naming-conventions.md) (confidence: high) — s / si / sn 接頭文字の定義
  - ASP3 カーネルオブジェクト (wiki/topics/asp3-kernel-objects.md) (confidence: high) —
  タスク/非タスクコンテキストの実際の使い分け（eXxx / eiXxx）

  Knowledge gaps:
  - context 指定子が実際に tecsgen でどの程度チェックされるか（コンパイルエラーになるのか単なる注釈なのか）の詳細は wiki に記載なし
  - ATK2（AUTOSAR OS）における OSEK割り込みコンテキストとの対応関係は記載なし
