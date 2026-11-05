---
date: 2026-08-16
description: "MCPサーバーの設定方法 — npx/node経由(Stdio)の設定例（GitHub連携・ローカルファイルシステム連携等）"
tags:
  - reference
  - claude-code
  - mcp
---

  #### ① npx / node を使う場合 (Stdio)

  例: GitHub 連携やローカルファイルシステム連携など

    {
      "mcpServers": {
        "github": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-github"],
          "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "github_pat_xxx..."
          }
        },
        "fetch": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-fetch"]
        }
      }
    }

  #### ② Python (uvx / python) を使う場合 (Stdio)

  例: SQLite データベース連携

    {
      "mcpServers": {
        "sqlite": {
          "command": "uvx",
          "args": ["mcp-server-sqlite", "--db-path", "C:/path/to/my_database.db"]
        }
      }
    }

  #### ③ リモートの MCP サーバーに接続する場合 (SSE)

  例: クラウド上の MCP サービスや自作リモートサーバー

    {
      "mcpServers": {
        "my-remote-tool": {
          "serverUrl": "https://mcp.example.com/sse"
        }
      }
    }
    ──────
  ### 4. 設定時のポイント・注意点

  1. 環境変数の保護 (env):
      • GitHub アクセストークンやデータベース接続文字列などの機密情報は、各サーバー設定内の "env" オブジェクトに記述します。
  2. パスの区切り文字 (Windows):
      • Windows 環境でファイルパスを指定する場合は、/ (スラッシュ) を使うか、\\ のようにエスケープしてください。
  3. コマンドの事前確認:
      • npx や uvx / python コマンドがターミナルで実行可能（PATH に通っている）状態であることを確認してください。

  ──────
  ### 5. 反映の確認

  mcp_config.json を保存すると、エージェントは自動的に設定された MCP サーバーから使用可能なツール（Tool）を取得します。
  チャット上で「利用可能な MCP ツールを教えて」と尋ねると、正しく読み込まれているか確認できます。

## Related
- [[Claude-Code-記事索引]]
