---
date: 2026-07-23
description: "Antigravity（IDE/エージェント）でMCPサーバーを設定・利用する方法 — UI管理画面とmcp_config.json編集の2手法、Stdio/SSE接続例"
tags:
  - reference
  - mcp
  - antigravity
---

  Antigravityでは、主に**UI（設定画面やスラッシュコマンド）**を使用する方法と、**JSON設定ファイル（mcp_config.json）*
  *を編集する方法の2つが用意されています。
  ──────
  ### 1. UI（管理画面）から設定する（推奨）

  Antigravity 2.0 アプリケーションや Antigravity IDE
  をお使いの場合は、手動でファイルを編集することなく、画面上でMCPサーバーを追加・管理できます。

  • サイドバーから開く:
  左側のメニューから Skills & Customizations（スキルとカスタマイズ）を選択し、Manage MCP Servers をクリックします。
  • スラッシュコマンドを使う:
  チャットの入力欄に /mcp と入力して実行すると、インタラクティブな MCP マネージャーがオーバーレイ表示されます。
  • 追加方法:
  MCP Store から提供されている公式のサーバーを選択してインストールするか、Add MCP
  ボタンからカスタムMCPサーバーのURLや実行コマンドを追加できます。
  ──────
  ### 2. 設定ファイル（JSON）で設定する

  プロジェクトごとに設定を分けたい場合や、設定ファイルをGitで管理したい場合は、mcp_config.json を直接編集します。

  #### 設定ファイルの配置場所

  設定ファイルはグローバルとワークスペース（プロジェクト）ローカルの2つのレベルで配置できます。

  • グローバル設定（システム全体で共有）:
      • Windowsの場合: mcp_config.json
  • ローカル設定（特定のプロジェクトのみ適用）:
      • 現在のワークスペース（notebooklm_cli_x）の場合: mcp_config.json


  #### 設定ファイルの記述例 (mcp_config.json)

  以下のように mcpServers オブジェクト配下にサーバー定義を記述します。

  ##### ① ローカルプロセス起動型 (Stdio) の場合（例: npmやuvxで動作するサーバー）

    {
      "mcpServers": {
        "sqlite-explorer": {
          "command": "npx",
          "args": [
            "-y",
            "@modelcontextprotocol/server-sqlite",
            "--dbPath",
            "E:/Ccur/python3/notebooklm_cli_x/db.sqlite"
          ],
          "env": {
            "DB_PATH": "E:/Ccur/python3/notebooklm_cli_x/db.sqlite"
          }
        }
      }
    }

  ##### ② リモート接続型 (SSE) の場合（例: 既に起動しているWebサービスに接続）

    {
      "mcpServers": {
        "my-remote-service": {
          "serverUrl": "https://mcp.example.com/sse"
        }
      }
    }
    ──────
  ### 3. MCPサーバーの使い方

  設定が完了すると、Antigravity（エージェント）は自動的にMCPサーバーの提供するツールやリソースを認識します。

  1. 自動連携:
  エージェントが「データベースを調べる必要がある」「Webで調べる必要がある」などと判断した際、適切なMCPサーバーが設定
  されていれば、エージェント自身が必要なMCPツールを自律的に呼び出します。
  2. 手動メンション（@記法）:
  チャット入力欄で @
  を入力すると、メンションメニューが開き、アクティブなMCPサーバーやツールを明示的に指定して会話のコンテキストに追加す
  ることができます（例: @sqlite-explorer）。

  │ [!IMPORTANT]
  │ 外部のコマンド実行やネットワーク接続を伴うMCPサーバーを追加した場合、セキュリティポリシー（Tool Execution
  │ Policy）に基づいて実行のたび、または初回起動時にユーザーの実行承認が求められます。承認して進めてください。

## Related

- [[agy-mcp定義]] — CLI 側（`~/.gemini/settings.json` の `mcpServers`）での定義。IDE 側の `mcp_config.json` とは別系統
- [[MCP-LIST|MCP-LIST]] — 他のMCPサーバー候補一覧
- [[brain/Skills]] — 併用する Claude Code スキル/コマンド一覧
