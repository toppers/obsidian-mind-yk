---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\terminateroutine.html
title: 終了処理ルーチン ― tTerminateRoutine
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: 終了処理ルーチン ― tTerminateRoutine"
---

# 終了処理ルーチン ― tTerminateRoutine

# 終了処理ルーチン ― `tTerminateRoutine`

終了処理ルーチンは、１ワードのデータをメッセージとして、データの優先度順で送受信するための同期・通信カーネルオブジェクトである。より大きいサイズのメッセージを送受信したい場合には、メッセージを置いたメモリ領域へのポインタを1ワードのデータとして送受信する方法がある。終了処理ルーチンは，終了処理ルーチンIDと呼ぶID番号によって識別する [NGKI1791]。

## 使用方法

### 終了処理ルーチンの生成

アプリケーション開発者は `tTerminateRoutine` セルタイプのセルを生成することにより、終了処理ルーチンを生成することができます。次の例では `MyTerminateRoutine` という名前の終了処理ルーチンセルを生成し、 `MyCell` の `eTaskBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{callsTerminateRoutinecTerminateRoutine;};celltMyCellTypeMyCell{cTerminateRoutine=MyTerminateRoutine.eTerminateRoutine;};celltTerminateRoutineMyTerminateRoutine{attribute=C_EXP("TA_NULL");count=1;maxDataPriority=C_EXP("TMAX_DPRI");pdqmb=C_EXP("NULL");};
```
tMyCellType.c
```
voideTaskBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

### 終了処理ルーチンの制御

`tTerminateRoutine` が提供する `eTerminateRoutine` という名前の受け口を利用することにより、終了処理ルーチンの制御及び状態の取得を行うことができます。
app.cdl
```
celltTerminateRoutineMyTerminateRoutine{};celltypetMyAnotherCellType{callsTerminateRoutinecTerminateRoutine;};celltMyAnotherCellTypeMyAnotherCell{cTerminateRoutine=MyTerminateRoutine.eTerminateRoutine;};
```
tMyAnotherCellType.c
```
// 終了処理ルーチンの送信intptr_tdata;PRIdataPriority;cTerminateRoutine_send(data,dataPriority);// 終了処理ルーチンの受信intptr_t*p_data;PRI*p_dataPriority;cTerminateRoutine_receive(p_data,p_dataPriority);
```

なお、非タスクコンテキスト内では、`eTerminateRoutine` の代わりに
`eiTerminateRoutine` を使用する必要があります。

## リファレンス

### セルタイプ
*celltype*`tTerminateRoutine`
終了処理ルーチンの生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_PDQ` 静的API [NGKI1800] により終了処理ルーチンの生成を行います。静的APIの引数の値には、一部を除き属性値が用いられます。
*attr *ID` id`=C_EXP("PDQID_$id$");
終了処理ルーチンのID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`
終了処理ルーチン属性 [NGKI1795] を `C_EXP` で囲んで指定します (省略可能)。
`TA_NULL`
デフォルト値（FIFO待ち）。
`TA_TPRI`
送信待ち行列をタスクの優先度順にする。
*attr *uint32_t` count`=1;
終了処理ルーチンの容量。
*attr *PRI` maxDataPriority`
終了処理ルーチンに送信できるデータ優先度の最大値。
*attr *void*` pdqmb`=C_EXP("NULL");
終了処理ルーチン管理領域の先頭番地。
*entry*sTerminateRoutine` eTerminateRoutine`
終了処理ルーチンの制御及び状態の取得を行うための受け口です。
*entry*siTerminateRoutine` eiTerminateRoutine`
終了処理ルーチンの制御を行うための受け口です (非タスクコンテキスト用)。

### シグニチャ
*signature*`sTerminateRoutine`
終了処理ルーチンの制御、及び状態の取得を行うためのシグニチャです。
ER` send`(*[in]*intptr_t* data*, *[in]*PRI* dataPriority*)
対象終了処理ルーチンに、dataで指定したデータを、dataPriorityで指定した優先度で送信します。対象終了処理ルーチンの受信待ち行列にタスクが存在する場合には、受信待ち行列の先頭のタスクが、dataで指定したデータを受信し、待ち解除されます。待ち解除されたタスクに待ち状態となったサービスコールからE_OKが返ります。

この関数は `snd_pdq` サービスコール [NGKI1855] のラッパーです。
Param data
送信データ。
Param dataPriority
送信データの優先度。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` sendPolling`(*[in]*intptr_t* data*, *[in]*PRI* dataPriority*)
対象終了処理ルーチンに、dataで指定したデータを、dataPriorityで指定した優先度で送信します（ポーリング）。対象終了処理ルーチンの受信待ち行列にタスクが存在する場合には、受信待ち行列の先頭のタスクが、dataで指定したデータを受信し、待ち解除されます。待ち解除されたタスクに待ち状態となったサービスコールからE_OKが返ります。

この関数は `psnd_pdq` サービスコール [NGKI3537] のラッパーです。
Param data
送信データ。
Param dataPriority
送信データの優先度。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` sendTimeout`(*[in]*intptr_t* data*, *[in]*PRI* dataPriority*, *[in]*TMO* timeout*)
対象終了処理ルーチンに、dataで指定したデータを、dataPriorityで指定した優先度で送信します（タイムアウト付き）。対象終了処理ルーチンの受信待ち行列にタスクが存在する場合には、受信待ち行列の先頭のタスクが、dataで指定したデータを受信し、待ち解除されます。待ち解除されたタスクに待ち状態となったサービスコールからE_OKが返ります。

この関数は `tsnd_pdq` サービスコール [NGKI1858] のラッパーです。
Param data
送信データ。
Param dataPriority
送信データの優先度。
Param timeout
タイムアウト時間。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` receive`(*[out]*intptr_t** p_data*, *[in]*PRI** p_dataPriority*)
対象終了処理ルーチンからデータを受信します。データの受信に成功した場合、受信したデータはp_dataが指すメモリ領域に、その優先度はp_dataPriorityが指すメモリ領域に返されます。

この関数は `rcv_pdq` サービスコール [NGKI1877] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Param p_dataPriority
受信データの優先度を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` receivePolling`(*[out]*intptr_t** p_data*, *[in]*PRI** p_dataPriority*)
対象終了処理ルーチンからデータを受信します（ポーリング）。データの受信に成功した場合、受信したデータはp_dataが指すメモリ領域に、その優先度はp_dataPriorityが指すメモリ領域に返されます。

この関数は `prcv_pdq` サービスコール [NGKI1878] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Param p_dataPriority
受信データの優先度を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` receiveTimeout`(*[out]*intptr_t** p_data*, *[in]*PRI** p_dataPriority*, *[in]*TMO* timeout*)
対象終了処理ルーチンからデータを受信します（タイムアウト付き）。データの受信に成功した場合、受信したデータはp_dataが指すメモリ領域に、その優先度はp_dataPriorityが指すメモリ領域に返されます。

この関数は `trcv_pdq` サービスコール [NGKI1879] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Param p_dataPriority
受信データの優先度を入れるメモリ領域へのポインタ。
Param timeout
タイムアウト時間。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERinitialize(void);`
対象終了処理ルーチンを再初期化します。対象終了処理ルーチンの終了処理ルーチン管理領域は、格納されているデータがない状態に初期化されます。

