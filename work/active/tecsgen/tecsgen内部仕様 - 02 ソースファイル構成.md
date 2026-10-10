---
date: 2026-08-16
description: "tecsgen内部仕様書 第2章（ソースファイル構成）— tecsgenのソースツリー全体のファイル一覧と役割。tecs_lang.rbの役割誤認、namespacepath.rbの配置誤り、componentobj/generate.rbの欠落を訂正。2.1 に tcflow.rb（C 言語フロー解析ツール）、2.2 に tecsflow.rb（セル単位の呼び出しフロー）、2.3 に tecsgen_rcov.rb（カバレッジ計測用ラッパー）、2.4 に tecsmerge.rb（テンプレートへの手書きコードのマージ）の処理内容を追記（2026-10-10）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen内部仕様]] (2026-08-16, 25KB threshold). Chapter 2 of 12. 2026-08-23、`tecslib/core/` 以下の実ファイル一覧と突き合わせて訂正。

> [!warning] 2026-08-23、ファイル配置と役割記述を3件訂正
> - `tecs_lang.rb` を「字句解析器（Lexer）」としていたのは誤り（5.1 で訂正済みの通り、字句解析は `bnf.y.rb` の `Generator#parse`/`next_token` に内蔵）。`tecs_lang.rb` の役割は `LANG`/文字コード解決のみ
> - `namespacepath.rb` を `syntaxobj/` に分類していたのは誤り。実ファイルは `componentobj/namespacepath.rb`（`syntaxobj/` には存在しない）
> - `componentobj/generate.rb`（74行、`Generate < Node` クラス — `generate` 文/指定子の CDL ノード）が一覧から漏れていた

## 2. ソースファイル構成

