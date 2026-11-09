---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\semaphore.html
title: セマフォ ― tSemaphore
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: セマフォ ― tSemaphore"
---

# セマフォ ― tSemaphore

# セマフォ ― `tSemaphore`

セマフォは、使用されていない資源の有無や数量を数値で表現することにより、その資源を使用する際の排他制御や同期を行うためのオブジェクトである。

## 使用方法

### セマフォの生成

アプリケーション開発者は `tSemaphore` セルタイプのセルを生成することにより、セマフォを生成することができます。次の例では `MySemaphore` という名前のセマフォセルを生成し、 `MyCell` の `eTaskBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{callsSemaphorecSemaphore;};celltMyCellTypeMyCell{cSemaphore=MySemaphore.eSemaphore;};celltSemaphoreMySemaphore{attribute=C_EXP("TA_NULL");count=0;max=1;};
```
tMyCellType.c
```
voideTaskBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

### セマフォの制御

`tSemaphore` が提供する `eSemaphore` という名前の受け口を利用することにより、セマフォの制御及び状態の取得を行うことができます。
app.cdl
```
celltSemaphoreMySemaphore{};celltypetMyAnotherCellType{callsSemaphorecSemaphore;};celltMyAnotherCellTypeMyAnotherCell{cSemaphore=MySemaphore.eSemaphore;};
```
tMyAnotherCellType.c
```
// セマフォ資源の返却cSemaphore_signal();// セマフォの現在状態の参照T_RSEM*pk_semaphoreStatus;cSemaphore_refer(pk_semaphoreStatus);
```

なお、非タスクコンテキスト内では、`eSemaphore` の代わりに
`eiSemaphore` を使用する必要があります。

## リファレンス

### セルタイプ
*celltype*`tSemaphore`
セマフォの生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_SEM` 静的API [NGKI1452] によりセマフォの生成を行います。静的APIの引数の値には、一部を除き属性値が用いられます。
*attr *ID` id`=C_EXP("SEMID_$id$");
セマフォのID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`
セマフォ属性 [NGKI1448] を `C_EXP` で囲んで指定します (省略可能)。
`TA_NULL`
デフォルト値（FIFO待ち）。
`TA_TPRI`
待ち行列をタスクの優先度順にする。
*attr *uint32_t` count`
セマフォの初期資源数。
*attr *uint32_t` max`=1;
セマフォの最大資源数。
*entry*sSemaphore` eSemaphore`
セマフォの制御及び状態の取得を行うための受け口です。
*entry*siSemaphore` eiSemaphore`
セマフォの制御を行うための受け口です (非タスクコンテキスト用)。

### シグニチャ
*signature*`sSemaphore`
セマフォの制御、及び状態の取得を行うためのシグニチャです。
ER` signal`(void)
対象セマフォに資源を返却します。対象セマフォの待ち行列にタスクが存在する場合には、待ち行列の先頭のタスクが待ち解除されます。

この関数は `sig_sem` サービスコール [NGKI3533] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERwait(void);`
対象セマフォから資源を獲得します。対象セマフォの資源数が１以上の場合には、資源数から１が減ぜられます。

この関数は `wai_sem` サービスコール [NGKI1510] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERwaitPolling(void);`
対象セマフォから資源を獲得します(ポーリング)。対象セマフォの資源数が１以上の場合には、資源数から１が減ぜられます。

この関数は `pol_sem` サービスコール [NGKI1511] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERwaitTimeout([in]TMOtimeout);`
対象セマフォから資源を獲得します(タイムアウト付き)。対象セマフォの資源数が１以上の場合には、資源数から１が減ぜられます。

この関数は `twai_sem` サービスコール [NGKI1512] のラッパーです。
Param timeout
タイムアウト時間
Return
正常終了 (`E_OK`) またはエラーコード。
`ERinitialize(void);`
対象セマフォを再初期化します。対象セマフォの資源数は初期資源数に初期化されます。

この関数は `ini_sem` サービスコール [NGKI1526] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERrefer([out]T_RSEM*pk_semaphoreStatus);`
セマフォの現在状態を参照します。

この関数は `ref_sem` サービスコール [NGKI1535] のラッパーです。
Param pk_semaphoreStatus
セマフォの現在状態を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siSemaphore`
セマフォの制御を行うためのシグニチャです (非タスクコンテキスト用)。
`ERsignal();`
この関数は `sig_sem` サービスコール [NGKI3533] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。

## 実装の詳細

### セマフォの生成

`tSemaphore` によるセマフォの生成は、以下に示しているようなファクトリ記述により静的 API 記述を生成することで実現されています。
kernel.cdl (抜粋)
```
factory{write("tecsgen.cfg","CRE_SEM(%s, { %s, %s, %s });",id,attribute,count,max);};
```

最初の `MySemaphore` を用いた例の場合、以下のような静的API記述が生成されます。
tecsgen.cfg
```
CRE_SEM(SEMID_tSemaphore_MySemaphore,{TA_NULL,0,1});
```

`tSemaphore` が持つ属性は、 `id` を除き実行時にはすべて未使用であるため、`[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### サービスコール

`eSemaphore` 及び `eiSemaphore` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tSemaphore_inline.h
```
InlineEReSemaphore_signal(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);return(sig_sem(ATTR_id));}
```

---

Source: [[index]]
