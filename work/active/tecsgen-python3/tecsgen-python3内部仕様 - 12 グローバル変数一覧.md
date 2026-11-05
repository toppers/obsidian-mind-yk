---
date: 2026-09-27
description: "tecsgen-python3内部仕様12章。Rubyグローバル変数→TecsgenContext属性の対応表（P1の言語・文字コード・出力制御分、P3のオプション・importパス分）、参照方法get_context()、Ruby互換の書き方規約（truthy・to_s・Symbol→str）"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 12章 グローバル変数一覧

[[tecsgen-python3内部仕様]] の12章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 12 グローバル変数一覧|Ruby版 12章]]。[[tecsgen-python3 P0基本方針決定]] の決定3（1つの設定オブジェクトへ集約）に従う。表は移植したフェーズごとに追記する。

## 12.1 設定オブジェクト（`context.py`）

- `TecsgenContext`（`dataclass`、mutable）。属性名は Ruby の変数名を snake_case にしたもの
- 参照は `get_context()`。テストは `reset_context()` で初期値に戻す
- **P1 での判断**: コア内部はモジュールのアクセサ `get_context()` で参照する（引数で持ち回すと、Ruby 版のメソッドの引数と対応しなくなるため）。プラグインからの参照方法も同じ `get_context()` に決まった（P5。2026-10-03 解消）。`plugin/` の 42 ファイルが `get_context()` を直接呼ぶ（引数では渡さない）
- `dbg_print`/`dbg_printf`（tecsgen.rb の `dbgPrint`/`dbgPrintf`）も `context.py` に置いた。全モジュールから呼ばれ、`$debug` だけに依存するため

## 12.2 対応表（P1 分）

| Ruby | Python | 設定元 |
|---|---|---|
| `$LANG_FILE` / `$CHARSET_FILE` | `lang_file` / `charset_file` | `TECS_LANG.setup` |
| `$LANG_CONSOLE` / `$CHARSET_CONSOLE` | `lang_console` / `charset_console` | 同上 |
| `$KCONV_CDL` / `$KCONV_CONSOLE` / `$KCONV_TECSGEN` | `kconv_cdl` / `kconv_console` / `kconv_tecsgen`（値は `"EUC"`・`"SJIS"`・`"UTF8"`・`"BINARY"`） | `TECS_LANG.set_kconv_var` |
| `$Ruby19_File_Encode` | `ruby19_file_encode` | 同上 |
| `$IN_EXERB` | `in_exerb`（常に偽） | — |
| `$kcode`（`-k`） | `kcode` | CLI（P6） |
| `$force_overwrite`（`-f`） | `force_overwrite` | CLI |
| `$verbose`（`-v`） | `verbose` | CLI |
| `$debug`（`-d`） | `debug` | CLI |
| `$LANG_FILE_DEFAULT` など・`$CODE_TYPE_ARRAY` | `tecs_lang.py` のモジュール定数 | — |
| （派生） | `file_codec` / `console_codec`（プロパティ） | 10章 |

`TECS_LANG` の初期化は、Ruby 版では require 時に走るクラス本体。Python 版は `TECS_LANG.setup(ctx, environ)` を**オプション解析の後**に呼ぶ（Ruby の `tecsgen.rb` と同じ順序）。

## 12.3 Ruby 互換の書き方規約（`ruby_compat.py`）

P1 で決めた、以降の移植すべてに適用する規約。

