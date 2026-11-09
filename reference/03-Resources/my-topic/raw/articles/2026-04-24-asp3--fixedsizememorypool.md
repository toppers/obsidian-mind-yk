---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\fixedsizememorypool.html
title: 固定長メモリプール ― tFixedSizeMemoryPool
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: 固定長メモリプール ― tFixedSizeMemoryPool"
---

# 固定長メモリプール ― tFixedSizeMemoryPool

# 固定長メモリプール ― `tFixedSizeMemoryPool`

固定長メモリプールは、生成時に決めたサイズのメモリブロック（固定長メモリブロック）を動的に獲得・返却するための同期・通信オブジェクトである。固定長メモリプールは、固定長メモリプールIDと呼ばれるID番号で識別する [NGKI2215]。

## 使用方法

### 固定長メモリプールの生成

アプリケーション開発者は `tFixedSizeMemoryPool` セルタイプのセルを生成することにより、固定長メモリプールを生成することができます。次の例では `MyFixedSizeMemoryPool` という名前の固定長メモリプールセルを生成し、 `MyCell` の `eTaskBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{callsFixedSizeMemoryPoolcFixedSizeMemoryPool;};celltMyCellTypeMyCell{cFixedSizeMemoryPool=MyFixedSizeMemoryPool.eFixedSizeMemoryPool;};celltFixedSizeMemoryPoolMyFixedSizeMemoryPool{attribute=C_EXP("TA_NULL");blockCount=TODO;blockSize=;mpf=C_EXP("NULL");mpfmb=C_EXP("NULL");};
```
tMyCellType.c
```
voideTaskBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

### 固定長メモリプールの制御

`tFixedSizeMemoryPool` が提供する `eFixedSizeMemoryPool` という名前の受け口を利用することにより、固定長メモリプールの制御及び状態の取得を行うことができます。
app.cdl
```
celltFixedSizeMemoryPoolMyFixedSizeMemoryPool{};celltypetMyAnotherCellType{callsFixedSizeMemoryPoolcFixedSizeMemoryPool;};celltMyAnotherCellTypeMyAnotherCell{cFixedSizeMemoryPool=MyFixedSizeMemoryPool.eFixedSizeMemoryPool;};
```
tMyAnotherCellType.c
```
// 固定長メモリブロックの獲得void**p_block;cFixedSizeMemoryPool_get(p_block);// 固定長メモリプールの現在状態の取得T_RMPF*pk_memoryPoolFixedSizeStatuscFixedSizeMemoryPool_refer(pk_memoryPoolFixedSizeStatus);
```

なお、非タスクコンテキスト内では、`eFixedSizeMemoryPool` の代わりに
`eiFixedSizeMemoryPool` を使用する必要があります。

## リファレンス

### セルタイプ
*celltype*`tFixedSizeMemoryPool`
固定長メモリプールの生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_MPF` 静的API [NGKI2221] により固定長メモリプールの生成を行います。静的APIの引数の値には、一部を除き属性値が用いられます。
*attr *ID` id`=C_EXP("MPFID_$id$");
固定長メモリプールのID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`
固定長メモリプール属性 [NGKI2218] を `C_EXP` で囲んで指定します (省略可能)。
`TA_NULL`
デフォルト値（FIFO待ち）。
`TA_TPRI`
送信待ち行列をタスクの優先度順にする。
*attr *uint32_t` blockCount`
TODO
*attr *uint32_t` blockSize`
TODO
*attr *MPF_T*` mpf`=C_EXP("NULL");
TODO
*attr *void*` mpfmb`=C_EXP("NULL");
固定長メモリプール管理領域の先頭番地。
*entry*sFixedSizeMemoryPool` eFixedSizeMemoryPool`
固定長メモリプールの制御及び状態の取得を行うための受け口です。
*entry*siFixedSizeMemoryPool` eiFixedSizeMemoryPool`
固定長メモリプールの制御を行うための受け口です (非タスクコンテキスト用)。

### シグニチャ
*signature*`sFixedSizeMemoryPool`
固定長メモリプールの制御、及び状態の取得を行うためのシグニチャです。
ER` get`(*[out]*void*** p_block*)
対象固定長メモリプールから固定長メモリブロックを獲得し、その先頭番地をp_blockが指すメモリ領域に返す。

この関数は `get_mpf` サービスコール [NGKI2287] のラッパーです。
Param p_block
獲得した固定長メモリブロックの先頭番地を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` getPolling`(*[out]*void*** p_block*)
対象固定長メモリプールから固定長メモリブロックを獲得し、その先頭番地をp_blockが指すメモリ領域に返す（ポーリング）。

この関数は `pget_mpf` サービスコール [NGKI2288] のラッパーです。
Param p_block
獲得した固定長メモリブロックの先頭番地を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` getTimeout`(*[out]*void*** p_block*, *[in]*TMO* timeout*)
対象固定長メモリプールから固定長メモリブロックを獲得し、その先頭番地をp_blockが指すメモリ領域に返す（タイムアウト付き）。

この関数は `tget_mpf` サービスコール [NGKI2289] のラッパーです。
Param p_block
獲得した固定長メモリブロックの先頭番地を入れるメモリ領域へのポインタ。
Param timeout
タイムアウト時間。
Return
正常終了 (`E_OK`) またはエラーコード。
ER` release`(*[in]*constvoid** block*)
対象固定長メモリプールに、blkで指定した固定長メモリブロックを返却する。

この関数は `rls_mpf` サービスコール [NGKI2304] のラッパーです。
Param block
返却する固定長メモリブロックの先頭番地。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERinitialize(void);`
対象固定長メモリプールを再初期化します。対象固定長メモリプールの固定長メモリプール管理領域は、格納されているデータがない状態に初期化されます。

この関数は `ini_mpf` サービスコール [NGKI2314] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERrefer([out]T_RSEM*pk_fixedSizeMemoryPoolStatus);`
固定長メモリプールの現在状態を参照します。

この関数は `ref_mpf` サービスコール [NGKI2323] のラッパーです。
Param pk_fixedSizeMemoryPoolStatus
固定長メモリプールの現在状態を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siFixedSizeMemoryPool`
固定長メモリプールの制御を行うためのシグニチャです (非タスクコンテキスト用)。TODO(元々非タスクコンテキスト？kernel.cdlを見る限り)
`ERsendPolling([in]intptr_tdata,[in]PRIdataPriority);`
この関数は `snd_mpf` サービスコール [NGKI1855] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。

## 実装の詳細

### 固定長メモリプールの生成

`tFixedSizeMemoryPool` による固定長メモリプールの生成は、以下に示しているようなファクトリ記述により静的 API 記述を生成することで実現されています。
kernel.cdl (抜粋)
```
factory{write("tecsgen.cfg","CRE_MPF( %s, {%s, %s, %s, %s, %s} );",id,attribute,blockCount,blockSize,mpf,mpfmb);};
```

最初の `MyFixedSizeMemoryPool` を用いた例の場合、以下のような静的API記述が生成されます。
tecsgen.cfg
```
CRE_MPF(MPFID_tFixedSizeMemoryPool_MyFixedSizeMemoryPool,{TA_NULL,TODO,TODO,NULL,NULL});
```

`tFixedSizeMemoryPool` が持つ属性は、 `id` を除き実行時にはすべて未使用であるため、`[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### サービスコール

`eFixedSizeMemoryPool` 及び `eiFixedSizeMemoryPool` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tFixedSizeMemoryPool_inline.h
```
InlineEReFixedSizeMemoryPool_get(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);return(get_mpf(ATTR_id));}
```

---

Source: [[index]]
