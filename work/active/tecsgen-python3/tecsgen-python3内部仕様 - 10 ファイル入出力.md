---
date: 2026-09-27
description: "tecsgen-python3内部仕様10章。文字コードの扱い（CDLをコーデック+surrogateescapeで復号しバイト列を保存）、TECSIO・AppFile・CFile・Console・RubyIOの設計とRuby版との差異"
project: tecsgen-python3
status: active
quarter: Q3-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

# tecsgen-python3 内部仕様 10章 ファイル入出力

[[tecsgen-python3内部仕様]] の10章。移植元は [[work/active/tecsgen/tecsgen内部仕様 - 10 ファイル入出力|Ruby版 10章]]。P1（2026-09-27）で実装した範囲を記述する。

## 10.1 文字コードのモデル

Ruby 版は Shift_JIS 以外の CDL を `ASCII-8BIT`（バイト列のまま）で読み、生成ファイルにもバイト列のまま書く。Python の `str` は文字コードを持たないため、次のモデルに置き換えた。

- CDL は `TecsgenContext.file_codec` で復号する。復号できないバイトは `errors="surrogateescape"` で保存する
- 生成ファイルは同じコーデックと `surrogateescape` で符号化する。**入力のバイト列はそのまま出力へ戻る**（`test_tecsio_round_trips_invalid_bytes` で確認）
- tecsgen 自身の文字列（メッセージ表など）は Unicode のまま扱い、書き出すときに CDL の文字コードへ符号化する。Ruby 版が `TECSMsg.get` の中で kconv していた変換を、出力時へ移したことになる

| `$CHARSET_FILE` | Ruby の読み方 | Python のコーデック |
|---|---|---|
| `eucJP` | ASCII-8BIT | `euc_jp` |
| `sjis` | Windows-31J で読み Shift_JIS へ | `cp932` |
| `utf8` | ASCII-8BIT | `utf-8` |
| なし・`iso8859-1` | ASCII-8BIT（Kconv::BINARY） | `utf-8`（変換しないのでバイト列が保存されれば足りる） |

> [!warning] Ruby 版との差異
> - Ruby 版は非 ASCII の CDL を**バイト単位**で字句解析している。正解データ `sample/error-13` では `syntax error near '\xe3'` と、UTF-8 の1文字の先頭1バイトだけが出力されている。**Python 版もバイト単位で字句解析し、全155ケースで一致している（2026-10-02 確認）**。
> - **`-k euc` と UTF-8 リテラル（2026-10-04 に差異を解消）**: Ruby 版の標準付属プラグイン（`GenOpaqueMarshaler`・`GenTransparentMarshaler`・`RPCPlugin`・`ATK1ISRPlugin`・`DataPumpHolderPlugin`・`ThroughPlugin` など）は、日本語のコメントをソースの UTF-8 リテラルのまま `file.print` で書く。ASCII-8BIT で開いた出力へはそのバイト列が入るので、`-k euc` では EUC-JP の本文に UTF-8 のコメントが混ざる。Python 版も同じにするため、これらのリテラルを `ruby_compat.utf8_literal` で包み、surrogateescape の文字にして `RubyIO` へ渡す（どのコーデックでも UTF-8 のバイト列のまま出る）。`-k sjis` では Ruby が Shift_JIS 指定で開いたファイルへ書くときにリテラルも変換するので、`utf8_literal` は文字列をそのまま返す。ソース中の日本語リテラルを全数調べ（`ast` で docstring 以外の非 ASCII 文字列定数を列挙。メッセージ表と C プリプロセッサのエラー文を除く）、書き出す側を包んだ。新しく日本語リテラルを書き出すプラグインを移植するときは、同じく `utf8_literal` で包む
> - **`-k sjis` と cp932（2026-10-04 に差異を解消）**: Ruby 版は Windows-31J の CDL を、Shift_JIS 指定で開いたファイルへ書くときに Windows-31J → UTF-8 → Shift_JIS（JIS X 0208 の厳密な表）と変換する。Windows-31J にあって Shift_JIS に無い文字（`～` U+FF5E・`∥`・`－` U+FF0D・`￠`・`￡`・`￢`・`¦`・丸数字・ローマ数字・`㈱`・`髙` など）が出力に入ると `Encoding::UndefinedConversionError` になり、`H1001`（`U+FF5E to Shift_JIS in conversion from Windows-31J to UTF-8 to Shift_JIS`）で終了コード 1 になる。Python 版は `ruby_compat.check_shift_jis` で同じ規則を `RubyIO.write` に入れた（cp932 の全文字を Ruby 3.2.3 で変換して集合を取り、Python の `shift_jis` で表せない文字から、Ruby が通す `U+0080`・`U+F8F0`〜`U+F8F3` を除いた集合と一致）。cp932 に対応する Unicode が無い `81 AD` のような並びは、Ruby では構造が正しいので字句解析を通り、書き出しで `"\x81\xAD" to UTF-8 in conversion from Windows-31J to UTF-8 to Shift_JIS` になる。Python 版も同じ例外にする
> - **`-k sjis` と不正なバイト列（2026-10-04 に確認して解消）**: Ruby 版は Windows-31J として不正なバイト列（UTF-8 の日本語、行末の孤立した先頭バイト、`0x80`・`0xA0`・`0xFD`〜`0xFF`）を含む行に正規表現を当てて `ArgumentError`（`invalid byte sequence in Windows-31J`）になり、CDL は `G1014`、C ヘッダは `B1002` になる。判定は文字の構造だけ（先頭 `81-9F`・`E0-FC` に後続 `40-7E`・`80-FC`、1バイトは `00-7F`・`A1-DF`）で、Python の cp932 デコードの成否とは一致しないので、正規表現で構造を調べる（`syntax/cdl_lexer.py` の `_lines`。C ヘッダの字句解析も同じ関数を使う）
> - **確認の方法と結果**: 同じ入力を WSL の Ruby 3.2.3 と Python 版で生成し、全ファイル・標準出力・標準エラーをバイト比較した。(1) 日本語を含む最小の CDL を `-k none`・`utf8`・`euc`・`sjis` で生成: 4通りとも一致（`tecsgen.rbdmp` を除く）。(2) `～` を含む `-k sjis`: 終了コード 1、`.tmp` を含む9ファイルが一致。(3) 不正バイト列4種（UTF-8 のコメント・`81 AD`・行末の `81`・`0x80`）: 一致。(4) `test/opaqueRPC` を `-k euc`・`utf8` で生成: 313ファイルが、`tmp_*.h` と標準出力にあるパス（作業ディレクトリと同梱 CDL の置き場所）を除いて一致。(5) `ThroughPlugin` 経由で日本語リテラルを出す CDL（59ファイル）を `-k none`・`utf8`・`euc`・`sjis` で生成: 4通りとも一致。テストは `tests/test_kcode_ruby_compat.py`

