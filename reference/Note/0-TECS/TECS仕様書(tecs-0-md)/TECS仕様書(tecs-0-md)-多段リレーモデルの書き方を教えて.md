---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 多段リレーモデルの書き方。アロケータ（▲）と send 結合を組み合わせ、複数セルを跨いでメモリ領域を引き渡す構造を描く（図3.15、§3.2.11）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-多段リレーモデルの書き方を教えて

多段リレーモデルは、アロケータにより確保されて `send` 引き数として受け口に渡されたメモリ領域を、再び呼び口から `send` 引き数として次のセルに引き渡す構造である（§3.2.11）。リレーアロケータを使って実現する。

---

## コンポーネント図での描き方（§3.2.11）

図3.15（TECS仕様書）が多段リレーモデルのコンポーネント図。アロケータ（▲）と `send` 結合を組み合わせて複数セルを跨いでメモリを引き渡す構造を描く。

構造のイメージ：
```
[アロケータ] ← ▲
    |
[sender] --send→ ▲ --send→ [relay] --send→ [receiver]
                              ↑
                         リレーアロケータ
```

## CDLでのリレーアロケータの指定

リレーアロケータはアロケータ指定子2（`<=` 記法）で記述する（§4.18.6）：

```
celltype tRelayCell {
    entry tDataSig eReceive;
    call  tDataSig cForward;
    
    // リレーアロケータ: 受け口で受け取った send 引き数メモリを
    // 呼び口の send 引き数として引き渡す
    allocator eReceive.data <= cForward.data;
};
```

## シグニチャの定義

```
signature tDataSig {
    ER transfer([send(tAllocSig)] void *data, [in] size_t size);
};
```

## セルの組み合わせ

```
cell tAllocator allocCell {};

cell tSender senderCell {
    cTransfer = relayCell.eReceive;
};

cell tRelayCell relayCell {
    cForward = receiverCell.eReceive;
};

cell tReceiver receiverCell {};
```

## 注意点

- セルフアロケータ（アロケータ指定子2の一種）は参照実装では未実装
- リレーアロケータは多段リレーモデル向きの実装方式

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.11「多段リレーモデル」§4.18.6「アロケータ指定子2」
- [アロケータ（allocator）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-allocator.md) (confidence: high) — リレーアロケータの定義

**Knowledge gaps:**
- wikiの主要記事には多段リレーモデルの独立記事が未作成
- リレーアロケータの完全なCDL構文はwikiに未記載（rawソースに情報あり）
