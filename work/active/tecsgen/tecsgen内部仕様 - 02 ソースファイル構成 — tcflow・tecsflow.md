---
date: 2026-10-10
description: "tecsgen内部仕様 第2章のうち、tcflow.rb（C 言語の関数呼び出し・変数参照の解析）と tecsflow.rb（セル単位の呼び出しフロー）の処理内容を、verbatim で分離したもの。25KB閾値による分割"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様 - 02 ソースファイル構成]] (2026-10-10, 25KB threshold). 2.1（tcflow）と 2.2（tecsflow）。

## 2.1 tcflow.rb（C 言語フロー解析ツール）

> [!note] 根拠
> 2026-10-10、移植元 r3304（`branches/ykominami_r3033/tecsgen/`）の `tcflow.rb`（148行）、`flowlib/classes.rb`、`flowlib/C_parser.y.rb` を読んで記述した。**実行はしていない**。`E:/Ccur/python3/asp3_stm32cube_TECS/tecsgen-rb/tcflow.rb` は、改行を除いて r3304 と同一。実行結果から確かめていない箇所には `(inferred)` を付けた。

`tcflow` は、C のソースファイルを解析して、**関数どうしの呼び出し関係と、グローバル変数の読み書きの回数**を集めるツール（バージョン `V1.0.0.1`、`$exe_name = "tcflow"`）。tecsgen 本体（CDL の処理）とは別のコマンドで、CDL は読まない。tecsgen 本体の C パーサ（`tecslib/core/C_parser.y.rb`、`import_C` 用）と同系統の `(inferred。GCC 拡張を消すヘッダや型名の扱いが似ている)`、別の C パーサ（`TCFLOW_Cparser`）を使う。

### 2.1.1 コマンドライン

`tcflow [options] files`

| オプション | 変数 | 意味 |
|---|---|---|
| `-c`, `--cpp=<cmd>` | `$cpp_cmd` | C プリプロセッサのコマンド。**指定が無ければ cpp を起動しない**。例: `-cpp_cmd=cl /E -I include_path` |
| `-g`, `--gen=<dir>` | `$gen_dir` | 出力ディレクトリ（既定 `gen`） |
| `-r`, `--read-rbdmp` | `$read_dump` | 解析せず、`<gen>/tcflow.rbdmp` を読み込む |
| `-l`, `--list` | `$b_list` | 全関数の一覧（変数に値を入れるだけ。2.1.5） |
| `-s`, `--summarize` | `$b_summarize` | 最上位関数ごとの要約（同上） |
| `-t`, `--print-all-token` | `$b_print_all_token` | 全トークンを標準出力に出す（これだけは `next_token` で実際に使われる） |

ファイル名の引数は複数指定できる。`@<リストファイル>` と書くと、そのファイルを `ASCII-8BIT` で読み、`#` で始まる行と空行を除いた各行（前後の空白を除く）をファイル名として使う。リストファイルが開けなければ `faile to open <file>`（原文のまま）を標準エラー出力に出す。ファイル名が無く、`-r` も無いときは、名前とバージョン、ヘルプを出して `exit 1` する。

### 2.1.2 処理の流れ

1. `ARGV` を解析する（`optparse`）。
2. `-r` なら `TCFlow::Function.load_funclist( "<gen>/tcflow.rbdmp" )` で関数一覧を読み込んで終わる。`C_parser.tab.rb` は読み込まない。
3. そうでなければ `flowlib/C_parser.tab.rb` を読み込み、標準エラー出力に `tcflow : V1.0.0.1` を出す。
4. 引数のファイル（`@` はリストに展開）ごとに、`TCFLOW_Cparser.new` で**ファイルごとに新しいパーサ**を作り、`parse( [ファイル], $cpp_cmd )` を呼び、`finalize`（本体は空）を呼ぶ。関数の一覧は `TCFlow::Function` のクラス変数 `@@Function_list` に溜まるので、複数ファイルを通して**1つの一覧に累積**する。
5. 全ファイルの後で `TCFlow::Function.dump_funclist( "<gen>/tcflow.rbdmp" )` で保存する（標準出力に `"Dump Funclist"` が出る。`p` を使うので引用符付き）。
6. 全体を `rescue Exception` で囲み、例外は `fatal error: <メッセージ>` を標準エラー出力に出して終わる。

