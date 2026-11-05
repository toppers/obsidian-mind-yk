---
date: 2026-05-22
description: "Claude Code がセッションをまたいでコンテキストを保持する仕組みの整理。CLAUDE.md・Auto Memory・Skills の3層構造、推奨ディレクトリ構成、claude.ai Projects(RAG)との違い"
tags:
  - reference
  - claude
  - claude-code
  - memory
---

### Claude CodeのProject Knowledgeとは

**結論：「Claude Codeがセッションをまたいでプロジェクトのコンテキストをどのように保持するか」の仕組み全体**を指します。

ただし**「Project Knowledge」という単一の機能名はない**ため、文脈によって指しているものが異なります。整理すると以下の3層構造です。

---

### 3層構造

#### 1. `CLAUDE.md`（最も重要）

プロジェクトルートに追加するMarkdownファイルで、Claude Codeはすべてのセッションの開始時に読み取ります。コーディング標準、アーキテクチャの決定、推奨ライブラリ、レビューチェックリストを設定するために使用します。 [Claude](https://code.claude.com/docs/ja/overview)

```
project/
├── CLAUDE.md          ← プロジェクト全体のルール
├── frontend/
│   └── CLAUDE.md     ← フロントエンド固有のルール
└── backend/
    └── CLAUDE.md     ← バックエンド固有のルール
```

Claude Codeは再帰的にこれらのファイルを読み込み、コンテキストとして解釈に含めます。フロントエンドの作業中はフロントエンド固有のルールが、バックエンドの作業中はバックエンド固有のルールが適用されます。 [Gihyo](https://gihyo.jp/article/2026/01/get-started-claude-code-06)

---

#### 2. Auto Memory（自動メモリ）

Claudeは自動メモリも構築し、ビルドコマンドやデバッグの洞察などの学習内容を保存し、何も書かずにセッション間で共有します。 [Claude](https://code.claude.com/docs/ja/overview)

つまり、あなたが明示的に書かなくても、Claude自身がセッションを通じて得た知見を蓄積する仕組みです。

---

#### 3. Skills（`.claude/skills/`）

Skillsは、Claudeに特定のタスクの実行方法を教えるためのナレッジパッケージです。フォルダ内の指示、スクリプト、リソースで構成され、プロジェクトの規約、ツールの使い方、ワークフローを文書化しておけば、Claudeがそれを参照して作業します。自動呼び出しで、ユーザーが明示的に指定しなくても、タスクに応じてClaudeが自動で適切なスキルを選択します。 [SIOS Tech Lab](https://tech-lab.sios.jp/archives/50570)

---

### 実践的なディレクトリ構成（推奨）

以下のファイル構成で知見を体系的に管理できます。

- `.claude/context.md` — プロジェクトの背景、目的、制約条件、技術スタック選定理由
- `.claude/project-knowledge.md` — 実装パターンや設計決定の知見、アーキテクチャの選択理由、避けるべきアンチパターン
- `.claude/project-improvements.md` — 過去の試行錯誤の記録、失敗した実装とその原因
- `.claude/common-patterns.md` — 頻繁に使用するコマンドパターン、定型的な実装テンプレート [Zenn](https://zenn.dev/driller/articles/2a23ef94f1d603)

---

### claude.aiのProjects（別物）との違い

よく混同されるのが **claude.ai（Web UI）のProjects**。こちらは：

ドキュメント、テキスト、コード、その他のファイルをプロジェクトのナレッジベースにアップロードでき、ClaudeはそれをRAG（Retrieval Augmented Generation）で参照します。有料プランのみで利用可能です。 [Claude](https://support.claude.com/en/articles/9517075-what-are-projects)

**整理すると：**

||Claude Code（CLI）|claude.ai Projects（Web）|
|---|---|---|
|仕組み|`CLAUDE.md` + Auto Memory + Skills|ファイルアップロード + RAG|
|保存場所|リポジトリ内|Anthropicのサーバー|
|Gitで管理|✅ できる|❌ できない|
|連携|現時点では未統合（Feature Requestとして挙がっている状態） [GitHub](https://github.com/anthropics/claude-code/issues/2511)|—|

**プログラマーとして実用上最も重要なのは`CLAUDE.md`の設計**です。コーディング規約、使用ライブラリのバージョン制約、アーキテクチャの決定理由をここに書けば、毎回のセッションでコンテキストを説明し直す手間がなくなります。

## Related

- [[Claude-Code-Skills]]
- [[CLAUDE.md-wsl2-index]]