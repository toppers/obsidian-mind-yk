---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 複合セルの書き方。CDLの composite キーワードで複合セルタイプを定義し cell 文で生成する。図では通常は内部構造を描かない（§3.2.8）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-複合セルの書き方を教えて

複合セルは複合セルタイプから生成されるセルである。CDLで `composite` キーワードを使って複合セルタイプを定義し、通常のセルと同様に `cell` 文で生成する。

---

## コンポーネント図での描き方（§3.2.8）

- 通常は複合セルの**内部構造は描かない**（図3.9 参照）
- 内部構造を見せる場合は内部セルを展開して描く（図3.8 参照）

通常の描き方（内部非表示）：
```
+------------------+
| tMyComposite     |
| compositeCell    |
|          cSig ------> ▶ eEntry  | otherCell |
|  ▶ eSig          |
+------------------+
```

## CDLでの複合セルタイプ定義

```
composite tMyComposite {
    entry tSig eSig;          // 外部公開の受け口
    call  tSig cSig;          // 外部公開の呼び口
    attr  { int32_t val = 0; };  // 外部から設定可能な属性
    
    cell tInner1 cInner1 {
        cCall = cInner2.eEntry;   // 内部セル間の結合
    };
    cell tInner2 cInner2 {};
    
    composite.cSig = cInner1.cSig;   // 外部呼び口を内部セルに接続
    cInner2.eSig => composite.eSig;  // 外部受け口を内部セルに接続（逆結合）
};
```

## CDLでの複合セルの生成

通常のセルと同様に `cell` 文で生成する：

```
cell tMyComposite myComposite {
    cSig = targetCell.eEntry;   // 外部呼び口の結合
    val  = 10;                  // 属性の指定
};
```

## 外部結合と内部結合

- **外部結合**: 複合セルタイプの外部から、その複合セルの呼び口を別のセルの受け口に結合する
- **内部結合**: 複合セルタイプ内部で、内部セル間または内部セルと外部口の間を結合する

---

**Sources used:**
- [複合セルタイプ（composite celltype）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-composite-celltype.md) (confidence: high) — CDL記述例・外部/内部結合
- TECS仕様書 V1.3.0.1 raw — §3.2.8「複合セル」（コンポーネント図）

**Knowledge gaps:**
- なし