- **真偽**: Ruby は nil と false だけが偽。`if x then` は `if truthy(x):` または `x is not None` と書く。Python の `if x:` は 0・空文字列・空リスト・`__len__` を持つオブジェクトを偽にするので使わない
- **Symbol**: P1・P2 では `str` で表していたが、P3 で `Symbol` クラス（`str` の派生、等値とハッシュを区別）に変えた。リテラルは `Y.NAME`、変換は `sym(x)`。詳細は [[tecsgen-python3内部仕様 - 04 クラス設計#Symbol|4.3]]
- **インスタンス変数**: `@foo` → `self._foo`。`attr_accessor`/`attr_reader` があるものは同名の公開属性（`Token.val` など）
- **文字列化**: `"#{x}"` や `x.to_s` は `to_s(x)`。Float は Ruby の書式（`1.0e+15`、`1.0e-05`）を再現した。`Hash#inspect` は正解データを採った Ruby 3.2 の書式（`{"k"=>1}`）
- **置換**: `sub`/`gsub` は `sub_first`/`gsub`（置換文字列の `\1` 等を Ruby の規則で解釈）
- **sprintf**: `%s` だけ `to_s` を通し、残りは Python の `%` に任せている。数値書式は P4 で詰めた（`%s` の幅はバイナリ文字列でバイト数など、[[tecsgen-python3内部仕様 - 08 コード生成#8.3 バイト一致のための Ruby 互換|8.3]]）
- **配列の添字**: 負の添字・範囲外の代入は `generator.py` の `_get_at`/`_set_at` を参考に明示的に書く

## 12.4 対応表（P3 分）

`tecsgen.rb`（トップ）の `initialize_global_var`・`analyze_option` が設定する変数。設定元はすべて `cli.py`。

| Ruby | Python | 備考 |
|---|---|---|
| `$arguments` | `arguments` | コマンドライン引数を空白区切りで連結 |
| `$unopt`（`-U`）/ `$unopt_entry` | `unopt` / `unopt_entry` | |
| `$gen_base` / `$gen`（`-g`） | `gen_base` / `gen` | `gen` は生成中の region で変わる |
| `$generate_all_template` / `$generate_no_template` | 同名 snake_case | |
| `$idx_is_id`（`-i`）/ `$unique_id`（`-u`） | `idx_is_id` / `unique_id` | |
| `$dryrun` / `$show_tree`（`-s`）/ `$yydebug`（`-y`） | `dryrun` / `show_tree` / `yydebug` | |
| `$run_dir` / `$base_dir` | `run_dir` / `base_dir` | |
| `$import_path`（`-I`）/ `$import_path_opt` | `import_path` / `import_path_opt` | 初期値 `["."]` |
| `$library_path`（`-L`）/ `$define`（`-D`） | `library_path` / `define` | |
| `$ram_initializer`（`-R`）/ `$rom`（`-r`） | `ram_initializer` / `rom` | |
| `$region_list`（`-G`）/ `$generating_region` | `region_list` / `generating_region` | |
| `$unit_test` / `$no_banner` / `$print_version` / `$target` | 同名 snake_case | |
| `$no_default_import_path` / `$c_suffix` / `$h_suffix` | 同名 snake_case | |
| `$cpp`（`-c`、`TECS_CPP`）/ `$b_cpp_specified` | `cpp` / `b_cpp_specified` | |
| `$tecspath`（`TECSPATH`）/ `$tecsgen_base_path` | `tecspath` / `tecsgen_base_path` | |
| `$title` / `$tool_version` | `title` / `tool_version` | |
| `$b_no_gcc_extension_support` | 同名 | |
| `$TECSFLOW` | `tecsflow` | Python 版では常に偽 |
| `ARGV`（オプションを除いた残り） | `argv` | Ruby 版は `ARGV` を書き換えて使う |

Ruby のクラス変数（`@@x`）は設定オブジェクトではなくクラス属性に写した（[[tecsgen-python3内部仕様 - 04 クラス設計#クラス変数|4.3]]）。

**cmake 対応（2026-10-05、P7）で増えたグローバル変数は無い**（確認 2026-10-09、Python 版 `02fd2cb`〜`dd33023` の差分）。`CMake`（`core/tecsgen.py`）の状態（`_sources`・`_includes`・`_defines`・`_link_options`・`_custom_commands`・`_lines`）は、上のクラス変数の扱いに従ってクラス属性で持つ。`Makefile` と同じく、`TECSGEN.reset()`（1プロセスで複数回実行するテスト用。Ruby 版には無い）と `TECSGEN.set_default_config()` が `CMake.reset()` を呼んで空に戻す。設定オブジェクト（`context.py`）への追加も無い。

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3 P0基本方針決定]] — 決定3
- [[tecsgen-python3内部仕様 - 10 ファイル入出力]] / [[tecsgen-python3内部仕様 - 11 エラー・警告処理]]
- [[reference/tecsgen_ruby_global_variables.csv]] — 全数走査の生データ
- [[tecsgen-python3移植計画]]
