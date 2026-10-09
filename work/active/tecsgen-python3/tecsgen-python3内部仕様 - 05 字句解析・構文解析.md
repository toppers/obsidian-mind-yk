---
date: 2026-09-27
description: "tecsgen-python3内部仕様5章。Ruby字句解析器の移植（latin-1で1バイト=1文字）、racc LALR表の抽出、racc C実装(cparse)準拠の駆動部とエラー回復、TYPE_NAME判定、文法アクション（P3で全移植）、Ruby実行オラクルによる差分テスト"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 5章 字句解析・構文解析

[[tecsgen-python3内部仕様]] の5章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析|Ruby版 5章]]。P2（2026-09-27）で実装した範囲と、P3 で移植した文法アクションを記述する。方式は [[tecsgen-python3 構文解析方式決定]] のとおり、Ruby 版の racc の表をそのまま使う。

## 5.1 構成

Ruby 版の `Generator`（`bnf.y.rb`）は、字句解析・構文解析・文法アクション・エラー報告を1クラスで兼ねる。Python 版は次のように分けた（`src/tecsgen/syntax/`）。

| Ruby 版 | Python 版 | 内容 |
|---|---|---|
| `Generator#parse` の走査ループ | `cdl_lexer.py`（`lex_files`・`RESERVED`） | トークン列 `@q` を作る |
| `Generator#parse`・`next_token`・`on_error`・`RESERVED2` | `cdl_parser.py`（`CdlParser`） | TYPE_NAME と指定子キーワードへの置換、G1015/G1016 |
| `Generator#_reduce_N` | `cdl_actions.py`（`CdlActions`、mixin） | 文法アクション（P3 で全移植） |
| `bnf.tab.rb` の `Racc_arg` | `cdl_tables.py`（生成物） | LALR 表 |
| `Generator` のエラー報告・入れ子の状態 | `tecsgen.core.generator.Generator`（P1） | [[tecsgen-python3内部仕様 - 11 エラー・警告処理\|11章]] |
| `C_parser`（`C_parser.y.rb`・`.tab.rb`） | `cdecl_lexer.py`・`cdecl_parser.py`（`CdeclParser`）・`cdecl_actions.py`・`cdecl_tables.py` | import_C 用 |
| racc ランタイム（`Racc::Parser`） | `racc_runtime.py`（`RaccParser`） | 表の駆動部 |

`CdlParser` は `CdlActions` と `RaccParser` を多重継承する（[[tecsgen-python3 P0基本方針決定]] の mixin の写し方）。

## 5.2 字句解析

