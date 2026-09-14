---
date: 2026-07-15
description: "Claude Codeスキルの分野別カテゴリ一覧 — 仕様書生成、コード品質、Git/セッション、ブラウザ操作、デザイン、Obsidian、MCP/SDK、agentmemory、スケジューリング、wiki等"
tags:
  - reference
  - claude-code
  - skills
---

# Claude Codeスキル 分野別カテゴリ

関連: [[Skillの分類]]（Anthropicのスキル9分類フレームワーク）、[[Claude-Code-Skills]]（有効化状態の一覧）、[[Skill-書き方]]・[[Skill-書き方2]]（スキルの書き方）、[[skill リスト]]（gistxプロジェクトでの有効スキル記録）

## ドキュメント/仕様書関連（このプロジェクト向け）

- internal-to-external-spec — 内部仕様書→外部仕様書変換
- internal-spec-notation-check / external-spec-notation-check — 表記揺れチェック
- internal-spec-contradiction-check / external-spec-contradiction-check — 矛盾チェック
- gen-internal-spec-index / gen-external-spec-index — インデックス生成
- reverse-gen-internal-spec — ソースから内部仕様書を逆生成
- python-cli-internal-spec — Python CLIアプリの内部仕様書生成
- spec-to-code — 仕様書から実装コード生成
- gerepo-external-spec — ghrepoプロジェクト専用の外部仕様書生成

## コード品質・デバッグ

- code-review — diffレビュー（correctness/簡素化/効率）
- simplify — 変更コードの整理・簡素化
- security-review / review — レビュー系
- debug-mypy / debug-ruff / debug-ruff-mypy — 型・lintエラー修正
- verify — 変更が実際に動くかE2Eで検証

## Git/セッション履歴

- commit-context — コミットとエージェントセッションの紐付け調査
- commit-history — エージェント関連コミット一覧
- session-history / handoff / recap / remember / recall — 過去セッションの振り返り・再開

## ブラウザ操作・Webアプリ

- claude-in-chrome — Chrome自動操作
- webapp-testing — Webアプリのテスト
- run — アプリの起動・動作確認

## ドキュメント生成（Office系）

- docx / pptx / xlsx / pdf — Office/PDFファイル操作

## デザイン・可視化

- frontend-design / web-artifacts-builder / artifact-design — UI/Artifact設計
- canvas-design / algorithmic-art — ビジュアルアート
- dataviz — グラフ・ダッシュボード
- theme-factory / gsap-*（多数） — アニメーション（GSAP関連一式）
- brand-guidelines — Anthropicブランド適用
- json-canvas — JSON Canvas形式

## Obsidian関連

- obsidian-cli / obsidian-bases / obsidian-markdown / json-canvas（obsidian:名前空間含む）

## MCP/SDK開発

- mcp-builder — MCPサーバー構築
- claude-api — Claude API/Agent SDK活用
- gemini-api-dev — Gemini API活用

## スキル自体の管理

- skill-creator — スキル新規作成・改善
- find-skills / find-skills-j — スキル検索（日本語版あり）
- anti-distill — スキルの反蒸留（情報保護）
- write-agentmemory-skill — agentmemory向けスキル作成

## agentmemory関連

- agentmemory-agents / agentmemory-architecture / agentmemory-config / agentmemory-hooks / agentmemory-mcp-tools / agentmemory-rest-api
- forget — 特定の記憶を削除

## スケジューリング・自動化

- loop — 定期実行
- schedule — cronベースの定期エージェント
- update-config — settings.json設定（フック・権限等）
- keybindings-help — キーバインド設定
- fewer-permission-prompts — 許可プロンプト削減

## コミュニケーション

- internal-comms — 社内向け文書作成
- standup — スタンドアップ報告
- slack-gif-creator — Slack向けGIF作成

## wikiナレッジベース

- wiki:wiki / wiki:ingest / wiki:compile / wiki:query / wiki:lint / wiki:refresh / wiki:research / wiki:retract / wiki:thesis / wiki:plan / wiki:project / wiki:assess / wiki:librarian / wiki:output / wiki:ll / wiki-manager

## graphify（コードグラフ化）

- graphify — コードベースをナレッジグラフ化してクエリ

## Vercel関連（多数、vercel:名前空間）

- デプロイ・環境変数・Next.js・AI SDK・認証・キャッシュ等の一式

## その他ユーティリティ

- android-cli — Android開発
- doc-coauthoring — ドキュメント共同執筆ワークフロー
- init — CLAUDE.md初期化
- claude-code-guide（エージェント） — Claude Code自体の使い方
