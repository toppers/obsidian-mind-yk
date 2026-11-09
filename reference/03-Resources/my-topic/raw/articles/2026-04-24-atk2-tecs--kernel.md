---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\kernel.html
title: カーネル ― tKernel
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: カーネル ― tKernel"
---

# カーネル ― tKernel

# カーネル ― `tKernel`

課題

to be filled in

## 使用方法

### カーネルの生成

アプリケーション開発者は `tKernel` セルタイプのセルを生成することにより、カーネルを生成することができます。次の例では `MyKernel` という名前のタスクセルを生成し、 `MyCell` の `sHookBody` を結合しています。
app.cdl
```
celltypetMyCellType{entrysHookBodyeStartupHookBody;};celltMyCellTypeMyCell{};celltKernelMyKernel{cStartupHookBody[0]=Sample.eStartupHookBody;cPreTaskHookBody=Sample.ePreTaskHookBody;cPostTaskHookBody=Sample.ePostTaskHookBody;cErrorHookBody=Sample.eErrorHookBody;cShutdownHookBody[0]=Sample.eShutdownHookBody;status="EXTENDED";useGetServiceId=TRUE;useParameterAccess=TRUE;StackMonitoring=TRUE;stackSize=512;ScalabilityClass="SC1";};
```
tMyCellType.c
```
voideStartupHookBody_main(){#ifdef TOPPERS_ENABLE_SYS_TIMERtarget_timer_initialize();#endif /* TOPPERS_ENABLE_SYS_TIMER */syslog_initialize();syslog_msk_log(LOG_UPTO(LOG_INFO));InitSerial();print_banner();blsm_autosar_init();}
```

## リファレンス

### セルタイプ
*celltype*`tKernel`
カーネルの生成を行うコンポーネントです。
*attr *char_t*` name`=C_EXP("$cell$")
カーネルの名前を指定します。
指定しない場合、セルの名前が使用されます。
*attr *char_t*` status`="EXTENDED"
エラーコード種別を指定します。
指定しない場合、EXTENDEDが使用されます。
`"EXTENDED"`
標準エラーと拡張エラーを検出
`"STANDARD"`
標準エラーのみ検出
*attr *bool_t` StackMonitoring`
スタックモニタリング使用の有無を指定します。
`True`
スタックモニタリングを使用します。
`False`
スタックモニタリングを使用しません。
*attr *uint32_t` stackSize`
C2ISR用スタックとフック用スタックを1つのスタックで確保する場合のスタックサイズを指定します。
*attr *char_t*` ScalabilityClass`="SC1"
OSのスケーラビリティクラスを指定します。
現在はSC1しかサポートしていません。
*attr *bool_t` useGetServiceId`
OSErrorGetServiceId()の使用有無を指定します。
`True`
OSErrorGetServiceId()を使用します。
`False`
OSErrorGetServiceId()を使用しません。
*attr *bool_t` useParameterAccess`
エラーが発生したシステムサービスの引数取得の使用有無を指定します。
`True`
エラーが発生したシステムサービスの引数取得有効。
`False`
エラーが発生したシステムサービスの引数取得無効。

