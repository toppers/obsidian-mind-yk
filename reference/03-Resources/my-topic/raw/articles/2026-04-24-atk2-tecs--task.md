---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\task.html
title: タスク ― tTask
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: タスク ― tTask"
---

# タスク ― tTask

# タスク ― `tTask`

タスクはプログラムの並行実行の単位です。

課題

to be filled in

## 使用方法

### タスクの生成

アプリケーション開発者は `tTask` セルタイプのセルを生成することにより、タスクを生成することができます。次の例では `MyTask` という名前のタスクセルを生成し、 `MyCell` の `eTaskBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{entrysTaskBodyeTaskBody;};celltMyCellTypeMyCell{};celltTaskMyTask{stackSize=1024;priority=42;cTaskBody=MyCell.eTaskBody;};
```
tMyCellType.c
```
voideTaskBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

### タスクの制御

`tTask` が提供する `eTask` という名前の受け口を利用することにより、タスクの制御及び状態の取得を行うことができます。
app.cdl
```
celltMyCellTypeMyCell{};celltMyAnotherCellTypeMyAnotherCell{cTask=MyTask.eTask;};
```
tMyAnotherCellType.c
```
// タスクの起動cTask_activate();// タスクの現在状態の参照TaskRefTypetaskStatus;cTask_getState(&taskStatus);
```

## リファレンス

### セルタイプ
*celltype*`tTask`
タスクの生成、制御及び状態の取得を行うコンポーネントです。
*attr *TaskType` idx`=C_EXP("$cell$")
タスクのIDの識別子を指定します。

指定しない場合、 セルの名前が使用されます。
*attr *bool_t` autoStart`
タスクを自動起動させるか指定します。
`True`
タスクを自動起動します。
`False`
タスクを自動起動しません。
*attr *char_t*` appMode`[]
タスクの自動起動を設定した場合、appMode[]で指定したappModeでタスクを自動起動させる（複数選択可能）。
*attr *uint32_t` priority`
タスクの起動時優先度を指定します。
*attr *uint32_t` activation`
タスクの最大起動要求回数を指定します。
*attr *char_t*` schedule`
タスクのスケジューリングポリシを指定します。
`Full`
フルプリエンプティブスケジューリング
`Non`
ノンプリエンプティブスケジューリング
*attr *char_t*` event`[]
タスクの持つイベントを指定します（複数指定可能）。
*attr *char_t*` resource`[]
タスクが獲得するリソースを指定します（複数選択可能）。
*attr *uint32_t` stackSize`
タスク用のスタックサイズを指定します。
*entry*sTask` eTask`
タスクの制御及び状態の取得を行うための受け口です。
*call*sTaskBody` cBody`
タスクの本体として呼び出される受け口をこの呼び口に結合します。
*entry*sTaskISR2` eTaskISR2`*entry*sTaskHook` eTaskHook`*entry*sTaskEvent` eTaskEvent`
### シグニチャ
*signature*`sTask`
タスクの制御、及び状態の取得を行うためのシグニチャです。
StatusType` activate`(void)
タスクに対して起動要求を行います。
この関数は `ActivateTask(TalskTypeTaskID）` のラッパーです。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` terminate`(void)
タスクを終了します。
この関数は `TermmateTask(void）` のラッパーです。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` chain`(void)
自タスクを終了し、指定したタスクを起動します。 todo
この関数は `ChainTask(TaskTypeTaskID）` のラッパーです。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` getId`(*[out]*TaskRefType* p_tskid*)
実行中のタスクIDを取得します。
結果はp_tskidに格納されます。
:return: 正常終了 (`E_OK`) またはエラーコード。
この関数は `GetTasklD(TaskRefTypeTasklD）` のラッパーです。
StatusType` getState`(*[out]*TaskStateRefType* p_state*)
タスクの状態を取得します。
結果はp_stateに格納されます。
:return: 正常終了 (`E_OK`) またはエラーコード。
この関数は `GetTaskState(TaskTypeTaskID,TaskStateRefTypeState）` のラッパーです。
*signature*`sTaskISR2`
タスクを操作するためのシグニチャISR2用
StatusType` activate`(void)
タスクに対して起動要求を行います。
この関数は `ActivateTask(TalskTypeTaskID）` のラッパーです。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` getId`(out]TaskRefType* p_tskid*)
実行中のタスクIDを取得します。
結果はp_tskidに格納されます。
:return: 正常終了 (`E_OK`) またはエラーコード。
この関数は `GetTasklD(TaskRefTypeTasklD）` のラッパーです。
StatusType` getState`(*[out]*TaskStateRefType* p_state*)
タスクの状態を取得します。
結果はp_stateに格納されます。
:return: 正常終了 (`E_OK`) またはエラーコード。
この関数は `GetTaskState(TaskTypeTaskID,TaskStateRefTypeState）` のラッパーです。
*signature*`sTaskHook`
タスクを操作するためのシグニチャ各Hook用
StatusType` getId`(out]TaskRefType* p_tskid*)
実行中のタスクIDを取得します。
結果はp_tskidに格納されます。
:return: 正常終了 (`E_OK`) またはエラーコード。
この関数は `GetTasklD(TaskRefTypeTasklD）` のラッパーです。
StatusType` getState`(*[out]*TaskStateRefType* p_state*)
タスクの状態を取得します。
結果はp_stateに格納されます。
:return: 正常終了 (`E_OK`) またはエラーコード。
この関数は `GetTaskState(TaskTypeTaskID,TaskStateRefTypeState）` のラッパーです。
*signature*`sEventTask`
イベントを操作するためのシグニチャ（Task用）
StatusType` set`(*[in]*EventMaskType* mask*)
TaskID で指定されたタスクに Mask で指定されたイベントを設定する。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` clear`(*[in]*EventMaskType* mask*)
Mask で指定されたイベントをクリアする。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` get`(*[out]*EventMaskRefType* p_mask*)
TaskID で指定されたタスクが保持しているイベントマスク値を取得する。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` wait`(*[in]*EventMaskType* mask*)
本関数を呼び出したタスクを待ち状態とする。
:return: 正常終了 (`E_OK`) またはエラーコード。
*signature*`sTaskEvent`
イベントを操作するためのシグニチャTask用
StatusType` set`(*[in]*TaskType* tskid*, *[in]*EventMaskType* mask*)
TaskID で指定されたタスクに Mask で指定されたイベントを設定する。
:return: 正常終了 (`E_OK`) またはエラーコード。
StatusType` get`(*[in]*TaskType* tskid*, *[out]*EventMaskRefType* p_mask*)
TaskID で指定されたタスクが保持しているイベントマスク値を取得する。
:return: 正常終了 (`E_OK`) またはエラーコード。

---

Source: [[index]]
