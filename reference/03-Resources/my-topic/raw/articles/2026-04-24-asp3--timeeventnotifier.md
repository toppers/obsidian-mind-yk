---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\timeeventnotifier.html
title: タイムイベント通知
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: タイムイベント通知"
---

# タイムイベント通知

# タイムイベント通知

タイムイベント通知は、時間の経過 (タイムイベントの発生) をアプリケーションに通知する機能です。

タイムイベント通知には以下の2種類があり、これらを総括してタイムイベント通知と呼びます:
周期通知
サービスコールまたは静的APIによる指定で動作開始要求が行われると、指定した周期で、繰り返し通知を行います。通知が行われる時刻は、周期通知が起動された時刻、または `TA_PHS` 属性が指定された場合は周期通知が生成された時刻を基準として、通知位相＋通知周期×(n-1) (n=1, 2, ...) と表すことができます。
アラーム通知
サービスコールで指定した相対時間後に通知を行います。

タイムイベントの通知は、次のいずれかの方法で行うことができます [NGKI3689]。

| 
通知方法
 | 
対応する(疑似)コード
 | 
| 
タイムイベントハンドラの呼出し
 | 
`handler.ciHandlerBody.main();`
 | 
| 
変数の設定
 | 
`*setVariableAddress=setVariableValue;`
 | 
| 
変数のインクリメント
 | 
`++*incrementedVariableAddress;`
 | 
| 
タスクの起動
 | 
`er=act_tsk(handler.id);`
 | 
| 
タスクの起床
 | 
`er=wup_tsk(handler.id);`
 | 
| 
セマフォの資源の返却
 | 
`er=sig_sem(handler.id);`
 | 
| 
イベントフラグのセット
 | 
`er=set_flg(handler.id,flagPattern);`
 | 
| 
データキューへの送信
 | 
`er=psnd_dtq(handler.id,dataqueueSentValue);`
 | 
これらの通知方法のうち、最後の5つは通知のためのサービスコールがエラーを返し、タイムイベントの通知に失敗する場合があります。タイムイベントの通知に失敗した場合、エラーの通知を次のいずれかの方法で行うことができます [NGKI3690]。

| 
エラー通知方法
 | 
対応する(疑似)コード
 | 
| 
なし
 |  | 
| 
変数の設定
 | 
`*setVariableAddressForError=er;`
 | 
| 
変数のインクリメント
 | 
`++*incrementedVariableAddressForError;`
 | 
| 
タスクの起動
 | 
`act_tsk(errorHandler.id);`
 | 
| 
タスクの起床
 | 
`wup_tsk(errorHandler.id);`
 | 
| 
セマフォの資源の返却
 | 
`sig_sem(errorHandler.id);`
 | 
| 
イベントフラグのセット
 | 
`set_flg(errorHandler.id,flagPatternForError);`
 | 
| 
データキューへの送信
 | 
`psnd_dtq(errorHandler.id,er);`
 | 
エラー通知が失敗した場合、エラーは無視され、何も行われません [NGKI3691]。

## 使用方法

### 周期通知・アラーム通知

アプリケーション開発者は `tCyclicNotifier` セルタイプのセルを生成することにより、周期通知を生成することができます。

```
celltCyclicNotifierCyclic{attribute=C_EXP("TA_STA");// 生成直後から動作開始cycleTime=1000000;// 1,000,000 マイクロ秒 (1秒) 周期};
```

同様に、 `tAlarmNotifier` セルタイプのセルを生成することにより、アラーム通知を生成することができます。

```
celltAlarmNotifierAlarm{};
```

タイムイベント通知を使用する場合、さらに通知方法を指定する必要があります。通知方法の指定について次に説明します。
以下の説明では `tAlarmNotifier` のみを使用しますが、 `tCyclicNotifier` でも同様の方法で指定することができます。

### 変数の設定・インクリメントによる通知

変数の設定により通知を行いたい場合、まずヘッダファイルで変数を宣言します。続いてヘッダファイルの変数宣言をTECS CDLから `import_C` により読込み、 `setVariableAddress` 属性でその変数のアドレスを指定し、`setVariableValue` で設定する値を指定します。
app.c
```
#include"app.h"intptr_tfoo_variable;
```
app.h
```
externintptr_tfoo_variable;
```

```
import_C("app.h");celltAlarmNotifierAlarm{setVariableAddress=C_EXP("&foo_variable");setVariableValue=42;};
```

変数のインクリメントにより通知を行いたい場合は、`incrementedVariableAddress` で変数のアドレスを指定します。

```
import_C("app.h");celltAlarmNotifierAlarm{incrementedVariableAddress=C_EXP("&foo_variable");};
```

### タスクの起動・起床による通知

タスクの起動により通知を行いたい場合、タイムイベント通知セルの呼び口 `ciNotificationHandler` を、タスクの `tTask::eiActivateNotificationHandler` に結合します。

