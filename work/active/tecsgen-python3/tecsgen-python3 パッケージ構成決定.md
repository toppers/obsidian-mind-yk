---
date: 2026-09-26
description: "tecsgen-python3のパッケージ構成を決定：Ruby版と1ファイル対1モジュールで対応させ、再オープンされたクラスは機能別mixinにする。標準プラグインはRubyと同名のモジュール名。全Rubyファイルの対応表付き"
status: accepted
project: tecsgen-python3
quarter: Q3-2026
tags:
  - decision
  - tecs
  - tecsgen
---

# Decision: tecsgen-python3 パッケージ構成決定

## Context

[[tecsgen-python3移植計画]] P0 の残り項目。Python 版のモジュール構成は、移植作業の全期間にわたって、移植元との突き合わせのしやすさに影響する。あとから変えるのは難しい。

判断材料（2026-09-26、移植元 r3304 を直接確認）:

- **Ruby 版は、クラスを複数のファイルで再オープンしてメソッドを追加している**。`generate.rb`・`optimize.rb`・`gen_xml.rb`・`tecsinfo.rb`・`unjoin_plugin.rb` が、モデル側のクラスにそれぞれの機能のメソッドを足す。例えば `Celltype` は6ファイル、`Namespace` は6ファイル、`Signature` は5ファイルにまたがる。プラグインでも `HRP2KernelObjectPlugin` が `Cell`・`Region` を再オープンしている。Python にはクラスの再オープンがない
- 読み込み順（`tecsgen.rb` 494〜520行）は、`syntaxobj` → `pluginModule` → `plugin` → `messages` → `types` → `value` → `componentobj` → `expression` → `optimize` → `tecsgen` → `generate` → `gen_xml` → `tool_info` → `tecsinfo` → `unjoin_plugin` → 基底プラグイン8種 → `C_parser` → `ctypes`
- **ファイルをまたいだ同名メソッドの再定義は、モデルクラスには無い**（`RubyVM::AbstractSyntaxTree` による全数確認）。見つかったのは次の2件だけ
  - `location.rb` と `tool_info.rb` が、同じクラス（`Cell_location`・`Join_location`・`TECSGEN` の一部メソッド）を重複定義している。ただし `location.rb` はどこからも読み込まれていない
  - `FuncHead#get_name` が `funchead.rb` の中で2回定義されている（67行目と87行目。Ruby では後の定義が有効）

## Options Considered

### 1. モジュール構成

1. **Ruby 版と1ファイル対1モジュールで対応させる**（採用）
2. 処理フェーズ別（frontend / model / semantics / backend / plugins）に再編する

### 2. 標準プラグインのモジュール名

1. **Ruby と同名**（`HRPPlugin.rb` → `HRPPlugin.py`）（採用）
2. snake_case に変換する（`hrp_plugin.py`）

## Decision

### 1. Ruby 版と1ファイル対1モジュールで対応させる

- 移植元のファイルと突き合わせやすいこと、[[tecsgen内部仕様]] の章との対応が保てることを、Python としての整理より優先する
- **再オープンされたクラスは、機能別モジュールの mixin で表す**。例えば `core/generate.py` に `CelltypeGenerate`・`NamespaceGenerate` などを置き、モデルクラスがそれらを多重継承する（[[tecsgen-python3 P0基本方針決定]] の決定2と整合する）
  - mixin 名は `<クラス名><機能名>`（`CelltypeGenerate`・`CelltypeOptimize`・`CelltypeTecsInfo`・`CelltypeGenXml`・`CelltypeUnjoin`）
  - 並べる順序: Ruby で**後から読み込まれる機能ほど左**に置き、その右に include されたモジュール（include を書いた順の逆）、最後にスーパークラスを置く。例: `class Celltype(CelltypeUnjoin, CelltypeTecsInfo, CelltypeGenXml, CelltypeGenerate, CelltypeOptimize, CelltypePluginModule, PluginModule, NSBDNode)`
  - Python では、クラス本体のメソッドが常に mixin より優先される。Ruby で後から再定義されるメソッドがクラス本体にあると、挙動が逆転してしまう。現時点ではそのような再定義は無いが、移植中に見つけた場合は、後から読み込まれる側の定義だけを移植する（先の定義は Ruby でも実行されない）
- **循環 import の扱い**: モデルクラスどうしは互いに参照し合う。各モジュールで `from __future__ import annotations` を使い、型注釈だけで使う import は `TYPE_CHECKING` の中に置く。実行時に必要な参照は、関数の中で import する
- パッケージの `__init__.py` では何も import しない。`syntaxobj.rb`・`componentobj.rb` は require を並べるだけのファイルなので、`__init__.py` に対応させる

### 2. 標準プラグインは Ruby と同名のモジュールにする

- CDL の `generate(HRPPlugin, ...)` に書かれたクラス名を、そのまま import 名として使える
- `-L` で追加する利用者プラグインも、Ruby 版と同じ探し方（クラス名＝ファイル名）になる
- PEP 8 の命名規則から外れるため、ruff の N999 を `src/tecsgen/plugin/**` で除外する

## 対応表（Ruby → Python）

