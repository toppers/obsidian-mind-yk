---
date: 2026-08-19
description: "QMD のアーキテクチャ概要 — スコア正規化・融合戦略のパイプライン、詳細は README.md/CLAUDE.md 参照"
tags:
  - work-note
---
[GitHub \- tobi/qmd: mini cli search engine for your docs, knowledge bases, meeting notes, whatever\. Tracking current sota approaches while being all local · GitHub](https://github.com/tobi/qmd)

❯ このプロジェクトのアーキテクチャを説明して

QMD (Query Markup Documents) のアーキテクチャ

概要

QMDは、Markdownのナレッジベースをローカルで検索するためのハイブリッド検索エンジンです。BM25全文検索（SQLite FTS5）＋ベクトル検索（sqlite-vec）＋LLMによるクエリ拡張・リランキング（node-llama-cpp / GGUFモデル）を組み合わせています。CLI・MCPサーバー・TypeScript SDKの3つの形態で提供されます。

ソース構成（src/）

┌──────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ファイル │                                                 役割                                                 │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│          │ 中核エンジン。DBスキーマ/マイグレーション、インデックス処理(reindexCollection)、チャンク分割(chunkDo │
│ store.ts │ cument*)、埋め込み生成、FTS/ベクトル検索(searchFTS, searchVec)、RRF融合(reciprocalRankFusion)、トッ  │
│          │ プレベルのhybridQuery/structuredSearchパイプラインを実装。他の大半のモジュールがここを呼び出す       │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ db.ts    │ SQLite接続のオープンとsqlite-vec拡張のロード（プラットフォーム別パス、Bun/Nodeのbetter-sqlite3差異を │
│          │ 吸収）                                                                                               │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ llm.ts   │ LlamaCppクラス。埋め込み/リランク/クエリ拡張の3モデルの遅延ロード、GPUバックエンド検出(CUDA/Vulkan/M │
│          │ etal/CPU)、HuggingFaceからのGGUFダウンロード＆キャッシュ(~/.cache/qmd/models/)                       │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ collecti │ コレクション/コンテキスト設定。YAML設定(qmd.yml)やインラインconfigの書き込みを、SQLiteを正とするスト │
│ ons.ts   │ アの下位レイヤーとして扱う                                                                           │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ast.ts   │ tree-sitterによるコードファイルのAST分割（--chunk-strategy                                           │
│          │ auto）。store.tsの正規表現/Markdownの区切りスコアとマージされる                                      │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ paths.ts │ qmd://仮想パスの解析・解決（コレクション相対パス⇄仮想パス）                                          │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ maintena │ Maintenanceクラス。vacuum、孤立データ削除、キャッシュクリアなどのハウスキーピング（qmd               │
│ nce.ts   │ cleanup/doctorから使用）                                                                             │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ cli/qmd. │ CLIエントリポイント。引数パース、全サブコマンドのディスパッチ                                        │
│ ts       │                                                                                                      │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ cli/form │ 検索結果のレンダリング（色付け、TTYハイパーリンク、JSON/CSV/MD/XML出力）                             │
│ atter.ts │                                                                                                      │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ mcp/serv │ MCPサーバー（stdio/HTTP）。query/get/multi_get/statusツールを公開する薄いラッパー                    │
│ er.ts    │                                                                                                      │
├──────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ index.ts │ 公開SDKのエントリポイント(createStore()/QMDStore)。内部のStoreを安定インターフェースでラップし、YAML │
│          │ /インラインconfigへの書き込みも担う                                                                  │
└──────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────┘

データフロー

1. インデックス
   コレクションglob → タイトル抽出 → コンテンツhash化
   → SQLite `documents` + FTS5 `documents_fts`

2. 埋め込み(embed)
   スマートチャンク分割(~900トークン、15%オーバーラップ、
   Markdown見出し優先 / コードは--chunk-strategy autoでtree-sitter AST分割)
   → node-llama-cppの embedBatch()
   → `content_vectors` + `vectors_vec`(sqlite-vec)

3. クエリ(query) ※hybridQuery / structuredSearch
   LLMクエリ拡張(元クエリ＋派生クエリ)
   → 各クエリでBM25とベクトル検索を並列実行
   → RRF融合 (k=60, 元クエリは×2重み, 上位ボーナス)
   → 上位30件を候補に
   → LLMリランキング (qwen3-reranker)
   → 順位帯ごとにRRFスコアとリランクスコアをブレンド
     (1-3位:75%RRF/25%rerank, 4-10位:60/40, 11位以降:40/60)

二重ランタイム対応（Node + Bun）

bin/qmdはロックファイル（package-lock.json→Node、bun.lock→Bun）を見てインストール時のランタイムを判定し、better-sqlite3/sqlite-vecのネイティブABI不整合を回避します。gitチェックアウト時はsrc/cli/qmd.tsを直接実行（bunまたはtsx経由）し、古いdist/を優先しません。そのためDB接続やプロセスライフサイクルに触る変更は、Node(vitest)とBun(bun:test)の両方でテストする必要があります。

モデル構成

3つのGGUFモデルを~/.cache/qmd/models/にキャッシュして使用:
- embeddinggemma-300M — ベクトル埋め込み（多言語対応が必要な場合はQMD_EMBED_MODELでQwen3-Embeddingに切替可）
- qwen3-reranker-0.6b — クロスエンコーダーによるリランキング
- qmd-query-expansion-1.7B（ファインチューン済み） — クエリ拡張

詳しいスコア正規化・融合戦略のパイプライン図はREADME.md、開発規約はCLAUDE.mdにまとめてあります。


## Related
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-使い方|QMD の使い方]]
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-SQLiteの場所|QMD インストール後の SQLite の所在]] — index.sqlite の探索順とエンジン本体の格納場所
