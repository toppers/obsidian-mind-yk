---
date: 2026-09-26
description: "tecsgen-python3のtree-sitter文法の読み込み方式を決定：移植元の生成済みparser.cをリポジトリに同梱し、tecsgenパッケージ内のC拡張として setuptools でビルドする。WindowsとWSLの両方でビルド・テスト済み"
status: superseded
project: tecsgen-python3
quarter: Q3-2026
tags:
  - decision
  - tecs
  - tecsgen
---

# Decision: tecsgen-python3 tree-sitter読み込み方式決定

> [!warning] Superseded（2026-09-27）
> P2 の実測で、tree-sitter では構文エラーの位置・件数・回復と TYPE_NAME の判定を Ruby 版と一致させられないと分かり、構文解析を racc 表駆動に切り替えた → [[tecsgen-python3 構文解析方式決定]]。この決定で同梱した文法・C 拡張は削除した（リポジトリ `6d69710`）。以下は当時の記録として残す。

## Context

[[tecsgen-python3移植計画]] P0 の最後の項目。Python 版は、CDL の構文解析に `tree-sitter-cdl`、`import_C` の C ヘッダ解析に `tree-sitter-tecs-cdecl` を使う（移植元 `tools-ts/`）。これまでの `example.py` は、Windows 用にビルド済みの DLL を `ctypes` で絶対パスから読み込んでいた。

判断材料（2026-09-26 確認）:

- **正解データとの比較は WSL（Linux）で行う**と決めている（[[tecsgen-python3移植計画]] P0）。Windows 用の DLL は WSL では使えない
- 2つの文法とも、tree-sitter が生成した `parser.c`（ABI 15、tree-sitter CLI 0.25.10）が SVN に登録されている。外部スキャナ（`scanner.c`）は無く、`parser.c` と付属ヘッダだけでビルドできる
- 用意されているバインディングは Node 用だけで、Python 用は無い
- C コンパイラは、Windows に MSVC（Visual Studio 18）、WSL に gcc 13.3 がある
- 移植元の README は、`tools/`（JS 版）と `tools-ts/`（TS 版）の生成物が同一だと書いている。実際には `tecs-cdecl` の `parser.c` と `tree_sitter/array.h` に違いがあった。調べると、`parser.c` は先頭の生成ツール名のコメント1行だけ、`array.h` はパーサ本体が使わない補助ヘッダの版の違いで、状態数・記号数は一致する。機能上は同一

## Options Considered

1. **C ソースを同梱し、パッケージ内の C 拡張としてビルドする**（採用）
2. 移植元 `tools/` に Python バインディングを生成し、文法を独立パッケージとして依存に加える
3. ビルド済みの共有ライブラリ（DLL/.so）を `ctypes` で読み込む（従来の方式）

## Decision

C ソースを同梱し、`tecsgen` パッケージ内の C 拡張モジュールとしてビルドする。

- `tools-ts/tree-sitter-{cdl,tecs-cdecl}/src` の `parser.c`・`tree_sitter/*.h`・`node-types.json` を、`src/tecsgen/syntax/grammars/{cdl,tecs_cdecl}/` に複製する。`svn export -r BASE --native-eol LF` を使い、改行を LF に保つ（取り込み元 r3305）
- 拡張モジュール `tecsgen.syntax._cdl`・`tecsgen.syntax._tecs_cdecl` は、tree-sitter 公式の Python バインディングと同じ形にする（`language()` が `"tree_sitter.Language"` という名前の PyCapsule を返す）
- `tecsgen.syntax.languages` の `cdl_language()`・`cdecl_language()` から、キャッシュした `Language` を取得する
- ビルドバックエンドを hatchling から setuptools に変えた。拡張の定義は `setup.py`、それ以外は `pyproject.toml` に置く

採用理由:

- `uv sync` だけで、Windows（MSVC）と WSL（gcc）の両方で動く
- 文法の版を、取り込み元のリビジョンでリポジトリ内に固定できる
- 案2は移植元 SVN へのコミットと、リポジトリ外へのパス依存が生じる。案3はビルド手順がリポジトリの外に出て、OS ごとに別のバイナリが要る

## 検証（2026-09-26）

- Windows（MSVC 14.51、Python 3.13.11 amd64）: `uv sync` でビルドし、pytest 6件が通った。ruff・ty も通った
- WSL（Ubuntu、gcc 13.3）: `UV_PROJECT_ENVIRONMENT=/tmp/tecsgen-venv` で別の仮想環境を作ってビルドし、pytest 6件が通った
- テスト内容: 2つの文法の名前と ABI バージョン、`Language` のキャッシュ、CDL と C ヘッダのサンプルがエラーなくパースできること、CDL の構文エラーを検出できること

## Consequences

- ビルドに C コンパイラが必要になる
- **Windows では、シェルに Visual Studio の x86 用開発者コマンドプロンプト環境が読み込まれていると、ビルドに失敗する**（[[Gotchas - CLI Build Tooling]]）。回避手順はリポジトリの README に書いた
- 文法を更新するときは、移植元で `grammar.ts` を直して生成し、もう一度複製する（手順は `src/tecsgen/syntax/grammars/README.md`）
- `example.py` の DLL 読み込みと環境変数 `TECSGEN_CDL_DLL` は廃止した

## Related

- [[tecsgen-python3移植計画]] — P0 の決定事項
- [[tecsgen-python3 パッケージ構成決定]] — `syntax/` パッケージの位置づけ
- [[tecsgen-python3内部仕様]] — 5章（字句解析・構文解析）の前提
- [[CDLParser(tree-sitter利用-JS版)]] — 同じ文法の JS 版での採用例
- [[tecsgen-python3]]