```
celltTaskMyTask{/* 省略 */};celltAlarmNotifierAlarm{ciNotificationHandler=MyTask.eiActivateNotificationHandler;};
```

同様に、`tTask::eiWakeUpNotificationHandler` に結合することで、タスクの起床により通知を行うことができます。

### セマフォの返却による通知

タスクの起動により通知を行いたい場合、タイムイベント通知セルの呼び口 `ciNotificationHandler` を、セマフォの `tSemaphore::eiNotificationHandler` に結合します。

```
celltSemaphoreMySemaphore{/* 省略 */};celltAlarmNotifierAlarm{ciNotificationHandler=MySemaphore.eiNotificationHandler;};
```

### イベントフラグのセットによる通知

イベントフラグのセットにより通知を行いたい場合、タイムイベント通知セルの呼び口 `ciNotificationHandler` を、セマフォの `tEventflag::eiNotificationHandler` に結合します。セットするフラグパターンは属性 `flagPattern` により指定します。

```
celltEventflagMyEventFlag{/* 省略 */};celltAlarmNotifierAlarm{ciNotificationHandler=MyEventFlag.eiNotificationHandler;flagPattern=1;};
```

### データキューへの送信による通知

データキューへの送信により通知を行いたい場合、タイムイベント通知セルの呼び口 `ciNotificationHandler` を、セマフォの `tDataqueue::eiNotificationHandler` に結合します。セットするフラグパターンは属性 `dataqueueSentValue` により指定します。

```
celltDataqueueMyDataqueue{/* 省略 */};celltAlarmNotifierAlarm{ciNotificationHandler=MyDataqueue.eiNotificationHandler;dataqueueSentValue=0xdeadbeef;};
```

### ハンドラ関数による通知

ハンドラ関数により通知を行いたい場合、`tAlarmNotifier`, `tCyclicNotifier` の代わりに `tAlarmHandler`, `tCyclicHandler` を使用します。通知先にシグニチャ `siHandlerBody` の受け口を定義し、タイムイベント通知セルの呼び口 `ciHandlerBody` をその受け口に結合します。
tMyCellType.c
```
voideiHandlerBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

```
celltypetMyCellType{entrysiHandlerBodyeiHandlerBody;};celltMyCellTypeMyCell{};celltAlarmHandlerAlarm{ciHandlerBody=MyCell.eiHandlerBody;};
```

注意

タイムイベントの通知方法は複数ありますが、各タイムイベント通知に対し一度に指定できる通知方法は一つに制限されます。
例えば、 `setVariableAddress` (設定先変数) と `incrementedVariableAddress` (インクリメント先変数) を同時に指定することはできず、この指定があるときにTECSジェネレータを実行すると、エラーが発生します。

通知方法を指定しなかった場合もエラーとなります。

### エラー通知

以上の通知方法のうち、タスクの起動, タスクの起床, セマフォの資源の返却, イベントフラグのセット, データキューへの送信の5つは、内部的にはそれぞれ対応するサービスコールの呼出しにより実現されています。
サービスコールの呼出しが行われるとき、様々な要因によりサービスコールが失敗しエラーを返すことがあります。エラーが発生する具体的状況をいくつか挙げてみましょう (網羅的ではありません):

- 
**タスクの起動** (`act_tsk`): タスク起動要求キューイングオーバーフロー (`E_QOVR`)

- 
**タスクの起床** (`wup_tsk`): タスクが休止状態 (`E_OBJ`)、タスク起床要求キューイングオーバーフロー (`E_QOVR`)

- 
**セマフォの資源の返却**: セマフォの資源数がすでに最大値に達している (`E_QOVR`)

- 
**イベントフラグのセット**: (ASP3+TECS で発生するエラーはありません)

- 
**データキューへの送信**: バッファオーバフロー (`E_TMOUT`)

タイムイベント通知には、こうした場合にもう一つの通知方法を用いてエラーを通知することができます。

エラー通知方法は、通常の通知と同様に指定することができます (ただし、ハンドラ関数をエラー通知に用いることはできません)。呼び口は `ciNotificationHandler` の代わりに `ciErrorNotificationHandler` を用い、属性は末尾に `ForError` を加えたものを使用しますが、いくつか例外が存在します。属性名の対応表を次に示します:

| 
通常通知
 | 
エラー通知
 | 
| 
`setVariableAddress`
 | 
`setVariableAddressForError`
 | 
| 
`setVariableValue`
 | 
--
 | 
| 
`incrementedVariableAddress`
 | 
`incrementedVariableAddressForError`
 | 
| 
`flagPattern`
 | 
`flagPatternForError`
 | 
| 
`dataqueueSentValue`
 | 
--
 | 
この表の右の列が空欄になっている属性は、対応する属性が存在せず、エラー番号が代わりの値として使用されます。

注意

通常の通知方法と同様に、エラー通知方法は複数ありますが、各タイムイベント通知に対し一度に指定できるエラー通知方法は一つに制限されます。

エラー通知方法の指定を省略することは可能ですが、TECSジェネレータの実行時に警告が出力されます。警告を表示したくない場合は属性 `ignoreErrors` を `true` に設定してください。

通常の通知方法がエラーが発生しないもの (タイムイベントハンドラの呼出し, 変数の設定, 変数のインクリメント) である場合、エラー通知方法を指定することはできず、指定した場合はエラーが発生します。

### 周期通知を制御する

`tCyclicNotifier` が提供する `eCyclic` という名前の受け口を利用することにより、周期通知の制御及び状態の取得を行うことができます。
app.cdl
```
celltCyclicNotifierCyclic{};celltypetMyCellType{callsCycliccCyclic;};celltMyCellTypeMyCell{cCyclic=Cyclic.eCyclic;};
```
tMyCellType.c
```
// 周期通知を動作開始cCyclic_start();// 周期通知の現在状態の参照T_RCYCcyclicStatus;cCyclic_refer(&cyclicStatus);
```

周期通知は非タスクコンテキストから操作することはできません。

### アラーム通知を制御する

`tAlarmNotifier` が提供する `eAlarm` という名前の受け口を利用することにより、アラーム通知の制御及び状態の取得を行うことができます。
app.cdl
```
celltAlarmNotifierAlarm{};celltypetMyCellType{callsAlarmcAlarm;};celltMyCellTypeMyCell{cAlarm=Alarm.eAlarm;};
```
tMyCellType.c
```
// アラーム通知を動作開始cAlarm_start(1000000);// 1,000,000 マイクロ秒 (1秒) 後に通知// アラーム通知の現在状態の参照T_RALMalarmStatus;cAlarm_refer(&alarmStatus);
```

非タスクコンテキスト内では、`eAlarm` の代わりに `eiAlarm` を使用する必要があります。

## リファレンス

### セルタイプ
*celltype*`tAlarmNotifier`
アラーム通知の生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_ALM` 静的API [NGKI2487] によりアラーム通知の生成を行います。

