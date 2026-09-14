---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 合流の書き方。複数の呼び口が一つの受け口に結合する状態。合流は許されるが逆の分流は許されない（§3.2.2）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-合流の書き方を教えて

合流は、**複数の呼び口が一つの受け口に結合する状態**のことである（§3.2.2）。TECSでは合流は許されるが、逆の分流（一つの呼び口から複数の受け口）は許されない。

---

## コンポーネント図での描き方（§3.2.2）

複数のセルの呼び口から一つの受け口へ向かう結合線をそれぞれ描く。

```
+----------+
| tTypeA   |
| cellA    |
|    cCall1 ---+
+----------+   |  sig
               +---->▶ eEntry  | cellB |
+----------+   |
| tTypeA   |   |
| cellC    |
|    cCall2 ---+
+----------+
```

複数の呼び口（`cellA.cCall1`、`cellC.cCall2`）が `cellB.eEntry` に合流する。

## CDLでの記述

```
cell tTypeA cellA {
    cCall = cellB.eEntry;   // 呼び口を eEntry に結合
};

cell tTypeA cellC {
    cCall = cellB.eEntry;   // 別のセルも同じ受け口に結合（合流）
};
```

## 合流時のアロケータ制約

send/receive引数を持つシグニチャでは、複数の呼び口が合流して1つの受け口に結合される場合、すべての呼び元が**同一のアロケータ**を使う必要がある。このため、具体的なアロケータの指定は受け口側セルタイプで行う。

## 注意点

- 合流は可能だが、シグニチャが形式的に一致しても関数の意味仕様が一致するかどうかはTECSでは保証しない
- 分流（1つの呼び口から複数の受け口）は不可 → 呼び口配列で代替

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.2「合流」
- [結合（join）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-join.md) (confidence: high) — 合流の定義・CDL記述
- [アロケータ（allocator）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-allocator.md) (confidence: high) — 合流時のアロケータ制約

**Knowledge gaps:**
- なし