```
trunk/tecsgen/
├── tecsgen.rb              # エントリポイント（TECSGEN クラス定義・起動）
├── tecsmerge.rb            # tecsmerge コマンド本体（テンプレートへの手書きコードのマージ、2.4）
├── tecsflow.rb             # tecsflow コマンド本体（セル単位の呼び出しフローの出力、2.2）
├── tecscde.rb              # TECSCDE 起動スクリプト
├── tecsgen_rcov.rb         # tecsgen のカバレッジ計測用ラッパー（SimpleCov、2.3）
├── tcflow.rb               # tcflow コマンド本体（C 言語の関数呼び出し・変数参照の解析、2.1）
├── flowlib/                # tcflow のライブラリ（2.1）
│   ├── C_parser.y.rb       # C 言語パーサ文法定義（TCFLOW_Cparser クラス。字句解析を内蔵）
│   ├── C_parser.tab.rb     # racc 生成パーサテーブル（同梱済み）
│   └── classes.rb          # TCFlow::Function クラス（解析結果の保持・ダンプ・表示）
├── tecslib/
│   ├── version.rb          # バージョン定義（$version, $package）
│   ├── core/
│   │   ├── tecs_lang.rb    # LANG/文字コード解決のみ（字句解析には関与しない、5.1）
│   │   ├── bnf.y.rb        # YACC 文法定義（Parser + Generator クラス）
│   │   ├── bnf.tab.rb      # racc 生成パーサテーブル（同梱済み）
│   │   ├── C_parser.y.rb   # C 言語パーサ文法定義（import_C 用）
│   │   ├── C_parser.tab.rb # C パーサテーブル（同梱済み）
│   │   ├── tecsgen.rb      # TECSGEN クラス（パス管理・処理制御）
│   │   ├── generate.rb     # コード生成（最大ファイル、5400行）
│   │   ├── optimize.rb     # 最適化処理
│   │   ├── plugin.rb       # Plugin 基底クラス
│   │   ├── pluginModule.rb # PluginModule モジュール（ポストコード生成）
│   │   ├── messages.rb     # ローカライズ済みメッセージ定義
│   │   ├── types.rb        # 型システム（CDL 型クラス群）
│   │   ├── ctypes.rb       # CType モジュール（C 型指定子のマージ、import_C 用）
│   │   ├── value.rb        # 値クラス群
│   │   ├── expression.rb   # 式クラス群（42KB）
│   │   ├── location.rb     # ソースコード位置（locale）管理
│   │   ├── gen_xml.rb      # XML 出力（tecsflow 用）
│   │   ├── tecsinfo.rb     # TECSInfo 実行時情報（30KB）
│   │   ├── tool_info.rb    # TOOL_INFO 機能
│   │   ├── unjoin_plugin.rb# unjoin プラグイン
│   │   ├── syntaxobj.rb    # syntaxobj/ ディレクトリのロード
│   │   ├── componentobj.rb # componentobj/ ディレクトリのロード
│   │   ├── syntaxobj/      # 構文オブジェクト（CDL パースツリーノード）
│   │   │   ├── node.rb         # Node 基底クラス（locale 管理・エラー出力）
│   │   │   ├── decl.rb         # 型・属性・変数宣言
│   │   │   ├── funchead.rb     # 関数ヘッダ（シグニチャ関数）
│   │   │   ├── paramdecl.rb    # パラメータ宣言
│   │   │   ├── paramlist.rb    # パラメータリスト
│   │   │   ├── typedef.rb      # typedef 宣言
│   │   │   ├── namedlist.rb    # 名前→オブジェクト マップ（NamedList）
│   │   │   ├── cdlinitializer.rb # CDL 初期化子
│   │   │   └── cdlstring.rb    # CDL 文字列
│   │   └── componentobj/   # コンポーネントモデルオブジェクト
│   │       ├── namespace.rb    # Namespace（名前空間）
│   │       ├── namespacepath.rb # 名前空間パス
│   │       ├── region.rb       # Region（リンクルート・ドメイン）
│   │       ├── signature.rb    # Signature（シグニチャ）
│   │       ├── celltype.rb     # Celltype（セルタイプ）
│   │       ├── compositecelltype.rb # CompositeCelltype（複合セルタイプ）
│   │       ├── compositecelltypejoin.rb # 複合セルタイプの結合処理
│   │       ├── cell.rb         # Cell（セルインスタンス、1930行）
│   │       ├── port.rb         # Port（呼び口・受け口）
│   │       ├── join.rb         # Join（結合記述、1363行）
│   │       ├── reversejoin.rb  # ReverseJoin（逆 require 結合）
│   │       ├── factory.rb      # Factory（ファクトリ記述）
│   │       ├── generate.rb     # Generate（generate 文/指定子ノード、74行。core/generate.rbとは別物）
│   │       ├── import.rb       # Import ディレクティブ処理
│   │       ├── import_c.rb     # import_C ディレクティブ処理（C ヘッダ解析）
│   │       ├── importable.rb   # Importable モジュール
│   │       ├── domaintype.rb   # DomainType（ドメイン）
│   │       ├── classtype.rb    # ClassType（クラス）
│   │       └── celltypeModule.rb # CelltypeModule モジュール
│   └── plugin/             # 標準付属プラグイン群（79 ファイル、r3301時点）
```

---

## 2.1 tcflow.rb（C 言語フロー解析ツール） — 詳細は [[tecsgen内部仕様 - 02 ソースファイル構成 — tcflow・tecsflow#2.1 tcflow.rb（C 言語フロー解析ツール）|2.1]]

C のソースを解析して、関数どうしの呼び出し関係とグローバル変数の読み書きの回数を集め、`<gen>/tcflow.rbdmp`（Ruby の `Marshal` 形式）に書くツール。解析結果の表示処理は `tcflow.rb` からは呼ばれていない（2026-10-10、r3304 を読んで確認）。

## 2.2 tecsflow.rb（セル単位の呼び出しフロー） — 詳細は [[tecsgen内部仕様 - 02 ソースファイル構成 — tcflow・tecsflow#2.2 tecsflow.rb（セル単位の呼び出しフロー）|2.2]]

`tecsgen.rbdmp`（コンポーネントモデル）と `tcflow.rbdmp`（C 関数の呼び出し関係）を突き合わせ、アクティブなセルの呼び口から、結合先のセルの受け口関数、その先の関数へとたどるフローを標準出力に出すツール。

## 2.3 tecsgen_rcov.rb（カバレッジ計測用ラッパー）

