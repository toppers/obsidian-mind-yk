---
date: 2026-05-14
description: "nvk/llm-wiki プラグインの導入記録 — GitHub リポジトリをマーケットプレイスとして追加してからインストールする手順"
tags:
  - reference
  - llm-wiki
  - obsidian
  - plugin
---

nvk/llm-wiki

● まずGitHubリポジトリをマーケットプレイスとして追加してからインストールします。

● Bash(claude plugin marketplace add nvk/llm-wiki 2>&1)
  ⎿  Adding marketplace…Cloning via SSH: git@github.com:nvk/llm-wiki.git
     Refreshing marketplace cache (timeout: 120s)…
     Cloning repository (timeout: 120s): git@github.com:nvk/llm-wiki.git
     … +3 lines (ctrl+o to expand)

● Bash(claude plugin install wiki@llm-wiki 2>&1)
  ⎿  Installing plugin "wiki@llm-wiki"...✔ Successfully installed plugin: wiki@llm-wiki (scope: user)

● インストール完了です。

  マーケットプレイス nvk/llm-wiki を追加し、wiki プラグインをユーザースコープでインストールしました。Claude
  Codeを再起動すると /wiki: コマンド群が有効になります。

  主なコマンド:
  - /wiki:init — wikiの初期化
  - /wiki:research — LLMによる調査・記事生成
  - /wiki:ingest — URLやファイルをソースとして取り込み
  - /wiki:query — wiki内を検索・質問

✻ Brewed for 2m 2s

