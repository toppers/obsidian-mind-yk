---
date: 2026-11-01
description: "TECS の CDL で `[ ... ]` の中に書ける指定子 36 個の一覧と、書ける場所・書式。context の引数（task・non-task・any）も。Ruby 版 tecsgen の文法から"
tags:
  - reference
  - tecs
  - tecsgen
  - cdl
---

# TECS CDL の指定子一覧

CDL の `[ ... ]` の中に書ける指定子（specifier）の一覧。書式は `[ 指定子, 指定子, … ]` で、カンマで並べる。

**出典（2026-11-01 に確認）**: Ruby 版 tecsgen（環境の 1.9.1）の文法ファイル `tecslib/core/bnf.y.rb`。`RESERVED2`（コメント「指定子 `[]` 内でのみ使用できるキーワード」）の 36 語と、各規則（`parameter_specifier`、`statement_specifier`、`celltype_statement_specifier`、`attribute_specifier`、`var_specifier`、`region_specifier`、`join_specifier`）を読んだ。`context` の引数は `componentobj/signature.rb`。tecsgen-python3 版が同じかは未確認。

これらの語は**指定子の `[ ]` の中でだけ**予約語で、外では識別子として使える。

## パラメータ（シグニチャの関数の引数）
| 指定子 | 書式 | 意味 |
|---|---|---|
| `in` | `in` | 入力 |
| `out` | `out` | 出力 |
| `inout` | `inout` | 入出力 |
| `send` | `send(アロケータ)` | 送信（アロケータ名を指定） |
| `receive` | `receive(アロケータ)` | 受信（アロケータ名を指定） |
| `size_is` | `size_is(式)`、`size_is(式, 最大値)` | 配列・ポインタの大きさ |
| `count_is` | `count_is(式)` | 要素の個数 |
| `string` | `string`、`string(式)` | 文字列（長さの指定も可） |
| `nullable` | `nullable` | NULL を許す |

`string`・`size_is`・`count_is` は、ポインタにも書ける。`typedef` には `string`、`string(式)` も書ける。

## シグニチャ全体・関数
| 指定子 | 書式 | 意味 |
|---|---|---|
| `callback` | `callback` | コールバック指定 |
| `context` | `context("task")` など | 呼び出されるコンテキスト。引数は下の「context の引数」 |
| `deviate` | `deviate` | 逸脱の指定 |
| `oneway` | `oneway` | 一方向の関数（戻り値や応答を待たない） |

## セルタイプ・コンポジット
| 指定子 | 書式 | 意味 |
|---|---|---|
| `singleton` | `singleton` | セルを1つしか作れない（コンポジットも可） |
| `idx_is_id` | `idx_is_id` | 索引を ID として使う（コンポジットでは効果なし） |
| `active` | `active` | アクティブなセルタイプ（コンポジットも可） |
| `pseudo_active` | `pseudo_active` | 疑似アクティブ |

## 呼び口・受け口（`celltype` の中の `call`／`entry` の前）
| 指定子 | 書式 | 意味 |
|---|---|---|
| `inline` | `inline` | インライン展開（受け口） |
| `ref_desc` | `ref_desc` | 受け口の記述子を参照（呼び口も可） |
| `optional` | `optional` | 呼び口を結合しなくてもよい |
| `dynamic` | `dynamic` | 動的結合（呼び口） |
| `omit` | `omit` | 省略可（呼び口・属性） |
| `allocator` | `allocator(ポート名.関数名 = 初期化子, …)` ほか | アロケータの指定。`=` は内部アロケータ、`<=` は多段リレーモデル向き |

コンポジットの呼び口・受け口には、`allocator`、`omit`、`optional`、`ref_desc`、`dynamic` を書ける。

## 属性・内部変数
| 指定子 | 書式 | 対象 |
|---|---|---|
| `omit` | `omit` | 属性 |
| `size_is` | `size_is(式)` | 属性、内部変数（`var`） |
| `choice` | `choice = { "文字列", … }` | 属性。取りうる文字列の選択肢 |

## セル
| 指定子 | 書式 | 意味 |
|---|---|---|
| `id` | `id(定数式)` | セルの ID |
| `prototype` | `prototype` | プロトタイプ宣言 |
| `restrict` | `restrict(…)` | 結合の制限 |
| `allocator` | `allocator(…)` | アロケータの指定 |
| `through` | `through(ポート名, プラグイン名, 引数)` | 結合にプラグインを通す |

結合（`join`）の側には、`through(プラグイン名, 引数)` を書ける（ポート名は無し）。

## リージョン
| 指定子 | 書式 | 意味 |
|---|---|---|
| `node` | `node` | ノード（リージョンの種別） |
| `linkunit` | `linkunit` | リンク単位 |
| `domain` | `domain(種別, 名前)` | ドメイン |
| `class` | `class(種別, 名前)` | クラス |
| `in_through` | `in_through(プラグイン名, 引数)`、`in_through()` | 領域に入る結合へのプラグイン（`()` は入りを許可） |
| `out_through` | `out_through(プラグイン名, 引数)`、`out_through()` | 領域から出る結合へのプラグイン |
| `to_through` | `to_through(領域名, プラグイン名, 引数)`、`to_through(領域名)` | 指定領域への結合へのプラグイン |
| `from_through` | `from_through(領域名, プラグイン名, 引数)`、`from_through(領域名)` | 指定領域からの結合へのプラグイン |

## 通常のキーワードでもあるもの
`generate(プラグイン名, 引数)` は、セルタイプ・セルの指定子として書ける。ただし `generate` は通常のキーワード（`RESERVED`）で、`RESERVED2` の 36 語には含まれない。

## context の引数
`context( … )` の引数に指定できる文字列は、**次の3つ**。

| 引数 | 意味 | 備考 |
|---|---|---|
| `"task"` | タスクコンテキストから呼ばれる | **未指定のときの既定値**（`Signature#get_context` が `task` を返す） |
| `"non-task"` | 非タスクコンテキスト（割込みハンドラなど）から呼ばれる | |
| `"any"` | どのコンテキストからも呼べる | |

- 書式は `[context("non-task")]` のように、シグニチャの前に書く。引数は文字列リテラル（二重引用符で囲む）。
- 上の3つ以外の文字列は、エラーではなく**警告 `W1001`**（「unknown context type. usually specify task, non-task or any」）。
- **重複**して指定すると、エラー `S1001`（「context specifier duplicate」）。
- 文法上は文字列のリスト（`string_literal_list`）だが、実装は**1つの文字列**として扱う。複数を並べたときの意味は未確認（TBC）。
- 使われ方: 生成する C の注釈（`context: …`）に出る。RPC 系のプラグインが参照し、`HRPRPCPlugin` は `"non-task"`・`"any"` を見て分岐する。`GenOpaqueMarshaler` と `GenTransparentMarshaler` は、`"task"` 以外だとエラーにする（`OPQ9999`）。

## 未確認の点（TBC）
- `restrict` の引数、`generate`・`through` の引数の細部、`allocator` の `alloc_list` の細部は、文法の一部しか読んでいない。
- tecsgen-python3 版が同じ集合かどうか。
- TECSCDE-DT-EL の CDL パーサ（tree-sitter 文法）が、これらの指定子をどこまで扱うか。

## Related
- [[tecsgen外部仕様 - 03 入力]] — CDL の入力
- [[tecsgen]] — tecsgen 仕様書群の入口
- [[tecsgen内部仕様 - 05 字句解析・構文解析]] — 字句・構文解析
