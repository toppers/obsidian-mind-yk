---
date: 2026-08-16
description: "tecsgen外部仕様書 第5章（コマンドラインインターフェース）— 書式、オプション一覧、環境変数、終了ステータス。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 5 of 10.

## 5. コマンドラインインターフェース

### 5.1 書式

```
tecsgen [OPTION...] CDL-File
ruby PATH_TO_TECSGEN/tecsgen.rb [OPTION...] CDL-File
```

### 5.2 オプション一覧

#### ファイル処理

| オプション | デフォルト | 説明 |
|---|---|---|
| `-g, --gen=dir` | `gen` | 生成ファイルの出力ディレクトリ |
| `-f, --force-overwrite` | — | テンプレートファイルを強制上書き |

#### C プリプロセッサ

| オプション | 説明 |
|---|---|
| `-c, --cpp=cpp_cmd` | 使用する C プリプロセッサコマンド |
| `-D, --define=def` | プリプロセッサマクロ定義（複数指定可） |
| `-I, --import-path=path` | インクルードパス追加（複数指定可） |
| `-L, --library-path=path` | Ruby ライブラリパス追加 |

#### コード生成

| オプション | 説明 |
|---|---|
| `-R, --RAM-initializer` | RAM 初期化コードを生成する（`INITIALIZE_TECS()` の呼び出しが必要） |
| `-r, --ram` | RAM のみで動作するコードを生成する（ROM サポート無効） |
| `-G, --generate-region=path` | 指定リージョンのコードのみ生成 |
| `-U, --unoptimize` | 呼び口・受け口の最適化を無効化する |
| `--unoptimize-entry` | 受け口最適化のみを無効化する |
| `--c-suffix=c` | 生成 C ファイルの拡張子を指定（デフォルト: `c`） |
| `--h-suffix=h` | 生成ヘッダファイルの拡張子を指定（デフォルト: `h`） |
| `--generate-all-template` | セルが存在しないセルタイプのテンプレートも生成する |
| `--generate-no-template` | テンプレートを一切生成しない |
| `--no-default-import-path` | デフォルトのインポートパス（`TECSPATH` 配下）を追加しない |

#### 診断・その他

| オプション | 説明 |
|---|---|
| `-d, --dryrun` | 文法チェックのみ（コード生成なし） |
| `-v, --verbose` | 詳細情報を出力 |
| `-k, --kcode=code` | CDL ファイルの文字コードを指定（`euc`/`sjis`/`none`/`utf8`） |
| `-i, --idx_is_id` | 全セルタイプに `idx_is_id` を適用する |
| `-u, --unique-id` | セルタイプをまたいで連番 ID を付与する（デフォルト: セルタイプごとに 1 から） |
| `--version` | バージョンを表示して終了 |
| `--no-banner` | バナー表示を抑制する |

### 5.3 環境変数

| 変数名 | 説明 |
|--------|------|
| `TECS_CPP` | C プリプロセッサコマンドを指定（`-c` オプションより優先度が低い） |
| `TECSPATH` | TECS ライブラリパス（`tecsgen/tecs/` を指定）。mruby / RPC プラグイン使用時に必要 |
| `TECSGEN_DEFAULT_RAM` | 設定した場合、デフォルトコード生成モードを ROM → RAM に変更する |
| `TECSGEN_LANG` | 言語・文字コード指定（例: `C.UTF-8`, `ja_JP.eucJP`） |
| `TECSGEN_FILE_LANG` | CDL ファイルの文字コードのみを指定 |
| `RUBYLIB` | Ruby ライブラリパス（`-L` オプションと同等） |

### 5.4 終了ステータス

| コード | 意味 |
|--------|------|
| `0` | 正常終了 |
| `1` | エラー終了 |

---

