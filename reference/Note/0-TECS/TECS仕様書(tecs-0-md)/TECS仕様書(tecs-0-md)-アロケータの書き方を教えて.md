---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — アロケータの書き方。シグニチャ定義→セルタイプ定義→セル結合の順。図では結合線に近接した▲からアロケータセルの受け口へ線を引く（§3.2.10）"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-アロケータの書き方を教えて

アロケータは `send`/`receive` 引き数を持つシグニチャで使用し、シグニチャ定義→セルタイプ定義→セル結合の順に記述する。

---

## コンポーネント図での描き方（§3.2.10）

アロケータは、結合の線に近接した**▲**（塗りつぶし三角形）からアロケータセルの受け口に結合の線を引いて表す。これは内部生成されるアロケータ呼び口からアロケータセルへの結合を表す。  
呼び元と呼び先の両方に呼び口にアロケータ呼び口が内部生成される。

## CDLでのシグニチャ定義

`send`/`receive` 引き数にアロケータシグニチャを指定する：

```
signature tAllocatorSig {
    ER alloc([out] void **p_mem, [in] size_t size);
    ER dealloc([in] void *mem);
};

signature tDataSig {
    ER sendData([send(tAllocatorSig)] void *data);
    ER receiveData([receive(tAllocatorSig)] void **pp_data);
};
```

## CDLでのセルタイプ定義

受け口側セルタイプで具体的なアロケータを指定する（合流する全呼び元が同一アロケータを使う必要があるため受け口側で指定）：

```
celltype tReceiver {
    entry tDataSig eReceive;
    allocator eReceive.receiveData.pp_data = allocCell.eAllocate;
};
```

## CDLでのセル結合

```
cell tAllocator allocCell {};    // アロケータセル

cell tSender senderCell {
    cSend = receiverCell.eReceive;
};

cell tReceiver receiverCell {};
```

## リレーアロケータ（多段リレーモデル向き）

受け取った `send` 引き数のメモリをそのまま次の呼び口の `send` に引き渡す場合はリレーアロケータを使う：

```
allocator eReceive.data <= cForward.data;   // リレーアロケータ指定
```

---

**Sources used:**
- TECS仕様書 V1.3.0.1 raw — §3.2.10「アロケータ」§4.18.6「アロケータ指定子2」
- [アロケータ（allocator）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-allocator.md) (confidence: high) — アロケータの定義・種類・シグニチャとの連携
- [シグニチャ（signature）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-signature.md) (confidence: high) — send/receive引き数

**Knowledge gaps:**
- 具体的なアロケータCDL構文の詳細はwikiに未記載（rawソースに情報あり）
