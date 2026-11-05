---
date: 2026-09-27
description: "tecsgen-python3内部仕様11章。Generatorのエラー/警告/情報の報告と位置選択、TECSMsgと移植したメッセージ表、Ruby String#subの置換規則の再現、Node.cdl_error系、差分テストでの検証結果"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 11章 エラー・警告処理

[[tecsgen-python3内部仕様]] の11章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 11 エラー・警告処理|Ruby版 11章]]。エラー番号体系（S/G/W/T/E/I/P/B/H/C/V）と出力書式は Ruby 版と**一致させる**（受入基準）。P1（2026-09-27）で実装。

## 11.1 Generator（`core/generator.py`）

Ruby 版の `Generator` は racc のパーサクラスで、構文解析とエラー報告を兼ねる。Python 版では構文解析を `syntax/cdl_builder.py`（P2）へ分け、`core/generator.py` にはエラー報告とパーサの入れ子状態だけを置いた。

- 件数: `_n_error`・`_n_warning`・`_n_info`（`get_n_*`）
- `error`/`error2`・`warning`/`warning2`・`info`/`info2` → 共通の `_report(locale, kind, msg, args)`
  1. `TECSMsg.get_*_message(body)` で番号から現在の言語の本文を引く（表に無ければ呼び出し側の本文のまま）
  2. `$1`, `$2`, … を引数で置換する。**Ruby の `String#sub!` と同じく、置換文字列中の `\1`・`\&`・`\\`・`` \` ``・`\'`・`\k<name>` を解釈する**（`ruby_compat.sub_first`）。引数は Ruby の `to_s` 規則で文字列にする（nil → 空、true → `true`、Float は Ruby の書式）
  3. 位置の選び方: import_C 中は C パーサの位置、そうでなければ「全構文解析が完了する前」または「locale が nil」のとき**解析中の位置**を使う（Node が記憶した位置は構文解析後にだけ使われる）
  4. `<file>:<line>:<col>: <kind>: <msg>` を `Console.puts` で出す。位置が無ければ `<kind>: <msg>`
- パーサの入れ子: `push_parser`/`pop_parser`/`current_parser`/`set_current_locale`。Ruby の配列の添字規則を `_get_at`/`_set_at` で再現した。`@@generator_nest == -1`（全パース終了後）で `current_locale` を引くと、**Ruby の `arr[-1]` と同じく最後に解析した位置**が返る（`test_after_parse_uses_given_locale` で固定）
- 警告・情報で本文に番号が無い場合、Ruby 版は `nil.to_sym` で例外になる。Python 版も `TypeError` にした
- `print_report()`（tecsgen.rb のトップレベル関数）もここに置いた: `N error(s)  M warning(s)`
- テスト用に `Generator.reset()` を追加（Ruby 版には無い）

## 11.2 TECSMsg とメッセージ表

- `core/messages.py` の `TECSMsg`。表は `tecsgen/messages/messages_{console,file}_{en_US,ja_JP}.py`（Ruby と同名）
- 表は `tools/port/gen_messages.py` で**生成**する。Ruby 自身にソースを eval させて JSON に書き出す（`tools/port/dump_messages.rb`）ので、文字列リテラルのエスケープや複数行リテラルの解釈が Ruby と一致する。件数: エラー334・警告32・情報0（console）、コメント78（file）、各2言語
- 番号の抽出は Ruby の `/^[A-Z0-9]+/`（`^` は行頭なので複数行の本文では2行目以降も対象）を `re.MULTILINE` で再現

## 11.3 Node の報告メソッド（`core/syntaxobj/node.py`）

- `Node.__init__` で `Generator.current_locale()` を記憶する
- `cdl_error`/`cdl_warning`/`cdl_info` は記憶した位置、`*2` は引数の位置、`cdl_error3` は位置なしで報告してから `check: <file>: line <n> for above error` を出す
- `BDNode`（owner）・`NSBDNode`（namespace）も移植した。`Import.get_current`（P2）と `Namespace`（P3）は関数内 import で参照する

## 11.4 検証（2026-09-27）

| テスト | 内容 | 結果 |
|---|---|---|
| `test_p1_ruby_oracle.py` | 移植元のソースを Ruby で実行するオラクル（`tests/ruby/p1_oracle.rb`）と比較。全メッセージ番号 × 特殊な置換文字列（`\1`・`\\`・`\k<x>` など）× 2言語、LANG 判定18通り、`parse_lang`、`to_s`/`inspect` | Windows（Ruby 4.0.6）・WSL（Ruby 3.2.3、正解データと同じ版）とも一致 |
| `test_p1_golden_messages.py` | 正解データ155ケースの stdout にあるエラー・警告行のうち、表に番号がある684行が、本文の雛形（`$n` は任意）と一致するか | 全行一致 |
| 同上 | meta.json の件数（print_report 由来）と出力行数の一致 | 2件を除き一致（下記） |
| `test_p1_units.py` | 位置の選択規則、件数、Token、NamedList、TECSIO、AppFile、CFile、Console | 通過 |

件数が合わない正解データ2件（どちらも Ruby 版自体の挙動。テストでは理由付きで除外）:

- `ErrorCase/attribute-err`: 意味解析中に `SystemStackError`（`expression.rb` の `elements_eval_const` の無限再帰）で異常終了し、print_report に届かない。**Python 版で `RecursionError` をどう扱うか（終了コード1と stderr の文言）を P3 で決める**
- `celltypePlugin`: エラー行が出るのに件数の行が無く、終了コードも0。これは Ruby 版の挙動で、Python 版も同じ出力・終了コード 0 で一致している（P5h、2026-09-28）

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 10 ファイル入出力]] / [[tecsgen-python3内部仕様 - 12 グローバル変数一覧]]
- [[tecsgen-python3移植計画]] — P1
- [[work/active/tecsgen/tecsgen内部仕様 - 11 エラー・警告処理|Ruby版 11章]]
