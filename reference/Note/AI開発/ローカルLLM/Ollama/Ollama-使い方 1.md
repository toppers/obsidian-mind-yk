---
date: 2026-06-13T00:00:00.000Z
description: "headroom MCPのOllama統合設定メモ — OLLAMA_MODEL/OLLAMA_ENDPOINT環境変数・headroom proxy起動手順"
tags:
  - reference
  - ollama
  - local-llm
  - headroom
---

uv run headroom proxy --port 8787

ykomi:~/repo/svn-toppers-TECS-2/git-svn-trunk-tags/tecscde (main) $ uv pip list --system
Using Python 3.13.11 environment at: /home/ykomi/.local/share/mise/installs/python/3.13.11

OLLAMA_MODEL 
OLLAMA_ENDPOINT

===========================
● OLLAMA_MODEL の使い方まとめ：

  設定方法

  この headroom パッケージ（max CLIツール）はOllamaをLLMプロバイダーとして使う場合、以下の2つの環境変数が両方とも必要です。

  設定ファイルの場所: ~/.config/headroom/.env（ユーザー設定ディレクトリ）

  LLM_PROVIDER=ollama
  OLLAMA_MODEL=llama3
  OLLAMA_ENDPOINT=http://localhost:11434

  初回セットアップ

  初回は対話式セットアップを使う方が簡単です：

  uvx --from headroom max

  起動後、CLIで config と入力するとプロバイダーを選択・再設定できます。

  各プロバイダーの対応環境変数

  ┌──────────────┬────────────────────────────────┐
  │ プロバイダー │            環境変数            │
  ├──────────────┼────────────────────────────────┤
  │ ollama       │ OLLAMA_MODEL + OLLAMA_ENDPOINT │
  ├──────────────┼────────────────────────────────┤
  │ openai       │ OPENAI_API_KEY                 │
  ├──────────────┼────────────────────────────────┤
  │ anthropic    │ ANTHROPIC_API_KEY              │
  ├──────────────┼────────────────────────────────┤
  │ google       │ GOOGLE_API_KEY                 │
  ├──────────────┼────────────────────────────────┤
  │ local_gguf   │ LOCAL_GGUF_MODEL_PATH          │
  └──────────────┴────────────────────────────────┘

  例

  LLM_PROVIDER=ollama
  OLLAMA_MODEL=llama3.2
  OLLAMA_ENDPOINT=http://localhost:11434

  Ollamaが localhost:11434 で動いていれば、その後 uvx --from headroom max で起動できます。
