---
date: 2026-09-09
description: "CodeGraphContext — ローカルコードをグラフDBにインデックスし AI アシスタントへコンテキストを提供する MCP サーバー＋CLI。20言語対応、.cgc 事前インデックス済みバンドル、ライブ監視。"
tags:
  - reference
---
# CodeGraphContext(cgc) - Python

ローカルのコードをグラフデータベースにインデックスし、呼び出し関係・クラス階層・コールチェーンを問い合わせ可能にする **MCP サーバー / CLI**。親リストは [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]。類似の知識グラフツールは [[graphify]]。

- [CodeGraphContext · GitHub](https://github.com/CodeGraphContext)　　アカウント
- [GitHub \- CodeGraphContext/CodeGraphContext](https://github.com/CodeGraphContext/CodeGraphContext)　　リポジトリ
	- **Turn code repositories into a queryable graph for AI agents.**
	- [CodeGraphContext/docs/translations/README\.ja\.md at main · CodeGraphContext/CodeGraphContext · GitHub](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/docs/translations/README.ja.md)
	- **コードリポジトリを AI エージェントが問い合わせ可能なグラフに変換します。**
	- ローカルのコードをグラフデータベースにインデックスし、AI アシスタントや開発者にコンテキストを提供する強力な **MCP サーバー** および **CLI ツールキット** です。スタンドアロンの CLI として包括的なコード解析を行うこともできれば、MCP 経由でお気に入りの AI IDE と接続して、AI による高度なコード理解を実現することもできます。
	- - **コードのインデックス処理:** コードを解析し、その構成要素のナレッジグラフを構築します。
	- **関係性の解析:** 呼び出し元、呼び出し先、クラス階層、コールチェーンなどを問い合わせできます。
	- **事前インデックス済みバンドル:** `.cgc` バンドルで著名なリポジトリを即座にロード。インデックス不要！（[詳細](https://github.com/CodeGraphContext/CodeGraphContext/blob/main/docs/translations/docs/BUNDLES.md)）
	- **ライブファイル監視:** ディレクトリの変更を監視し、グラフをリアルタイムで自動更新します（`codegraphcontext watch`）。
	- **インタラクティブなセットアップ:** ユーザーフレンドリーなコマンドラインウィザードで簡単に設定できます。
	- **デュアルモード:** 開発者向けのスタンドアロン **CLI ツールキット**、および AI エージェント向けの **MCP サーバー** の両方として動作します。
	- **マルチ言語サポート:** 20 のプログラミング言語に完全対応しています。
	- **柔軟なデータベースバックエンド:** FalkorDB Lite（デフォルト）、KuzuDB、LadybugDB、FalkorDB Remote、Nornic DB、または Neo4j（すべてのプラットフォームで Docker / ネイティブ動作）。
	- インストール
		- pip install codegraphcontext
	- インデックス作成
		- cgc index .
	- グラフDB
		- KuzuDB (デフォルト)
		- FalkorDB Lite
		- Neo4j
- [GitHub \- CodeGraphContext/codegraphcontext\.github\.io: Hosting docs for CodeGraphContext · GitHub](https://github.com/CodeGraphContext/codegraphcontext.github.io)
	- サイト
- [[CodeGraph - techsavvyash]]
	-  LLM-powered code intelligence platform with SCIP indexing, Neo4j graph database, and MCP server integration