### 2.1.3 字句解析・構文解析（`flowlib/C_parser.y.rb`）

- **入力**: `parse( files, cpp_cmd )`。`cpp_cmd` が有る場合は、`<gen>/tmp_<ファイルの基底名>` に「GCC 拡張を消すヘッダ（`__attribute__`、`__extension__`、`__builtin_va_list`、`restrict`、`__asm__`、`__builtin_offsetof` を定義するもの）」と元のファイルを連結して書き出し、`IO.popen( "<cpp_cmd> <tmp ファイル>" )` の出力を読む。cpp の出力は `<gen>/tmp_<基底名>_2.c` にも保存する。無い場合は元のファイルを直接読む。読み込むたびに `reading <ファイル>` を標準エラー出力に出す。
- **字句解析**: 1行ずつ読み、正規表現で識別子・数値・文字列などのトークンに切る。`# <行番号> "<ファイル名>"` の形の行（cpp の行番号情報）で、以降のトークンの行番号とファイル名を更新する。それ以外の `#` で始まる行は読み飛ばす。トークンは `Token.new( 値, ファイル, 行, 桁 )` として持つ。
- **型名の扱い**: `typedef` で宣言された名前は `@type_name_list` に登録し、`next_token` で `IDENTIFIER` を `TYPE_NAME` に置き換える（C 文法の曖昧さの解消）。ただし `.`・`->` の直後では置き換えず、`; : , ( ) { }` で戻す。解析中の関数の引数・ローカル変数として登録された名前は、型名として扱わない。ファイルの区切り（`:EOF`）で `@type_name_list` を空にする。
- **構文**: C の文法（式、宣言、文、関数定義、K&R 形式の旧引数宣言、`typedef`）。構文エラーは `syntax error near '<トークン>'`、EOF では `Unexpected EOF` を報告する。

### 2.1.4 解析結果の記録（`flowlib/classes.rb` の `TCFlow::Function`）

関数定義（`func_def`）を認識すると `TCFlow::Function.new( 位置 )` を作り、関数本体の解析中に次を記録して、最後に `set_name( 関数名 )` で名前を確定し、`@@Function_list[ 名前 ]` に登録する。

| 保持するもの | 内容 |
|---|---|
| `@param_var` | 引数名。`parameter_list` が関数より先に解釈されるので、`Function.param_list` で受け取ったものを `new` のときに登録する |
| `@local_var` | ローカル変数名（`new_local`）。**現状は登録されない**（2.1.5） |
| `@global_var` | 名前 → `[読んだ回数, 書いた回数]`。引数・ローカル変数以外への参照を数える |
| `@call_func` | 呼んでいる関数名 → `Function`（定義済み）、または `0`（未定義） |
| `@b_ref` | 他の関数から参照されたか（偽なら最上位の関数） |
| `@locale` | 定義位置 `[ファイル, 行, 桁]` |

記録の規則（構文アクション）:

- **関数呼び出し**: `postfix_expression '(' argument_list ')'` のとき `ref_func( 名前 )`。名前が定義済みの関数ならそれを `@call_func` に入れ、呼ばれた側に `referenced` で参照済みの印を付ける。未定義なら `@@Function_list[名前] = 0` と `@call_func[名前] = 0` にする。後で同名の関数が定義されると（`set_name`）、`0` だったものは参照済みになる
- **変数の読み**: `unary_expression` が `()` で終わらない式のとき `ref_var( 名前 )`
- **変数の書き込み**: `代入演算子` の左辺で `ref_var( 名前, true )`（書き込み回数を数える）
- メンバアクセスや添字は文字列化して名前に含める（`a.b`、`a->b`、`a[]`）。この名前がそのまま `@global_var` のキーになる
- 引数名・ローカル変数名（`@local_var` と `@param_var`）への参照は数えない

### 2.1.5 出力と現状の制約

