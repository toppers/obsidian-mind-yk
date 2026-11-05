---
date: 2026-10-09
description: "Codex CLI の `codex --help` 出力の整理 — サブコマンド一覧とグローバルオプション(承認・サンドボックス・リモート・worktree等)"
tags:
  - reference
  - codex
  - cli
---

# Codex CLI ヘルプ(`codex --help`)

> 関連: [[mcp]] / [[AGENTS.md]] / [[skills-category]]

書式: `codex [OPTIONS] [PROMPT]` または `codex [OPTIONS] <COMMAND> [ARGS]`。サブコマンドを省くと、オプションは対話 CLI に渡される(2026-10-14 の出力の冒頭に表示された説明)。取得日 2026-10-09、再取得 2026-10-14(サブコマンド24個とオプションに差は無かった。バージョンは `codex --version` で確認、未記録)。

## サブコマンド

| コマンド | 内容 |
|---|---|
| `agents` | 共有ローカル app-server デーモン上の全エージェントセッションを閲覧 |
| `exec` (`e`) | 非対話で実行 |
| `review` | 非対話でコードレビュー |
| `login` / `logout` | 認証の管理 / 保存済み認証情報の削除 |
| `mcp` | 外部 MCP サーバの管理 |
| `plugin` | Codex プラグインの管理 |
| `app-server` | [実験的] app server と関連ツールの実行 |
| `remote-control` | [実験的] リモートコントロール有効で app-server デーモンを管理 |
| `app` | デスクトップアプリを起動(未導入ならインストーラを開く) |
| `completion` | シェル補完スクリプトの生成 |
| `update` | 最新版へ更新 |
| `doctor` | インストール・設定・認証・実行環境の診断 |
| `sandbox` | Codex 提供のサンドボックス内でコマンド実行 |
| `debug` | デバッグツール |
| `apply` (`a`) | Codex エージェントが出した最新の diff を `git apply` で作業ツリーへ適用 |
| `resume` | 過去の対話セッションを再開(既定はピッカー、`--last` で直近) |
| `queue` | 既存セッションへメッセージをキュー投入 |
| `archive` / `unarchive` | 保存済みセッションのアーカイブ / 復元(ID または名前) |
| `delete` | 保存済みセッションを完全削除 |
| `migrate-rollouts` | 旧ローカルセッションをページ分割スレッド履歴へ検査・移行 |
| `fork` | 過去の対話セッションを分岐(`--last` で直近) |
| `cloud` | [実験的] Codex Cloud のタスクを閲覧し、変更をローカルへ適用 |
| `exec-server` | [実験的] スタンドアロンの exec-server サービスを実行 |
| `features` | 機能フラグの確認 |
| `help` | ヘルプ表示 |

## 主なオプション

| オプション | 内容 |
|---|---|
| `-c, --config <key=value>` | `~/.codex/config.toml` の値を上書き。ドット区切りで入れ子指定、値は TOML として解釈(失敗時は文字列) |
| `--enable` / `--disable <FEATURE>` | 機能フラグの有効化 / 無効化(`-c features.<name>=true/false` と同等、繰り返し可) |
| `--remote <ADDR>` | TUI をリモート app server に接続(`ws://host:port`、`wss://host:port`、`unix://[PATH]`) |
| `--remote-auth-token-env <ENV_VAR>` | リモート websocket に送る Bearer トークンを入れた環境変数名 |
| `--strict-config` | config.toml に未知のフィールドがあればエラー |
| `-i, --image <FILE>...` | 初回プロンプトへ画像を添付 |
| `-m, --model <MODEL>` | 使用モデル |
| `--oss` / `--local-provider <lmstudio\|ollama>` | オープンソースプロバイダ / ローカルプロバイダの指定 |
| `-p, --profile <NAME>` | `$CODEX_HOME/<name>.config.toml` をユーザ設定の上に重ねる |
| `-s, --sandbox <MODE>` | `read-only` / `workspace-write` / `danger-full-access` |
| `-a, --ask-for-approval <POLICY>` | `on-request`(モデルが判断)/ `never`(確認なし、失敗は即モデルへ返す) |
| `--approve-for-me` | 承認要求を workspace-write サンドボックスの自動レビューへ回す |
| `--dangerously-bypass-approvals-and-sandbox` | 確認・サンドボックスを全て省略。外部でサンドボックス済みの環境専用 |
| `--dangerously-bypass-hook-trust` | 永続化されたフック信頼なしで有効フックを実行。フック元を検証済みの自動化専用 |
| `-C, --cd <DIR>` | 作業ルートを指定 |
| `--worktree` | 新しい管理 Git worktree 内でセッション実行 |
| `--add-dir <DIR>` | 主ワークスペースと並んで書き込み可にする追加ディレクトリ |
| `--search` | ライブ Web 検索(Responses の `web_search`)を有効化。呼び出しごとの承認なし |
| `--no-alt-screen` | 代替スクリーンを使わず、スクロールバックを保持するインライン表示 |
| `--no-daemon` | 共有バックグラウンドサーバを使わず実行 |
| `-h` / `-V` | ヘルプ / バージョン |

## 注意

- `--dangerously-*` の2つは安全確認を外すため、このvaultの通常運用では使わない前提です。
- `--approve-for-me`、`agents`、`queue`、`exec-server` などの新しいサブコマンド・オプションは、挙動を実機で未確認です (unverified)。