> [!note] 根拠
> 2026-10-10、移植元 r3304（`branches/ykominami_r3033/tecsgen/`）の `tecsgen_rcov.rb`（64行）と、`tecsgen.rb` の起動部（593〜607行）を読んで記述した。**実行はしていない**。`tecsgen-rb/tecsgen_rcov.rb` は、改行を除いて r3304 と同一。実行結果から確かめていない箇所には `(inferred)` を付けた。

`tecsgen_rcov.rb` は、**tecsgen の処理そのものは変えずに、Ruby のコードカバレッジ（どのソース行が実行されたか）を計測しながら tecsgen を実行する**ラッパー。使い方は `tecsgen_rcov.rb [options] CDL-file.cdl`（通常の `tecsgen` の代わりに呼ぶ）。ファイル冒頭のコメントに「SimpleCov を使用するため、ruby V1.9 以降が必要」とある（gem `simplecov` が要る）。

### 2.3.1 処理の流れ

1. **ロードパス**: `$:.unshift( File.dirname( __FILE__ ) )` で、このファイルのディレクトリを先頭に加える。手順 4 の `require 'tecsgen'` が、同じディレクトリの `tecsgen.rb` を見つけるため。
2. **SimpleCov の設定**:
   - `SimpleCov.command_name "tecsgen#{Time.now.to_f}"`: 実行ごとに異なる名前にする。複数回の実行の結果を、SimpleCov が別々の実行として保存・統合できるようにするためと読める `(inferred)`
   - `SimpleCov.root File.dirname( File.expand_path __FILE__ )`: ルートを tecsgen のディレクトリにする。計測の対象はその配下（`tecsgen.rb` と `tecslib/**`）で、レポートの出力先（`coverage/`）の基準にもなる `(inferred)`
   - `SimpleCov.start`: 計測を開始する。**計測の開始より後に読み込まれたファイルだけが対象**なので、次の `require 'tecsgen'` より前に置く必要がある
   - コメントアウトされている部分（`at_exit` での `SimpleCov.result.format!`、`add_filter`）は使っていない。除外の設定は無く、既定の動作になる
3. 標準出力へ `simplecov begin` を出す。
4. `require 'tecsgen'`: **これが tecsgen の実行そのもの**。`tecsgen.rb` はロードされた時点で、末尾の起動部が実行される。`$TECSCDE` と `$TECSFLOW` がどちらも真でなければ、`TECSGEN.init`、`TECSGEN.new`、`run1`（構文解析・意味解析）、`run2`（最適化・コード生成）、`dump_tecsgen_rbdmp` を順に呼ぶ。回復できないエラー（`StandardError`）は、`tecsgen: exit because of unrecoverble error.` などを標準エラー出力に出して `exit 1` する。コマンドライン引数は `ARGV` をそのまま `tecsgen.rb` が読む。`tecsgen` が読み込む `tecslib/` 以下のファイルも、手順 2 の後なので計測の対象になる。
5. 標準出力へ `simplecov end` を出す。手順 4 から戻ったときだけ出る（`tecsgen` が `exit 1` で終わるときは出ない `(inferred)`）。
6. **終了時**: `SimpleCov.start` が終了時のフックを登録しているので、`exit` で終わるときも含めて、結果が自動的に書き出される（SimpleCov の標準の動作 `(inferred)`）。

### 2.3.2 出力

SimpleCov の既定どおり、ルート直下の `coverage/` に、レポート（`index.html`）と、機械可読のデータ（`coverage.json`、`.resultset.json`、`.last_run.json`、`.history.json` など）が出る `(inferred)`。tecsgen-rb のリポジトリ（`asp3_stm32cube_TECS/tecsgen-rb/coverage/`）に、これらのファイルが実際にあり、このラッパーを使った跡と見られる。

### 2.3.3 位置づけ・注意