この関数は `ini_pdq` サービスコール [NGKI1902] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERrefer([out]T_RSEM*pk_terminateRoutineStatus);`
終了処理ルーチンの現在状態を参照します。

この関数は `ref_pdq` サービスコール [NGKI1911] のラッパーです。
Param pk_terminateRoutineStatus
終了処理ルーチンの現在状態を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siTerminateRoutine`
終了処理ルーチンの制御を行うためのシグニチャです (非タスクコンテキスト用)。
`ERsendPolling([in]intptr_tdata,[in]PRIdataPriority);`
この関数は `snd_pdq` サービスコール [NGKI1855] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。

## 実装の詳細

### 終了処理ルーチンの生成

`tTerminateRoutine` による終了処理ルーチンの生成は、以下に示しているようなファクトリ記述により静的 API 記述を生成することで実現されています。
kernel.cdl (抜粋)
```
factory{write("tecsgen.cfg","CRE_PDQ( %s, { %s, %s, %s, %s} );",id,attribute,count,maxDataPriority,pdqmb);};
```

最初の `MyTerminateRoutine` を用いた例の場合、以下のような静的API記述が生成されます。
tecsgen.cfg
```
CRE_PDQ(PDQID_tTerminateRoutine_MyTerminateRoutine,{TA_NULL,1,TMAX_DPRI,NULL});
```

`tTerminateRoutine` が持つ属性は、 `id` を除き実行時にはすべて未使用であるため、`[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### サービスコール

`eTerminateRoutine` 及び `eiTerminateRoutine` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tTerminateRoutine_inline.h
```
InlineEReTerminateRoutine_send(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);return(snd_pdq(ATTR_id));}
```

---

Source: [[index]]
