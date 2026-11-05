---
date: 2026-09-27
description: "tecsgen-python3移植計画のうち完了済みフェーズP0（準備と方針決定）・P1（基盤）・P2（構文解析のフロントエンド）の詳細をverbatim分離したアーカイブ。正解データ採取、racc表駆動への切替、持ち越し事項"
project: tecsgen-python3
status: tracking
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3 移植計画 Archive — P0–P2

[[tecsgen-python3移植計画]] の「フェーズ」節から、完了済みの P0〜P2 の詳細を移したもの（2026-09-27、25KB 閾値に近づいたため）。内容は移動元のまま（P0 の「下の『現状の問題』」だけを移動元へのリンクに直した）。P3 以降と計画全体は [[tecsgen-python3移植計画]] を参照。

### P0 準備と方針決定（1〜2セッション） — 2026-09-26 完了

- [x] リポジトリを整える（2026-09-26 完了、`main` にコミット `aca0899`。内容は [[tecsgen-python3移植計画#現状の問題（2026-09-26 確認 → 同日修正済み）|移植計画の「現状の問題」]] を参照。`mypy` は追加しない、`yklibpy` は使わない — ユーザー確認済み）
- [x] tree-sitter の読み込み方を決める（2026-09-26 決定 → [[tecsgen-python3 tree-sitter読み込み方式決定]]） → **2026-09-27 に superseded**（P2 で racc 表駆動へ変更）
  - 移植元の生成済み `parser.c` をリポジトリに同梱し、`tecsgen.syntax._cdl`・`_tecs_cdecl` という C 拡張として setuptools でビルドする
  - Windows（MSVC）と WSL（gcc）の両方でビルドし、テストが通ることを確認した。`example.py` の DLL 読み込みは廃止した
- [x] ゴールデン生成スクリプトを作る（2026-09-26 完了）
  - **入力には `svn export -r BASE --native-eol LF` で書き出したソースを使う**。Windows 上の SVN 作業コピー（`E:/Crepo/toppers-tecs-svn/.../ykominami_r3033`）では、Ruby ソースも CDL もすべて CRLF になっている。一方、リポジトリ本体（`svn cat -r BASE`）は LF で、`svn status` にも変更は出ない。生成コードのテンプレートは Ruby ソースのヒアドキュメントに埋め込まれているため、作業コピーをそのまま使うと Linux 上でも出力が CRLF になる（最初の採取では4,650ファイルに CR が混入し、採り直した）。LF のソースを WSL の `/tmp` に書き出したことで、採取時間も26分から41秒になった（`/mnt/e` から Ruby ソースを読む処理が遅かったため）
  - **実行環境は WSL Ubuntu に決定**（ユーザー決定）。Ruby 3.2.3・gcc 13.3・移植元 SVN r3304。Windows では使えなかった。gcc が無く、代わりの `clang -E` では cygwin 前提の `pthread.h` が見つからないため。さらに Windows 版 Ruby は CRLF で出力する。Python 版との比較も WSL 上で行う
  - `make` は使わない。`test/` の Makefile・シェルスクリプトから tecsgen の呼び出しを抜き出してマニフェスト（`tools/golden/cases.toml`）にし、`tools/golden/generate_golden.py` で1ケースずつ実行する。ケースごとにテストツリーの作業コピーを作り直してから実行する
  - 結果: 157ケース中155件を採取（`tests/golden/`、約4,900ファイル・38MB）。`.gitattributes` で `tests/golden/**` を改行変換の対象外にした（`core.autocrlf=input` の環境で内容が変わらないように）。採取しなかった2件: `import_C/z`（シェル変数に依存）と `mruby`（MRUBYPATH・ASP のソースツリーが無い）。ErrorCase の26件は、Makefile に書かれた期待エラー・警告数と全件一致した。同じケースを2回実行して、出力が決定的なことも確認した
  - 保存しないもの: `*.rbdmp`（Marshal 形式）と `tmp_*.h`（C プリプロセッサの出力）。ハッシュとサイズだけを記録する。絶対パスは `@WORK@`・`@SOURCE@` に置き換える
  - `sjis` だけは、ケースに `TECSGEN_FILE_LANG=ja_JP.SJIS` を与えた。Makefile が利用者のロケールを Shift_JIS と前提しているため
  - **Ruby 版自体が失敗するケースがある**（それも正解データとして記録している）
    - `class`・`rpc`・`DataPumpHolder`: 既知の問題 9.7.1（`TransparentRPCSignaturePlugin` の参照切れ）を実行で確認した（[[work/active/tecsgen/tecsgen内部仕様 - 09 プラグイン機構|内部仕様 9.7.1]]）
    - `simple/trace`: `TLVTracePlugin.rb` が見つからない
    - `optimize/*`: `t_syslog.h` が見つからない
    - `composite_namespace`・`sample/*` など: 古いテストデータで、現行の文法では構文エラーになる
- [x] 設計判断を記録する（2026-09-26 決定 → [[tecsgen-python3 P0基本方針決定]]）
  - CLI オプションは Ruby 版と**完全互換**
  - Ruby の mixin（`PluginModule`・`CelltypePluginModule`・`Importable`・`CType`・`HasType`）は**多重継承**で写す（MRO は include を書いた順の逆に並べる）
  - グローバル変数（111種・809箇所）は**1つの設定オブジェクト**へ集約する
- [x] パッケージ構成を決める（2026-09-26 決定 → [[tecsgen-python3 パッケージ構成決定]]）
  - Ruby 版と**1ファイル対1モジュール**で対応させる。再オープンされたクラスは機能別の mixin にする
  - 標準プラグインのモジュール名は **Ruby と同名**（`HRPPlugin.py`）

### P1 基盤（Node・エラー処理・入出力） — 2026-09-27 実装・検証済み（`main` にコミット `2a281c4`）

- [x] `Node`/`BDNode`/`NSBDNode`、`Generator` のエラー・警告・情報カウンタと位置の選択、`print_report`、`Token`（`core/syntaxobj/node.py`・`core/generator.py`）
- [x] `messages.rb` の多言語メッセージ: `tools/port/gen_messages.py` が Ruby にソースを eval させて生成（エラー334・警告32・コメント78件×2言語）
- [x] `TECS_LANG`・`Console`（`core/tecs_lang.py`）、`TECSMsg`（`core/messages.py`）
- [x] `NamedList`、`AppFile`/`MemFile`（`core/generate.py`）、`CFile`（`core/plugin.py`）、`TECSIO`（`syntax/tecsio.py`）
- [x] 新設: `context.py`（`TecsgenContext`・`get_context()`・`dbg_print`）、`ruby_compat.py`（`truthy`・`to_s`・`inspect`・`sub_first`/`gsub`・`sprintf`・`rb_print`/`rb_puts`・`RubyIO`）
- 検証: pytest 53件（Windows・WSL とも通過）。Ruby 版を実行するオラクル（`tests/ruby/p1_oracle.rb`）との差分テストで、全メッセージの置換・LANG 判定・`to_s` が一致。正解データの stdout のエラー／警告684行が移植したメッセージ表と一致。`ruff`・`ty` 問題なし
- 仕様書: [[tecsgen-python3内部仕様 - 10 ファイル入出力|10章]]・[[tecsgen-python3内部仕様 - 11 エラー・警告処理|11章]]・[[tecsgen-python3内部仕様 - 12 グローバル変数一覧|12章]]（P1 範囲）。1・2章は未執筆
- P1 で見つけた、後続フェーズへの持ち越し
  - **P2**: Ruby 版は非 ASCII の CDL をバイト単位で字句解析している（`sample/error-13` の `near '\xe3'`）。エラー位置と切り出しをバイト単位で再現する必要がある
  - **P3**: `ErrorCase/attribute-err` で Ruby 版が `SystemStackError`（`elements_eval_const` の無限再帰）で落ちる。Python 版での再現方法（終了コード・stderr）を決める
  - **P5**: `celltypePlugin` でエラー行が出るのに件数の行が無く終了コード0（原因未調査 — TBC → **解消**: Ruby 版の挙動で、Python 版も一致。[[tecsgen-python3内部仕様 - 11 エラー・警告処理]]、P5h）。プラグインからの設定オブジェクトの参照方法も P5 の前に決める（→ **解消**: `get_context()`。[[tecsgen-python3内部仕様 - 12 グローバル変数一覧]]）
  - 開発環境: x86 の VS 開発者プロンプトから起動したシェル（`VSCMD_ARG_TGT_ARCH=x86`）では、setuptools が C 拡張を x86 でビルドしようとして失敗する。`VSCMD_*` を外すと通る

### P2 構文解析のフロントエンド — 2026-09-27 実装・検証済み（`main` にコミット `db3cb47`・`1b88fdb`・`6d69710`、2026-09-27 push 済み）

- **方式を変更した**: tree-sitter をやめ、Ruby の字句解析器を移植し、racc の LALR 表を取り出して駆動する（[[tecsgen-python3 構文解析方式決定]]、ユーザー決定）。着手時の実測で、Ruby 版が実際にパースした384ファイルのうち tree-sitter と受理結果が食い違うものが4件、両方エラーでも位置・件数が違うものが複数あり、racc のエラー回復と TYPE_NAME の判定を tree-sitter では再現できないと分かったため
- [x] LALR 表の抽出（`tools/port/gen_racc_tables.py` → `syntax/cdl_tables.py`・`cdecl_tables.py`）
- [x] racc の駆動部（`syntax/racc_runtime.py`）。**移植元は racc の C 実装 `cparse.c`**。Ruby 版 tecsgen は C 実装を使っており、pure-Ruby 実装とはエラー回復が違う（error トークンの shift で先読みを捨てない）
- [x] CDL・C の字句解析器（`syntax/cdl_lexer.py`・`cdecl_lexer.py`）。latin-1 で1バイト＝1文字として走査し、`near 'ã'` まで再現
- [x] パーサ本体（`syntax/cdl_parser.py`・`cdecl_parser.py`）。TYPE_NAME の判定は `typename_resolver` を差し替える形にし、P3 で `Namespace` につなぐ
- [x] 文法アクションの骨格（`tools/port/gen_action_stubs.py` → `syntax/cdl_actions.py` 325個・`cdecl_actions.py` 121個）。字句解析の状態を変える呼び出し（`set_in_specifier`・`set_no_type_name`・`TYPEOF` の読み飛ばし）だけ移植した
- [x] tree-sitter の文法・C 拡張・依存を削除し、ビルドを hatchling に戻した
- 検証: Ruby 版を実行するオラクル（`tests/ruby/p2_oracle.rb`、記録は `tests/golden/p2/`）との差分テストで、全155ケースについて、字句解析（CDL の parse 551回・338,400トークン）、駆動部（CDL 551回＋import_C 177回。構文エラー20ケースの回復を含む）、通しの構文解析（構文エラーの出力21ケース・24行）がすべて一致。pytest 512件（Windows）/ 507件＋5件スキップ（WSL）、`ruff`・`ty` 問題なし
- **合格条件を変更した**: 「パース直後のモデル JSON の一致」は、アクションがモデルクラス（P3）に依存するため P3 の最初の合格条件へ移した。P2 は字句解析と駆動部の完全一致を合格条件とした
- 仕様書: [[tecsgen-python3内部仕様 - 05 字句解析・構文解析|内部仕様5章]]
- P2 で見つけた、後続フェーズへの持ち越し
  - **P3**: 文法アクション本体（CDL 325個・C 121個）の移植。`unported_rules` が空になることを確認する。`Import`（2段階のファイル探索、パース中の同期的な入れ子パース）・`Import_C`（cpp の実行）、`typename_resolver` を `Namespace.is_typename` につなぐ、`_push_model_stacks`
  - **P3**: Ruby 版の `Token` の値は、識別子が Symbol、リテラルが String。Python 版はどちらも `str` なので、区別が要る箇所を洗い出す（**解消**: P3 で `Symbol` クラス（`str` の派生）を導入して区別した。[[tecsgen-python3内部仕様 - 05 字句解析・構文解析]]、2026-10-03 確認）
  - 開発環境: WSL の `/tmp` は WSL の再起動で消える。オラクルの作業ディレクトリは `~/p2work`、WSL の仮想環境は `UV_PROJECT_ENVIRONMENT=$HOME/.venvs/tecsgen-python3` に置く。これを付けずに WSL で `uv run` すると、Windows 用の `.venv` が作り直されてしまう

## Related

- [[tecsgen-python3移植計画]] — 移動元（P3 以降・方針・リスク）
- [[tecsgen-python3]] — 親ノート
- [[tecsgen-python3 P0基本方針決定]] / [[tecsgen-python3 パッケージ構成決定]] / [[tecsgen-python3 構文解析方式決定]]
