---
date: 2026-09-09
description: "techsavvyash/codegraph（SCIP索引＋Neo4j＋MCP）の導入メモ — headroom スタックとの Neo4j ポート衝突を docker-compose.override.yml で解消。実行手順・MCP 環境変数・既知バグ2件。"
tags:
  - reference
  - tool
  - code-graph
  - mcp
---

# CodeGraph - techsavvyash
[techsavvyash/codegraph](https://github.com/techsavvyash/codegraph) — SCIP 索引 + Neo4j グラフDB + MCP サーバのコードインテリジェンス基盤（Go）。類似ツールは [[CodeGraph - colbymchenry]]・[[CodeGraphContext(cgc)]]。カタログは [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]。
- LLM-powered code intelligence platform with SCIP indexing, Neo4j graph database, and MCP server integration
- 導入メモ（headroom との Neo4j ポート衝突を override で解消・MCP 環境変数・既知バグ）: [[CodeGraph - techsavvyash]]
## 何が衝突していたか

現行の codegraph が使う Docker サービスは **Neo4j だけ**。qdrant / opensearch は RFC-004 で廃止済みで、参照しているのは古い `infra/docker/compose.platform.yml` のみ（**使わないこと**）。つまり `headroom-qdrant-1` との衝突は「そのファイルを使わなければ発生しない」。実際の衝突点は [[headroom-index|headroom]] の `headroom-neo4j-1` が握る **7474 / 7687** だけ。

## 対処: `docker-compose.override.yml` を作成

`docker compose` はこのファイルを `docker-compose.yml` と自動マージするので、`make docker-up` でもそのまま効く。

```yaml
services:
  neo4j:
    ports: !override            # !override が無いと Compose は "追記" して 7687 が復活する
      - "7475:7474"             # HTTP  -> http://localhost:7475
      - "7688:7687"             # Bolt  -> bolt://localhost:7688
```

Bolt を 7688 にしたのは、既存の `C:\Users\ykomi\.codegraph.yaml` が既に `bolt://localhost:7688` を指しているため。設定変更は不要。

## 実行手順

```bash
# 起動（override 自動適用。過去の孤児コンテナを消すなら --remove-orphans）
docker compose up -d --remove-orphans
#   または: make docker-up

# スキーマ作成（初回のみ）
./bin/codegraph schema create

# 確認
./bin/codegraph status          # -> ✓ Connected（7688 経由）

# インデックス
./bin/codegraph index scip . --service="codegraph"
```

[[headroom-index|headroom]] スタックと **同時起動できる**（コンテナ名 `code-graph-neo4j` vs `headroom-neo4j-1`、ホストポートも別、ボリューム・ネットワークはプロジェクト名前空間で分離）。

## MCP サーバ / chat-ui から使う場合

MCP バイナリは yaml ではなく**環境変数**を読む（`NEO4J_URI` と `NEO4J_USER` — `USERNAME` ではない点に注意）:

```powershell
$env:NEO4J_URI = "bolt://localhost:7688"
$env:NEO4J_USER = "neo4j"
$env:NEO4J_PASSWORD = "password123"
./bin/codegraph-mcp
```

chat-ui 経由なら、`web/chat-ui` を起動するシェルで同じ3変数を export しておけば子プロセスに継承される。

## 既知バグ2件（2026-09-09 時点）

- **CLI は環境変数 `NEO4J_URI` を読まない**（viper の `AutomaticEnv` が `neo4j.uri` ↔ `NEO4J_URI` を変換しない実装バグ）。CLI 側は `~/.codegraph.yaml` か `--neo4j-uri bolt://localhost:7688` フラグで指定する。README の記述は不正確。
- **`./bin/codegraph status` の出力に `URI: bolt://localhost:7687` と出る**が、これは表示用のデフォルト値を出しているだけの表示バグ。実接続は 7688 で成功している（`schema info` が実データを返すことで確認済み）。

## 停止 / リセット

```bash
docker compose down          # 停止（データは volume に残る）
make db-reset                # down → up → schema 再作成
docker compose down -v       # データも消す
```

## Related

- [[AIコーディングツール・知識グラフ・コードベース分析・リポジトリ管理ツールのリファレンスリスト]]
- [[CodeGraph - colbymchenry]] — 同名の別ツール（Neo4j 不要・完全ローカル）
- [[CodeGraphContext(cgc)]] — さらに別の同系ツール
- [[headroom-index]] — Neo4j ポートを取り合う相手