`tecslib/core/` → `src/tecsgen/core/`。ファイル名は snake_case にする。ただし次の場合は名前を変える。

- Python 標準ライブラリと同名になる: `types` → `cdl_types`、`ctypes` → `c_types`
- 予約語になる: `import` → `import_cdl`

| Ruby | Python | 備考 |
|---|---|---|
| `tecsgen.rb`（トップ） | `cli.py`・`__main__.py` | オプション解析（`analyze_option`）を含む |
| （グローバル変数） | `context.py` | 新設。P0 決定3の設定オブジェクト |
| `tecslib/version.rb` | `version.py` | |
| `core/tecsgen.rb` | `core/tecsgen.py` | `TECSGEN` クラス（run1/run2） |
| `core/tecs_lang.rb` | `core/tecs_lang.py` | |
| `core/messages.rb` | `core/messages.py` | |
| `tecslib/messages/messages_*.rb` | `messages/messages_*.py` | 言語名から動的に選ぶため、ファイル名はそのまま |
| `core/bnf.y.rb`（`Generator` のエラー処理・位置情報） | `core/generator.py` | |
| `core/bnf.y.rb`（構文解析・字句解析） | `syntax/cdl_lexer.py`・`cdl_parser.py`・`cdl_actions.py`・`cdl_tables.py` | 2026-09-27 変更（当初は tree-sitter の構文木を走査する `cdl_builder.py`）。racc の表を移植する方式にしたため4つに分けた → [[tecsgen-python3 構文解析方式決定]] |
| `core/bnf.y.rb`（`TECSIO`） | `syntax/tecsio.py` | 文字コード変換 |
| `core/C_parser.y.rb` | `syntax/cdecl_lexer.py`・`cdecl_parser.py`・`cdecl_actions.py`・`cdecl_tables.py` | 同上（当初は `cdecl_builder.py`） |
| `core/bnf.tab.rb`・`core/C_parser.tab.rb` | （移植しない） | racc の生成物 |
| `core/types.rb` | `core/cdl_types.py` | 名前を変更 |
| `core/ctypes.rb` | `core/c_types.py` | 名前を変更 |
| `core/value.rb`・`expression.rb` | `core/value.py`・`core/expression.py` | |
| `core/plugin.rb`・`pluginModule.rb` | `core/plugin.py`・`core/plugin_module.py` | |
| `core/optimize.rb`・`generate.rb`・`gen_xml.rb`・`tecsinfo.rb`・`unjoin_plugin.rb` | 同名の `.py` | 再オープン部分は機能別 mixin |
| `core/tool_info.rb` | `core/tool_info.py` | |
| `core/location.rb` | （移植しない） | どこからも読み込まれていない。同じクラスを `tool_info.rb` が定義している |
| `core/syntaxobj.rb`・`componentobj.rb` | `core/syntaxobj/__init__.py`・`core/componentobj/__init__.py` | |
| `core/syntaxobj/*.rb`（9ファイル） | `core/syntaxobj/*.py` | 同名 |
| `core/componentobj/*.rb`（19ファイル） | `core/componentobj/*.py` | `import.rb` → `import_cdl.py`、`celltypeModule.rb` → `celltype_module.py`。`generate.rb` は `core/generate.py` とは別パッケージなので同名のまま |
| `tecslib/plugin/*.rb`（78ファイル） | `plugin/*.py` | **Ruby と同名** |
| `tecslib/plugin/lib/*.rb`（7ファイル） | `plugin/lib/*.py` | 同名 |
| `tecsgen/tecs/`（同梱 CDL ライブラリ、928KB） | `tecs/`（パッケージデータ） | 移植元 r3304 からそのまま複製する |
| `tecsmerge.rb` | `tecsmerge.py` | P6 |
| `tecsflow.rb`・`tcflow.rb`・`tecscde.rb`・`tecsgen_rcov.rb` | （対象外） | 計画のスコープ外 |

## Consequences

- 移植元の各ファイルと Python モジュールが1対1で対応するので、移植の進捗をファイル単位で管理できる
- 内部仕様2章（ソースファイル構成）は「全面差替」ではなく、この対応表を中心に書ける。[[tecsgen-python3内部仕様]] の見込みを更新する
- `HRP2KernelObjectPlugin` の `Cell`・`Region` 再オープンは、コア側の mixin では表せないと見ていた。**2026-10-03 解消**: Ruby 版（r3033）でも、この再オープンは `=begin … =end` の中にあり無効なコードだった。Python 版 `HRP2KernelObjectPlugin` は `Cell`・`Region` を拡張せず（状態はクラス変数）、拡張手段を決める必要は無い
- `FuncHead#get_name` は、後の定義（87行目）だけを移植する

## Related

- [[tecsgen-python3移植計画]] — P0 の決定事項
- [[tecsgen-python3 P0基本方針決定]] — 多重継承の決定（本決定の前提）
- [[tecsgen-python3内部仕様]] — 2章・4章の前提
- [[work/active/tecsgen/tecsgen内部仕様 - 02 ソースファイル構成|Ruby版 内部仕様2章]]
- [[tecsgen-python3]]
- [[ソフトウェアアーキテクチャ]]
