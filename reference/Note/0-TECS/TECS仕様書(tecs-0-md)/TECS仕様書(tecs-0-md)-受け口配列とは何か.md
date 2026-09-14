---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 受け口配列とは何か。添数で呼び元セルを識別する配列化された受け口。呼び口配列と対にすると複数呼び元へのコールバックを実現できる"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-受け口配列とは何か

受け口配列は、**配列化された受け口**である。添数で呼び元セルを識別することができる。呼び口配列と対にすることで複数呼び元に対するコールバックを実現できる。

---

## 定義

| 種別 | 説明 |
|------|------|
| **受け口配列** | 配列化された受け口。添数で呼び元セルを識別 |

## コンポーネント図での表現

コンポーネント図では、受け口名に配列の添数を添えて記す（§3.2.4）。

## 受け口配列の受け口関数

受け口配列の場合は `CELLIDX idx` に加えて添数 `id_x` も引数に取る：

```c
ER tMyCell_eEntryArray_func(CELLIDX idx, int_t id_x, int32_t val)
{
    CELLCB *p_cellcb = GET_CELLCB(idx);
    // id_x で呼び元を識別して処理
    return E_OK;
}
```

## 呼び口配列との組み合わせ（コールバック実現）

呼び口配列と受け口配列を対にして、複数のセルに対するコールバックを実現できる（§3.2.6）。  
この場合、呼び口配列の添数と受け口配列の添数を対応付けて結合する。

---

**Sources used:**
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 受け口配列の定義
- [TECSコンポーネントモデル](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-model.md) (confidence: high) — 一対多の結合モデル
- [TECSコンポーネント実装](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-implementation.md) (confidence: high) — 受け口配列の関数引数
- TECS仕様書 V1.3.0.1 raw — §3.2.4「受け口配列」

**Knowledge gaps:**
- なし
