---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\dataqueue.html
title: データキュー― tDataqueue
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: データキュー― tDataqueue"
---

# データキュー― tDataqueue

# データキュー― `tDataqueue`

データキューは、1ワードのデータをメッセージとして、FIFO順で送受信するための同期・通信オブジェクトである。
より大きいサイズのメッセージを送受信したい場合には、メッセージを置いたメモリ領域へのポインタを1ワードのデータとして送受信する方法がある。
データキューは，データキューIDと呼ぶID番号によって識別する[NGKI1657]．

課題

to be filled in

## リファレンス

### セルタイプ
*celltype*`tDataqueue`
データキューの生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_DTQ` 静的API [NGKI1665] によりデータキュー    の生成を行います。静的APIの引数の値には、一部を除き属性値が用いられます。
*attr *ID` id`=C_EXP("DTQID_$id$");
データキューのID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`=C_EXP("TA_NULL")
タスク属性 [NGKI3526] を `C_EXP` で囲んで指定します (省略可能)。
`TA_TPRI`
送信待ち行列をタスクの優先度順にする
`TA_NULL`
送信待ち行列はFIFO順になる[NGKI1662]。
*attr *uint_t` dataCount`=1;
データキュー管理領域に格納できるデータ数です。デフォルトは１に設定されます。
*attr *void*` dataqueueManagementBuffer`=C_EXP("NULL");
データキュー管理領域の先頭番地。デフォルトは C_EXP("NULL")に設定されます。
NULLとした場合，dtqcntで指定した数のデータを格納できるデータキュー管理領域が，
コンフィギュレータまたはカーネルにより確保される[NGKI1682]。
*entry*sDataqueue` eDataqueue`
データキューの制御及び状態の取得を行うための受け口です。
*entry*siDataqueue` eiDataqueue`
データキューの制御を行うための受け口です (非タスクコンテキスト用)。
`entrysiNotificationHandlereiNotificationHandler;`
タイムイベント通知 の通知方法として「データキューへの送信による通知」を用いる場合に結合する受け口です。

### シグニチャ
*signature*`sDataqueue`
データキューの制御、及び状態の取得を行うためのシグニチャです。
ER` send`(*[in]*intptr_t* data*)
データキューへの送信。

この関数は `snd_dtq` サービスコール [NGKI1718] のラッパーです。
Param data
送信データ。
Return
正常終了（E_OK）またはエラーコード。
ER` sendPolling`(*[in]*intptr_t* data*)
データキューへの送信（ポーリング）。

この関数は `psnd_dtq` サービスコール [NGKI3535] のラッパーです。
Param data
送信データ。
Return
正常終了（E_OK）またはエラーコード。
ER` sendTimeout`(*[in]*intptr_t* data*, *[in]*TMO* timeout*)
データキューへの送信（タイムアウト付き）。

この関数は `tsnd_dtq` サービスコール [NGKI1721] のラッパーです。
Param data
送信データ。
Param timeout
タイムアウト時間。
Return
正常終了（E_OK）またはエラーコード。
ER` sendForce`(*[in]*intptr_t* data*)
データキューへの強制送信。

この関数は `fsnd_dtq` サービスコール [NGKI3536] のラッパーです。
Param data
送信データ。
Return
正常終了（E_OK）またはエラーコード。
ER` receive`(*[out]*intptr_t** p_data*)
データキューからの受信。

この関数は `rcv_dtq` サービスコール [NGKI1751] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Return
正常終了（E_OK）またはエラーコード。
ER` receivePolling`(*[out]*intptr_t** p_data*)
データキューからの受信（ポーリング）。

この関数は `prcv_dtq` サービスコール [NGKI1752] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Return
正常終了（E_OK）またはエラーコード。
ER` receiveTimeout`(*[out]*intptr_t** p_data*, *[in]*TMO* timeout*)
データキューからの受信（タイムアウト付き）。

この関数は `trcv_dtq` サービスコール [NGKI1753] のラッパーです。
Param p_data
受信データを入れるメモリ領域へのポインタ。
Param timeout
タイムアウト時間。
Return
正常終了（E_OK）またはエラーコード。
ER` initialize`(void)
データキューの再初期化。

この関数は `ini_dtq` サービスコール [NGKI1772] のラッパーです。
Return
正常終了（E_OK）またはエラーコード。
ER` refer`(*[out]*T_RDTQ** pk_dataqueueStatus*)
データキューの状態参照。

この関数は `ref_dtq` サービスコール [NGKI1781] のラッパーです。
Param pk_dataqueueStatus
データキューの現在状態を入れるパケットへのポインタ。
Return
正常終了（E_OK）またはエラーコード。
*signature*`siDataqueue`
データキューの制御を行うためのシグニチャです (非タスクコンテキスト用)。
`ERsendPolling([in]intptr_tdata);`
タスクに対して起動要求を行います。

この関数は `iact_tsk` サービスコール [NGKI3529][NGKI0562] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERsendForce([in]intptr_tdata);`
タスクを起床します。

この関数は `iwup_tsk` サービスコール [NGKI3531][NGKI0562] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。

## 実装の詳細

### データキューの生成

`tDataqueue` によるデータキューの生成は、以下に示しているようなファクトリ記述により静的 API 記述を生成することで実現されています。
kernel.cdl (抜粋)
```
factory{write("tecsgen.cfg","CRE_DTQ(%s, { %s, %s, %s });",id,attribute,dataCount,dataqueueManagementBuffer);};
```

最初の `MyDataqueue` を用いた例の場合、以下のような静的API記述が生成されます。
tecsgen.cfg
```
CRE_DTQ(DTQID__tDataqueue_Dataqueue,{TA_NULL,1,C_EXP("NULL")});
```

`tDataqueue` が持つ属性は、 `id` を除き実行時にはすべて未使用であるため、`[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### サービスコール

`eDataqueue` 及び `eiDataqueue` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tDataqueue_inline.h
```
InlineEReDataqueue_send(CELLIDXidx,intptr_tdata){CELLCB*p_cellcb=GET_CELLCB(idx);return(snd_dtq(ATTR_id,data));}
```

---

Source: [[index]]