注意

通知方法に関係する属性はTECSのコンポーネントモデル上はすべて「省略可能」として定義されていますが、実際には専用のTECSジェネレータプラグインの働きにより、複雑な条件によって指定が制約されています。可能な指定方法については使用方法のセクションを参照してください。
*attr *ID` id`=C_EXP("ALMID_$id$")
アラーム通知のID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`=C_EXP("TA_NULL")
アラーム通知属性を `C_EXP` で囲んで指定します (省略可能)。ASP3では指定できる属性はありません [NGKI3423] ので、指定できる値は `C_EXP("TA_NULL")` のみです [NGKI3424]。
*attr *bool_t` ignoreErrors`=false
通知方法としてエラーが発生する可能性があるもの (タスクの起動, タスクの起床, セマフォの資源の返却, イベントフラグのセット, データキューへの送信) を指定しているとき、エラー通知方法を指定しなかった場合、TECSジェネレータ実行時に警告を出力するかを指定します (省略可能)。

デフォルト値は `false` で、エラー通知方法が未指定の場合に警告を出力します。
*attr *intptr_t*` setVariableAddress`=0
通知方法として「変数の設定」を使用する場合に、設定先の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t` setVariableValue`=0
通知方法として「変数の設定」を使用する場合に、変数に設定する値を指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t*` incrementedVariableAddress`=0
通知方法として「変数のインクリメント」を使用する場合に、インクリメント対象の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *FLGPTN` flagPattern`=0
通知方法として「イベントフラグのセット」を使用する場合に、セットするフラグパターンを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t` dataqueueSentValue`=0
通知方法として「データキューへの送信」を使用する場合に、データキューに送信する値を指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t*` setVariableAddressForError`=0
エラー通知方法として「変数の設定」を使用する場合に、エラーコードを設定する先の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t*` incrementedVariableAddressForError`=0
エラー通知方法として「変数のインクリメント」を使用する場合に、インクリメント対象の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *FLGPTN` flagPatternForError`=0
エラー通知方法として「イベントフラグのセット」を使用する場合に、セットするフラグパターンを指定します。

他の通知方法を使用する場合は、指定してはけません。
`callsiNotificationHandlerciNotificationHandler`
通知先のセルを結合します。結合可能なセルタイプ・受け口は通知方法ごとに異なります。

| 
通知方法
 | 
セルタイプ, 受け口
 | 
| 
タイムイベントハンドラの呼出し
 | 
`tTimeEventHandler::eiNotificationHandler`
 | 
| 
変数の設定
 | 
結合してはいけません
 | 
| 
変数のインクリメント
 | 
結合してはいけません
 | 
| 
タスクの起動
 | 
`tTask::eiActivateNotificationHandler`
 | 
| 
タスクの起床
 | 
`tTask::eiWakeUpNotificationHandler`
 | 
| 
セマフォの資源の返却
 | 
`tSemaphore::eiNotificationHandler`
 | 
| 
イベントフラグのセット
 | 
`tEventflag::eiNotificationHandler`
 | 
| 
データキューへの送信
 | 
`tDataqueue::eiNotificationHandler`
 | 
上記の表にないセルタイプ・受け口を結合した場合、TECSジェネレータ実行時にエラーが発生します。
`callsiNotificationHandlerciErrorNotificationHandler`
エラー通知先のセルを結合します。結合可能なセルタイプ・受け口は通知方法ごとに異なります。

| 
エラー通知方法
 | 
セルタイプ, 受け口
 | 
| 
なし
 | 
結合してはいけません
 | 
| 
変数の設定
 | 
結合してはいけません
 | 
| 
変数のインクリメント
 | 
結合してはいけません
 | 
| 
タスクの起動
 | 
`tTask::eiActivateNotificationHandler`
 | 
| 
タスクの起床
 | 
`tTask::eiWakeUpNotificationHandler`
 | 
| 
セマフォの資源の返却
 | 
`tSemaphore::eiNotificationHandler`
 | 
| 
イベントフラグのセット
 | 
`tEventflag::eiNotificationHandler`
 | 
| 
データキューへの送信
 | 
`tDataqueue::eiNotificationHandler`
 | 
上記の表にないセルタイプ・受け口を結合した場合、TECSジェネレータ実行時にエラーが発生します。
`entrysAlarmeAlarm`
アラーム通知の制御及び状態の取得を行うための受け口です (タスクコンテキスト用)。
`entrysiAlarmeiAlarm`
アラーム通知の制御を行うための受け口です (非タスクコンテキスト用)。
*celltype*`tCyclicNotifier`
周期通知の生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_CYC` 静的API [NGKI3727] により周期通知の生成を行います。

