---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\initializeroutine.html
title: 初期化ルーチン ― tInitializeRoutine
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: 初期化ルーチン ― tInitializeRoutine"
---

# 初期化ルーチン ― tInitializeRoutine

# 初期化ルーチン ― `tInitializeRoutine`

初期化ルーチンは、カーネルが実行を制御する処理単位で、カーネルの動作開始の直前に、カーネル非動作状態で実行される [NGKI1791]。

## 使用方法

### 初期化ルーチンの生成

アプリケーション開発者は `tInitializeRoutine` セルタイプのセルを生成することにより、初期化ルーチンを生成することができます。次の例では `MyInitializeRoutine` という名前の初期化ルーチンセルを生成し、 `MyCell` の `eTaskBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{callsInitializeRoutineBodycInitializeRoutine;};celltMyCellTypeMyCell{cInitializeRoutine=MyInitializeRoutine.eInitializeRoutine;};celltInitializeRoutineMyInitializeRoutine{attribute=C_EXP("TA_NULL");};
```
tMyCellType.c
```
voideTaskBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

### 初期化ルーチンの制御

`tInitializeRoutine` が提供する `eInitializeRoutine` という名前の受け口を利用することにより、初期化ルーチンの制御及び状態の取得を行うことができます。
app.cdl
```
celltInitializeRoutineMyInitializeRoutine{};celltypetMyAnotherCellType{callsInitializeRoutineBodycInitializeRoutine;};celltMyAnotherCellTypeMyAnotherCell{cInitializeRoutine=MyInitializeRoutine.eInitializeRoutine;};
```
tMyAnotherCellType.c
```
// 初期化ルーチン本体cInitializeRoutine_main();
```

なお、非タスクコンテキスト内では、`eInitializeRoutine` の代わりに
`eiInitializeRoutine` を使用する必要があります。

## リファレンス

### セルタイプ
*celltype*`tInitializeRoutine`
初期化ルーチンの生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_PDQ` 静的API [NGKI1800] により初期化ルーチンの生成を行います。静的APIの引数の値には、一部を除き属性値が用いられます。
*attr *ID` id`=C_EXP("PDQID_$id$");
初期化ルーチンのID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`
初期化ルーチン属性 [NGKI1795] を `C_EXP` で囲んで指定します (省略可能)。
`TA_NULL`
デフォルト値（FIFO待ち）。
`TA_TPRI`
送信待ち行列をタスクの優先度順にする。
*attr *uint32_t` count`=1;
初期化ルーチンの容量。
*attr *PRI` maxDataPriority`
初期化ルーチンに送信できるデータ優先度の最大値。
*attr *void*` pdqmb`=C_EXP("NULL");
初期化ルーチン管理領域の先頭番地。
*entry*sInitializeRoutineBody` eInitializeRoutine`
初期化ルーチンの制御及び状態の取得を行うための受け口です。
*entry*siInitializeRoutine` eiInitializeRoutine`
初期化ルーチンの制御を行うための受け口です (非タスクコンテキスト用)。

### シグニチャ
*signature*`sInitializeRoutineBody`
初期化ルーチンの制御、及び状態の取得を行うためのシグニチャです。
ER` send`(*[in]*intptr_t* data*, *[in]*PRI* dataPriority*)
対象初期化ルーチンに、dataで指定したデータを、dataPriorityで指定した優先度で送信します。対象初期化ルーチンの受信待ち行列にタスクが存在する場合には、受信待ち行列の先頭のタスクが、dataで指定したデータを受信し、待ち解除されます。待ち解除されたタスクに待ち状態となったサービスコールからE_OKが返ります。

この関数は `snd_pdq` サービスコール [NGKI1855] のラッパーです。
Param data
送信データ。
Param dataPriority
送信データの優先度。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` sendPolling`(*[in]*intptr_t* data*, *[in]*PRI* dataPriority*)
対象初期化ルーチンに、dataで指定したデータを、dataPriorityで指定した優先度で送信します（ポーリング）。対象初期化ルーチンの受信待ち行列にタスクが存在する場合には、受信待ち行列の先頭のタスクが、dataで指定したデータを受信し、待ち解除されます。待ち解除されたタスクに待ち状態となったサービスコールからE_OKが返ります。

この関数は `psnd_pdq` サービスコール [NGKI3537] のラッパーです。
Param data
送信データ。
Param dataPriority
送信データの優先度。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` sendTimeout`(*[in]*intptr_t* data*, *[in]*PRI* dataPriority*, *[in]*TMO* timeout*)
対象初期化ルーチンに、dataで指定したデータを、dataPriorityで指定した優先度で送信します（タイムアウト付き）。対象初期化ルーチンの受信待ち行列にタスクが存在する場合には、受信待ち行列の先頭のタスクが、dataで指定したデータを受信し、待ち解除されます。待ち解除されたタスクに待ち状態となったサービスコールからE_OKが返ります。

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
対象初期化ルーチンからデータを受信します。データの受信に成功した場合、受信したデータはp_dataが指すメモリ領域に、その優先度はp_dataPriorityが指すメモリ領域に返されます。

この関数は `rcv_pdq` サービスコール [NGKI1877] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Param p_dataPriority
受信データの優先度を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` receivePolling`(*[out]*intptr_t** p_data*, *[in]*PRI** p_dataPriority*)
対象初期化ルーチンからデータを受信します（ポーリング）。データの受信に成功した場合、受信したデータはp_dataが指すメモリ領域に、その優先度はp_dataPriorityが指すメモリ領域に返されます。

この関数は `prcv_pdq` サービスコール [NGKI1878] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Param p_dataPriority
受信データの優先度を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` receiveTimeout`(*[out]*intptr_t** p_data*, *[in]*PRI** p_dataPriority*, *[in]*TMO* timeout*)
対象初期化ルーチンからデータを受信します（タイムアウト付き）。データの受信に成功した場合、受信したデータはp_dataが指すメモリ領域に、その優先度はp_dataPriorityが指すメモリ領域に返されます。

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
対象初期化ルーチンを再初期化します。対象初期化ルーチンの初期化ルーチン管理領域は、格納されているデータがない状態に初期化されます。

この関数は `ini_pdq` サービスコール [NGKI1902] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERrefer([out]T_RSEM*pk_initializeRoutineStatus);`
初期化ルーチンの現在状態を参照します。

