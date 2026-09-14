---
date: 2026-08-27
description: "markdown-queryキットのgraphrag戦略（LightRAGベースのナレッジグラフRAG）導入手順 — 依存追加・索引作成・検索・既知の制約"
tags:
  - reference
  - ai
  - agents
---

# dahatake skills graphrag

確認できました。このリポジトリで「RAG」に該当するのは markdown-query キットの graphrag 戦略（LightRAG ベースのナレッジグラフ RAG）です。手順をまとめます。

前提：これはオプション機能

markdown-query の既定の検索（heading / semantic_paragraph / pageindex / auto）は BM25 全文検索であり、RAG（LLM でエンティティ抽出→グラフ構築→回答生成）ではありません。RAG が必要なのは「複数文書をまたいだ関係性の要約」のような、snippet 検索では答えられない質問のときだけです。コスト・実行時間が大幅に増えるので、まず既定戦略で足りないか確認してください（詳細: markdown-query/skill/references/graphrag-strategy.md）。

1. 追加依存を入れる

graphrag は markdown-query のインストーラや kit.toml の依存リストには含まれていません（lightrag-hku は既定で入らない）。キットの venv に手動で追加します。

# 導入済みキットの venv を有効化してから
tools/kits/markdown-query/.venv-mdq-gui/bin/pip install "lightrag-hku>=1.4.16,<1.5"

# Windows
tools\kits\markdown-query\.venv-mdq-gui\Scripts\pip.exe install "lightrag-hku>=1.4.16,<1.5"

さらに ローカルの Ollama が必要です（既定 LLM: qwen2.5:7b、既定 embedding: nomic-embed-text、http://127.0.0.1:11434）。外部依存なしで動作確認だけしたい場合は --graphrag-llm-provider mock --graphrag-embed-provider mock を使えます（回答は [no-context] を含むダミーになります）。

2. 索引を作る（insert）

bash tools/kits/markdown-query/mdq.sh index --strategy graphrag \
    --root <対象ディレクトリ> \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-llm-provider ollama --graphrag-llm-model qwen2.5:7b \
    --graphrag-embed-provider ollama --graphrag-embed-model nomic-embed-text

Windows は mdq.ps1 に読み替え。既存の heading 系 SQLite 索引とは別ディレクトリ（LightRAG 専用 working_dir）を使うので干渉しません。

3. 検索する（query）

bash tools/kits/markdown-query/mdq.sh search --strategy graphrag \
    --q "質問文をここに" \
    --graphrag-working-dir .mdq/graphrag-ja-jp \
    --graphrag-query-mode local \
    --format jsonl

- --graphrag-query-mode は local（既定・グラフ近傍を使う）か naive（グラフ抜きの単純ベクトル検索）のみ。global/hybrid/mix はコスト過大のためブロックされています。
- 出力は {"strategy": "graphrag", ..., "answer": "..."}。heading 戦略のような path:line citation は返らないので、Agent がその形式を期待するワークフローでは併用不可です。

知っておくべき制約

- mdq watch（差分索引）非対応。更新は --rebuild（working_dir を丸ごと再構築）か、削除を伴わない追加分のみ --rebuild なしで再実行。
- 削除の反映（pruning）は非対応、--rebuild 必須。
- mdq stats / list / get は SQLite 前提なので graphrag には使えません。
- セキュリティ: --graphrag-base-url は既定で loopback のみ許可。社外 LLM にコーパスが流出しうるため、--graphrag-allow-remote-ollama を付けない限り非 loopback URL は拒否されます。

詳細な既定値・アルゴリズムは markdown-query/skill/references/graphrag-strategy.md を、auto 戦略との使い分けは同ディレクトリの query-routing.md（graphrag は auto の候補外）を参照してください。

#　インストール
GraphRAG インデックス実行までに行った処理をメモリに保存しました。

保存した内容（mdq-graphrag-index-setup.md）:
1. mdq.ps1 index --strategy graphrag ... を初回実行 → GraphRAGUnavailable（lightrag モジュール未インストール）で失敗
2. 原因調査: tools/kits/markdown-query/.venv-mdq-gui に lightrag-hku と rank_bm25 が入っていなかった（pyproject.toml には依存として書かれているが venv には未反映）
3. ollama list で qwen2.5:7b / nomic-embed-text が既に取得済みであることを確認（追加取得不要）
4. .venv-mdq-gui/Scripts/python.exe -m pip install "rank_bm25>=0.2.2" "lightrag-hku>=1.4.16,<1.5" を実行して不足パッケージを導入（pandas, aiohttp, google-genai 等の依存も付随してインストール）
5. 同じ index コマンドを再実行 → バックグラウンドで実行中（現在も継続中）

## Related
- [[dahatake skills]]
