---
date: 2026-07-07
description: "cloudflare-api MCP のエラー原因調査 — MCP 登録はあるが Cloudflare 側が要求する OAuth Bearer token が Codex 実行時に渡っていない"
tags:
  - reference
  - codex
  - mcp
  - troubleshooting
---

• 原因は、cloudflare-api の MCP 登録はあるものの、Cloudflare MCP 側が要求する OAuth Bearer token が現在の Codex 実行時に
  渡っていないためです。

  確認結果です。

  - codex mcp get cloudflare-api は成功し、登録は有効です。
  - 登録内容は streamable_http / https://mcp.cloudflare.com/mcp です。
  - C:\Users\ykomi\.codex\config.toml には URL だけがあり、明示的な bearer token 設定はありません。
  - 直接 GET https://mcp.cloudflare.com/mcp すると Cloudflare は 401 Unauthorized を返し、本文は Missing or invalid
    access token でした。

  - OAuth protected resource metadata は 200 OK で返るため、DNS や endpoint 不達ではありません。

  つまり MCP client for cloudflare-api failed to start は、ローカル実行ファイルの起動失敗ではなく、remote MCP の初期化時
  に認証が通らず、Codex 側が MCP client start failure として表示したものです。

  対処は再ログインです。

  rtk codex mcp login cloudflare-api

  それでも失敗する場合は、保存済み OAuth 状態が壊れている可能性があるため、cloudflare-api を一度 remove して再登録、再ロ
  グインするのが次の確認点です。
===
• UserPromptSubmit hook (failed)
  error: hook exited with code 1

• 指定コマンドをそのまま実行して、認証フローの結果を確認します。ブラウザ連携や外部 OAuth が必要な場合は、承認待ちになる
  可能性があります。

✔ You approved codex to always run commands that start with rtk codex mcp login

• Ran rtk codex mcp login cloudflare-api
  └ Authorize `cloudflare-api` by opening this URL in your browser:
    … +1 lines (ctrl + t to view transcript)

    Successfully logged in to MCP server 'cloudflare-api'.

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• cloudflare-api の MCP ログインは成功しました。

  実行結果:

  Successfully logged in to MCP server 'cloudflare-api'.

  これで先ほどの Missing or invalid access token による起動失敗は解消しているはずです。次回 Codex 起動時、または MCP 再
  初期化時に cloudflare-api が認証済みで使われます。

• Stop hook (failed)
  error: hook exited with code 1
