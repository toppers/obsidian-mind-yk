---
date: 2026-06-16T00:00:00.000Z
description: "Ollamaのインストール・モデルダウンロード・環境変数設定手順 — OpenAI互換API経由でローカルLLMを利用する設定メモ"
tags:
  - reference
  - ollama
  - local-llm
  - setup
---

# Ollama設定手順

## 1. インストール＆モデルダウンロード

```bash
# ollama公式サイトからインストール後
ollama pull qwen2.5-coder:32b    # コード生成向け
ollama pull llama3.1:8b           # 軽量モデル
ollama pull deepseek-r1:32b       # 推論特化
```

## 2. サーバー起動

```bash
ollama serve   # デフォルトで http://localhost:11434
```

## 3. 環境変数設定（PowerShell）

```powershell
$env:OPENAI_BASE_URL = "http://localhost:11434/v1"
$env:OPENAI_API_KEY = "ollama"
```

## 4. .envファイルに保存（永続化）

```
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
```

## 5. モデル指定（必要に応じて）

```powershell
$env:OPENAI_MODEL = "qwen2.5-coder:32b"
```

## 推奨モデル（コード機能重視）

| モデル | サイズ |
|--------|--------|
| qwen2.5-coder:32b | 32B |
| deepseek-r1:32b | 32B |
| llama3.1:8b | 8B |
| phi4:14b | 14B |

## 注意事項

- 16GB VRAMなら32Bモデルが動作可能
- 8GB VRAM以下は8Bモデル推奨
- OllamaのAPIエンドポイントは `/v1`（OpenAI互換）を使う
- 設定完了後、MiCode起動で自動的にローカルLLMが使用される

## 関連

- [[_ローカルLLM-まとめ]]
- [[Ollama-使い方]]
