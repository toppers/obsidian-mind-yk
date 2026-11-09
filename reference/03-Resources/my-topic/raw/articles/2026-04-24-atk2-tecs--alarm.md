---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\alarm.html
title: アラーム ― tAlarm
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: アラーム ― tAlarm"
---

# アラーム ― tAlarm

# アラーム ― `tAlarm`

アラームは繰り返し処理用のオブジェクトです。
アラームはカウンタに接続して、カウンタの起動によって動作します。

課題

to be filled in

## 使用方法

### アラームの生成

アプリケーション開発者は `tAlarm` セルタイプのセルを生成することにより、アラームを生成することができます。次の例では `MyAlarm` という名前のアラームセルを生成し、 `MyCell` の `eAlarmHandlerBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{entrysHandlerBodyeAlarmHandlerBody;};celltMyCellTypeMyCell{};celltAlarmMyAlarm{alarmTime=10;cycleTime=10;cBody=MyCell.eAlarmHandlerBody;};
```
tMyCellType.c
```
voideAlarmHandlerBody_main(){}
```

## リファレンス

### セルタイプ
*celltype*`tAlarm`
アラームの生成を行うコンポーネントです。
*attr *char_t*` name`=C_EXP("$cell$")
アラームの名前を指定します。
指定しない場合、セルの名前が使用されます。
*attr *uint8_t` id`=C_EXP("$ID$")
アラームのIDを指定します。
*attr *char_t*` counter`
アラームに接続するカウンタを指定します。
*attr *char_t*` action`
アラームアクションを指定します。
`SETEVENT`
イベントのセット。
`ACTIVATETASK`
タスクの起動。
`ALARMCALLBACK`
コールバックの呼び出し。
*attr *char_t*` task`="OMISSIBLE"
アラームのアクションで起動するタスクを指定します。
*attr *char_t*` event`="OMISSIBLE"
アラームのアクションでセットするイベントを指定します。
*attr *char_t*` callbackName`="OMISSIBLE"
アラームのアクションで呼び出すコールバックを指定します。
*attr *bool_t` autoStart`
アラームの自動起動設定。
`True`
自動起動する。
`False`
自動起動しない。
*attr *uint32_t` alarmTime`=0
アラーム自動起動時の初回満了時刻を指定します。
*attr *uint32_t` cycleTime`=0
アラーム自動起動時の周期時間を指定します。0の場合は単発アラームとなります。
*attr *char_t*` appMode`[]={"OMISSIBLE"}
自動起動するアプリケーションモードを指定します。

### シグニチャ
*signature*`sAlarm`
アラームを操作するためのシグニチャ（Task,ISR2用）。
StatusType` getBase`(*[out]*AlarmBaseRefType* p_info*)
アラームの情報を取得する。
アラーム情報は p_info で示す構造体(AlarmBaseRefType)に格納される。
StatusType` get`(*[out]*TickRefType* p_tick*)
アラームが満了するまでのティック数を取得し、 p_tick の領域に格納する。
StatusType` setRelative`(*[in]*TickType* incr*, *[in]*TickType* cycle*)
アラームが現在のティックから incr で指定された相対時刻が経過した後に満了するよう設定する。
初回の満了後、cycle が 0 でない場合は、cycle の周期でアラームを満了させる。
StatusType` setAbsolute`(*[in]*TickType* start*, *[in]*TickType* cycle*)
アラームが start で指定された絶対時刻に達した際に満了するよう設定する。
初回の満了後、cycle が 0 でない場合は cycle の周期でアラームを満了させる。
StatusType` cancel`(void)
アラームを停止する。
*signature*`sAlarmHook`
アラームを操作するためのシグニチャ（Hook用）。
StatusType` getBase`(*[out]*AlarmBaseRefType* p_info*)
アラームの情報を取得する。
アラーム情報は p_info で示す構造体(AlarmBaseRefType)に格納される。
StatusType` get`(*[out]*TickRefType* p_tick*)
アラームが満了するまでのティック数を取得し、 p_tick の領域に格納する。

---

Source: [[index]]
