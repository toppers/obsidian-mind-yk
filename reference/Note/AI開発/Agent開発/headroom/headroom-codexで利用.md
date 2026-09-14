---
date: 2026-08-16
description: "`headroom wrap codex` でのCodex連携方法、Docker上の既存プロキシを再利用する場合の設定"
tags:
  - work-note
---

• 結論、推奨は headroom wrap codex です。プロキシ起動、Codex設定、Codex起動をまとめて行いま
  す。

  リポジトリ版を使う場合:
  uv sync --extra proxy
  uv run headroom wrap codex

  グローバルインストールする場合:

  uv tool install --python 3.13 "headroom-ai[all]"
  headroom wrap codex

  wrap codex は以下を自動実行します。

  - ローカルプロキシを 127.0.0.1:8787 で起動
  - C:\Users\ykomi\.codex\config.toml をHeadroom向けに設定
  - Codexをプロキシ経由で起動
  - 初回変更時に config.toml.headroom-backup を作成

  動作確認:

  Invoke-RestMethod http://127.0.0.1:8787/health
  Invoke-RestMethod http://127.0.0.1:8787/stats

  設定を元に戻す場合:

  headroom unwrap codex

  毎回自動設定せず、手動で接続することもできます。

  headroom proxy --port 8787
  $env:OPENAI_BASE_URL = "http://127.0.0.1:8787/v1"
  codex

  ただし、ChatGPTサブスクリプション認証では手動の OPENAI_BASE_URL だけだとプロキシを迂回する場
  合があるため、headroom wrap codex が確実です。なお、headroom mcp serve のMCP登録はプロキシ利
  用とは別機能です。

  根拠: docs/content/docs/proxy.mdx:562、headroom/cli/wrap.py:2656

─ Worked for 12m 48s ─────────────────────────────────────────────────────────────────────────


› すでにDocker Desktopでheadroom をport 8787 で実行している状態ではどうすればよい


• Docker上の既存プロキシを再利用する場合のCodex設定と、認証方式ごとの差分を実装から確認しま
  す。

• Started `/root/docker_codex_config`

• Started `/root/docker_codex_config`

• Waiting for agents

• Finished waiting
  └ No agents completed yet

• Waiting for agents

• Finished waiting
  └ No agents completed yet

• Waiting for agents

• Finished waiting
  └ No agents completed yet

• Docker上のHeadroomをそのまま使う場合は、プロキシを新規起動せずCodexだけ接続します。

  headroom wrap codex --no-proxy --port 8787

  事前確認:

  Invoke-RestMethod http://127.0.0.1:8787/health

  Docker側ではポート公開が必要です。

  8787:8787

  通常の headroom wrap codex --port 8787 でも既存Headroomを検出して再利用しますが、Docker版を
  使う意図が明確な --no-proxy を推奨します。

  Codex実行後の確認:

  Invoke-RestMethod http://127.0.0.1:8787/stats

  stats のリクエスト数や節約量が増えていれば、Codexの通信がDocker上のHeadroomを通っています。

  手動設定する場合は、C:\Users\ykomi\.codex\config.toml に以下が必要です。

  model_provider = "headroom"
  openai_base_url = "http://127.0.0.1:8787/v1"

  [model_providers.headroom]
  name = "Headroom"
  base_url = "http://127.0.0.1:8787/v1"
  supports_websockets = true
  requires_openai_auth = true

  requires_openai_auth = true はChatGPTサブスクリプション認証の場合です。OPENAI_API_KEY を使う
  場合は省略します。設定を自動処理してくれるため、基本的には headroom wrap codex --no-proxy
  --port 8787 だけで十分です。

## Related
- [[headroom-index]]
