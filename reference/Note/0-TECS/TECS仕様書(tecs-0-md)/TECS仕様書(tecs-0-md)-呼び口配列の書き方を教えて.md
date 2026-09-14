---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 呼び口配列の書き方。CDL記述と、図では呼び口名に配列の添数を添える記法（cCall[0] 等、§3.2.3）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-呼び口配列の書き方を教えて

呼び口配列は、配列化された呼び口であり、添数で呼び先セルを切り替えることができる。分流（1つの呼び口から複数の受け口）の代替手段として使用する。

---

## コンポーネント図での描き方（§3.2.3）

呼び口名に**配列の添数**を添えて記す（例：`cCall[0]`、`cCall[1]`）。

```
+------------------+
| tTypeA           |
| cellA            |
|   cCall[0] --------> ▶ eEntry  | cellB |
|   cCall[1] --------> ▶ eEntry  | cellC |
+------------------+
```

## CDLでの記述

呼び口の宣言に `[]` で要素数を指定する：

```
celltype tTypeA {
    call tSig cCall[];    // 呼び口配列
};

cell tTypeA cellA {
    cCall[0] = cellB.eEntry;   // 添数0 の呼び口を cellB に結合
    cCall[1] = cellC.eEntry;   // 添数1 の呼び口を cellC に結合
};
```

## セルタイプコードでの使い方

呼び口配列の場合は添数も指定して呼び出す：

```c
ER ret = cCall_func(idx, 0, arg1);   // 添数0 の呼び先を呼び出し
ER ret = cCall_func(idx, 1, arg1);   // 添数1 の呼び先を呼び出し
```

## 受け口配列との組み合わせ

呼び口配列と受け口配列を対にすることで、複数呼び元に対するコールバックを実現できる（§3.2.6）。呼び口配列の添数と受け口配列の添数を対応付けて結合する。

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.3「呼び口配列」§3.2.6「呼び口配列と受け口配列」
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 呼び口配列の定義
- [TECSコンポーネント実装](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-implementation.md) (confidence: high) — 呼び口配列の呼び出し

**Knowledge gaps:**
- CDLでの呼び口配列の要素数指定構文の詳細はwikiに未記載
