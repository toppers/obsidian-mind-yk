---
date: 2026-06-08
description: "TECSのコンテキスト（タスク/非タスク）。シグニチャ接頭文字（s/si）との対応とITRON OSでの適用（tecs-0 wiki版）"
tags:
  - tecs
  - reference
  - tecs-0-wiki
  - cdl
---
● tecs-0 wiki のインデックスは確認済み（5記事一致）。コンテキストに関連する記事を検索します。

  Searched for 2 patterns (ctrl+o to expand)

● 追加で context キーワード全体を検索します。

  Searched for 2 patterns (ctrl+o to expand)

● Update(~\wiki\topics\tecs-0\log.md)
  ⎿  Added 1 line
      1  # tecs-0 Wiki Log
      2
      3 +## [2026-06-08] query | "コンテキストとは何か" → partial answer from 1 article (standard; limited coverage)
      4  ## [2026-06-08] query | "受け口配列とは何か" → answered from 3 articles (standard)
      5  ## [2026-06-08] query | "呼び口配列とは何か" → answered from 2 articles (standard)
      6  ## [2026-06-08] query | "結合とは何か" → answered from 1 article (standard)

● tecs-0 wiki では「コンテキスト」の扱いが非常に限定的です。正直にお伝えします。

  ---
  「コンテキスト」についての tecs-0 wiki の記載

  tecs-0 wiki には、コンテキストについての独立した説明はありません。唯一の言及は CDL言語仕様
  の命名規則テーブルの中にある以下の1行のみです：

  ┌────────────────────────────────────┬──────────┬──────┐
  │                要素                │ 接頭文字 │ 備考 │
  ├────────────────────────────────────┼──────────┼──────┤
  │ シグニチャ（非タスクコンテキスト） │ si       │      │
  └────────────────────────────────────┴──────────┴──────┘

  つまり、「非タスクコンテキスト向けのシグニチャには si 接頭文字を使う」という命名規則として言及されているにとどまります。

  「タスクコンテキストとは何か」「非タスクコンテキストとは何か」「なぜ区別するか」「[context(...)]
  指定子の意味と使い方」といった概念的な説明は tecs-0 wiki には記載されていません。

  ---
  Sources used:
  - CDL言語仕様 (wiki/concepts/cdl-language-spec.md) (confidence: high) — si
  接頭文字が非タスクコンテキスト向けシグニチャを示すという命名規則の記載のみ

  Related in other wikis:
  - tecs wiki: CDL シグニチャ記述例 (wiki/references/cdl-signature-examples.md) — [context("non-task")] 指定子の構文と意味を詳細に解説
  - tecs wiki: ASP3 カーネルオブジェクト (wiki/topics/asp3-kernel-objects.md) — タスク/非タスクコンテキストの実際の使い分け（eXxx /
  eiXxx 二種類の受け口）
  - tecs wiki: CDL 命名規則 (wiki/references/cdl-naming-conventions.md) — s / si / sn 接頭文字の体系的な説明

  Knowledge gaps:
  - tecs-0 wiki にはコンテキストの概念説明がない。/wiki:ingest でコンテキストを解説した仕様書章を追加するか、tecs wiki
  の情報を参照してください
