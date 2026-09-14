---
date: 2026-06-18
description: "TECSにおける受け口配列の書き方 — CDL宣言構文、TCD表記、Cコードでの実装パターン（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 受け口配列の書き方を教えて

受け口配列は、同じシグニチャを持つ受け口を配列として宣言します。

## CDLでの宣言

```cdl
celltype tMyCell {
    entry sMySignature eArr[];    // 受け口配列（サイズ自動）
};
```

## 組上げ記述（結合）

複数の呼び口から個別の受け口配列要素に結合できます：

```cdl
// 呼び元セルA
cell tCallerA CallerA {
    cPort = MyCell.eArr[0];    // eArr[0] に結合
};

// 呼び元セルB
cell tCallerB CallerB {
    cPort = MyCell.eArr[1];    // eArr[1] に結合
};

cell tMyCell MyCell {};
```

## TCD表記

受け口名に添数を添えて表記します：

```
+------------------+
| tMyCell          |
|   eArr[0] <|     |<--- CallerA.cPort
|   eArr[1] <|     |<--- CallerB.cPort
+------------------+
```

## Cコードでの実装

```c
// 添数に応じて処理を分岐する受け口関数
ER eArr_funcName(CELLIDX idx, int32_t param) {
    CELLCB *p_cellcb = GET_CELLCB(idx);
    // idx を使ってどの受け口要素が呼ばれたか判別可能
    return E_OK;
}
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-受け口配列とは何か]] | [[TECS仕様書(html版)-呼び口配列の書き方を教えて]] | [[TECS仕様書(html版)-目次]]
