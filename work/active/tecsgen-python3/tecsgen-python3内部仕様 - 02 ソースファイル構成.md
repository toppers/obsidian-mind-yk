---
date: 2026-10-02
description: "tecsgen-python3内部仕様 第2章（ソースファイル構成）— Ruby版との1ファイル対1モジュールの対応表（決定は別ノート）の要約、Python版で新設・分割・移植しなかったファイル、プラグインと同梱 CDL の置き場所。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3内部仕様]] の第2章（全12章）。全ファイルの対応表は決定ノート [[tecsgen-python3 パッケージ構成決定]] にあります（正本）。本章は実装後（2026-10-02）の実態との差を中心に書きます。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 02 ソースファイル構成|Ruby版 第2章]]。

## 2. ソースファイル構成

### 2.1 対応の規則

- Ruby の `tecslib/core/` → `src/tecsgen/core/`。ファイル名は snake_case
- 標準ライブラリや予約語と衝突する名前は変える: `types` → `cdl_types`、`ctypes` → `c_types`、`import` → `import_cdl`
- 標準付属プラグインは Ruby と**同名**（`HRPPlugin.rb` → `plugin/HRPPlugin.py`）。CDL の `generate(HRPPlugin, ...)` の名前をそのまま import 名に使うため
- `__init__.py` は何も import しない（`syntaxobj.rb`・`componentobj.rb` は `__init__.py` に当たる）

### 2.2 実装後に決まった分割

| Ruby | Python | 理由 |
|---|---|---|
| `core/generate.rb`（5,399行） | `core/generate.py`（Namespace・Signature・型）、`core/generate_celltype.py`、`generate_celltype_ph.py`、`generate_celltype_cell.py`、`generate_celltype_templ.py` | `Celltype` の生成が巨大なため、生成物ごと（ヘッダ・セル・テンプレート）に分けた（P4） |
| `core/bnf.y.rb` | `core/generator.py`、`syntax/cdl_lexer.py`・`cdl_parser.py`・`cdl_actions.py`・`cdl_tables.py`、`syntax/tecsio.py` | 字句解析・racc 駆動部・文法アクション・LALR 表・文字コード変換に分けた（P2・P3） |
| `core/C_parser.y.rb` | `syntax/cdecl_*.py` の4つ | 同上（`import_C` の C 宣言） |
| racc の駆動部（Ruby の標準ライブラリ） | `syntax/racc_runtime.py` | Ruby 側は標準ライブラリなので、Python では自前で移植 |
| `core/tecsinfo.rb` | `core/tecsinfo.py` | 同名 |

### 2.3 Python 版で新設したファイル

`context.py`・`host.py`・`state.py`・`ruby_compat.py`・`ruby_optparse.py`・`syntax/_model.py`・`syntax/racc_runtime.py`（役割は [[tecsgen-python3内部仕様 - 01 概要|1章]]）、`tecsmerge.py`（Ruby の `tecsmerge.rb`）。

### 2.4 移植しないファイル

| Ruby | 理由 |
|---|---|
| `bnf.tab.rb`・`C_parser.tab.rb` | racc の生成物。表だけを `syntax/*_tables.py` に取り出した |
| `core/location.rb` | どこからも読み込まれていない（同じクラスを `tool_info.rb` が定義） |
| `tecsflow.rb`・`tcflow.rb`・`flowlib/` | スコープ外 |
| `tecscde.rb`・`cdelib/` | 旧 TECSCDE。TypeScript 版が置き換える |
| `tecsgen_rcov.rb` | 開発用 |

### 2.5 プラグインと同梱 CDL

- `plugin/*.py`: Ruby の `tecslib/plugin/*.rb`（78ファイル）と `plugin/lib/*.rb`（7ファイル）に対応。標準付属は 85 本中 83 本を移植（as of 2026-10-03）。残る `HRP2Cache`・`HRP2PostHook` は動かす経路が無く対象外（[[tecsgen-python3外部仕様 - 06 プラグインシステム|外部仕様 6章]]）
- `tecs/`: Ruby の `tecsgen/tecs/`（標準 CDL ライブラリ、102 ファイル）をそのまま複製し、パッケージデータとして wheel に含める（`.gitattributes` で改行変換なし。2026-10-02、P6a）
- `messages/`: Ruby の `tecslib/messages/messages_*.rb` と同名。言語名から動的に選ぶ

### 2.6 リポジトリのその他の構成

| パス | 内容 |
|---|---|
| `tests/` | pytest。`golden/`（Ruby 版の正解データ）、`ruby/`（オラクル）、`user_plugins/`（`-L` の検証用） |
| `tools/golden/` | 正解データの採取（`generate_golden.py`・`collect_kernel.py`・`collect_packages.py`・`collect_tecsmerge.py`） |
| `tools/port/` | 一致一覧（`p4_progress.py`）、WSL での一括検証（`wsl_check.ps1`・`wsl_check.sh`） |

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3 パッケージ構成決定]] — 全ファイルの対応表
- [[tecsgen-python3内部仕様 - 04 クラス設計]]
