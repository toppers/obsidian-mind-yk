---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\tecs\IMPref_allocator.html
title: セルタイプコードでのアロケータ
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: セルタイプコードでのアロケータ"
---

# セルタイプコードでのアロケータ

# セルタイプコードでのアロケータ

シグニチャの関数の引数の基本指定子として send または receive を指定すると、引数としてアロケータによりアロケートされたメモリ領域のアドレスが渡されます。
渡されたメモリ領域は、受け取った側で解放します。

send 指定された引数の場合、呼び元でアロケートし、呼び先でデアロケートします。
receive 指定された引数の場合、呼び先でアロケートし、呼び元でデアロケートします。
アロケート、デアロケート操作は、アロケータ呼び口を通して行います。

## アロケータ呼び口

TECS では、メモリアロケータをセルとして実装しますが、アロケータセルの受け口に結合する呼び口が必要となります。
この呼び口のことをアロケータ呼び口と呼びます。
アロケータ呼び口は TECS CDL に明示的に記述しません。TECS ジェネレータにより生成されます。

アロケータ呼び口には、以下の名前が与えられます。

(アロケータ呼び口名)  = (呼び口名または受け口名) + '_' + (関数名) + '_' + (引数名)

## アロケータ使用の具体例

以下に、アロケータを使用する例を示します。

TECS CDL のコード例には、呼び先のセルタイプおよびセル、呼び元のセルタイプおよびセルが実装されているとします。
ジェネレータによって呼び先および呼び元の双方に、アロケータ呼び口およびその結合が自動的に挿入されます。

【TECS CDL 記述例】

```
signaturesSendRecv{/* この関数名に send, receive を使ってしまうとアロケータ指定できない */ERsnd([send(sAlloc),size_is(sz)]int8*buf,[in]int32sz);ERrcv([receive(sAllocTMO),size_is(*sz)]int8**buf,[out]int32*sz);};celltypetTestComponent{entrysSendRecveS;};// 受け口側で、send/receive 指定された引数ごとにアロケータを指定[allocator(eS.snd.buf=alloc.eA,eS.rcv.buf=alloc.eA)]celltTestComponentcomp{};celltypetTestClient{callsSendRecvcS;};// 呼び口側では、アロケータを指定しないcelltTestClientcl{cS=comp.eS;};
```

【アロケータ呼び口が挿入されたコード（TECS ジェネレータにより内部生成された状態）】

以下のコードは、内部状態を説明するためのものであって、以下のような TECS CDL コードを記述するものではありません。

```
celltypetTestComponent{entrysSendRecveS;/* 自動生成されたアロケータ呼び口 */callsAlloccS_snd_buf;<<<自動生成された呼び口callsAlloccS_rcv_buf;<<<自動生成された呼び口};[allocator(eS.snd.buf=alloc.eA,eS.rcv.buf=alloc.eA)]celltTestComponentcomp{/* 自動生成されたアロケータ呼び口の結合 */eS_snd_buf=alloc.eA;<<<自動生成された結合eS_rcv_buf=alloc.eA;<<<自動生成された結合};celltypetTestClient{callsSendRecvcS;/* 自動生成されたアロケータ呼び口 */callsAlloccS_snd_buf;<<<自動生成された呼び口callsAlloccS_rcv_buf;<<<自動生成された呼び口};celltTestClientcl{cS=comp.eS;/* 自動生成されたアロケータ呼び口の結合 */cS_snd_buf=alloc.eA;<<<自動生成された結合cS_rcv_buf=alloc.eA;<<<自動生成された結合};
```

セルタイプ tTestClient の呼び口 cS の関数の send, receive 指定された引数に対して、以下のようなアロケータ呼び口関数が、生成されます。
アロケート関数、デアロケート関数の両方が使用できますが、send 指定された引数の場合、通常、呼び元で使用する必要があるのは、アロケート関数です。
rceive 指定された引数の場合は、デアロケート関数です。

```
// allocator port for call port: cS func: send param: bufERcS_snd_buf_alloc(int32_tsize,void**p);ERcS_snd_buf_dealloc(constvoid*p);// allocator port for call port: cS func: receive param: bufERcS_rcv_buf_alloc(int32_tsize,void**p);ERcS_rcv_buf_dealloc(constvoid*p);// allocator port for call port: cA func: send param: bufERcA_snd_buf_alloc(subscript,int32_tsize,void**p);ERcA_snd_buf_dealloc(subscript,constvoid*p);// allocator port for call port: cA func: receive param: bufERcA_rcv_buf_alloc(subscript,int32_tsize,void**p);ERcA_rcv_buf_dealloc(subscript,constvoid*p);
```

セルタイプ tTestComponent の受け口 eS の関数の send, receive 指定された引数に対しても、同様なアロケータ呼び口関数が、生成されます。

【未決定事項】アロケータを一々使い分けるのは、誤りのもとである。まとめる手段が必要。

## アロケータの例

アロケータセルの例を以下に示します。

【TECS CDL 記述例】

```
signaturesAlloc{ERalloc([in]size_tlen,[out]void*p);ERdealloc([in]void*p);};celltypetAlloc{entrysAlloceA;};cellalloc{};
```

## リレーアロケータ

リレーアロケータの TECS CDL 記述例を示します。

【TECS CDL 記述例】

```
signaturesSendRecv{/* この関数名に send, receive を使ってしまうとアロケータ指定できない */ERsnd([send(sAlloc),size_is(sz)]int8_t*buf,[in]int32_tsz);ERrcv([receive(sAlloc),size_is(*sz)]int8_t**buf,[out]int32_t*sz);};celltypetThroughComponent{[allocator(/* 受け口から呼び口へリレー */snd.buf<=cSR.snd.buf,/* cSR:前方参照可能 */rcv.buf<=cSR.rcv.buf)]entrysSendRecveS;callsSendRecvcSR;};/* セルの定義で、受け口の send/receive 指定された引数のアロケータ指定不要 */celltThroughComponentcomp{cSR=TargetCell.eS;/* TargetCell でアロケータ指定が必要 */};
```

リレーアロケータの場合も、上述のアロケータの例と同様に、アロケータ呼び口と結合が生成されます。
tThroughComponent のセルタイプコードでは、以下のアロケータ呼び口関数が生成されます。
ただし、受け取ったものをそのまま渡すため、これらの呼び口関数は、実際には使用する必要はありません。
もし、受け取ったものをそのまま渡すのではなく、再アロケート(reallc) するような場合には、これらの呼び口を用いることになります。
（この例では realloc は含まれません）

```
// allocator port for call port: eA func: snd param: bufEReA_snd_buf_alloc(subscript,int32_tsize,void**p);EReA_snd_buf_dealloc(subscript,constvoid*p);// allocator port for call port: eA func: rcv param: bufEReA_rcv_buf_alloc(subscript,int32_tsize,void**p);EReA_rcv_buf_dealloc(subscript,constvoid*p);// allocator port for call port: eS func: snd param: bufEReS_snd_buf_alloc(int32_tsize,void**p);EReS_snd_buf_dealloc(constvoid*p);// allocator port for call port: eS func: rcv param: bufEReS_rcv_buf_alloc(int32_tsize,void**p);EReS_rcv_buf_dealloc(constvoid*p);// allocator port for call port: cSR func: snd param: bufERcSR_snd_buf_alloc(int32_tsize,void**p);ERcSR_snd_buf_dealloc(constvoid*p);// allocator port for call port: cSR func: rcv param: bufERcSR_rcv_buf_alloc(int32_tsize,void**p);ERcSR_rcv_buf_dealloc(constvoid*p);
```

---

Source: [[index]]
