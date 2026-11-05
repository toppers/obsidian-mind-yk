---
date: 2026-08-16
description: "tecsgen外部仕様書 第9章（使用例）— 最小構成、ディレクトリ指定、カーネルヘッダ、ドライラン、典型的なビルドフロー。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - spec
---

Domain note split from [[tecsgen外部仕様]] (2026-08-16, 25KB threshold). Chapter 9 of 10.

## 9. 使用例

### 9.1 最小構成

```bash
tecsgen myapp.cdl
```

`gen/` ディレクトリに生成コードを出力する。

### 9.2 ディレクトリ指定

```bash
tecsgen -g build/gen/ myapp.cdl
```

### 9.3 カーネルヘッダを含む場合

```bash
tecsgen -I asp3/include/ -I asp3/kernel/ myapp.cdl
```

### 9.4 ドライラン（文法チェックのみ）

```bash
tecsgen -d myapp.cdl
```

### 9.5 典型的なビルドフロー

```bash
# CDL → C コード生成
tecsgen -g gen/ -I kernel/include/ app.cdl

# テンプレートを既存実装にマージ
tecsmerge -e gen/ src/

# ビルド
make
```

---

