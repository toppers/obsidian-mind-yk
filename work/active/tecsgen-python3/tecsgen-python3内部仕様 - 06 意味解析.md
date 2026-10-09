---
date: 2026-09-27
description: "tecsgen-python3内部仕様6章（P3範囲）。TECSGEN.run1の構文解析→意味解析1・2の流れ、Import/Import_Cと差し替え可能なHost、CLIとSystemStackErrorの再現、3チェックポイントのモデルダンプを比べるRubyオラクル差分テストと結果"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 6章 意味解析

[[tecsgen-python3内部仕様]] の6章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 06 意味解析|Ruby版 6章]]。P3（2026-09-27）で実装した範囲を記述する。処理の順序と内容は Ruby 版と同じなので、ここでは Python 版の構成と検証方法を中心に書く。

## 6.1 実行の流れ（`core/tecsgen.py`）

`TECSGEN.run1` が次の3段階を順に呼ぶ（Ruby 版 `core/tecsgen.rb` と同じ）。

| 段階 | 主な処理 |
|---|---|
| `syntax_analisys(argv)` | ルート namespace を作り、引数の CDL をすべて `Import` する。最後に `Generator.end_all_parse` |
| `semantics_analisys_1` | `Cell.create_reverse_join` → `DescriptorType.check_signature` → `Signature.set_descriptor_list` → `Celltype.check_dynamic_join` → `set_definition_join`（1回目）→ ポストコード生成（引数があるときだけ）→ `create_reverse_join` と `set_definition_join`（2回目）→ `set_max_entry_port_inner_cell` → `set_require_join` |
| `semantics_analisys_2` | `Cell.make_cell_list2` → `create_reverse_require_join` → `set_port_reference_count` → `check_join` → `check_ref_but_undef` |