周期通知は、動作している状態と動作していない状態のいずれかをとり [NGKI2366]、動作している状態にすることを動作開始、動作していない状態にすることを動作停止と呼びます。

周期通知による通知は、基準時刻を基準として、 `cyclePhase+cyclicTime*(n-1)` (n=1, 2, ...) で表される時刻に行われます。基準時刻は属性 `TA_PHS` を指定した場合は周期通知の生成がされた時刻、指定されなかった場合は周期通知が最後に動作開始した時刻が用いられます [NGKI2365]。

注意

通知方法に関係する属性はTECSのコンポーネントモデル上はすべて「省略可能」として定義されていますが、実際には専用のTECSジェネレータプラグインの働きにより、複雑な条件によって指定が制約されています。可能な指定方法については使用方法のセクションを参照してください。
*attr *ID` id`=C_EXP("CYCID_$id$")
周期通知のID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`=C_EXP("TA_NULL")
周期通知属性を `C_EXP` で囲んで指定します [NGKI2370] (省略可能)。複数個指定する場合、ビット毎の論理和演算子を用いて `C_EXP("TA_STA|TA_PHS")` のようにして指定します。
`TA_STA`
周期通知の生成時に周期通知を動作開始します。
`TA_PHS`
周期通知を生成した時刻を基準時刻とします。
*attr *RELTIM` cycleTime`
周期通知の通知周期をマイクロ秒単位で指定します。
*attr *RELTIM` cyclePhase`=0
周期通知の通知位相をマイクロ秒単位で指定します (省略可能)。
*attr *bool_t` ignoreErrors`=false
通知方法としてエラーが発生する可能性があるもの (タスクの起動, タスクの起床, セマフォの資源の返却, イベントフラグのセット, データキューへの送信) を指定しているとき、エラー通知方法を指定しなかった場合、TECSジェネレータ実行時に警告を出力するかを指定します (省略可能)。

デフォルト値は `false` で、エラー通知方法が未指定の場合に警告を出力します。
*attr *intptr_t*` setVariableAddress`=0
通知方法として「変数の設定」を使用する場合に、設定先の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t` setVariableValue`=0
通知方法として「変数の設定」を使用する場合に、変数に設定する値を指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t*` incrementedVariableAddress`=0
通知方法として「変数のインクリメント」を使用する場合に、インクリメント対象の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *FLGPTN` flagPattern`=0
通知方法として「イベントフラグのセット」を使用する場合に、セットするフラグパターンを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t` dataqueueSentValue`=0
通知方法として「データキューへの送信」を使用する場合に、データキューに送信する値を指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t*` setVariableAddressForError`=0
エラー通知方法として「変数の設定」を使用する場合に、エラーコードを設定する先の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *intptr_t*` incrementedVariableAddressForError`=0
エラー通知方法として「変数のインクリメント」を使用する場合に、インクリメント対象の変数を指すポインタを指定します。

他の通知方法を使用する場合は、指定してはけません。
*attr *FLGPTN` flagPatternForError`=0
エラー通知方法として「イベントフラグのセット」を使用する場合に、セットするフラグパターンを指定します。

他の通知方法を使用する場合は、指定してはけません。
`callsiNotificationHandlerciNotificationHandler`
通知先のセルを結合します。結合可能なセルタイプ・受け口は通知方法ごとに異なります。

| 
通知方法
 | 
セルタイプ, 受け口
 | 
| 
タイムイベントハンドラの呼出し
 | 
`tTimeEventHandler::eiNotificationHandler`
 | 
| 
変数の設定
 | 
結合してはいけません
 | 
| 
変数のインクリメント
 | 
結合してはいけません
 | 
| 
タスクの起動
 | 
`tTask::eiActivateNotificationHandler`
 | 
| 
タスクの起床
 | 
`tTask::eiWakeUpNotificationHandler`
 | 
| 
セマフォの資源の返却
 | 
`tSemaphore::eiNotificationHandler`
 | 
| 
イベントフラグのセット
 | 
`tEventflag::eiNotificationHandler`
 | 
| 
データキューへの送信
 | 
`tDataqueue::eiNotificationHandler`
 | 
上記の表にないセルタイプ・受け口を結合した場合、TECSジェネレータ実行時にエラーが発生します。
`callsiNotificationHandlerciErrorNotificationHandler`
エラー通知先のセルを結合します。結合可能なセルタイプ・受け口は通知方法ごとに異なります。

| 
エラー通知方法
 | 
セルタイプ, 受け口
 | 
| 
なし
 | 
結合してはいけません
 | 
| 
変数の設定
 | 
結合してはいけません
 | 
| 
変数のインクリメント
 | 
結合してはいけません
 | 
| 
タスクの起動
 | 
`tTask::eiActivateNotificationHandler`
 | 
| 
タスクの起床
 | 
`tTask::eiWakeUpNotificationHandler`
 | 
| 
セマフォの資源の返却
 | 
`tSemaphore::eiNotificationHandler`
 | 
| 
イベントフラグのセット
 | 
`tEventflag::eiNotificationHandler`
 | 
| 
データキューへの送信
 | 
`tDataqueue::eiNotificationHandler`
 | 
上記の表にないセルタイプ・受け口を結合した場合、TECSジェネレータ実行時にエラーが発生します。
`entrysCycliceCyclic`
周期通知の制御及び状態の取得を行うための受け口です (タスクコンテキスト用)。

非タスクコンテキスト用の受け口はありません。
*celltype*`tTimeEventHandler`
タイムイベント通知セルで、通知方法「タイムイベントハンドラの呼出し」により通知を行いたい場合に使用するセルタイプです。

一般的なアプリケーションではこのセルタイプを直接する必要はなく、 `tAlarmHandler` または `tCyclicHandler` を使用することが推奨されます。
`entrysiNotificationHandlereiNotificationHandler`
通知元のタイムイベント通知セルの `tAlarmNotifier::ciNotificationHandler` または `tCyclicNotifier::ciNotificationHandler` に結合します。
`callsiHandlerBodyciHandlerBody`
タイムイベントハンドラの本体となる受け口を結合します。
*celltype*`tAlarmHandler`
アラーム通知の生成、制御及び状態の取得を行うコンポーネントです。このセルタイプはハンドラ関数により通知を行う場合に使用します。他の通知方法を使用したい場合、 `tAlarmNotifier` を使用してください。

本コンポーネントは `CRE_ALM` 静的API [NGKI2487] によりアラーム通知の生成を行います。
*attr *ID` id`=C_EXP("ALMID_$id$")
アラーム通知のID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`=C_EXP("TA_NULL")
アラーム通知属性を `C_EXP` で囲んで指定します (省略可能)。ASP3では指定できる属性はありません [NGKI3423] ので、指定できる値は `C_EXP("TA_NULL")` のみです [NGKI3424]。
`entrysAlarmeAlarm`
アラーム通知の制御及び状態の取得を行うための受け口です (タスクコンテキスト用)。
`entrysiAlarmeiAlarm`
アラーム通知の制御を行うための受け口です (非タスクコンテキスト用)。
`callsiHandlerBodyciHandlerBody`*celltype*`tCyclicHandler`
周期通知の生成、制御及び状態の取得を行うコンポーネントです。このセルタイプはハンドラ関数により通知を行う場合に使用します。他の通知方法を使用したい場合、 `tCyclicNotifier` を使用してください。

