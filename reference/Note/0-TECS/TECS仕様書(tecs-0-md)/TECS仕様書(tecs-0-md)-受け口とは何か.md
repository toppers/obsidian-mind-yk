---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 受け口（entry port）とは何か。セルが機能を提供するための口。同じシグニチャを持つ呼び口のみと結合できる"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-受け口とは何か

受け口（entry port）は、**セルが機能を提供するための口**である。シグニチャに対応付けられ、受け口名を持つ。同じシグニチャを持つ呼び口のみと結合できる。

---

## 定義

- セルが機能を提供するための口
- シグニチャの関数群によって機能を提供
- 受け口名を持つ
- 受け口の関数は**インライン実装**することができる（セルタイプヘッダに記述）
- コンポーネント図では**塗りつぶした三角形**（セルの内向き）で表す

## 受け口関数

受け口に対応するシグニチャの関数について、セルタイプの実装として記述された関数。

非シングルトンセルタイプの場合：
```c
ER tMyCell_eEntry_func(CELLIDX idx, int32_t val)
{
    CELLCB *p_cellcb = GET_CELLCB(idx);
    int32_t limit = ATTR_limit;
    VAR_count++;
    return E_OK;
}
```

受け口配列の場合は `CELLIDX idx` に加えて添数 `id_x` も引数に取る。

## CDLでの記述例

```
celltype tB {
    entry tMySignature  eMyEntry;   // 受け口: シグニチャ tMySignature
};
```

---

**Sources used:**
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 受け口の定義・インライン実装
- [TECSコンポーネント実装](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-implementation.md) (confidence: high) — 受け口関数の記述形式

**Knowledge gaps:**
- なし