- **ファイル**: `<gen>/tcflow.rbdmp` だけ。`Marshal.dump( @@Function_list )` の結果（Ruby の `Marshal` 形式）。`tecsgen.rbdmp` と同じく Ruby 専用の形式。`<gen>` ディレクトリは `tcflow.rb` が作らないので、無ければ `File.write` が失敗して `fatal error` になる `(inferred)`
- **標準出力・標準エラー出力**: `tcflow : V1.0.0.1`、`reading <ファイル>`（標準エラー出力）、`"Dump Funclist"`（標準出力）、`-t` のときのトークン一覧、構文エラーのメッセージ。**解析結果そのもの（呼び出しのツリーや要約）は出力されない**
- **表示処理が無効**: `Function.print_all_functions`（呼び出しツリー）、`print_summarize`（最上位関数ごとの要約）、`list_all_functions`（一覧）は `classes.rb` に実装されているが、`tcflow.rb` からの呼び出しは**コメントアウト**されている。`-l`・`-s` は `$b_list`・`$b_summarize` に値を入れるだけで、何も起きない。ツリー表示の中の変数一覧・要約の中の `print` も多くがコメントアウトされている。`-r` で読み込んだ後も、何も表示しない。したがって現状の `tcflow` は、`tcflow.rbdmp` を作る（読む）ための前段で、結果を見るには `classes.rb` の表示処理を呼ぶ別のスクリプトが要る
- **ローカル変数が登録されない**: `new_local` を呼ぶ構文アクション（`declaration_list`）が `C_parser.y.rb` でコメントアウトされている。`classes.rb` の `is_local_var?` にも「`@local_var[var]` が真にならない」という注記がある。そのため、関数内のローカル変数への参照は、引数でない限り**グローバル変数への参照として数えられる** `(inferred)`
- **`exit` が捕まる**: ヘルプ表示後の `exit 1` とリストファイルが開けないときの `exit 1` は、`SystemExit`（`Exception` の子）なので、末尾の `rescue Exception` に捕まり、`fatal error: exit` を出して**終了コード 0 で終わる** `(inferred、実行未確認)`
- **未実装・未使用**: `finalize` は空。`tcflow` の `-c` が無いと、マクロ・`#include` は展開されず、`#` で始まる行は読み飛ばされる

### 2.1.6 tecsgen-python3 での扱い

`tcflow`（と `tecsflow`、`flowlib/`）は、tecsgen-python3 では tcflow・tecsflow とも移植済み（2026-10-14 訂正。状況は [[tecsgen-python3移植計画]]、[[tecsgen-python3内部仕様 - 02 ソースファイル構成]]、[[tecsgen-python3外部仕様 - 01 概要]]）。移植では、tecsgen 本体と同じく racc のテーブルを使う方式（`C_parser.tab.rb`）が自然だが、`tcflow.rbdmp` は Ruby の `Marshal` 形式なので、そのままは再現できない（`tecsflow` の `tecsgen.rbdmp` も同じ理由で pickle に置き換えた。2026-10-14）。

## 2.2 tecsflow.rb（セル単位の呼び出しフロー）

> [!note] 根拠
> 2026-10-10、移植元 r3304（`branches/ykominami_r3033/tecsgen/`）の `tecsflow.rb`（515行）、`tecsgen.rb`（`TECSGEN.init`・`analyze_option`・`load_modules`・起動部）、`tecslib/core/tecsgen.rb`（`dump_tecsgen_rbdmp`）、`tecslib/core/generate.rb`（Makefile.tecsgen の TECSFlow ターゲット、呼び口関数のマクロ）を読んで記述した。**実行はしていない**。`tecsgen-rb/tecsflow.rb` は、改行を除いて r3304 と同一。実行結果から確かめていない箇所には `(inferred)` を付けた。

`tecsflow` は、**tecsgen が出したコンポーネントモデル**（`tecsgen.rbdmp`）と、**tcflow が出した C 関数の呼び出し関係**（`tcflow.rbdmp`、2.1）を突き合わせて、「どのセルのどの呼び口が、どのセルのどの受け口関数に届き、その関数がさらに何を呼ぶか」というセル単位の呼び出しフローを、標準出力に出すツール。バージョン `1.G.0`（`$tool_version`）。

### 2.2.1 3つのコマンドの関係

`Makefile.tecsgen`（`generate.rb`）が、次の依存関係のターゲットを出す（セルを持つリージョンのみ）。

```
tecsgen ──► gen/tecsgen.rbdmp ─┐
                               ├─► tecsflow -g gen
tcflow  ──► gen/tcflow.rbdmp ──┘
```

