---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\event.html
title: イベント ― tEvent
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: イベント ― tEvent"
---

# イベント ― tEvent

# イベント ― `tEvent`

イベントは、タスク－タスク間、タスク－C2ISR間での同期ための機能です。

課題

to be filled in

## 使用方法

### イベントの生成

アプリケーション開発者は `tEvent` セルタイプのセルを生成することにより、イベントを生成することができます。次の例では `MyEvent` という名前のイベントセルを生成しています。
app.cdl
```
celltypetMyCellType{callsEventMaskcEventMask;};celltMyCellTypeMyCell{};celltEventMyEvent{eEventMask=MyCell.cEventMask;};
```
tMyCellType.c
```

```

## リファレンス

### セルタイプ
*celltype*`tEvent`
イベントの生成を行うコンポーネントです。
*attr *char_t*` name`=C_EXP("$cell$")
イベントの名前を指定します。
指定しない場合、セルの名前が使用されます。
*attr *uint32_t` mask`=C_EXP("AUTO")
イベントのマスク値を指定します。
指定しない場合、イベントマスク値は自動的に設定されます。
*attr *EventMaskType` p_mask`=C_EXP("$cell$");
### シグニチャ
*signature*`sEventMask`EventMaskType` get`(void)

---

Source: [[index]]