- tecsgen の本体の処理（2〜12章）には関与しない。**計測のためだけのエントリポイント**で、通常のビルドには使われない（`Makefile.tecsgen` が呼ぶのは `tecsgen`、`tecsflow`、`tcflow`）
- テストの CDL 群をこれで実行すれば、tecsgen のどの行がテストで実行されていないかを調べられる（用途は推測 `(inferred)`）
- `-d`・`-v` などのオプションは `tecsgen` のものがそのまま使える（`ARGV` を共有するため）
- 自前の終了処理は無い。`SimpleCov.start` の外では、`tecsgen.rb` の `exit` の扱いを変えていない

### 2.3.4 tecsgen-python3 での扱い

対象外（[[tecsgen-python3 パッケージ構成決定]]。`tecsflow.rb`・`tcflow.rb`・`tecscde.rb` と並んで「計画のスコープ外」）。Python 版のカバレッジは、テストの実行側（`pytest` に `coverage` または `pytest-cov` を付ける）で測るもので、このラッパーに当たるファイルは移植しない。

## 2.4 tecsmerge.rb（テンプレートへの手書きコードのマージ）

> [!note] 根拠
> 2026-10-10、移植元 r3304（`branches/ykominami_r3033/tecsgen/`）の `tecsmerge.rb`（760行）を読んで記述した。**実行はしていない**（tecsgen-python3 の `tecsmerge.py` は Ruby 版と73シナリオで一致を確認済みだが、本節は Ruby 版のソースの読み取り）。`tecsgen-rb/tecsmerge.rb` は、改行を除いて r3304 と同一。実行結果から確かめていない箇所には `(inferred)` を付けた。

`tecsmerge` は、tecsgen が生成する**セルタイプのコードのテンプレート**（`<セルタイプ>_templ.c`、インライン関数を書くセルタイプインラインヘッダ `<セルタイプ>_templ.h`）と、利用者がそれを元に書き足した**現在のコード**を突き合わせて、手書きの部分を新しいテンプレートに引き継ぐツール。tecsgen は実行のたびにテンプレートを作り直すため、セルタイプに次の変更があっても、手書きの関数本体を失わずに済ませる。

- 受け口関数が増えた
- 受け口の名前が変更された
- 受け口関数の名前が変更された

### 2.4.1 コマンドライン

```
tecsmerge [options] files_templ.c   src_dir
tecsmerge [options] gen_dir         src_dir
```

最後の引数が出力先のディレクトリ（コード中の変数名は `dst`）、それ以外が入力（ファイルまたはディレクトリ）。引数が2つ未満ならヘルプを出して `exit 1`。入力がディレクトリなら、その中の `_templ.c`・`_templ.h` で終わるファイル（`/_templ.[ch]$/`）すべてを対象にする。

| オプション | 変数 | 意味 |
|---|---|---|
| `-e`, `--exist-only` | `$b_exist` | 出力先にファイルがあるときだけマージする（無いときはコピーもしない） |
| `-p`, `--port=old:new` | `PortRenamer.new` | 受け口名の変更。`new` を省略（`-p old`）すると、名前は変えずに、続く `-f` の対象の受け口として指定するだけになる |
| `-f`, `--func=old:new` | `PortRenamer.add_func` | 受け口関数名の変更。**直前の `-p` の受け口**に属する。コードは `-p` で指定した受け口の名前を前に補う（`"#{受け口名}_#{old}"`）ので、`old:new` は受け口を除いた関数名で書く。ファイル冒頭のコメントは「`受け口名_関数名` の形でなくてはならない」と書いていて、コードと食い違う `(inferred)` |
| `-s`, `--show_change_set` | `$b_show` | 名前変更の指定を表示する |
| `-o`, `--old-mode` | `$old_mode` | 旧モード（関数ヘッダを置き換えない。2.4.3） |

### 2.4.2 処理の流れ