| ターゲット | 実行するもの |
|---|---|
| `tecsflow`（`tecsflow_sub`） | `tecsflow -g $(GEN_DIR)`（前提: `tecsgen.rbdmp`、`tcflow`）。リンクルートが複数あるときは、各リージョンのディレクトリで `make tecsflow` する |
| `tecsflow_u` | `tecsflow -g $(GEN_DIR) -U` |
| `tcflow`・`tcflow_exec` | `tcflow -g $(GEN_DIR) -c '$(CC) -E -DTECSFLOW $(CFLAGS) -I ./' $^`。入力は `$(CELLTYPE_SRCS) $(PLUGIN_CELLTYPE_SRCS)`（セルタイプのソース）。`-DTECSGEN` を足すとよい場合のコメントが付く |

- **`tecsgen.rbdmp`** は、`tecsgen` の起動部（`run1`・`run2` の後）で `dump_tecsgen_rbdmp` が書く。コード生成の後に行うのは、`unjoin_plugin` の後でなければならないため。リンクルート（Region）ごとに、最適化をリセットし（`reset_optimize`）、セル ID とドメインを設定し（`set_cell_id_and_domain`）、`-U` でなければ最適化し（`optimize`）、`Marshal.dump( Namespace.get_root )` を `<gen>/tecsgen.rbdmp` に書く。リンクルートが複数あれば、`<gen>/<リージョンのグローバル名>/` に分けて書く。したがって、**ダンプされるモデルは最適化後のもの**（`-U` のときを除く）
- **呼び口関数の名前**: tcflow は `-DTECSFLOW` で cpp を通す。このとき `generate.rb` は、呼び口関数のマクロを `#ifndef TECSFLOW` と `#else /* TECSFLOW */` の両方で生成し、TECSFLOW 側では `(p_that)->呼び口[添字].関数__T(...)`（最適化なし）や `...->VMT->関数__T(...)` の形にする。このため、C 関数の本体に現れる呼び口関数の呼び出しは、tcflow の解析結果の上では `->呼び口名.関数名__T` という名前になる。tecsflow は、この名前を手がかりに TECS の呼び出しを見分ける

### 2.2.2 起動

1. `$tecsflow_base_path`（このファイルのディレクトリ）を求め、`$TECSFLOW = true`、`$title = "tecsflow"`、`$tool_version = "1.G.0"` を設定する。
2. `flowlib/classes.rb`、`tecslib/version.rb`、`tecsgen.rb` を読む。`tecsgen.rb` は、`$TECSFLOW` が真なら末尾の通常起動（`run1`・`run2`・`dump_tecsgen_rbdmp`）をしない。
3. `TECSGEN.init( nil, true )` を呼ぶ。第2引数 `no_tecsgen_option = true` のため、**tecsgen のオプション解析（`analyze_option`）を行わない**。`initialize_global_var`（`$unopt = false` など）と `load_modules` だけを行い、`$TECSFLOW` なので `setup`（インポートパスの調整と gen ディレクトリの作成）はしない。`load_modules` は `$title` があるので、標準エラー出力に `tecsflow version 1.G.0 (tecsgen version <版>)  <著作権>` を出す。
4. tecsflow 自身の `analyze_option`:

| オプション | 意味 |
|---|---|
| `-g`, `--gen=<dir>` | 出力ディレクトリ（`$gen = $gen_base = dir`）。ダンプの入力先でもある |
| `-h`, `--help` | ヘルプを出して `exit 1` |
| `--version` | `$print_version = true`。tecsgen と違い、`$TECSFLOW` では `load_modules` で終了しないので、ほかには効果がない `(inferred)` |

5. `TECSGEN.new` を作る（CDL の解析はしない）。`$gen` から `$tecsgen_dump_file_name = "<gen>/tecsgen.rbdmp"`、`$tcflow_dump_file_name = "<gen>/tcflow.rbdmp"` を決める（`-g` の解析より後なので、`-g` が反映される）。
6. `Namespace` と `Cell` を**再オープン**して、フロー出力のメソッドを足す（`Locale_printer` を include）。最後に `TECSFlow.main` を呼ぶ。

