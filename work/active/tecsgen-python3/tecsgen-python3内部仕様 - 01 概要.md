---
date: 2026-10-02
description: "tecsgen-python3内部仕様 第1章（概要）— 移植の位置付け、Ruby版との対応の取り方、構成要素（cli・core・syntax・plugin・tecs）、移植で新設した層（Host・TecsgenContext・ruby_compat）と検証の考え方。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3内部仕様]] の第1章（全12章）。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 01 概要|Ruby版 第1章]]。

## 1. 概要

### 1.1 位置付け

tecsgen-python3 は Ruby 版 tecsgen v1.9.1（`branches/ykominami_r3033`）の Python 3 への移植です。**Ruby 版の実行結果を正解**とし、同じ入力に対する生成物・標準出力・終了コードの一致を受入基準にします（[[tecsgen-python3外部仕様 - 04 出力|外部仕様 4章]]）。そのため、設計は Python として整えるよりも、Ruby 版との突き合わせのしやすさを優先します。

### 1.2 Ruby 版との対応の取り方

| 方針 | 内容 | 決定 |
|---|---|---|
| 1ファイル対1モジュール | Ruby のファイルと Python のモジュールを同名で対応させる（[[tecsgen-python3内部仕様 - 02 ソースファイル構成\|2章]]） | [[tecsgen-python3 パッケージ構成決定]] |
| 多重継承 | Ruby の再オープンされたクラス・mixin は、機能別 mixin の多重継承で表す（4章） | [[tecsgen-python3 P0基本方針決定]]・[[tecsgen-python3 Mixin粒度決定]] |
| 設定オブジェクト | Ruby のグローバル変数は `TecsgenContext` に集約する（12章） | 同上 |
| 構文解析 | Ruby 版の字句解析器と racc の LALR 表を移植して動かす（5章） | [[tecsgen-python3 構文解析方式決定]] |
| Ruby の癖は再現する | 優先順位の誤り、nil の扱い、`sprintf` の幅などをそのまま写す。一致は「同じ振る舞い」で測る | 計画ノートの基本方針 |

### 1.3 構成要素

```
src/tecsgen/
  cli.py, __main__.py        コマンドライン（オプション解析・実行の入口）
  context.py                 設定オブジェクト（Ruby のグローバル変数）
  host.py                    ファイル・カレントディレクトリ・外部コマンドの窓口
  state.py                   モデル側のクラス変数の初期化（テスト用）
  ruby_compat.py             Ruby の to_s・sub・Symbol・数値変換などの再現
  ruby_optparse.py           Ruby の optparse の再現
  tecsmerge.py               tecsmerge
  core/                      本体（モデル・意味解析・最適化・生成）
    syntaxobj/, componentobj/
  syntax/                    字句解析・構文解析（CDL と import_C の C ヘッダ）
  plugin/                    標準付属プラグイン
  messages/                  メッセージ表
  tecs/                      同梱の標準 CDL ライブラリ
```

### 1.4 Python 版で新設した層

Ruby 版にはなく、Python 版の検証と配布のために置いたもの。

| 層 | 役割 |
|---|---|
| `Host`（`host.py`） | `File.exist?`・`Dir.chdir`・`IO.popen` などを1か所に集める。差分テストでは Ruby 版の記録を再生する `RecordedHost` に差し替え、移植元のテストツリーや cpp が無い環境でも同じ入力を与える |
| `TecsgenContext`（`context.py`） | グローバル変数の集約。属性名は Ruby の変数名を snake_case にしたもの |
| `ruby_compat.py` | 出力をバイト単位で一致させるための Ruby 組み込みの再現。標準出力の改行は常に LF |
| `state.py` | 1プロセスで何度も実行するテストのために、クラス変数をまとめて初期化 |

### 1.5 検証の仕組み

1. **正解データ**: Ruby 版を実行して採る（`tests/golden/`、手順は `tools/golden/README.md`）。テストケース 155 件（うちプラグイン不使用 119、プラグイン使用のものはカーネル 11 を加えて 46 件）、配布パッケージ 16、`tecsmerge` 73 シナリオ、`--help`・`--version`
2. **オラクル**: Ruby 版に小さなフックを足して、パース後・意味解析後のモデルを JSON で記録し、`RecordedHost` で再生して Python 版のモデルと比べる（`tests/ruby/p3_oracle.rb`）
3. **比較の段階**: 生成物だけでなく、フェーズごとの内部状態も比べる。どこでずれたかを特定するため
4. **実行**: `pwsh tools/port/wsl_check.ps1`（WSL で uv sync・ruff・ty・pytest を一括）

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3移植計画]] — フェーズと進捗
- [[tecsgen-python3外部仕様]]