この関数は `ref_pdq` サービスコール [NGKI1911] のラッパーです。
Param pk_initializeRoutineStatus
初期化ルーチンの現在状態を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siInitializeRoutine`
初期化ルーチンの制御を行うためのシグニチャです (非タスクコンテキスト用)。
`ERsendPolling([in]intptr_tdata,[in]PRIdataPriority);`
この関数は `snd_pdq` サービスコール [NGKI1855] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。

## 実装の詳細

### 初期化ルーチンの生成

`tInitializeRoutine` による初期化ルーチンの生成は、以下に示しているようなファクトリ記述により静的 API 記述を生成することで実現されています。
kernel.cdl (抜粋)
```
factory{write("tecsgen.cfg","CRE_PDQ( %s, { %s, %s, %s, %s} );",id,attribute,count,maxDataPriority,pdqmb);};
```

最初の `MyInitializeRoutine` を用いた例の場合、以下のような静的API記述が生成されます。
tecsgen.cfg
```
CRE_PDQ(PDQID_tInitializeRoutine_MyInitializeRoutine,{TA_NULL,1,TMAX_DPRI,NULL});
```

`tInitializeRoutine` が持つ属性は、 `id` を除き実行時にはすべて未使用であるため、`[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### サービスコール

`eInitializeRoutine` 及び `eiInitializeRoutine` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tInitializeRoutine_inline.h
```
InlineEReInitializeRoutine_send(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);return(snd_pdq(ATTR_id));}
```

---

Source: [[index]]
