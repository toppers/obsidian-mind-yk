---
date: 2026-05-26
description: "ck (seek) — grepのドロップイン代替。regex/lexical(BM25)/semantic/hybridの4モード対応。MCPサーバー機能でClaude/Cursor連携可能。Rust製。"
tags:
  - reference
  - tool
  - cli
  - semantic-search
  - mcp
---

# ck (seek) リファレンス

grep のドロップイン代替。4つの検索モードと MCP サーバー機能を持つ Rust 製 CLI。

## 検索モード

| モード | コマンド | 説明 |
|--------|---------|------|
| Regex（デフォルト） | `ck "pattern" src/` | 通常のgrep互換 |
| Lexical | `ck --lex "phrase" .` | BM25全文検索、フレーズ検索に強い |
| Semantic | `ck --sem "concept" src/` | 意味ベース検索（埋め込みモデル使用） |
| Hybrid | `ck --hybrid "pattern" .` | regex + semantic の組み合わせ |

## クイックスタート

```bash
# Regex（インデックス不要）
ck "error" src/
ck -i "TODO" .              # 大文字小文字無視
ck -r "fn main" .           # 再帰
ck -n "import" lib.py       # 行番号付き

# Semantic（自動インデックス）
ck --sem "error handling" src/
ck --sem --limit 5 "authentication"
ck --sem --threshold 0.8 "auth"   # 高精度フィルタ

# Lexical
ck --lex "user authentication"
ck --lex "http client request"

# Hybrid
ck --hybrid "async function"
ck --hybrid "error" --limit 10
```

## 結果フィルタリング

```bash
--topk N / --limit N    # 上位N件（semanticデフォルト: 10）
--threshold SCORE       # 最小スコア（semantic: 0.6, hybrid: 0.01-0.05）
--scores                # スコアを表示 [0.950] file:line:match
```

## インデックス管理

```bash
ck --status .               # インデックス状態確認
ck --status-verbose .       # 詳細統計
ck --index .                # 事前インデックス作成（CI用）
ck --add file.rs            # 単一ファイル追加
ck --clean .                # インデックス削除
ck --clean-orphans .        # 孤立ファイルのみ削除
ck --switch-model nomic-v1.5  # モデル変更（クリーン+再構築）
```

## 埋め込みモデル

| モデル | 特徴 |
|--------|------|
| `bge-small`（デフォルト）| 軽量・高速 |
| `nomic-v1.5` | 高品質（8kコンテキスト） |
| `jina-code` | コード特化 |
| `mxbai-xsmall` | 超軽量 |

## 出力フォーマット

```bash
ck --json --sem "bug" src/      # JSON（ツール/スクリプト用）
ck --jsonl --sem "error" src/   # JSONL（AIエージェント推奨）
ck --jsonl --sem "func" --no-snippet  # スニペットなし
```

## MCP サーバー（AI エージェント連携）

```bash
ck --serve    # MCPサーバーを起動
```

提供ツール: `semantic_search`, `regex_search`, `hybrid_search`, `index_status`, `reindex`, `health_check`

Claude Desktop / Cursor / MCP互換クライアントから接続可能。

## 高度な機能

```bash
ck --full-section "auth" .    # 関数/クラス全体を返す（tree-sitter使用）
                              # 対応: Python/JS/TS/Haskell/Rust/Ruby
ck --tui                      # インタラクティブTUI（fzf風セマンティック版）
ck --sem "auth" --rerank      # リランキングで精度向上
```

## 関連

- [[concept-grep リファレンス]] — 同系統のセマンティックgrep
