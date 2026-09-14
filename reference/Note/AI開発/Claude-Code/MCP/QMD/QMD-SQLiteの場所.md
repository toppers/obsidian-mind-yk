---
date: 2026-09-07
description: "qmd インストール後の SQLite の所在 — 検索インデックス(index.sqlite)の探索順(グローバル ~/.cache/qmd、プロジェクトローカル .qmd、qmd.yml 隣接、SDK 指定)と、SQLite エンジン本体(better-sqlite3 / bun:sqlite / sqlite-vec 拡張)の格納場所"
tags:
  - reference
  - qmd
  - mcp
---

# QMD インストール後の SQLite の所在

「SQLite」には 2 つの意味がある — **検索インデックスの DB ファイル** と **SQLite エンジン／ネイティブライブラリ**。以下は両方。コード上の参照箇所は 2026-09-07 に qmd ソースを読んだ時点のもの (inferred)。

## 1. SQLite データベースファイル（＝検索インデックス本体）

| 種類 | 場所 | 決定箇所 |
|------|------|----------|
| グローバルインデックス（通常はこれ） | `~/.cache/qmd/index.sqlite` → Windows では `C:\Users\ykomi\.cache\qmd\index.sqlite` | `src/store.ts:562-565` |
| 環境変数で移動した場合 | `$XDG_CACHE_HOME/qmd/index.sqlite`（`XDG_CACHE_HOME` 優先） | 同上 |
| プロジェクトローカルインデックス（`qmd init` を実行したフォルダ） | `<プロジェクト>/.qmd/index.sqlite` | `src/cli/qmd.ts:412-416` |
| YAML 設定（`qmd.yml`）ベース | 設定ファイルと同じディレクトリの `index.sqlite` | `src/collections.ts:153` |
| SDK 利用時 | `createStore(dbPath)` / `createStore({ dbPath })` で渡した任意パス | `src/index.ts`, `src/store.ts:1845` |

- `qmd status` を実行すると実際に使われているパスが `Index: ...` として表示される（`src/cli/qmd.ts:499`）。
- 関連ファイル（いずれも SQLite ではない）:
  - LLM モデルのキャッシュ … `~/.cache/qmd/models/`
  - MCP デーモンの pid / log … `~/.cache/qmd/mcp.pid` / `~/.cache/qmd/mcp.log`

> [!note] このVaultの実インデックス
> このVaultは MCP / CLI / SessionStart フックすべてが `vault-manifest.json` の `qmd_index` フィールド（未設定ならフォルダ名スラッグ）で同一ストアにスコープされる。実パスは `qmd status` で確認する。

## 2. SQLite エンジン／ネイティブライブラリ

`bin/qmd` がロックファイルで Node か Bun かを判定して実行を切り替える（`src/db.ts`）。

- **npm / Node インストール時**: `better-sqlite3`（`package.json` で 12.10.0 に固定）。SQLite 本体はこのネイティブモジュールにコンパイル同梱され、`node_modules/better-sqlite3/build/Release/better_sqlite3.node` に存在。
- **Bun インストール時**: Bun 実行ファイル内蔵の `bun:sqlite` を使用（別途ファイルなし）。macOS のみ、拡張機能ロード制限を回避するため Homebrew の `libsqlite3.dylib`（`/opt/homebrew/opt/sqlite/lib/...`）に差し替え。
- **`sqlite-vec` 拡張（ベクトル検索用のローダブル拡張）**: プラットフォーム別パッケージ（Windows なら `sqlite-vec-windows-x64`）が `node_modules/` に入り、そこから `.dll` / `.so` / `.dylib` を実行時に `loadExtension()` で読み込む（`src/db.ts:48-53, 94-103`）。

## Related
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/QMD-アーキテクチャ|QMD のアーキテクチャ]]
- [[reference/Note/AI開発/Claude-Code/MCP/QMD/使い方|QMD の使い方]]
- [[reference/Note/PC/qmd MCPクライアント-サーバーのインストール|qmd MCPクライアント/サーバーのインストール]] — Windows でネイティブモジュール(better-sqlite3)のビルドが失敗した経緯
