---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 受け口配列の書き方。図では受け口名に配列の添数を添える記法（eEntry[0] 等、§3.2.4）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-受け口配列の書き方を教えて

受け口配列は、配列化された受け口であり、添数で呼び元セルを識別することができる。呼び口配列と対にすることで複数呼び元に対するコールバックを実現できる。

---

## コンポーネント図での描き方（§3.2.4）

受け口名に**配列の添数**を添えて記す（例：`eEntry[0]`、`eEntry[1]`）。

```
+----------+
| tTypeA   |
| cellA    |
|   cCb -------> ▶ eEntry[0]  |  cellB  |
+----------+                  |         |
                              |  (受け口配列) |
+----------+                  |         |
| tTypeC   |                  |         |
| cellC    |                  |         |
|   cCb -------> ▶ eEntry[1]  |         |
+----------+
```

## CDLでの記述

受け口の宣言に `[]` で要素数を指定する：

```
celltype tTypeB {
    entry tSig eEntry[];    // 受け口配列
};
```

## セルタイプコードでの使い方

受け口配列の受け口関数は `CELLIDX idx` に加えて添数 `id_x` も引数に取る：

```c
ER tTypeB_eEntry_func(CELLIDX idx, int_t id_x, int32_t val)
{
    CELLCB *p_cellcb = GET_CELLCB(idx);
    // id_x で呼び元を識別して処理
    return E_OK;
}
```

## 呼び口配列との組み合わせ（コールバック実現）

呼び口配列と受け口配列を対にして、複数のセルに対するコールバックを実現できる（§3.2.6）：

```
cell tTypeA cellA {
    cCb = cellB.eEntry[0];   // cellA → cellB.eEntry[0]
};
cell tTypeC cellC {
    cCb = cellB.eEntry[1];   // cellC → cellB.eEntry[1]
};
```

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.4「受け口配列」§3.2.6「呼び口配列と受け口配列」
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 受け口配列の定義
- [TECSコンポーネント実装](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-implementation.md) (confidence: high) — 受け口配列の関数引数

**Knowledge gaps:**
- CDLでの受け口配列の要素数指定構文の詳細はwikiに未記載
