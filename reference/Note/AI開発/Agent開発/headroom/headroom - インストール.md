---
date: 2026-06-18
description: "headroom のインストールで詰まった点 — headroom wrap claude は TTY 必須で、エージェント内のサブシェルから直接起動できない"
tags:
  - reference
  - agent
  - headroom
  - troubleshooting
---

● headroom が起動しましたが、--print モードで stdin/promptが不足しているエラーです。これは headroom wrap claude
  がインタラクティブモード（TTY）で実行される必要があるためです。エージェント内のサブシェルから直接起動することはできません。

  状況まとめ:
  - headroom は正常に動作 (プロキシはポート 8787 で稼働中)
  - wrap claude はインタラクティブな TTY セッションが必要
  - MCP 設定の更新が必要: 現在の設定と異なるパスが検出された

  推奨する対処:
  1. 端末（PowerShell/Terminal）で直接実行してください:
  uv tool run --python 3.13 --from "headroom-ai[all]" headroom wrap claude
  2. MCP 設定を最新化したい場合:
  headroom mcp install --proxy-url http://127.0.0.1:8787 --force

  端末から手動実行が必要です。