### 2.2.3 読み込み（`TECSFlow.main`）

1. `reading '<gen>/tecsgen.rbdmp'` を出し、ファイルを読み、`TCFlow::Function.load_funclist`（引数に `tecsgen.rbdmp` を渡している点に注意。直後に上書きされるので実害はない `(inferred)`）、`Marshal.load` でルート名前空間を復元する。「ここではクラス変数を設定していないため、それらを参照するメソッドは使用できない」旨の注記がある。失敗したら `pp` で例外を出し、`fatal: fail to load '<file>' in <file reading|Marshal.load>` を出して `exit 1`。
2. `reading '<gen>/tcflow.rbdmp'` を出し、`TCFlow::Function.load_funclist` で `$tcflow_funclist` を得る。失敗したら同様に `exit 1`。
3. `Namespace.set_root`、`$root_namespace.print_all_cells`、`print_unref_function` の順に呼ぶ。

### 2.2.4 セルごとのフローの出力（`Namespace#print_all_cells`）

名前空間を再帰的にたどり、**アクティブなセルタイプのセル（複合セルタイプのセルは除く）**ごとに次を行う。

1. `[active cell] <セルのパス> (<ファイル> <行>)` を出す。
2. セルの結合（Join）のうち、定義が呼び口（`Port`）のものについて、シグニチャの関数ごとに `->呼び口.関数__T` を `call_funcs`（値は「受け口関数から呼ばれたか」）に偽で登録する。
3. セルタイプの受け口ごと、シグニチャの関数ごとに、受け口関数 `<セルタイプのグローバル名>_<受け口>_<関数>` を `$tcflow_funclist` で引く。有れば、その関数が呼んでいる関数（`get_call_funcs`）のうち `call_funcs` にあるものを真にする。無ければ `ep_func <名前> not found. why not defined ?` を出す。
4. **偽のまま残ったもの**（受け口関数から呼ばれていない呼び口関数＝このセルが自分から呼ぶもの。タスクのメイン関数やハンドラなど）のそれぞれから、`print_call_func_flow` でフローをたどる。コメントに「受け口関数から呼ばれているなら、実際にはアクティブではない」とある。

### 2.2.5 フローのたどり方（`Cell#print_call_func_flow` ほか）

`->呼び口[]*.関数__T` の名前を正規表現で `[呼び口, 関数, 添字]` に分解する（`TECSFlow.analyze_call_port_func_name`）。分解できれば TECS の呼び出し、できなければ TECS 外の C 関数。

**TECS の呼び口関数のとき**:
- 添字がなければ、`get_join_list.get_item( 呼び口 )` で結合を求め、`print_call_func_flow_sub` に渡す。添字（呼び口配列）があれば、先頭の結合の `get_array_member2` の要素ごとに、添字を 0 から振って処理する。
- `print_call_func_flow_sub`: 結合があれば、呼び先のセルと受け口（最適化後は `get_rhs_cell`・`get_rhs_port`・`get_rhs_subscript`、`$unopt` のときは `get_rhs_cell1`・`get_rhs_port1`・`get_rhs_subscript1`）を求め、`print_flow` で `<呼び元セル>.<呼び口>[添字].<関数> => <呼び先セル>.<受け口>[添字].<関数>` の1行を出し、呼び先セルの `print_entry_func_flow` で受け口関数の中をさらにたどる。呼び元セルが決まっていない（`no_caller_cell`）ときは、呼び元のセル名を省略する。
- 結合が無ければ: 親のセル（複合セルタイプの内側をたどっているとき）があれば、複合セルタイプの輸出された呼び口（`get_port_list` の `get_cell`・`get_cell_elem_name`）から対応する結合を探し、親のセルの結合先へ進む。親の結合も無ければ（親の呼び口が祖父母の輸出ポートに結ばれている再帰的な場合）、`->親の呼び口.関数__T` として親のセルで続ける。複合セルタイプに見つからなければ `<セル>.<呼び口> not found in composite <複合セルタイプ>`。親がなければ `<セル>.<呼び口> not joined`。

