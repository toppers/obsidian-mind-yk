---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\counter.html
title: カウンタ ― tCounter
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: カウンタ ― tCounter"
---

# カウンタ ― tCounter

# カウンタ ― `tCounter`

カウンタは処理タイミング通知用のオブジェクトです。
ティックという単位で事象をカウントします。
カウンタは2種類あります。
ソフトウェアカウンタ

システムサービスでティックをインクリメントする
ハードウェアカウンタ
ハードウェア（タイマなど）がティックをインクリメントする

主にアラーム、スケジュールテーブルに接続して使用する。
.. todo:

```
tobefilledin
```

## 使用方法

### カウンタの生成

アプリケーション開発者は `tCounter` セルタイプのセルを生成することにより、カウンタを生成することができます。次の例では `MyCounter` という名前のカウンタセルを生成します。
app.cdl
```
celltCounterMyCounter{*counterType="SOFTWARE"minimumCycle=10;maximumAllowedValue="100";};
```
tMyCellType.c
```
voideAlarmHandlerBody_main(){}
```

## リファレンス

### セルタイプ
*celltype*`tCounter`
カウンタの生成を行うコンポーネントです。
*attr *uint8_t` id`=C_EXP("$ID$")
カウンタのIDの識別子を指定します。
*attr *char_t*` name`=C_EXP("$cell$")
カウンタの名前を指定します。
指定しない場合、セルの名前が使用されます。
*attr *char_t*` counterType`="SOFTWARE"`カウンタのタイプを指定します。``HARDWARE`
ハードウェアカウンタ
`SOFTWARE`
ソフトウェアカウンタ
*attr *uint32_t` minimumCycle`
接続されたアラームがカウンタに指定できる最小周期値を指定します。
*attr *uint32_t` maximumAllowedValue`
カウンタのティックの最大値を指定します。
*attr *uint32_t` ticksPerBase`
カウンタ固有の値（OSは不使用）

### シグニチャ
*signature*`sCounter`
カウンタを操作するためのシグニチャ
StatusType` signal`(void)

---

Source: [[index]]
