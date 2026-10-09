---
date: 2026-10-02
description: "tecsgen-python3外部仕様 第9章（使用例）— インストール、最小構成、ディレクトリ指定、カーネルヘッダ、ドライラン、tecsmerge を含む典型的なビルドフロー、利用者プラグインの指定。"
project: tecsgen-python3
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

[[tecsgen-python3外部仕様]] の第9章（全10章）。コマンドの使い方は [[work/active/tecsgen/tecsgen外部仕様 - 09 使用例|Ruby版 第9章]]と同じで、`ruby` を付けずに `tecsgen` を直接呼べます。

## 9. 使用例

### 9.1 インストール

```sh
uv tool install .
tecsgen --version
```

### 9.2 最小構成

```sh
tecsgen myapp.cdl
```

`gen/` に生成コードを出力します。

### 9.3 ディレクトリ指定・カーネルヘッダ

```sh
tecsgen -g build/gen/ myapp.cdl
tecsgen -I asp3/include/ -I asp3/kernel/ myapp.cdl
```

### 9.4 ドライラン（文法チェックのみ）

```sh
tecsgen -d myapp.cdl
```

### 9.5 利用者プラグインを使う

```sh
tecsgen -L ./myplugins myapp.cdl     # ./myplugins/MyPlugin.py を探す
```

プラグインは Python で書きます（[[tecsgen-python3外部仕様 - 06 プラグインシステム\|6章]]）。

### 9.6 典型的なビルドフロー

```sh
# CDL → C コード生成
tecsgen -g gen/ -I kernel/include/ app.cdl

# テンプレートを既存実装にマージ（コピー先にあるファイルだけ）
tecsmerge -e gen/ src/

# ビルド
make
```

関数の名前を変えたときは、`tecsmerge -p ePort -f oldFunc:newFunc gen/ src/` のように指定します。

## Related

- [[tecsgen-python3外部仕様]] — 目次
- [[tecsgen-python3外部仕様 - 05 コマンドラインインターフェース]]