## 10.2 TECSIO（`syntax/tecsio.py`）

- `TECSIO.foreach(file)` は行のイテレータ。Ruby の `IO#each` と同じく **LF だけで行を分け**、改行文字を含めて返す。CRLF は変換しない
  - Python のテキストモード（`newline=""`）は単独の CR でも行を分けるため使わない。バイト列を LF で分けてから行ごとに復号する（EUC-JP・cp932・UTF-8 は LF が文字の途中に現れないので、行単位の復号で結果は変わらない）
- `str_code_convert` は恒等関数として残した（呼び出し箇所を Ruby 版と対応させるため）

## 10.3 AppFile・MemFile（`core/generate.py`）

- `AppFile.open(name)`: 同じ名前の2回目以降は追記モード。`--force-overwrite` でなければ `name.tmp` に書く
- `AppFile.update()`: `name` が読めれば `readlines` 同士（バイト列）を比べ、同じなら `.tmp` を消し、違えば `os.replace` で置き換える。`-v` のときは Ruby 版と同じ文言（`changed` / `renaming '…' => '…'` / `not changed`）を出す
- 開いたファイルの一覧はクラス変数（挿入順）。テスト用に `AppFile.reset()` を追加した（Ruby 版には無い）

## 10.4 CFile（`core/plugin.py`）

プラグインがファイルを書くときに使う。コーデックの選び方は Ruby 版の条件をそのまま写した。

1. ファイルを Shift_JIS で開いた（`$Ruby19_File_Encode == "Shift_JIS"`）→ `cp932`（Ruby の IO が書き込み時に変換するため）
2. `$KCONV_CONSOLE` が BINARY → `utf-8`（変換しない）
3. それ以外 → `$KCONV_CDL` のコーデック

判定に**コンソール側**の変数を使うのは Ruby 版の実装のとおり（移植元の挙動を保つ。`test_cfile_codec` の3件目で固定）。`puts` は末尾が改行でも改行を足す点も Ruby 版と同じ。

## 10.5 Console と標準出力（`core/tecs_lang.py`・`ruby_compat.py`）

- `Console.print`/`puts` は `TecsgenContext.console_codec` で符号化して書く
- Ruby の `print`/`puts` を直接使っている箇所は `ruby_compat.rb_print`/`rb_puts` で書く（UTF-8）
- どちらも `sys.stdout.buffer` へバイト列で書き、改行を変換しない（Windows でも LF）。テキスト層を先に flush して出力順を保つ
- ファイル出力の共通部品として `ruby_compat.RubyIO`（`print`・`puts`・`printf`・`close`）を置いた

## Related

- [[tecsgen-python3内部仕様]] — 目次
- [[tecsgen-python3内部仕様 - 11 エラー・警告処理]] / [[tecsgen-python3内部仕様 - 12 グローバル変数一覧]]
- [[tecsgen-python3移植計画]] — P1
- [[work/active/tecsgen/tecsgen内部仕様 - 10 ファイル入出力|Ruby版 10章]]
