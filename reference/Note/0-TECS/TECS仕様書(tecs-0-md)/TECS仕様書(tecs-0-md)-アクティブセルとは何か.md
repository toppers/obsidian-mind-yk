---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — アクティブセルとは何か。タスク・ハンドラ等CPU資源割付けを伴うセル、またはそれらを内包するセル。セルタイプに active 指定子で指定する"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-アクティブセルとは何か

アクティブセルとは、**タスク・ハンドラ等CPU資源割付けを伴うセル、またはそれらを内包するセル**のことである。アクティブかどうかはセルタイプに `active` 指定子で指定される。

---

## 定義

セルが**アクティブ**である条件：
- タスク・ハンドラ等のCPU資源割付けを伴うセル
- またはそれらを内包するセル（複合セルタイプの場合）

## アクティブセルの特徴

- アクティブセルは受け口を一つも持たなくてもよい
- 非アクティブで受け口も未結合かつファクトリを持たないセルは誤り（呼び出されない）

## セルタイプでの指定

セルタイプに `active` 指定子を付けることでアクティブセルタイプを定義する：

```
celltype tMyActiveCell {
    [active]
    entry tSig eEntry;
    ...
};
```

## コンポーネント図での表現（§3.2.7）

コンポーネント図では、アクティブセルの長方形の辺を**二重線**で記すことでアクティブセルであることを示す。

## 複合セルタイプとの関係

内部セルのいずれかがアクティブセルタイプに属する場合、複合セルタイプもアクティブとなる。  
ただし、アクティブな複合セルタイプに1つもアクティブな内部セルがない場合は誤り。

---

**Sources used:**
- [セル（cell）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-cell.md) (confidence: high) — アクティブ属性の定義
- [セルタイプ（celltype）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-celltype.md) (confidence: high) — active指定子
- TECS仕様書 V1.3.0.1 raw — §3.2.7「アクティブ」（コンポーネント図）

**Knowledge gaps:**
- CDLでのactiveセルタイプの完全な構文例はwikiに詳細なし
