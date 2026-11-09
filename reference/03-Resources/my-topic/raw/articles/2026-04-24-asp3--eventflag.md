---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\asp3\eventflag.html
title: イベントフラグ ― tEventflag
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: イベントフラグ ― tEventflag"
---

# イベントフラグ ― tEventflag

# イベントフラグ ― `tEventflag`

イベントフラグは、イベントの有無をビットごとのフラグで表現することにより、同期を行うためのオブジェクトです。

## 使用方法

### イベントフラグの生成

アプリケーション開発者は `tEventflag` セルタイプのセルを生成することにより、イベントフラグを生成することができます。次の例では `MyEventflag` という名前のイベントフラグセルを生成し、 `MyCell` の `eTaskBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{callsEventflagcEventflag;};celltMyCellTypeMyCell{cEventflag=MyEventflag.eEventflag;};celltEventflagMyEventflag{attribute=C_EXP("TA_NULL");flagPattern=0;};
```
tMyCellType.c
```
voideTaskBody_main(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);// ...}
```

### イベントフラグの制御

todo
`tTask` が提供する `eTask` という名前の受け口を利用することにより、タスクの制御及び状態の取得を行うことができます。
app.cdl
```
celltTaskMyTask{};celltypetMyAnotherCellType{callsTaskcTask;};celltMyAnotherCellTypeMyAnotherCell{cTask=MyTask.eTask;};
```
tMyAnotherCellType.c
```
// フラグのセットFLGPTNsetPattern;cEventflag_set(setPattern);// フラグの現在状態の参照T_RFLG*pk_eventflagStatus;cEventflag_refer(pk_eventflagStatus);
```

なお、非タスクコンテキスト内では、`eEventflag` の代わりに
`eiEventflag` を使用する必要があります。

## リファレンス

### セルタイプ
*celltype*`tEventflag`
イベントフラグの生成、制御及び状態の取得を行うコンポーネントです。

本コンポーネントは `CRE_FLG` 静的API [NGKI1558] によりイベントフラグの生成を行います。静的APIの引数の値には、一部を除き属性値が用いられます。
*attr *ID` id`=C_EXP("FLGID_$id$");
イベントフラグのID番号の識別子 (詳しくは カーネルオブジェクトのID番号 を参照) を `C_EXP` で囲んで指定します (省略可能)。
*attr *ATR` attribute`=C_EXP("TA_NULL");
イベントフラグ属性 [NGKI1550] を `C_EXP` で囲んで指定します (省略可能)。
`TA_NULL`
デフォルト値（FIFO待ち）。
`TA_TPRI`
待ち行列をタスクの優先度順にする。
`TA_WMUL`
複数のタスクが待つのを許す。
`TA_CLR`
タスクの待ち解除時にイベントフラグをクリアする。
*attr *FLGPTN` flagPattern`
イベントフラグのビットパターン（符号なし整数）。
*attr *ACPTN` accessPattern`[4]
todo
*entry*sEventflag` eEventflag`
イベントフラグの制御及び状態の取得を行うための受け口です。
*entry*siEventflag` eiEventflag`
イベントフラグの制御を行うための受け口です (非タスクコンテキスト用)。

### シグニチャ
*signature*`sEventflag`
イベントフラグの制御、及び状態の取得を行うためのシグニチャです。
ER` set`(*[in]*FLGPTN* setPattern*)
イベントフラグに対して、setPatternで指定されるビットをセットします。サービスコール呼び出し前のビットパターンとsetPatternの値のビット毎の論理和に更新します。

この関数は `set_flg` サービスコール [NGKI3534] のラッパーです。
Param setPattern
セットするビットパターン。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERclear([in]FLGPTNclearPattern);`
イベントフラグに対して、clearPatternが対応するビットが０になっているビットをクリアします。

この関数は `clr_flg` サービスコール [NGKI1611] のラッパーです。
Param clearPattern
クリアするビットパターン（ビット毎の反転値）。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERwait([in]FLGPTNwaitPattern,[in]MODEwaitFlagMode,[out]FLGPTN*p_flagPattern);`
イベントフラグのビットパターンがwaitPatternとWaitFlagModeで指定される待ち解除条件満たすのを待ちます。