### シグニチャ
*signature*`sKernelTask`
Task用のカーネル本体を呼び出すシグニチャ
StatusType` schedule`(void)
明示的な再スケジューリングを行う。
void` enableAllInterrupts`(void)
disableAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` disableAllInterrupts`(void)
ターゲットの割込みをすべて禁止し、クリティカルセクションに入る。
void` resumeAllInterrupts`(void)
suspendAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendAllInterrupts`(void)
ターゲットの割込み状態を保存した後、ターゲットの割込みをすべて禁止しクリティカルセクションに入る。
void` resumeOsInterrupts`(void)
suspendOSInterrupts によって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendOsInterrupts`(void)
ターゲットの割込み状態を保存した後、C2ISRをすべて禁止しクリティカルセクションに入る。
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
void` shutdownOs`(*[in]*StatusType* ercd*)
すべてのOSサービスを終了する。
*signature*`sKernelISR1`
ISR1用のカーネル本体を呼び出すシグニチャ
void` enableAllInterrupts`(void)
disableAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` disableAllInterrupts`(void)
ターゲットの割込みをすべて禁止し、クリティカルセクションに入る。
void` resumeAllInterrupts`(void)
suspendAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendAllInterrupts`(void)
ターゲットの割込み状態を保存した後、ターゲットの割込みをすべて禁止しクリティカルセクションに入る。
void` resumeOsInterrupts`(void)
suspendOSInterrupts によって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendOSInterrupts`(void)
ターゲットの割込み状態を保存した後、C2ISRをすべて禁止しクリティカルセクションに入る。
*signature*`sKernelISR2`
ISR2用のカーネル本体を呼び出すシグニチャ
void` enableAllInterrupts`(void)
disableAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` disableAllInterrupts`(void)
ターゲットの割込みをすべて禁止し、クリティカルセクションに入る。
void` resumeAllInterrupts`(void)
suspendAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendAllInterrupts`(void)
ターゲットの割込み状態を保存した後、ターゲットの割込みをすべて禁止しクリティカルセクションに入る。
void` resumeOsInterrupts`(void)
suspendOSInterrupts によって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendOSInterrupts`(void)
ターゲットの割込み状態を保存した後、C2ISRをすべて禁止しクリティカルセクションに入る。
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
void` shutdownOs`(*[in]*StatusType* ercd*)
すべてのOSサービスを終了する。
*signature*`sKernelErrorHook`
カーネル本体を呼び出すシグニチャ（ErrorHook用）
void` resumeAllInterrupts`(void)
suspendAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendAllInterrupts`(void)
ターゲットの割込み状態を保存した後、ターゲットの割込みをすべて禁止しクリティカルセクションに入る。
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
void` shutdownOs`(*[in]*StatusType* ercd*)
すべてのOSサービスを終了する。
*signature*`sKernelTaskHook`
カーネル本体を呼び出すシグニチャ（TaskHook用）
void` resumeAllInterrupts`(void)
suspendAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendAllInterrupts`(void)
ターゲットの割込み状態を保存した後、ターゲットの割込みをすべて禁止しクリティカルセクションに入る。
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
*signature*`sKernelPreTaskHook`
カーネル本体を呼び出すシグニチャ（PreTaskHook用）
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
*signature*`sKernelPostTaskHook`
カーネル本体を呼び出すシグニチャ（PostTaskHook用）
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
*signature*`sKernelStartupHook`
カーネル本体を呼び出すシグニチャ（StartupHook用）
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
void` shutdownOs`(*[in]*StatusType* ercd*)
すべてのOSサービスを終了する。
*signature*`sKernelShutdownHook`
カーネル本体を呼び出すシグニチャ（ShutdownHook用）
AppModeType` getActiveApplicationMode`(void)
OS起動時に指定されたアプリケーションモードを取得する。
*signature*`sKernelAlarmCallback`
カーネル本体を呼び出すシグニチャ（AlarmCallback用）
void` resumeAllInterrupts`(void)
suspendAllInterruptsによって設定された割込み禁止状態を割込み許可状態に戻す。
void` suspendAllInterrupts`(void)
ターゲットの割込み状態を保存した後、ターゲットの割込みをすべて禁止しクリティカルセクションに入る。
*signature*`snKernel`
カーネル起動シグニチャ
void` startOs`(*[in]*AppModeType* mode*)
指定されたアプリケーションモードでOSを起動する。
*signature*`sEventISR2`StatusType` set`(*[in]*TaskType* tskid*, *[in]*EventMaskType* mask*)
TaskID で指定されたタスクに Mask で指定されたイベントを設定する。
Return
正常終了 (`E_OK`) またはエラーコード。
StatusType` get`(*[in]*TaskType* tskid*, *[out]*EventMaskRefType* p_mask*)
TaskID で指定されたタスクが保持しているイベントマスク値を取得する。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`sEventHook`StatusType` get`(*[in]*TaskType* tskid*, *[out]*EventMaskRefType* p_mask*)
TaskID で指定されたタスクが保持しているイベントマスク値を取得する。
Return
正常終了 (`E_OK`) またはエラーコード。

---

Source: [[index]]
