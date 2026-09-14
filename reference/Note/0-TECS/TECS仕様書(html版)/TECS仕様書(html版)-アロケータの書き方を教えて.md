---
date: 2026-06-18
description: "TECSにおけるアロケータの書き方 — [allocator()]指定子のCDL構文、呼び口・受け口のメモリ確保機構（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# アロケータの書き方を教えて

**アロケータ**は、呼び口から受け口へのポインタ受け渡しに使われるメモリ確保機構です。`[allocator()]` 指定子を使って設定します。

## セルタイプでの宣言

```cdl
celltype tMyCell {
    call sMySignature cPort;
};
```

## 組上げ記述でのアロケータ指定

```cdl
[allocator(cPort::funcName = eAllocEntry)]
cell tMyCell MyCell {
    cPort = OtherCell.ePort;
};
```

または複合セルタイプ内で：

```cdl
composite tMyComposite {
    call sSignature cExported;
    cell tInner Inner {
        [allocator()] cPort = eExported;
    };
};
```

## 実装モデルでの説明

アロケータはTLSFアロケータとの組み合わせで動的メモリ管理を実現します。送信バッファ等のメモリをコンポーネント境界で確保・解放する際に使用します。

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [実装モデル](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-implementation-model.md) (confidence: medium)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: medium)

## 関連

[[TECS仕様書(html版)-多段リレーモデルの書き方を教えて]] | [[TECS仕様書(html版)-複合セルの書き方を教えて]] | [[TECS仕様書(html版)-目次]]
