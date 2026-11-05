---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第5章（CLI）— Ruby版と完全互換の27オプション、環境変数、終了ステータス、-Lと RUBYLIB の差異、-v の差異、tecsmerge の書式。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第5章（全10章）。オプションの意味は [[work/active/tecsgen/tecsgen外部仕様 - 05 コマンドラインインターフェース|Ruby版 第5章]]と同じです。Ruby 版の `tecsgen.rb` にあるオプションはすべて同じ順序・同じ説明文で実装されています（2026-10-02 確認）。

## 5. コマンドラインインターフェース

### 5.1 書式

```
tecsgen [OPTION...] CDL-File...
tecsmerge [OPTION...] files_templ.c src_dir
tecsmerge [OPTION...] gen_dir       src_dir
```

### 5.2 tecsgen のオプション

Ruby 版 5.2 の表と同じ。下は表に載っていないものを含む全一覧です。

| 短形 | 長形 | 引数 | 説明 |
|---|---|---|---|
| `-D` | `--define` | def | `import_C` 用の cpp シンボル定義 |
| `-G` | `--generate-region` | path | 指定リージョンのコードだけ生成 |
| `-I` | `--import-path` | path | import / import_C のパス |
| `-L` | `--library-path` | path | プラグインを探すディレクトリ（Python 版の意味。5.5） |
| `-R` | `--RAM-initializer` | | RAM 初期化コードを生成 |
| `-U` | `--unoptimize` | | 呼び口・受け口の最適化を無効化 |
| `-c` | `--cpp` | cpp_cmd | C プリプロセッサ |
| `-d` | `--dryrun` | | 文法チェックのみ |
| `-f` | `--force-overwrite` | | テンプレートを強制上書き |
| `-g` | `--gen` | dir | 生成先ディレクトリ（既定 `gen`） |
| `-i` | `--idx_is_id` | | 全セルタイプに `idx_is_id` を適用 |
| `-k` | `--kcode` | code | CDL の文字コード（`euc`・`sjis`・`none`・`utf8`） |
| `-r` | `--ram` | | RAM のみで動作するコードを生成 |
| `-s` | `--show-tree` | | 構文木を表示 |
| `-t` | `--generator-debug` | | ジェネレータのデバッグ表示 |
| `-u` | `--unique-id` | | セルタイプをまたいで連番 ID を付与 |
| `-v` | `--verbose` | | 詳細情報を出力 |
| `-y` | `--yydebug` | | パーサのデバッグ表示 |
| | `--unoptimize-entry` | | 受け口最適化だけを無効化 |
| | `--no-banner` | | バナーを出さない |
| | `--version` | | バージョンを表示して終了 |
| | `--unit-test` | | 単体テスト用 |
| | `--generate-all-template` | | セルが無いセルタイプのテンプレートも生成 |
| | `--generate-no-template` | | テンプレートを生成しない |
| | `--no-default-import-path` | | 既定のインポートパス（`TECSPATH` 配下）を足さない |
| | `--c-suffix` | c | 生成 C ファイルの拡張子 |
| | `--h-suffix` | h | 生成ヘッダの拡張子 |

長いオプション名は、一意に決まる前方一致で省略でき（`--gen-r` など）、引数付きの短いオプションは引数を続けて書けます（`-Igen`）。`-h`・`--help` はヘルプを標準出力へ出して終了します。これらは Ruby の `optparse` と同じ挙動です。

### 5.3 環境変数

| 変数名 | Python 版での扱い |
|---|---|
| `TECS_CPP` | 対応。C プリプロセッサ（`-c` が優先） |
| `TECSPATH` | 対応。未設定のときはパッケージ同梱の `tecs/` |
| `TECSGEN_DEFAULT_RAM` | 対応。設定すると既定の生成モードが ROM から RAM になる |
| `TECSGEN_LANG`・`TECSGEN_FILE_LANG` | 対応（言語・文字コード指定） |
| `RUBYLIB` | **対応しない**。代わりの環境変数も作らない（5.5） |

### 5.4 終了ステータス

| コード | 意味 |
|---|---|
| `0` | 正常終了 |
| `1` | エラー終了（Ruby 版が例外で落ちる入力も、標準出力を同じにして 1 で終わる） |

### 5.5 Ruby版との差異

| 項目 | Ruby 版 | Python 版 |
|---|---|---|
| `-L` | Ruby ライブラリのパス追加 | 利用者プラグインを探すディレクトリ（複数指定可）。`<クラス名>.py`・`tecslib/plugin/<クラス名>.py` を探す。組み込みと同名のプラグインは上書きできない（[[tecsgen-python3 -L ユーザプラグイン探索設計]]） |
| `RUBYLIB` | `-L` と同等 | 対応しない |
| `--help` | — | 出力は Ruby 版とバイト一致（標準出力） |
| `--version` | — | 出力は Ruby 版とバイト一致（標準エラー出力） |
| `-v` | `ruby X.Y.Z [...]` の行 | `python X.Y.Z [...]` の行。`sMalloc.cdl is found in ...` のようなパスの行は、インストール先のパスになる |

### 5.6 tecsmerge のオプション

| 短形 | 長形 | 説明 |
|---|---|---|
| `-e` | `--exist-only` | コピー先にファイルがあるときだけマージ |
| `-p` | `--port=old:new` | 受け口名の変更（`new` を省略すると、直後の `-f` のための指定だけになる） |
| `-f` | `--func=old:new` | 受け口関数名の変更（直前の `-p` の受け口に対する指定） |
| `-s` | `--show_change_set` | 変更内容を表示 |
| `-o` | `--old-mode` | 関数本体の開始を `{` でなく `#[</ENTRY_FUNC>]#` で見る旧方式 |

Ruby 版と同じく、`-f` を `-p` より前に書く・キーワード行が欠けた入力などは例外として終了コード 1 になります。マージの結果（標準出力・終了コード・書き出されるファイル、バックアップ `_1` を含む）は Ruby 版と一致します。

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3 P0基本方針決定]] — CLI 完全互換の決定
- [[tecsgen-python3内部仕様 - 04 クラス設計]]