この関数は `wai_flg` サービスコール [NGKI1618] のラッパーです。
Param waitPattern
待ちビットパターン。
Param waitFlagMode
待ちモード。
Param p_flagPattern
待ち解除時のビットパターンを入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERwaitPolling([in]FLGPTNwaitPattern,[in]MODEwaitFlagMode,[out]FLGPTN*p_flagPattern);`
イベントフラグのビットパターンがwaitPatternとWaitFlagModeで指定される待ち解除条件満たすのを待ちます（ポーリング）。

この関数は `pol_flg` サービスコール [NGKI1619] のラッパーです。
Param waitPattern
待ちビットパターン。
Param waitFlagMode
待ちモード。
Param p_flagPattern
待ち解除時のビットパターンを入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERwaitTimeout([in]FLGPTNwaitPattern,[in]MODEwaitFlagMode,[out]FLGPTN*p_flagPattern,[in]TMOtimeout);`
イベントフラグのビットパターンがwaitPatternとWaitFlagModeで指定される待ち解除条件満たすのを待ちます（タイムアウトあり）。

この関数は `twai_flg` サービスコール [NGKI1620] のラッパーです。
Param waitPattern
待ちビットパターン。
Param waitFlagMode
待ちモード。
Param p_flagPattern
待ち解除時のビットパターンを入れるメモリ領域へのポインタ。
Param timeout
タイムアウト指定。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERinitialize(void);`
対象イベントフラグを再初期化します。対象イベントフラグのビットパターンは初期ビットパターンに初期化されます。

この関数は `ini_flg` サービスコール [NGKI1639] のラッパーです。
Return
正常終了 (`E_OK`) またはエラーコード。
`ERrefer([out]T_RFLG*pk_eventflagStatus);`
イベントフラグの現在状態を参照します。

この関数は `ref_flg` サービスコール [NGKI1648] のラッパーです。
Param pk_eventflagStatus
イベントフラグの現在状態を入れるメモリ領域へのポインタ。
Return
正常終了 (`E_OK`) またはエラーコード。
*signature*`siEventflag`
イベントフラグの制御を行うためのシグニチャです (非タスクコンテキスト用)。
`ERset([in]FLGPTNsetPattern);`
イベントフラグに対して、setPatternで指定されるビットをセットします。サービスコール呼び出し前のビットパターンとsetPatternの値のビット毎の論理和に更新します。

この関数は `set_flg` サービスコール [NGKI3534] のラッパーです。
Param setPattern
セットするビットパターン。
Return
正常終了 (`E_OK`) またはエラーコード。

## 実装の詳細

### イベントフラグの生成

`tEventflag` によるイベントフラグの生成は、以下に示しているようなファクトリ記述により静的 API 記述を生成することで実現されています。
kernel.cdl (抜粋)
```
factory{write("tecsgen.cfg","CRE_FLG(%s, { %s, %s});",id,attribute,flagPattern);};
```

最初の `MyEventflag` を用いた例の場合、以下のような静的API記述が生成されます。
tecsgen.cfg
```
CRE_FLG(FLGID_tEventflag_MyEventflag,{TA_NULL,0});
```

`tEventflag` が持つ属性は、 `id` を除き実行時にはすべて未使用であるため、`[omit]` 指定を行うことでこれらの属性値へのメモリ割り当てが行われないようにしています。

### サービスコール

`eEventflag` 及び `eiEventflag` に対する呼出しは、以下に示すような受け口関数により TOPPERS/ASP3 カーネルのサービスコールへの呼出しに変換されます。
tEventflag_inline.h
```
InlineEReEventflag_set(CELLIDXidx){CELLCB*p_cellcb=GET_CELLCB(idx);return(set_flg(ATTR_id,FLGPTNsetptn));}
```

---

Source: [[index]]
