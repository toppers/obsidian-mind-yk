---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\isr.html
title: 割込み管理 －tISR
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: 割込み管理 －tISR"
---

# 割込み管理 －tISR

# 割込み管理 －`tISR`

割込みサービスルーチン（割込み処理関数）を登録して、割込み発生時に呼び出す機能です。

課題

to be filled in

## 使用方法

### 割込みの生成

アプリケーション開発者は `tISR` セルタイプのセルを生成することにより、割込みを生成することができます。次の例では `MyISR` という名前の割込みセルを生成し、 `MyCell` の `eISRBody` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{entrysHandlerBodyeISRBody;};celltMyCellTypeMyCell{};celltISRMyISR{cBody=MyCell.eISRBody;category=2;priority=15;entryNumber=48;interruptsource="ENABLE";};
```
tMyCellType.c
```
voideISRBody_main(CELLIDXidx){}
```

## リファレンス

### セルタイプ
*celltype*`tISR`
割込みの生成を行うコンポーネントです。
*attr *char_t*` name`=C_EXP("$cell$")
割込みの名前を指定します。
指定しない場合、セルの名前が使用されます。
*attr *uint32_t` category`
割込みのカテゴリを指定します。
`1`
カテゴリ1ISR(C11SR）
OSのコードを経由せずに高速に呼び出される
割込み制御関連以外のOSのシステムサービスを呼び出せない
C11SRは，C21SRよりも割込み優先度が高い
`2`
カテゴリ2ISR(C21SR）
OSのコードを経由して呼び出される
OSのサービスを呼び出せる
*attr *uint32_t` priority`
割込みの優先度を指定します。
*attr *uint32_t` entryNumber`
割込み番号を指定します。
*attr *char_t*` interruptsource`
割込み要因の初期状態を指定します。
SC3、SC4のみで使用可能です。
categoryに1を指定した場合に、本パラメータにDISABLEを指定した場合、ジェネレータはエラーを検出します。
SC3、SC4で本パラメータを省略した場合、ジェネレータはエラーを検出します。
`ENABLE`
有効
`DISABLE`
無効
*attr *char_t*` resource`
割込みが獲得するリソースを選択します（複数選択可能）。

### シグニチャ
*signature*`sHandlerBody`
割込みハンドラを呼び出すためのシグニチャです。
void` main`(void)

---

Source: [[index]]