ポストコード生成（`PluginModule.gen_plugin_post_code`）はプラグインが無ければ何もしない。プラグインがあると P5 まで `PluginNotPorted` で止まる（[[tecsgen-python3内部仕様 - 04 クラス設計#4.5 プラグイン|4.5]]）。

`TECSGEN.run2`（最適化・生成）は P4。

## 6.2 Import と Import_C

- **`Import`（`componentobj/import_cdl.py`）**: Ruby 版と同じ2段階の探索（プラグインから呼ばれたときは `$gen` を先に見る → `$import_path` を順に探す）。読込み済みのパス（`expand_path` した値）は2度読まない。見つかった CDL は別の `CdlParser` インスタンスで入れ子にパースする
- **`Import_C`（`componentobj/import_c.py`）**: C ヘッダを cpp に通し、出力を `CdeclParser` で読む
- パースの前後では `Namespace`・`Signature`・`Celltype`・`Cell`・`CompositeCelltype` の入れ子のスタックを積み・戻す（`_push_model_stacks`・`_pop_model_stacks`。P2 では空だった）
- TYPE_NAME の判定は `Namespace.is_typename` につないだ（P2 の差し替え口 `typename_resolver` の既定値）

### ファイルシステムと外部コマンド（`host.py`）

ファイルの存在判定・ディレクトリ一覧・読み書き・`mkdir`・カレントディレクトリ・cpp の実行（`popen_read`）は、すべて `Host` を通す（`get_host()`/`set_host()`）。本番は実際の OS を使い、テストは記録から再生する `RecordedHost` に差し替える（6.4）。

## 6.3 CLI（`cli.py`）

- `tecsgen.rb`（トップ）の `initialize_global_var`・オプション解析（`ruby_optparse.py` で Ruby の OptionParser を再現）・`analyze_option`・`TECS_LANG` の初期化・`TECSGEN.run1` を、同じ順序で呼ぶ。設定は `TecsgenContext` に入れる（[[tecsgen-python3内部仕様 - 12 グローバル変数一覧#12.4 対応表（P3 分）|12.4]]）
- `cli.run(argv, environ, base_path)` が終了コードを返す（テストから直接呼べる形）
- **無限再帰**: `ErrorCase/attribute-err` では Ruby 版が `SystemStackError` で止まる（ユーザー決定により同じ落ち方を再現）。Python 版は `RecursionError` を捕まえて、標準エラーに `tecsgen: stack level too deep (SystemStackError)` を1行出し、終了コード1で終える。比べるのは標準出力・終了コード・標準エラーの例外名まで（バックトレースは比べない）

## 6.4 差分テスト

### 記録（Ruby 版オラクル）

`tests/ruby/p3_oracle.rb` を `ruby -r` で読み込ませ、正解データの全155ケースを実行して記録する（`tools/port/run_p3_oracle.sh`、WSL）。記録は `tests/golden/p3/<ケース>.jsonl.gz`（約11MB）。2回採って同一になること（決定的であること）を確認した。

- **3つのチェックポイント**（`parse`: `end_all_parse` の直後、`sem1`: 意味解析1の後、`sem2`: 意味解析2の後）で、モデルのダンプ・それまでの標準出力・エラーと警告の件数
- **モデルのダンプ**: ルート namespace と、モデルのクラス変数から辿る反射的なダンプ。オブジェクトは `{"c": クラス名, "iv": {変数名: 値}}`、2回目以降の出現は `{"ref": 番号}`。Symbol は `{"y": 名前}` で String と区別する
- **外部とのやりとり**: ファイルの存在判定・ディレクトリ一覧・読んだファイル・cpp の出力。同じコマンドがケース内で何度も呼ばれるので、cpp の出力は呼び出し順の列で持つ
- **ノイズの除去**: Ruby 処理系自身のファイル（`/usr/lib/ruby/`・`/var/lib/gems/`・`*.rb` など）への問い合わせだけを除く。範囲を広げると `/usr/include` の問い合わせまで消えて再生がずれる
- `PluginModule#load_plugin` の呼び出し（プラグインを読んだケースの判定に使う）

### 比較（`tests/test_p3_model.py`）

- `RecordedHost` で記録を再生するので、Windows でも Ruby と移植元なしで動く
- `tests/p3_model_dump.py` が Python 側を同じ形式でダンプし、Ruby 側とオブジェクトを対応付けながら構造を比べる（属性名は `_x` ↔ `@x`）
- 比べないもの: `TOOL_INFO`（P4）、`TECSGEN::Join_location`・`TECSGEN::Cell_location`（obsolete）、プラグインの基底クラス `ThroughPlugin`（P5）のクラス変数
- プラグインを読むケースはスキップ（P5 まで。ユーザー決定）。`attribute-err` は `tests/test_p3_cli.py` で CLI として確認する

### 結果（as of 2026-09-27）

| 対象 | 結果 |
|---|---|
| プラグインを読まない119ケース × 3チェックポイント | モデルのダンプ・標準出力・件数がすべて一致 |
| プラグインを読む35ケース | 対象外（P5） |
| `ErrorCase/attribute-err` | 標準出力一致・終了コード1・標準エラーに `SystemStackError` |
| テスト全体 | Windows 789 passed / 36 skipped、WSL 784 passed / 41 skipped（WSL で多い分は Ruby を要する P1 のテスト） |

## Ruby版との差異

- 処理の順序と結果は Ruby 版と一致させる。構造上の差異は、外部とのやりとりを `Host` に集めたこと
- `SystemStackError` の再現は、標準エラーの1行目までに限る

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 04 クラス設計]] / [[tecsgen-python3内部仕様 - 05 字句解析・構文解析]]
- [[tecsgen-python3移植計画]] — P3
- [[work/active/tecsgen/tecsgen内部仕様 - 06 意味解析|Ruby版 6章]]
- [[Patterns - 検証と調査#移植の正解は、移植元を実際に実行するオラクルで取る（2026-09-27）|オラクルのパターン]]
