---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第2章（動作環境）— Python 3.13.11以上、実行時依存なし、検証済みOS（Windows 11・WSL/Linux）、C プリプロセッサ、インストール方法。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第2章（全10章）。Ruby 版（[[work/active/tecsgen/tecsgen外部仕様 - 02 動作環境|第2章]]）の Ruby 処理系に関する項目を、Python 版では下表に差し替えます。

## 2. 動作環境

### 2.1 実行環境

| 項目 | 内容 |
|---|---|
| 実装言語 | Python 3 |
| 必要な Python | 3.13.11 以上（`pyproject.toml` の `requires-python`） |
| 実行時の依存パッケージ | なし（標準ライブラリだけ）。パーサの表、メッセージ表、標準 CDL ライブラリ（`tecs/`）はパッケージに同梱 |
| 検証済み OS | Windows 11、WSL（Linux）。両環境でテスト一式が通る（2026-10-02）。macOS 26.6.2（arm64、GitHub Actions の `macos-latest`、Apple clang 21）で `uv sync`・`tecsgen --version`・pytest が通る（2026-10-04、pytest は 1020 件成功・83 件スキップ。スキップは Ruby の実機を使う差分テストなど、WSL と同じ内訳）。ただし確認したのはテスト一式とバージョン表示までで、実際の CDL を手で流す利用は未確認 |
| C プリプロセッサ | `import_C` に必要。既定は `gcc -E -DTECSGEN`（`-c`・`TECS_CPP` で変更可）。カーネル付属のターゲットでは交差コンパイラ（例 `arm-none-eabi-gcc`）を指定する |

### 2.2 インストール

```sh
uv tool install .          # リポジトリのルートで。wheel を作って入れてもよい
tecsgen --version
```

`tecsgen` と `tecsmerge` の2コマンドが入ります。`TECSPATH` を設定しない場合は、パッケージ同梱の `tecs/`（Ruby 版の `tecs/` と同内容）を使います。

### 2.3 Ruby版との差異

| 項目 | Ruby 版 | Python 版 |
|---|---|---|
| 処理系 | Ruby 1.9.2 以降 | Python 3.13.11 以降 |
| 配布 | `tecsgen.rb` の置き場所に依存 | `uv tool install` / wheel |
| 標準ライブラリ以外の依存 | なし | なし |
| Windows | Cygwin または exerb 版 | Windows ネイティブ（Python）。Cygwin は未検証 |
| `-v` の表示 | `ruby X.Y.Z [...]` の行 | `python X.Y.Z [...]` の行、`... is found in` の行にはインストール先のパスが出る |

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3外部仕様 - 05 コマンドラインインターフェース]] — `-c`・`TECS_CPP`・`TECSPATH`