本コンポーネントは `CRE_CYC` 静的API [NGKI3727] により周期通知の生成を行います。

周期通知は、動作している状態と動作していない状態のいずれかをとり [NGKI2366]、動作している状態にすることを動作開始、動作していない状態にすることを動作停止と呼びます。

周期通知による通知は、基準時刻を基準として、 `cyclePhase+cyclicTime*(n-1)` (n=1, 2, ...) で表される時刻に行われます。基準時刻は属性 `TA_PHS` を指定した場合は周期通知の生成がされた時刻、指定されなかった場合は周期通知が最後に動作開始した時刻が用いられます [NGKI2365]。
*attr *ID` id`=C_EXP("CYCID_$id$")
周期通知のID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`=C_EXP("TA_NULL")
周期通知属性を `C_EXP` で囲んで指定します [NGKI2370] (省略可能)。複数個指定する場合、ビット毎の論理和演算子を用いて `C_EXP("TA_STA|TA_PHS")` のようにして指定します。
`TA_STA`
周期通知の生成時に周期通知を動作開始します。
`TA_PHS`
周期通知を生成した時刻を基準時刻とします。
*attr *RELTIM` cycleTime`
周期通知の通知周期をマイクロ秒単位で指定します。
*attr *RELTIM` cyclePhase`=0
周期通知の通知位相をマイクロ秒単位で指定します (省略可能)。
`entrysCycliceCyclic`
周期通知の制御及び状態の取得を行うための受け口です (タスクコンテキスト用)。

非タスクコンテキスト用の受け口はありません。
`callsiHandlerBodyciHandlerBody`
### シグニチャ
*signature*`siHandlerBody`
タイムイベントハンドラの本体の呼出しに用いるシグニチャです。
void` main`(void)
ハンドラの本体です。タイムイベントが発生した際に、カーネルによって呼び出されます。
*signature*`sAlarm`
アラーム通知の制御、及び状態の取得を行うためのシグニチャです (タスクコンテキスト用)。
ER` start`(*[in]*RELTIM* alarmTime*)
アラーム通知を動作開始します。既に動作している状態である場合、通知時刻の再設定のみが行われます。

この関数は `sta_alm` サービスコール [NGKI3543] のラッパーです。
Param alarmTime
通知時刻 (現在時刻からの相対時間, マイクロ秒単位)
Return
正常終了 (`E_OK`) またはエラーコード。
ER` stop`(void)
アラーム通知を動作停止します。動作していない状態である場合、何も行われずに正常終了します。

この関数は `stp_alm` サービスコール [NGKI3545] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` refer`(*[out]*T_RALM** pk_alarmStatus*)
アラーム通知の現在状態を参照します。

この関数は `ref_alm` サービスコール [NGKI2572] のラッパーです。
Param pk_alarmStatus
アラーム通知の現在状態を入れるメモリ領域へのポインタ
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siAlarm`
アラーム通知の制御、及び状態の取得を行うためのシグニチャです (非タスクコンテキスト用)。
ER` start`(*[in]*RELTIM* alarmTime*)
アラーム通知を動作開始します。既に動作している状態である場合、通知時刻の再設定のみが行われます。