1. オプションを解析する。`-f` の指定が重複する、または旧名と新名が同じだと、`error: ...` を出して `$n_err` を数える。1件でもあれば `N errors` を出して `exit 1`。`-s` なら `PortRenamer.show` で指定を表示する。`$old_mode` に応じて、関数本体の区切りを選ぶ（`CDLContents.merge_DELIMITERS :OLD_FUNC_BODY` または `:NEW_FUNC_BODY`）。
2. 出力先がディレクトリでなければ（無い、またはファイル）エラーで `exit 1`。入力が存在しなければ `exit 1`。
3. 入力ごとに `merge( 入力, 出力先 )`:
   - 入力のファイル名が `_templ.c` / `_templ.h` で終わらなければ、`error: ...: not end with _templ.c/h` で `exit 1`。出力先のファイルは、`_templ` を取り除いた名前（`<出力先>/<基底名>`）。
   - **出力先にファイルが無い**: `-e` が無ければ、入力をそのままコピーする（`ASCII-8BIT`）。`-e` があれば `info: <出力先> skipped` を出して何もしない。
   - **出力先にファイルがある**: `merging <入力> to <出力先>` を出して、次の順に処理する（`old` が出力先の現在のファイル、`templ` が入力のテンプレート）。

| 段階 | 処理 | エラーがあれば |
|---|---|---|
| 1 | `old.rename` — `-p`・`-f` の指定で、old の受け口名・関数名を置き換える | `<出力先> not generated because of error` を出して `exit 1` |
| 2 | `old.check templ` — テンプレートに無い受け口・関数を報告する | 同上、`exit 2` |
| 3 | `templ.merge old` — 手書きの部分を old から templ に持ち込む | 同上、`exit 3` |
| 4 | `rename_dst` — 出力先の現在のファイルを `<出力先>_1`、`_2`、…（存在しない最小の番号）にリネームしてバックアップ（`info: backup generated for ... to ...`） | リネームに失敗したら `exit 1` |
| 5 | `templ.write` — マージ結果を出力先のファイル名で書く | — |

### 2.4.3 ファイルの構造(区切りのキーワード)

ファイルを次の行で区切り、状態機械（`CDLContents#initialize`）で読む。正規表現は行頭（`^`）に固定され、`*`・`[`・`]` はエスケープされ、`..._NAME` の部分は名前の取り出し（`(\w*)`）になる。

| 状態 | キーワード行 | 直前に来てよい状態 |
|---|---|---|
| `HEAD` | （ファイルの先頭） | — |
| `PREAMBLE_COMMENT` | `/* #[<PREAMBLE>]#` | `HEAD` |
| `PREAMBLE_BODY` | ` * #[</PREAMBLE>]#` | `PREAMBLE_COMMENT` |
| `ENTRY_COMMENT` | `/* #[<ENTRY_PORT>]# 受け口名` | `PREAMBLE_BODY`、関数本体の終わり |
| `ENTRY_BODY` | ` * #[</ENTRY_PORT>]#` | `ENTRY_COMMENT` |
| `ENTRY_FUNC_COMMENT` | `/* #[<ENTRY_FUNC>]# 関数名` | `ENTRY_BODY`、関数本体の終わり |
| `ENTRY_FUNC_BODY` | 新モード: 行頭の `{` ／ 旧モード: ` * #[</ENTRY_FUNC>]#` | `ENTRY_FUNC_COMMENT` |
| `ENTRY_FUNC_BODY2`（旧モードのみ） | ` * #[/ENTRY_FUNC>]#`（バグ互換の綴り） | `ENTRY_FUNC_COMMENT` |
| `POSTAMBLE_COMMENT` | `/* #[<POSTAMBLE>]#` | 関数本体の終わり、`PREAMBLE_BODY` |
| `POSTAMBLE_BODY` | ` * #[</POSTAMBLE>]#` | `POSTAMBLE_COMMENT` |
| `EOF` | （ファイルの終わり） | `POSTAMBLE_BODY`、関数本体の終わり、`PREAMBLE_BODY` |

