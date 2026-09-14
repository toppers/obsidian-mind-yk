---
date: 2026-06-18
description: "TECSにおける多段リレーモデルの書き方 — 複数のリレーアロケータを経由してメモリバッファを複数コンポーネントに渡すパターン（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 多段リレーモデルの書き方を教えて

**多段リレーモデル**は、メモリバッファが複数のコンポーネントを経由して伝達されるパターンです。複数のリレーアロケータを連鎖させて実現します。

## 概念

```
[AppCell] ---> [RelayCell1] ---> [RelayCell2] ---> [ServiceCell]
    ↑ buf確保         ↑ buf中継          ↑ buf中継        ↑ buf使用
```

各中間コンポーネントは受け取ったバッファポインタを次のコンポーネントへ転送します。

## CDLでの記述

```cdl
// リレーセルタイプ（中間層）
celltype tRelay {
    entry sService eIn;             // 受け口（上流から受け取る）
    call  sService cOut;            // 呼び口（下流へ転送する）
    [allocator(cOut::write = eIn::write)]   // アロケータのリレー
};

// 組上げ記述
cell tApp App {
    cSvc = Relay1.eIn;
};
cell tRelay Relay1 {
    [allocator(cOut::write = eIn::write)]
    cOut = Relay2.eIn;
};
cell tRelay Relay2 {
    [allocator(cOut::write = eIn::write)]
    cOut = Service.eService;
};
cell tService Service {};
```

## TCD表記

```
+-------+   [alloc]  +--------+  [alloc]  +--------+  +----------+
| App   |----------->| Relay1 |---------->| Relay2 |->| Service  |
+-------+            +--------+           +--------+  +----------+
```

> **注記**: 多段リレーモデルの詳細はTECS仕様書（HTML版）の TINETプラグイン関連ドキュメントに記載があります。

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: medium)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: medium)
- tecs_html wiki: [実装モデル](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-implementation-model.md) (confidence: medium)

## 知識ギャップ

tecs_html wikiの現在のコンパイル済み記事には多段リレーモデルの詳細例が限られています。TINET+TECS関連のrawソース（`raw/articles/2026-06-12-tinet-tlsf-tecs*`）に詳細が含まれている可能性があります。

## 関連

[[TECS仕様書(html版)-アロケータの書き方を教えて]] | [[TECS仕様書(html版)-複合セルの書き方を教えて]] | [[TECS仕様書(html版)-目次]]