この関数は `ista_alm` サービスコール [NGKI3543][NGKI0562]  のラッパーです。
Param alarmTime
通知時刻 (現在時刻からの相対時間, マイクロ秒単位)
Return
正常終了 (`E_OK`) またはエラーコード。
ER` stop`(void)
アラーム通知を動作停止します。動作していない状態である場合、何も行われずに正常終了します。

この関数は `istp_alm` サービスコール [NGKI3545][NGKI0562]  のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`sCyclic`
周期通知の制御、及び状態の取得を行うためのシグニチャです (タスクコンテキスト用)。

非タスクコンテキスト用のシグニチャはありません。
ER` start`(void)
周期通知を動作開始します。既に動作している状態である場合、次回通知時刻の再設定のみが行われます。

この関数は `sta_cyc` サービスコール [NGKI2431] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` stop`(void)
周期通知を動作停止します。動作していない状態である場合、何も行われずに正常終了します。

この関数は `stp_cyc` サービスコール [NGKI2455] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` refer`(*[out]*T_RCYC** pk_cyclicHandlerStatus*)
周期通知の現在状態を参照します。

この関数は `ref_cyc` サービスコール [NGKI2463] のラッパーです。
Param pk_cyclicHandlerStatus
周期通知の現在状態を入れるメモリ領域へのポインタ
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siNotificationHandler`
タイムイベント通知の通知先を指定するためシグニチャです。
アプリケーション定義のセルではこのシグニチャの呼び口・受け口を定義しないでください。

このシグニチャに関数は含まれていません。

## 実装の詳細

### タイムイベント通知の生成

`tAlarmNotifier` 及び `tCyclicNotifier` によるタイムイベント通知の生成は、パラメータの指定方法が特殊な為ファクトリ記述では行えず、代わりに TECS ジェネレータセルタイププラグイン `NotifierPlugin` を利用して行います。
kernel.cdl (抜粋)
```
[active,generate(NotifierPlugin,"factory=\"CRE_ALM({{id}}, { {{attribute}}, {{{_handler_params_}}} });\", ""output_file=tecsgen.cfg")]celltypetAlarmNotifier{/* ... */};
```

`NotifierPlugin` は、対象のセルタイプに、タイムイベント通知固有の属性及び呼び口のセットが定義されていると仮定し、セルに指定された属性値と、プラグインの引数として指定されたテンプレート文字列を基にして、適切な静的 API 記述を生成します。以下はテンプレート文字列を抜粋したものです。
`tAlarmNotifier` のテンプレート文字列
```
CRE_ALM({{id}},{{{attribute}},{{{_handler_params_}}}});
```

この中に含まれる二重中かっこで囲われた属性名 (e.g., `{{id}}`) は、対応する属性値で置換されます。ただし、 `{{_handler_params_}}` は特別な扱いを受け、この後説明する通知先指定アルゴリズムにより、通知先を指定するパラメータ列で置換されます。
例えば、タスクイベント通知の使用方法の一つとしてタスクを通知先とする場合を例として挙げましたが、この場合は次の静的 API 記述が生成されます。
tecsgen.cfg
```
CRE_ALM(ALMID_tAlarmNotifier_Alarm,{TA_NULL,{TNFY_ACTTSK,TSKID_tTask_MyTask}});
```

属性値は `id` を除き、全て静的 API 記述の引数、または `NotifierPlugin` の入力としてのみ用いられます。この為、 `[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### 通知先の指定

タイムイベント通知の通知先としてカーネルオブジェクトを指定する場合、静的 API にはハンドラ関数ではなく、通知先オブジェクトの ID を直接指定することになります。 `NotifierPlugin` では、通知先オブジェクトの ID を呼び口 `ciNotificationHandler` 及び `ciErrorNotificationHandler` の結合先の属性値を読み取ることで、通知先を決定します。

したがって、これらの呼び口に対応するシグニチャ `siNotificationHandler` は実行時には使用されず、このため、このシグニチャには関数は定義されていません。

通知先指定アルゴリズムの役割は、セルの属性値・呼び口の結合先の組み合わせを、オペレーティングシステムの仕様で定義されている通知方法 [NGKI3689] にマッピングし、その通知方法を指定するのに必要な適切なパラメータ列を生成することです。このアルゴリズムの説明に入る前に、いくつか用語を定義しておきましょう。
ハンドラ
通常通知とエラー通知を、ここではハンドラと呼びます。例えば「各ハンドラに対応する呼び口がある」と言う場合、通常通知用の呼び口とエラー通知用の呼び口が個別に存在することを意味します。
共通呼び口
通知先オブジェクトを結合するための呼び口 (ハンドラ毎に存在し、それぞれ `ciNotificationHandler` 及び `ciErrorNotificationHandler`) は共通呼び口と呼ばれます。

これらの呼び口が共通呼び口と呼ばれる理由は、通知先オブジェクトが種類が何であっても、全てこの呼び口に結合することで、通知先を指定することになる為です。
ハンドラタイプ
通知方法を細分化し、通常通知とエラー通知の違いを表せるようにしたものです。

| 
通知方法
 | 
通常のハンドラ
 | 
エラーハンドラ
 | 
| 
なし
 | 
N/A
 | 
`NullHandlerType`
 | 
| 
タイムイベントハンドラの呼出し
 | 
`UserHandlerType`
 | 
N/A
 | 
| 
変数の設定
 | 
`SetVariableHandlerType`
 | 
`SetVariableToErrorCodeHandlerType`
 | 
| 
変数のインクリメント
 | 
`IncrementVariableHandlerType`
 | 
| 
タスクの起動
 | 
`ActivateTaskHandlerType`
 | 
| 
タスクの起床
 | 
`WakeUpTaskHandlerType`
 | 
| 
セマフォの資源の返却
 | 
`SignalSemaphoreHandlerType`
 | 
| 
イベントフラグのセット
 | 
`SetEventflagHandlerType`
 | 
| 
データキューへの送信
 | 
`SendToDataqueueHandlerType`
 | 
`SendErrorCodeToDataqueueHandlerType`
 | 
通知先指定アルゴリズムは各タイムイベント通知セル (厳密に言うと、`NotifierPlugin`が適用されたセルタイプのセル) に対し、以下の手順を実施します。

- 
以下のステップを各ハンドラに対して実行する。

- 
現在処理中のハンドラに対応する共通呼び口の結合先のセルのIDとセルタイプ名を取得する。また、通知先指定に関わる属性の属性値及び、指定の有無 (いずれも `[optional]` として指定されているが、ここではそれは重要ではない) を取得する。

- 
各ハンドラタイプが持つ属性・結合先セルタイプ名の組み合わせと、実際に指定されたものを照合する。完全一致するものが存在しなかった場合、エラーを出力して当該セルの処理を終了する。

- 
現在処理中のハンドラ用の静的 API 記述のパラメータ列を含む断片を生成する。

- 
通常のハンドラが「エラーが発生する可能性がある」ものとしてマークされている場合、エラーハンドラが指定されている (`NullHandlerType` 以外のハンドラタイプである) ことを確認する。もし指定されておらず、`ignoreErrors` が `true` ではない場合、警告を出力する。

- 
通常のハンドラが「エラーが発生する可能性がある」ものとしてマークされていないのにも関わらず、エラーハンドラが指定されている場合、エラーを出力する。

- 
前のステップで得られた静的 API 記述の断片と、指定されたテンプレート文字列を用い、最終的な静的 API 記述を生成する。

### ユーザハンドラの呼び出し

呼び口 `ciNotificationHandler` に `tTimeEventHandler::eiNotificationHandler` が結合された場合、ハンドラタイプ `UserHandlerType` が選択され、ユーザハンドラの呼び出しに必要な静的 API 記述が生成されます。

ユーザの便宜のために単体でユーザハンドラ受け口に直接結合可能な `tAlarmHandler`, `tCyclicHandler` が用意されています。これらは複合セルタイプで、それぞれ `tAlarmNotifier`, `tCyclicNotifier` と、`tTimeEventHandler` が含まれ、`tTimeEventHandler::ciHandlerBody` がエクスポートされており、ユーザはこれをアプリケーション定義のセルの受け口に結合するだけで使用することができます。

ユーザハンドラの呼び出しに必要な静的 API の引数は以下の通りです [NGKI3722]。
*type*`T_NFY_HDR`
タイムイベントハンドラ呼出し用の付随情報を含む構造体。
intptr_t`exinf`
タイムイベントハンドラに渡される引数。
TMEHDR`tmehdr`
タイムイベントハンドラの先頭番地。

従って `T_NFY_HDR::tmehdr` にハンドラ関数を指定する訳ですが、ユーザハンドラの受け口関数を直接ここに指定することはできません。受け口関数のシグニチャは状況によって4通りに変化します。

```
voidtCelltype_eiHandlerBody_main(CELLIDXidx);// tCelltypeが非singleton, 受け口が配列でないvoidtCelltype_eiHandlerBody_main(void);// singleton, 受け口が配列でないvoidtCelltype_eiHandlerBody_main(CELLIDXidx,int_tsubscript);// 非singleton, 受け口配列voidtCelltype_eiHandlerBody_main(int_tsubscript);// singleton, 受け口配列
```

このため、カーネルからの呼出しを仲介するための関数が必要となります。この関数は**アダプタ関数**と呼ばれ、`NotifierPlugin` によって生成されます。

アダプタ関数は受け口関数を呼ぶ際、最大3個の情報 (受け口関数, `idx`, `subscript`) が必要となります。`T_NFY_HDR::exinf` を介して引数を受け取ることができますが、これを介して直接渡せる引数は1個だけです。解決策には様々なものがありますが、`NotifierPlugin` では引数のうち1個を `T_NFY_HDR::exinf` を介して渡し、受け口関数と残った引数はその値ごとに関数を特殊化するアプローチを採用しています。このアプローチは最も時間・空間効率に優れていると考えられています。

生成例を示します。以下はハンドラ受け口が非配列で、所属セルタイプが `[singleton]` では**ない**場合の出力例です (紙面の節約のため、簡略化しています)。
tecsgen.cfg
```
CRE_CYC(ALMID_tCyclicHandler_CyclicHandler,{TA_NULL,{TNFY_HANDLER,&tCT_CB_tab[1],tTimeEventHandler_tCyclicNotifier_tCT_eiHandlerBody_adap},50,0});
```
tTimeEventHandler.c
```
voidtTimeEventHandler_tCyclicNotifier_tCT_eiHandlerBody_adap(intptr_textinf){tCT_eiHandlerBody_main((CELLIDX)extinf);}
```

次はハンドラ受け口が配列で、周期通知が複数ある場合の出力です。アダプタ関数が特定のセル `Cell` に特殊化されていることに着目してください。
tecsgen.cfg
```
CRE_CYC(ALMID_tCyclicHandler_CyclicHandler,{TA_NULL,{TNFY_HANDLER,0,tTimeEventHandler_tCyclicNotifier_tCT_eiHandlerBody_adap_Cell},50,0});CRE_CYC(ALMID_tCyclicHandler_CyclicHandler,{TA_NULL,{TNFY_HANDLER,1,tTimeEventHandler_tCyclicNotifier_tCT_eiHandlerBody_adap_Cell},50,0});
```
tTimeEventHandler.c
```
voidtTimeEventHandler_tCyclicNotifier_tCT_eiHandlerBody_adap_Cell(intptr_textinf){tCT_eiHandlerBody_main(&tCT_CB_tab[1],(int_t)extinf);}
```

### サービスコール

`eCyclic` 、 `eAlarm` 及び `eiAlarm` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tAlarmNotifier_inline.h
```
InlineEReAlarm_start(CELLIDXidx,RELTIMalarmTime){CELLCB*p_cellcb=GET_CELLCB(idx);return(sta_alm(ATTR_id,alarmTime));}
```

---

Source: [[index]]