**受け口関数の中（`print_entry_func_flow`）**:
- 受け口関数の位置（ファイルと行）を出し、`set_printed` し、その関数が呼ぶ関数ごとに `print_call_func_flow` を呼ぶ。見つからなければ `not found '<受け口関数名>' !!!`。
- 出力済みの関数（`@@printed_func_nsp_list`、CDL 風のパス `<セルのパス>.<受け口>.<関数>`）は `: printed` だけ出して打ち切る（循環・重複の対策）。
- セルタイプが複合セルタイプのときは、輸出された受け口を `find_export` で内側のセルとその受け口に置き換え、` == [inner]<セル>.<受け口>` を出して、内側のセルで続ける（`parent_cell` に外側のセルを push）。

**TECS 外の C 関数のとき**:
- `$tcflow_funclist` に有り、未出力なら、`<関数名> (<位置>) [Function Out of TECS]` を出して `set_printed` し、呼んでいる関数を `no_caller_cell = false` で再帰的にたどる。出力済みなら `<関数名>: printed`。無ければ `<関数名>: [Function Out of TECS, not defined]`。

インデントは深さ（4空白×レベル）で、負のレベルは「インデントせずに絶対値を返す」の意味で使われる（`print_indent`）。

### 2.2.6 未参照の一覧（`TECSFlow.print_unref_function`）

1. `--- unreferenced entry functions ---` を出し、`Cell.print_unused_func` で、出力済みのセル（`@@printed_cell_list`）のセルタイプのうち、**受け口関数のうち未出力のもの**について、`[unreferenced entry function] <セル>.<受け口>.<関数>` を出し、その先のフローも出す。複合セルタイプの内側のセルは除く。
2. `--- unreferenced C functions ---` を出し、`TCFlow::Function.update`（`@call_func` の更新）の後、未出力かつ最上位（誰からも参照されない）の TECS 外の C 関数について、`[Function Out of TECS, unreferenced] <関数名> (<位置>)` と呼び出しのツリー（`print_all_functions 0`）を出す。

### 2.2.7 制約・注意(読み取れたこと)

- **`-U` が使えない `(inferred、実行未確認)`**: `Makefile.tecsgen` の `tecsflow_u` は `tecsflow -g $(GEN_DIR) -U` を呼ぶが、tecsflow の `analyze_option` に `-U` は無く、tecsgen の `analyze_option`（`-U`＝`--unoptimize`、`$unopt = true`）は `no_tecsgen_option = true` で呼ばれない。そのため `-U` は `OptionParser::InvalidOption` になると読める。`$unopt` は `initialize_global_var` で偽に初期化されるだけで、tecsflow の中では真にならない。`$unopt` の分岐（`get_rhs_cell1` 側）は、現状は使われない
- **入力は2つのダンプ**: `tecsgen.rbdmp` を作った `tecsgen` の実行と、`tcflow.rbdmp` を作った `tcflow` の実行が、同じ CDL・同じソースに基づいている必要がある（検査はない）
- **Ruby の `Marshal` に依存する**: `tecsgen.rbdmp` はモデルのクラス（`Namespace`・`Cell` ほか）をそのまま復元するので、tecsflow は tecsgen のクラス定義を前提にしている。tecsgen-python3 が `tecsgen.rbdmp` を書かず `tecsgen.pickle`（Python のクラスを復元する）を書くのは、このため（2026-10-14 訂正）
- **再オープンするクラス**: `Namespace`・`Cell`（表示用のメソッドを足す）。tecsgen-python3 の Mixin 粒度決定のノートに `tecsflow.rb` が出てくる理由

### 2.2.8 tecsgen-python3 での扱い

`tecsflow`・`tcflow`・`flowlib/` は初期スコープ外（[[tecsgen-python3内部仕様 - 02 ソースファイル構成]]、[[tecsgen-python3外部仕様 - 08 制約・制限]]）。移植するなら、tcflow（2.1）と合わせて、`tecsgen.rbdmp` に代わる Python 側のモデル保存形式（たとえば `pickle`）の設計から始めることになる。

## Related

- [[tecsgen内部仕様 - 02 ソースファイル構成]] — 2章（ファイルツリーと各節の索引）
- [[tecsgen内部仕様]] — 目次
- [[tecsgen-python3移植計画]] — `flowlib` は後回し
- [[tecsgen-python3 Mixin粒度決定]] — `tecsflow.rb` が再オープンするクラス
