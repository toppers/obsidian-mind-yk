---
date: 2026-09-26
description: "tecsgen-python3のP0基本方針3件を決定：CLIをRuby版と完全互換、Ruby mixinは多重継承、グローバル変数は1つの設定オブジェクトへ集約。MRO順の注意点付き"
status: accepted
project: tecsgen-python3
quarter: Q3-2026
tags:
  - decision
  - tecs
  - tecsgen
---

# Decision: tecsgen-python3 P0基本方針決定

## Context

[[tecsgen-python3移植計画]] の P0 で、実装着手前に決める必要のある設計判断が3件あった。いずれも後から変えると移植済みコード全体に影響するため、着手前に確定させる。2026-09-26、ユーザーが3件とも決定した。

## Options Considered

### 1. CLI オプション

1. **Ruby版と完全互換**（採用）
2. Python らしい新しいオプション体系に作り直す

### 2. Ruby mixin の写し方

対象の mixin: `PluginModule`（Cell・Celltype・CompositeCelltype・Signature・Join・ClassType・DomainType・Generate）、`CelltypePluginModule`（Celltype・CompositeCelltype）、`Importable`（Import・Import_C）、`CType`（`ctypes.rb` の C 型クラス10個）、`HasType`（`types.rb` の3クラス）。

1. **多重継承（mixin クラス）**（採用）
2. `typing.Protocol` と委譲で表す
3. 共通処理を関数にしてモジュールに置く

### 3. グローバル変数の扱い

[[reference/tecsgen_ruby_global_variables.csv]] で、当初は111種・809箇所とした。**2026-10-03 に数え直した**: 110種・808箇所（809 は CSV のヘッダ行を含む行数）。正規表現ベースの走査だが、`$1` のような特殊変数は含まれない。Ruby 組み込みは `$LOAD_PATH`（1箇所）だけ。ほかに、実際の変数でないものが混ざる: テンプレート置換の記号（`$id$`・`$cell$`・`$ct$` など。`gsub` の正規表現の中）、RCS キーワード（`$Id: …$`）、racc の表の文字列（`"$start"`・`"$end"`）、メッセージ中の `$RUBYLIB`。移植の対象は設定オブジェクトに集約した実変数で、これらは対象外。

1. **1つの設定オブジェクトへ集約する**（採用）
2. Python のモジュール変数へそのまま写す
3. 用途別に複数の設定オブジェクトへ分ける

## Decision

### 1. CLI は Ruby版と完全に同じにする

- 既存のビルドスクリプト（ASP3/HRP3 の Makefile など）で、コマンド名を変えるだけで置き換えられることを優先する
- オプション名・短縮形・引数の書き方・既定値・環境変数（`TECS_CPP`・`TECSPATH`・`TECSGEN_DEFAULT_RAM`・`TECSGEN_LANG`・`TECSGEN_FILE_LANG`）・終了ステータス・`--version` とバナーの出力文言を一致させる
- 一覧の正本は [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|外部仕様5章]] ではなく、`tecsgen.rb` の `analyze_option` のソースとする（仕様書に漏れがあっても拾えるように）
- Ruby の `optparse` の挙動（長いオプション名の前方一致による省略、`-gdir` のように引数を続けて書く形式）も互換の範囲に含める
- Ruby 固有のオプションは、名前をそのままに意味を Python へ置き換える。`-L, --library-path` はプラグインの探索パスへ追加する。`RUBYLIB` は対応しない（2026-10-01 決定。代わりの環境変数も作らない。[[tecsgen-python3 -L ユーザプラグイン探索設計]]）

### 2. Ruby mixin は多重継承で写す

- mixin は状態を持たない基底クラス（`PluginModule` など）として定義し、`class Cell(PluginModule, NSBDNode)` のように**本来の基底クラスより前**に並べる
- **MRO の順序に注意する**: Ruby では、後から `include` したモジュールほどメソッド探索で先に見つかる。`Celltype` は `include PluginModule` の後に `include CelltypePluginModule` を書いているため、Ruby の ancestors は `Celltype → CelltypePluginModule → PluginModule → NSBDNode` になる。Python では `class Celltype(CelltypePluginModule, PluginModule, NSBDNode)` のように、**include を書いた順の逆**で並べる
- mixin の中の `@@` クラス変数やモジュールメソッド（`def self.xxx`）は、どのクラスが所有するかを移植時に1つずつ確認する（**解消**、2026-10-03 に Ruby 版 r3033 と Python 版を突き合わせた: mixin にあたるモジュール（`CType`・`CelltypePluginModule`・`Importable`・`HasType`）に `@@` は無い。`@@` を持つモジュールは単独で使う `Makefile` だけで、Python 版では `core/tecsgen.py` の `Makefile` クラスの `ClassVar`。モジュールメソッド（`PluginModule.gen_plugin_post_code` など、`TECSInfo.reset_print_info`）は `classmethod` に移した。`types.rb` の `def self.xxx` は `StructType` などのクラスのメソッド。書き方は[[tecsgen-python3内部仕様 - 04 クラス設計#クラス変数|4章]]）

### 3. グローバル変数は1つの設定オブジェクトへ集約する

- CLI 解析の結果と実行中の状態を、1つの設定オブジェクト（仮称 `TecsgenContext`、`dataclass`）にまとめる
- 実行中に値を書き換えられる（mutable）ようにする。Ruby 版では、プラグインが実行中にグローバル変数を書き換える箇所がある（例: TECSInfoPlugin が `--unoptimize-entry` を強制する）
- プラグインからの参照方法（引数で渡すか、モジュールのアクセサで取得するか）は内部仕様12章の執筆時に決める（**解消**: モジュールのアクセサ `get_context()`。[[tecsgen-python3内部仕様 - 12 グローバル変数一覧]]、2026-10-03）
- 内部仕様12章は「Ruby のグローバル変数 → 設定オブジェクトの属性」の対応表として書く

## Consequences

- 受入テスト（Ruby版で作った正解データとの比較）に、CLI の互換性テストを加える。オプションの組み合わせごとに、Ruby版と Python版の終了コードと出力を比べる
- 多重継承にしたので、各クラスの MRO が Ruby の ancestors と一致するかを単体テストで確認する
- 設定オブジェクトがプラグイン API の一部になる。プラグインを移植する前（P5 の前）に属性名を固定する必要がある
- 外部仕様5章・内部仕様4章・内部仕様12章は、この決定を前提に執筆する

## Related

- [[tecsgen-python3移植計画]] — P0 の決定事項
- [[tecsgen-python3]] — 親ノート
- [[tecsgen-python3外部仕様]] — 5章（CLI）
- [[tecsgen-python3内部仕様]] — 4章（クラス設計）・12章（グローバル変数）
- [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|Ruby版 外部仕様5章]]
- [[work/active/tecsgen/tecsgen内部仕様 - 12 グローバル変数一覧|Ruby版 内部仕様12章]]
- [[ソフトウェアアーキテクチャ]]
