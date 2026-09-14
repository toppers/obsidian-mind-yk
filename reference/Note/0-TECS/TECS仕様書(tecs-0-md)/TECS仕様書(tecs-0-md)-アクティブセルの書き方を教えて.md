---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — アクティブセルの書き方。active 指定子での定義と、コンポーネント図では長方形の辺を二重線で描く記法（§3.2.7）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-アクティブセルの書き方を教えて

アクティブセルはタスク・ハンドラ等CPU資源割付けを伴うセルであり、セルタイプに `active` 指定子を付けることで定義する。

---

## コンポーネント図での描き方（§3.2.7）

アクティブセルは長方形の辺を**二重線**で記すことで示す（通常のセルは単線）。

```
╔══════════════════╗
║ tActiveType      ║   ← 二重線でアクティブを示す
║ activeCell       ║
║        cCall ---------> ▶ eEntry  | otherCell |
╚══════════════════╝
```

## CDLでのアクティブセルタイプの定義

セルタイプに `[active]` 指定子を付ける：

```
[active]
celltype tMyTask {
    call tSig cSomeService;
    attr {
        PRI  priority = 5;
        SIZE stackSize = 1024;
    };
};
```

## CDLでのセル記述

通常のセルと同じ記述方法：

```
cell tMyTask myTask {
    cSomeService = serviceCell.eService;
    priority    = 3;
    stackSize   = 2048;
};
```

## ファクトリとの組み合わせ

アクティブセルタイプでは通常、OSカーネルのタスク定義（静的API）をファクトリで自動生成する：

```
[active]
celltype tMyTask {
    call tSig cSomeService;
    factory {
        write("cfg1_out.c", "CRE_TSK(TASK_$id$, { $priority$, $stackSize$, ... });");
    };
};
```

## 特性

- アクティブセルは受け口を一つも持たなくてもよい
- 内部セルがアクティブの場合、複合セルタイプもアクティブになる

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.7「アクティブ」（コンポーネント図）
- [セルタイプ（celltype）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-celltype.md) (confidence: high) — active指定子
- [ファクトリ（factory）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-factory.md) (confidence: high) — 静的API生成

**Knowledge gaps:**
- CDLでのactiveセルタイプの完全な構文例はwikiに詳細なし
