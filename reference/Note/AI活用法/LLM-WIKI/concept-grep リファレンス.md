---
date: 2026-05-26
description: "concept-grep — 意味ベースのセマンティックgrep CLI。ソースファイルをクエリの「意味」で検索する。埋め込みモデルを使用。OpenAI互換APIに対応。"
tags:
  - reference
  - tool
  - cli
  - semantic-search
---

# concept-grep リファレンス

セマンティックgrep — ソースファイルを意味で検索する CLI ツール。

## 基本構文

```bash
concept-grep <query> [paths]
```

## 主要オプション

| オプション | 説明 |
|-----------|------|
| `-r, --recursive` | ディレクトリを再帰的に検索 |
| `-s, --score` | 類似度スコアを表示 |
| `-g, --graph` | 類似度をバーグラフで表示 |
| `-v, --invert-match` | 最も類似度が低いファイルを表示 |
| `-n, --top N` | 上位N件のみ表示 |
| `-p, --top-percent N` | 類似度上位N%を表示（デフォルト: 10%） |
| `--index` | 指定ファイルの `.concept` ファイルを生成 |
| `--summary [LINES]` | embed_source サマリーを表示（デフォルト: 5行） |
| `--include GLOB` | 指定globパターンにマッチするファイルのみ対象 |
| `--exclude GLOB` | 指定globパターンのファイルを除外 |
| `--keyword-weight N` | ハイブリッド検索のキーワードスコア重み（デフォルト: 0.3） |
| `--force` | `.git` なしでも `.concept/` を作成 |

## モデル設定

```bash
# 環境変数で設定
CONCEPT_EMBED_MODEL=<model>
CONCEPT_API_BASE=<openai-compatible-url>

# CLIオプションで設定
concept-grep --model <model> --api-base <url> <query> <paths>
```

## 関連

- [[ck-seek リファレンス]] — より高機能なgrep代替（regex/lexical/semantic/hybrid対応）
