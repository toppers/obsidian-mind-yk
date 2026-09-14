---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — コールバックの書き方。専用機構がないため明示的な結合として記述し、複数セルへは受け口配列と呼び口配列を対にする（§3.2.5）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-コールバックの書き方を教えて

TECSではコールバック専用の機構を持たない。コールバックは**明示的な結合**として記述し、複数セルへのコールバックは**受け口配列と呼び口配列を対に**して実現する。

---

## 基本的なコールバックの書き方（§3.2.5）

２つのセルが相互に接続し合う基本形（セルA→セルB + セルB→セルA）：

### コンポーネント図

```
+----------+     sig1      +----------+
| tTypeA   |               | tTypeB   |
| cellA    |               | cellB    |
|   cMain --------->▶ eMain|          |
|   ▶ eCb  <---------cCb   |          |
+----------+     sig2      +----------+
```

### CDLでの記述

```
celltype tTypeA {
    call  tSig1 cMain;    // 主体的な呼び口
    entry tSig2 eCb;      // コールバック受け口
};

celltype tTypeB {
    entry tSig1 eMain;    // 主体的な受け口
    call  tSig2 cCb;      // コールバック呼び口
};

cell tTypeA cellA {
    cMain = cellB.eMain;   // 主体的な結合
};

cell tTypeB cellB {
    cCb = cellA.eCb;       // コールバック結合（明示的に記述）
};
```

## 複数セルへのコールバック（§3.2.6）

呼び口配列と受け口配列を対にして実現する：

### コンポーネント図

```
[cellA] --cCb--> ▶ eMain[0] |cellB|
                              ▶ eMain[1]
[cellC] --cCb-->             ^ ^
```

### CDLでの記述

```
celltype tService {
    entry tSig1 eService;
    call  tSig2 cNotify[];   // 呼び口配列（複数の通知先）
};

celltype tClient {
    call  tSig1 cService;
    entry tSig2 eNotify[];   // 受け口配列（複数クライアントを識別）
};

cell tService serviceCell {
    cNotify[0] = clientA.eNotify[0];
    cNotify[1] = clientB.eNotify[0];
};

cell tClient clientA {
    cService = serviceCell.eService;
};
cell tClient clientB {
    cService = serviceCell.eService;
};
```

## セルタイプコードでのコールバック受け口実装

```c
ER tTypeA_eCb_func(CELLIDX idx, int32_t result)
{
    CELLCB *p_cellcb = GET_CELLCB(idx);
    // コールバック処理
    return E_OK;
}
```

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §2.6.1「コールバック」§3.2.5「コールバック」§3.2.6「呼び口配列と受け口配列」
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 配列化の定義
- [TECSコンポーネント実装](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-implementation.md) (confidence: high) — 受け口関数の記述

**Knowledge gaps:**
- なし
