---
date: 2026-09-27
description: "tecsgen-python3内部仕様7章（P4）。TECSGEN.run2のoptimize_and_generate・finalize・dump_tecsgen_rbdmp、optimize.rbのセルID付け・ドメイン分け・呼び口/受け口最適化をmixinで移植した構成とRuby互換の注意点"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 7章 最適化

[[tecsgen-python3内部仕様]] の7章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 07 最適化|Ruby版 7章]]。P4（2026-09-27）で実装した。処理の順序と内容は Ruby 版と同じなので、Python 版の構成と Ruby 互換のための注意点を書く。

## 7.1 実行の流れ（`core/tecsgen.py`）

`cli.run` は `run1`（[[tecsgen-python3内部仕様 - 06 意味解析|6章]]）の後に `run2` と `dump_tecsgen_rbdmp` を呼ぶ（Ruby 版トップの `tecsgen.rb` と同じ順）。

| メソッド | 内容 |
|---|---|
| `optimize_and_generate` | link root ごとに: `-G` の絞り込み → セルの無い region を飛ばす → `$gen` の決定（link root が複数なら `gen/<region>` を `mkdir`）→ `reset_optimize` → エラーが無ければ `set_cell_id_and_domain` と（`-U` でなければ）`optimize` → `-s` なら木を表示 → エラーがあれば `print_report` して終了コード1 → `generate`・`generate_post`（[[tecsgen-python3内部仕様 - 08 コード生成|8章]]） |
| `finalize` | `-G` で link root でないものの警告 → エラーが無ければ `AppFile.update` → `print_report` → エラーがあれば標準エラーに1行出して終了コード1 → `gen/tecsgen.timestamp`（空）を書く |
| `dump_tecsgen_rbdmp` | link root ごとに `reset_optimize`・`set_cell_id_and_domain`・`optimize` をやり直す。**`tecsgen.rbdmp`（Marshal 形式）は書かない**（[[tecsgen-python3 P0基本方針決定]]）。代わりに最後に `tecsgen.pickle` を書く（`core/unjoin_plugin.py` がプラグインの参照を外す。[[tecsgen-python3移植計画]]）。`-v` ではやり直しの経過が標準出力に出るので、そこも移植した |

`exit n` は `TecsgenExit` を投げ、`cli.run` が終了コードに変える。Ruby の `rescue`（StandardError）で捕まえない例外（`TecsgenExit`・`RecursionError`・未移植部分の `NotImplementedError`）は、`generate.reraise_if_not_standard_error` で投げ直す。

## 7.2 optimize.rb（`core/optimize.py`）

Ruby 版は `Namespace`・`Celltype` を再オープンしている。Python 版は `NamespaceOptimize`・`CelltypeOptimize` の mixin にして、各クラスの基底に入れた（[[tecsgen-python3 Mixin粒度決定]]）。

- **セル ID**（`set_cell_id`）: ID 指定のあるセルを先に置き、残りを空いた番号に詰める。S3001（`id > 0` なら `id >= セル数` でエラー。上限ちょうどでもエラーになる Ruby 版の判定をそのまま再現）・S3002・S3003
- **ドメイン**（`set_domain`・`set_domain_class`）: `@domain_roots`・`@domain_class_roots`・`@domain_class_roots2`・`@@domain_class_roots` を作る。インスタンス変数 `@domain_class_roots` とクラス変数 `@@domain_class_roots` は Python では同じ属性名 `_domain_class_roots` になるので、インスタンス側は `__dict__` で読み書きする
- **呼び口最適化**（`optimize_call`）: 呼び先のセル・ポートを集めて重複を除き、`cell_unique`・`skelton_useless`・`VMT_useless` を決める。重複除去は Ruby の `uniq`（モデルのオブジェクトは同一性で比べる）
- **受け口最適化**（`optimize_entry`）: 呼び口側の結果を受け口へ伝える。`$unopt_entry` なら行わない
- `header_included?` → `header_included`（生成時にヘッダの `#include` を1回だけにする）

## 7.3 検証

[[tecsgen-python3内部仕様 - 08 コード生成#8.5 差分テスト|8.5]] の通しの差分テストで、生成物と標準出力（`-v` の ID 付け・最適化の経過を含む。`top/id` など）を比べる。
