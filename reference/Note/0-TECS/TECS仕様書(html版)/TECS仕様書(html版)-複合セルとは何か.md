---
date: 2026-06-18
description: "TECSにおける複合セル（Composite Cell）の定義 — 内部に複数のセルを持ち外部に受け口・呼び口をエクスポートする複合セルタイプ（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 複合セルとは何か

**複合セル (Composite Cell)** は、`composite` キーワードで定義されたセルタイプから生成されたセルです。内部に複数のセルを持ち、内部構造を隠蔽しながら外部に受け口・呼び口をエクスポートします。

## 特性

- 内部セルを持つ（内部構造のカプセル化）
- 外部に受け口・呼び口・属性をエクスポートして公開する
- エクスポートした属性は内部セルに伝達される
- TCD図上では外側の長方形が複合セルを示す

## CDLでの宣言

```cdl
[singleton]
composite tMyComposite {
    entry sSignature eExported;      // 受け口エクスポート
    call  sSignature cExported;      // 呼び口エクスポート
    attr {
        int32_t param;               // 属性エクスポート
    };

    // 内部セル
    cell tInner Inner {
        [allocator()] cPort = eExported;   // アロケータ指定
        param = composite.param;           // 属性の伝達
    };
    cell tInner2 Inner2 {
        cPort = Inner.eOther;
    };
};
```

## TCD表記

```
+----------------------------------------+
| tMyComposite (composite)               |
|   +------------+    +------------+     |
|   | tInner     |--->| tInner2    |     |
|   |            |    |            |     |
|   +------------+    +------------+     |
|> eExported                             |
+----------------------------------------+
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-セルタイプとは何か]] | [[TECS仕様書(html版)-複合セルの書き方を教えて]] | [[TECS仕様書(html版)-目次]]
