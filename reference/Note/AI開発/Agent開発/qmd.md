---
date: 2026-09-14
description: "QMD — vault 全体を対象とするセマンティック検索ツール（BM25＋ベクトル検索の融合）。詳細ノートは Claude-Code/MCP/QMD 配下にあり、本ノートはその入口"
tags:
  - reference
  - tool
  - qmd
---

# qmd
[GitHub \- tobi/qmd: mini cli search engine for your docs, knowledge bases, meeting notes, whatever\. Tracking current sota approaches while being all local · GitHub](https://github.com/tobi/qmd)
vault 全体に対するセマンティック検索を提供するツール。MCP サーバー（`mcp__qmd__query` 等）と CLI（`qmd --index <name> query`）の両系統があり、検索インデックスは SQLite に保持される。

詳細は `reference/Note/AI開発/Claude-Code/MCP/QMD/` 配下の各ノートにある。

## 詳細ノート

### 使い方・コマンド

- [[qmd-cmd-使い方]] — QMD のコマンドの使い方
- [[QMD-CMD-使い方-tobl]] — CLAUDE.md 記載コマンド一覧の使い方（tobl版）。フュージョン戦略・スコア解釈を含む
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/使い方|QMD — 使い方（status 実行結果）]] — `mcp__qmd__status` の実行結果メモ

### 構成・内部

- [[QMD-アーキテクチャ]] — スコア正規化・融合戦略のパイプライン概要
- [[QMD-クラス依存関係]] — クラス依存関係メモ（Mermaid の `<<interface>>` 注釈の検証結果を含む）
- [[QMD-クラス依存関係図]] — Mermaid classDiagram 形式の依存関係図

### 環境・データ

- [[QMD-SQLiteの場所]] — 検索インデックス `index.sqlite` の探索順と所在
- [[QMD-コレクション一覧]] — MCP サーバーが持つコレクション9件と実パス（as of 2026-09-10）

## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]] — 「検索(BM25検索、Vector検索、RAGなど)」節からの参照元
- [[qmd MCPクライアント-サーバーのインストール]] — インストール手順