- 直前の状態が表に合わない遷移は、`error <行>: unsuitable previous keyword` と、前後のキーワード・期待されるキーワードを出して `$n_err` を数える。
- 新モードでは、`PREAMBLE_BODY` または `POSTAMBLE_BODY` の中の**行頭の `{`** は関数本体の始まりとして扱わない（#1002 の対策）。
- 解析結果は `CDLContents`（`head`、`preamble_comment`、`preamble_body`、受け口ごとの `CDLEntryPort`、`postamble_comment`、`postamble_body`）に入る。`CDLEntryPort` は、`entry_comment`、`entry_body`、関数ごとの `entry_func_comment`・`entry_func_body`、関数の順序 `entry_func_array` を持つ。
- **新モードと旧モードの違い**: 新モードは、関数本体を行頭の `{` から始まるとみなす。このため、関数ヘッダ（`ENTRY_FUNC` 行から `{` の直前まで）は `entry_func_comment` に入り、**テンプレート側のものが使われる**（受け口関数のシグニチャの変更が反映される）。旧モードは、` * #[</ENTRY_FUNC>]#` の行までがコメントで、その後の関数ヘッダも関数本体に含まれるため、**関数ヘッダは置き換わらない**（`-o` の説明が "function head not substituted"）。

### 2.4.4 マージの規則(`templ.merge old`)

テンプレートを土台にして、手書きの部分だけを old から持ち込む。

| 部分 | どちらのものが残るか |
|---|---|
| `head`（先頭〜`PREAMBLE` の前） | old |
| `preamble_comment`、`entry_comment`、`postamble_comment` | templ |
| `preamble_body`、`postamble_body` | old |
| 受け口ごとの `entry_body` | old |
| 受け口関数の関数本体 | old（old に無い関数は templ のまま） |
| 受け口関数のコメント（新モードでは関数ヘッダを含む） | templ |
| 受け口・関数の並び順 | templ |

- templ の受け口が old に無ければ `port merged: <受け口名>`（新しい受け口）。templ の関数が old の受け口に無ければ `func merged: <関数名>`（新しい関数）。old にもあれば `func remained: <関数名>`（手書きを引き継いだ関数）。
- old にあって templ に無い受け口・関数（削除されたもの）は、出力に出ない。`old.check` が `info: <受け口名> is deleted port` / `info: <関数名> is deleted function` を標準エラー出力に出すだけで、**手書きのコードも一緒に消える**（バックアップに残る）。

### 2.4.5 名前の変更(`old.rename`)

`-p`・`-f` で指定された名前を、**old の側で**置き換えてからマージする（テンプレートの名前に合わせる）。

- **受け口の変更** `-p old:new`: old の受け口を探し、無ければ `warning: <old>: renaming port not found`。有れば `new` で登録し直す。続けて、その受け口の関数名のうち受け口名を含むもの（`受け口名_関数名`）を、`sub( /<old>/, <new> )` で新しい受け口名に置き換える（先頭の1か所。名前の途中に一致する場合も置き換わる `(inferred)`）。
- **受け口関数の変更** `-f old:new`（直前の `-p` の受け口に属する）: `受け口名_old` を `受け口名_new` にする。`entry_func_array`、`entry_func_comment`、`entry_func_body` のキーを置き換える。無ければ `warning: <old>: renaming function not found`。
- `-f` を `-p` より前に指定すると `error: <old>: specify -p before -f` を出すが、直後の `n_err += 1`（`$` が無い）は未定義のローカル変数への加算なので `NoMethodError` になると読める `(inferred、実行未確認)`。

### 2.4.6 そのほか読み取れたこと

- **エンコーディング**: ファイルは `ASCII-8BIT`（Ruby 1.9 以上）で読み書きする。文字コードの変換はしない。
- **バージョン**: `parser.version = #{$version}` は、`#` 以降がコメントで、行末の `=` が次の行に続くため、`parser.version = parser.release = nil` と読める。`--version` で版は表示されない `(inferred)`。
- **終了コード**: 引数エラー・入力や出力先の不備・名前変更の指定エラーは `1`。マージの各段階のエラーは段階の番号（1、2、3）。

### 2.4.7 tecsgen-python3 での扱い

**移植済み**（P6、2026-10-02）。`tecsmerge.py` が、Ruby 版と標準出力・標準エラー出力・終了コード・生成ファイルがバイト一致する（73シナリオで確認。[[tecsgen-python3移植計画 Archive — P6]]、[[tecsgen-python3外部仕様]]）。

## Related

- [[tecsgen内部仕様]] — 目次
- [[tecsgen-python3移植計画]] — `flowlib` は後回し
- [[tecsgen-python3 Mixin粒度決定]] — `tecsflow.rb` が再オープンするクラス

