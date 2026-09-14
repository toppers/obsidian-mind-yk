---
date: 2026-06-18
description: "TECSにおける複合セル（composite celltype）の書き方 — composite宣言、内部セル・エクスポート構文、属性伝達（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 複合セルの書き方を教えて

複合セル（composite）は `composite` キーワードを使って宣言します。内部に複数のセルを持ち、受け口・呼び口・属性を外部にエクスポートします。

## CDLでの宣言

```cdl
[singleton]
composite tMyComposite {
    // 外部に公開する受け口・呼び口・属性
    entry sSignature eExported;         // 受け口エクスポート
    call  sSignature cExported;         // 呼び口エクスポート
    attr {
        int32_t param = 0;              // 属性エクスポート
    };

    // 内部セルの定義
    cell tInner Inner1 {
        [allocator()] cPort = eExported; // アロケータ指定
        param = composite.param;         // 属性の伝達
    };
    cell tInner2 Inner2 {
        cConnect = Inner1.eOther;        // 内部セル間の結合
    };
};
```

## 組上げ記述（利用側）

```cdl
cell tMyComposite MyComp {
    param     = 42;
    cExported = OtherCell.ePort;    // エクスポートした呼び口を結合
};
```

## 特徴

| 特徴 | 説明 |
|------|------|
| **カプセル化** | 内部セルの構造は外部から隠蔽される |
| **エクスポート** | 受け口・呼び口・属性を外部に公開できる |
| **属性伝達** | `composite.attrName` で内部セルへ属性を伝達 |
| **図上の表記** | 外側の長方形が複合セルを表す |

## TCD表記

```
+------------------------------------------+
| tMyComposite                             |
|   +----------+         +----------+      |
|   | tInner   |-------->| tInner2  |      |
|   +----------+         +----------+      |
|> eExported                               |
+------------------------------------------+
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-複合セルとは何か]] | [[TECS仕様書(html版)-セルタイプとは何か]] | [[TECS仕様書(html版)-アロケータの書き方を教えて]] | [[TECS仕様書(html版)-目次]]
