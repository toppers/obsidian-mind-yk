---
date: 2026-09-27
description: "tecsgen-python3のCDL・import_C構文解析をtree-sitterからracc表駆動へ切替。Ruby字句解析器を移植しbnf.tab.rbのLALR表とracc C実装(cparse)の駆動部を再現。実測でtree-sitterはエラー位置・回復・TYPE_NAMEを再現できないと判明"
status: accepted
project: tecsgen-python3
quarter: Q3-2026
tags:
  - decision
  - tecs
  - tecsgen
---

# Decision: tecsgen-python3 構文解析方式決定

## Context

[[tecsgen-python3移植計画]] の P2 は、tree-sitter の構文木を走査してモデルを組み立てる計画だった（P0 の [[tecsgen-python3 tree-sitter読み込み方式決定]] もこの前提）。移植計画の主要リスク「tree-sitter 文法が racc 文法と同じ言語を受理しない」の対策として、P2 の最初に実測した（2026-09-27）。

WSL で正解データの全155ケースを Ruby 版で実行し直し、`Generator#parse` をフックして Ruby 版が実際にパースした384ファイルを記録した（フックを入れても stdout は正解データと全件一致）。同じファイルを tree-sitter-cdl でパースして突き合わせた結果:

| 判定 | 件数 | 内容 |
|---|---|---|
| 両方とも受理 | 361 | 正常系はほぼ通る |
| tree-sitter だけ拒否 | 1 | `sjis.cdl`。SJIS の2バイト目の 0x5C（`\`）をバイト単位で読むと文字列のエスケープになる |
| tree-sitter だけ受理 | 3 | `[in]int32`・`typedef bool BOOL` など。Ruby 版は TYPE_NAME をシンボル表で判定するので構文エラーになる |
| 両方エラー | 19 | うち `error-6/7/8`・`sample1_flat` などは位置・件数が違う。racc の `statement: error` によるエラー回復は、tree-sitter の ERROR ノードから再現できない |

受入基準は、エラーコード・件数・終了コードまで Ruby 版と一致すること（[[tecsgen-python3外部仕様]]）。G1016 の位置と `near '…'` の切り出し、エラー回復後の件数は、tree-sitter の構文木からは作れない。

## Options Considered

1. **racc 表駆動に切り替える**（採用）— Ruby の字句解析器を移植し、`bnf.tab.rb`・`C_parser.tab.rb` の LALR 表を Ruby に eval させて取り出し、racc の駆動部を Python に移植する
2. **tree-sitter を続ける** — 正常系は通るが、構文エラーの位置・件数・回復の一致は諦めるか、ケースごとに個別対応する。TYPE_NAME は Builder 側で後から判定する
3. **併用** — 正常系は tree-sitter、ERROR が出たときだけ racc 互換パーサで再パースしてエラーを出す。パーサを2系統保守することになる

## Decision

**racc 表駆動に切り替える**（2026-09-27、ユーザー決定）。

- 文法アクション（CDL 325個、C 121個）の移植量は、どの方式でも同じ。tree-sitter の Builder も同じ意味処理を同じ順序で再現する必要があった
- 表を取り出すので、文法を別に書き直す必要がなく、受理する言語が構造上 Ruby 版と一致する
- TYPE_NAME の判定（字句解析器がシンボル表を引く）も、Ruby 版と同じ位置で行える

## Consequences

- tree-sitter の文法・C 拡張・`tree-sitter` 依存を削除し、ビルドバックエンドを hatchling に戻した（リポジトリ `6d69710`）。[[tecsgen-python3 tree-sitter読み込み方式決定]] は superseded
- **移植元は racc の C 実装（`cparse.c`）**。Ruby 版 tecsgen は cparse を使っており、pure-Ruby 実装（`racc/parser.rb`）とはエラー回復の挙動が違う。cparse は error トークンを shift しても先読みを捨てず、`_reduce_none` を呼ばない。最初に pure-Ruby 実装を写したところ、構文エラーの20ケースがすべて一致せず、cparse.c を読んで判明した（詳細は [[tecsgen-python3内部仕様 - 05 字句解析・構文解析|内部仕様5章]]）
- CDL の字句解析は latin-1 で1バイト＝1文字として走査する（Ruby の ASCII-8BIT と同じ）。`sample/error-13` の `near '\xe3'` もこれで再現できた
- 文法アクションの本体は P3 のモデルクラスに依存するので、P2 では骨格だけを生成し、字句解析の状態を変える呼び出しだけを移植した。P2 の合格条件は「字句解析と駆動部が Ruby と完全一致すること」に変え、「パース直後のモデル JSON の一致」は P3 へ移した
- `tools-ts/` の tree-sitter 文法は、TECSCDE（[[CDLParser(tree-sitter利用-JS版)]]）では引き続き使われている。影響するのは tecsgen-python3 だけ

## Related

- [[tecsgen-python3移植計画]] — P2 の結果
- [[tecsgen-python3 tree-sitter読み込み方式決定]] — 置き換えた決定
- [[tecsgen-python3内部仕様 - 05 字句解析・構文解析]] — 実装の詳細
- [[tecsgen-python3]]
- [[reference/Racc代替のPythonパーサジェネレータ比較|Racc代替のPythonパーサジェネレータ比較]]・[[reference/tecsgen動的typedef判定とPythonパーサ選定|tecsgen動的typedef判定とPythonパーサ選定]] — 事前の検討。本決定は代替ジェネレータを使わず、racc の生成済み表そのものを使う
- [[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析|tecsgen内部仕様 5章]] — 移植元
- [[perf/competencies/ソフトウェアアーキテクチャ|ソフトウェアアーキテクチャ]] — 実測に基づいて自分たちの先行決定を覆した設計判断
- [[perf/competencies/開発ツール・自動化基盤|開発ツール・自動化基盤]] — Ruby 版の実行を記録するオラクルと差分テスト基盤
