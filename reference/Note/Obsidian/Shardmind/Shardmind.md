---
date: 2026-08-18
description: "ShardMind（Obsidianvaultテンプレート管理パッケージマネージャー）の概要問答控え"
tags:
  - reference
  - obsidian
  - shardmind
---

❯ このプロジェクトは何をするものか教えて

このプロジェクトは ShardMind という、Obsidian vault のテンプレート（"shard"）を管理するパッケージマネージャーです。

概要

- 目的: Obsidian の vault テンプレート（設定・ノート構造・プラグイン設定など一式）を「shard」という単位でパッケージ化し、インストール・更新・既存 vault への適用（adopt）を管理する CLI ツール。
- 例え: npm/Homebrew のようなパッケージマネージャーの仕組みを、Obsidian vault のテンプレート配布・更新に応用したもの。
- エージェント非依存: エンジン自体は AI エージェントに依存しないが、shard の中身次第で Claude Code / Codex / Gemini CLI などのフックをサポートできる設計。

主な機能（コマンド）

┌───────────────────────────┬──────────────
│         コマンド          │                                     役割                                     │
├───────────────────────────┼──────────────
│ shardmind install <shard> │ 新規に shard を vault にインストール(値の入力ウィザード、モジュール選択など) │
├───────────────────────────┼──────────────
│ shardmind update          │ インストール済み shard を最新版に更新(3-way マージでユーザーの変更を保持)    │
├───────────────────────────┼──────────────
│ shardmind adopt <shard>   │ 既存の vault に後から shard の管理下を適用する                               │
├───────────────────────────┼──────────────
│ shardmind(引数なし)       │ 現在の状態表示(status)                                                       │
└───────────────────────────┴──────────────

技術スタック

- TypeScript + Pastel(CLI フレームワーク)+ Ink/React(ターミナル UI)
- Nunjucks でテンプレートレンダリング、node-diff3 で 3-way マージ(git と同じ思想)
- 状態は vault ローカルの .shardmind/ ディレクトリに保存(git 的なモデル、グローバル状態なし)

開発スタイル

- spec-driven: docs/ARCHITECTURE.md(設計思想)、docs/IMPLEMENTATION.md(実装詳細)、docs/SHARD-LAYOUT.md(v6 レイアウト契約)が先に書かれ、コードはそれを実装する形。
- テスト重視(fixture-first、TDD 必須の箇所あり)、コミットも小さく段階的に分けるルールが徹底されています。

現在は v0.1 に向けて開発中で、進捗は GitHub issue #70 で管理されています。

ーーーー
「shardmind」はこのプロジェクト（obsidian-mind vault）固有の用語のようです。README/ARCHITECTUREを確認します。

  Searched for 3 patterns, read 2 files

ShardMind（このリポジトリ obsidian-mind 自体ではなく、それが利用している外部ツール）とは何かがREADME:115に明記されています。

ShardMindとは

**ShardMindは「Obsidianヴォールト・テンプレート用のパッケージマネージャー」**です（github.com/breferrari/shardmind）。

このリポジトリ（obsidian-mind）自体はObsidianヴォールトのテンプレートで、ShardMindはそれをインストール・更新するためのエンジンという関係です。

何をしてくれるか

- shardmind install github:breferrari/obsidian-mind — ウィザード形式でヴォールトを新規セットアップ。名前・組織・ヴォールトの用途・使う agent（Claude Code / Codex / Gemini CLI）・QMD（検索機能）の有効化などを聞き取り、git初期化・QMDブートストラップ・brain/North Star.md のパーソナライズまで自動でやる
- オプションモジュール — 使わない機能はスキップできる
- 3-way マージによるアップグレード — テンプレート側の更新（新機能追加など）と、ユーザーが自分のヴォールトに加えたカスタマイズを、コンフリクトを検知しながらマージできる
- shardmind adopt — 既にただ git clone しただけの素のヴォールトを、後からShardMind管理下に「編入」できる（中身は一切失わず .shardmind/ サイドカーだけ追加）

重要な設計原則：Additive, not load-bearing

- デフォルト設定でインストールすると、git clone した場合とバイト単位で同一になる（クローンのUXを一切損なわない）
- .shardmind/ フォルダと shard-values.yaml を削除しても、ヴォールトはそのまま動き続ける — ShardMindは「あれば便利」だが「なければ動かない」ものではない

このプロジェクト内での実体

- .shardmind/shard.yaml（E:\Crepo\...\obsidian-mind\.shardmind\shard.yaml:1-43）— このテンプレートのマニフェスト。name/version/依存バージョン(node>=22.6.0, shardmind>=0.1.3)、およびライフサイクルフック（bootstrap / personalize / post-update）を定義
- .shardmindignore — shardmind install 時に除外するファイル（CONTRIBUTING、翻訳、マーケティング素材など）
- .shardmind/hooks/*.ts — 実際のフック実装（bootstrap.ts, personalize.ts, post-update.ts）

要するに「vault-manifest.json」がこのテンプレート自身の実行時設定（QMDインデックス名など）を持つのに対し、shard.yaml はShardMindエンジンから見たこのテンプレートのメタデータ、という役割分担です。
Stop says: Session end checklist:
- Archive completed projects? (work/active/ -> work/archive/YYYY/)
- Update indexes? (Index.md, Memories.md, People & Context, Brag Doc)
- New notes linked? (orphans are bugs)
- Run /om-vault-audit if many notes were created/modified

## Related
- [[North Star]]
