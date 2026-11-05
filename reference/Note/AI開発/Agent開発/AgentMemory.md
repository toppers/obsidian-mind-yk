---
date: 2026-08-29
description: "agentmemory を Docker Compose（iii-engine）+ npx ワーカーで起動する手順控え — ポート一覧・Claude Code接続コマンド・v0.11.2固定の注意点"
tags:
  - reference
  - tool
  - agentmemory
  - mcp
---

- ● 構成が分かりました。Docker
  Composeはiii-engine（バックエンドランタイム）を動かすもので、agentmemoryのワーカー（Node.js）は別プロセスとして接続します。
  ---
  構成の全体像

  [Claude Code] → MCP → [agentmemory npm プロセス] → ws://localhost:49134 → [iii-engine in Docker]
                           REST :3111
  ---
  - 手順
  1. iii-engine を Docker Compose で起動
  cd E:\Crepo\github-ai\agentmemory
  docker compose up -d
  - 起動確認：
  docker compose ps
  - iii-init が Exited (0)、iii-engine が running であればOK
  1. .env を作成（必要に応じて）
  Copy-Item .env.example .env
  エディタで .env を開き、必要なキーを設定
  最小構成ではキー不要（BM25 + ローカル埋め込みで動作）

  2. agentmemory を起動（iii-engine に接続）
  
  # Docker上のiii-engineに接続するよう環境変数を指定
  $env:III_ENGINE_URL = "ws://localhost:49134"
  npx -y @agentmemory/agentmemory@latest

  別ターミナルで：

  curl http://localhost:3111/agentmemory/livez
  # → 200 が返れば起動成功

  3. Claude Code に接続

  npx -y @agentmemory/agentmemory@latest connect claude-code

  ---
  ポート一覧
│ ポート │                    用途                    │
│ 49134  │ iii-engine WebSocket（agentmemory が接続） │
│ 3111   │ REST API / MCP                             │
│ 3112   │ Streams                                    │
│ 3113   │ Viewer（ブラウザで記憶を確認）             │

  ---
  注意点

  - iii-engine バージョンは v0.11.2 固定（docker-compose.yml コメント参照）。v0.11.6以降は非互換のため変更しないこと。
  - Windows のネイティブ環境では agentmemory connect が非対応。MCP 設定は手動で ~/.claude/settings.json に追記が必要。
  - Viewer は http://localhost:3113 で記憶の状態を確認できます。

✻ Sautéed for 2m 33s

※ recap: agentmemoryをDocker Composeで動かす方法を説明した。iii-engineをdocker compose
  upで起動し、agentmemoryをnpxで別プロセスとして接続する構成。次はdocker compose upを実行して動作確認する。 (disable recaps in /config)

## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]