- Ruby 版と同じく、1行ずつ正規表現を**同じ順序で**当てる。コメントは `/* */` と `+---` 〜 `---+` の2種類、行をまたぐ文字列（行末 `\`）もある。改行を含む文字列のエラーは、Ruby 版と同じく `Generator.error` を通さず直接出力し、件数だけ加算する
- **文字コード**: Ruby 版は Shift_JIS 以外を ASCII-8BIT で読み、1バイトを1文字として走査する。Python 版は latin-1 で復号して同じにする。桁もバイト単位になり、非 ASCII 文字の先頭バイトだけが未知の記号として切り出される（`near '\xe3'`）。切り出した値は latin-1 のバイト列に戻してから `file_codec`＋`surrogateescape` で復号し直し、[[tecsgen-python3内部仕様 - 10 ファイル入出力|10章]] の文字列表現にそろえる。Shift_JIS は cp932 で復号し、文字単位で走査する
- 正規表現は `re.ASCII` で使う（Ruby の `\s`・`\w` は ASCII-8BIT では ASCII だけに当たる）。Windows-31J の全角文字・半角カナには `\w`・`\s` は当たらない（Ruby 3.2.3（WSL）と 4.0.6 で確認、2026-10-03。Shift_JIS・EUC-JP・ASCII-8BIT でも同じ）ので、`re.ASCII` で一致する
- Ruby 版の誤記と思われる箇所もそのまま写した（改行を含む文字列の正規表現の `\e`）
- C ヘッダ側は行末の空白を先に取り除く（Ruby の `rstrip!`。NUL も取り除くので、Python の `rstrip()` の既定は使わない）。整数の接尾辞を付けたまま `to_i` する
- 読み込みに失敗すると CDL は G1014、C は B1002＋`print_exception`（Ruby の例外メッセージの書式は Ruby 3.2 に合わせた。ファイル無し・ディレクトリの2種は、Ruby 3.2.3 の `Errno::ENOENT` の `No such file or directory @ rb_sysopen - …`、`Errno::EISDIR` の `Is a directory @ io_fread - …` と文字列が一致することを実行で確認した（2026-10-03）。権限無し（`Permission denied @ rb_sysopen - …`）は書式からで、実行では未確認）

## 5.3 LALR 表

`tools/port/gen_racc_tables.py` が、Ruby に `bnf.tab.rb`・`C_parser.tab.rb` を eval させて `Racc_arg` を JSON で受け取り、Python モジュールにする（P1 のメッセージ表と同じ方式）。

- `bnf.tab.rb` は Racc 1.4.14、`C_parser.tab.rb` は Racc 1.8.1 の生成物。表の形式は同じ
- トークン種別は、Ruby の Symbol（`:IDENTIFIER`）も String（`'{'`）も Python では `str` にする。生成時に名前の衝突がないことを検査している。EOF（Ruby の `false`）は0番
- 表に無い種別（未知の記号など）は error トークン（1番）になる

## 5.4 駆動部（racc の C 実装に準拠）

`racc_runtime.RaccParser.do_parse` は、racc の **C 実装 `cparse.c` の `parse_main`** を移植した。Ruby 版 tecsgen が実際に使っているのは C 実装で、pure-Ruby 実装（`racc/parser.rb` の `_racc_do_parse_rb`）とはエラー回復の挙動が違う。

| 点 | C 実装（採用） | pure-Ruby 実装 |
|---|---|---|
| エラー回復で error トークンを shift したとき | 先読みトークンを捨てない。同じトークンで再びエラーになったとき（error_status が 3）に読み捨てる | 次のトークンを読む |
| shift での error_status の減算 | 先読みを問わず減らす | 先読みが error トークンか EOF なら減らさない |
| `_reduce_none` | 呼ばず、右辺の先頭の値を積む | 呼ぶ |
| next_token が nil を返す（C_parser） | EOF とし、値を `"$"` にする | EOF |

最初に pure-Ruby 実装を写したところ、構文エラーのある20ケースで Ruby 版と一致しなかった。Windows の Ruby で両方の実装を実行して違いを確かめ、`cparse.c` を読んで移植し直した。C_parser の `on_error` が `v == "$"` で EOF を判定しているのは、この C 実装の仕様による。

文法アクションは `yyerror`・`yyaccept` を使わないが、ランタイムには移植してある（エラー回復中の `yyerror` だけは未対応で、呼ばれると例外）。

## 5.5 パーサ本体

- **`CdlParser.next_token`**: `IDENTIFIER` を、`typename_resolver` が真なら `TYPE_NAME` に、指定子 `[ ]` の中なら `RESERVED2` の種別に置き換える。トークンを取り出すたびに `Generator.set_current_locale` を呼ぶ（エラーの位置になる）
- **TYPE_NAME の判定**: Ruby 版は `Namespace.is_typename?` でシンボル表を引く。`CdlParser.typename_resolver`・`CdeclParser.typename_resolver` の既定値を P3 で `Namespace.is_typename` にした（P2 のテストは記録から判定を与える関数に差し替えて使う）
- **`CdeclParser.next_token`**: `typedef`・`struct` で始まる文だけをパーサに渡し、それ以外は読み飛ばす。`;`・`{`・`(` などで `set_no_type_name(False)`、`.`・`->` で `True`。パーサの入れ子の状態は `Generator` とは別に持つ
- `parse` の前後で、`Namespace`・`Signature`・`Celltype`・`Cell`・`CompositeCelltype` のスタックを積み・戻す（`_push_model_stacks`・`_pop_model_stacks`、P3）
- Ruby 版の `Generator.parse`・`get_plugin`・`is_reuse?` は `CdlParser.parse_file`・`current_plugin`・`current_is_reuse`

## 5.6 文法アクション

`tools/port/gen_action_stubs.py` が、racc の文法ファイルパーサ（`Racc::GrammarFileParser`）で規則とアクションのソースを取り出し、骨格を生成する（**一度だけ**。本体は手で移植するので、既存のファイルは上書きしない）。規則数・右辺の長さ・メソッド名が表と一致することを検査している。

- 各メソッドに、規則（左辺 : 右辺）・移植元の行番号・Ruby のアクションをコメントで残す
- **字句解析の状態を変える呼び出しだけは P2 で移植した**。構文解析の結果そのものに効くため: `set_in_specifier`/`unset_in_specifier`（CDL 2箇所）、`set_no_type_name`（C 27箇所）、C の `TYPEOF` のアクション（自分で `next_token` を呼び、`typeof( … )` の括弧の中を読み飛ばす）
- 残りは P2 では `self._unported(N)` を呼んで `result` を返し、呼ばれた規則番号を `unported_rules` に記録していた
- **P3 で全アクション（CDL 325・C 121）の本体を移植した**。アクションが使うモデルのクラスは `syntax/_model.py` から引く。racc の既定どおり、アクションが値を返さない規則は `val[0]` を結果にする
- P2 の `test_p2_parser.py` は、モデルを作らずに字句解析の状態だけを追うため、字句解析に効くアクション（CDL の規則 419・420、C の `set_no_type_name` を呼ぶ規則など）だけを残し、他は素通しにした版で動かしている

## 5.7 差分テスト（Ruby 版を実行するオラクル）

`tests/ruby/p2_oracle.rb` を `ruby -r` で読み込ませ、正解データの全155ケースを実行して、parse の呼び出しごとに次を記録する（`tools/port/run_p2_oracle.sh`、WSL）。記録は `tests/golden/p2/`（gzip、約7MB）。

- 読んだファイルの中身（import_C の cpp 出力も含むので、テストは移植元の作業コピーなしで動く）
- 字句解析直後の `@q`、`next_token` が返した置換後のトークン、`_reduce_N` の呼び出し順、`on_error` の呼び出し、例外による中断

| テスト | 内容 | 結果（2026-09-27） |
|---|---|---|
| `test_p2_lexer.py` | 字句解析の結果が `@q` と一致 | CDL の parse 551回・338,400トークン、全件一致 |
| `test_p2_driver.py` | Ruby の置換後トークン列を駆動部に入れ、トークンの読み出し・reduce・`on_error` の呼び出し列が一致 | CDL 551回＋import_C 177回、全件一致（構文エラー20ケースの回復を含む） |
| `test_p2_parser.py` | 字句解析から `on_error` まで通しで動かし、返したトークン列と構文エラーの出力行が一致 | 全155ケース一致。構文エラーのある21ケース・24行も一致 |

`ErrorCase/attribute-err` は Ruby 版がパース中のアクションで SystemStackError になる。記録には中断が残り、テストは中断までを比べる。P3 で、CLI として同じ落ち方をすることを確認した（[[tecsgen-python3内部仕様 - 06 意味解析#6.3 CLI（`cli.py`）|6.3]]）。アクションの結果（モデル）の比較は [[tecsgen-python3内部仕様 - 06 意味解析#6.4 差分テスト|6.4]]。

## Ruby版との差異

- 構文解析の結果は Ruby 版と一致させる。構造上の差異は5.1の分割だけ
- `Token` の値は、Ruby 版と同じく識別子・キーワードが Symbol、リテラルが String。P2 まではどちらも `str` だったが、P3 で `Symbol` クラスを導入して区別した（[[tecsgen-python3内部仕様 - 04 クラス設計#Symbol|4.3]]）

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3 構文解析方式決定]]
- [[tecsgen-python3移植計画]] — P2
- [[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析|Ruby版 5章]]
- [[tecsgen-python3内部仕様 - 11 エラー・警告処理]]
