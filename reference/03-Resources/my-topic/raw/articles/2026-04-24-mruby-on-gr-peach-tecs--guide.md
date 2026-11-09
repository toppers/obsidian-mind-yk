---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-gr-peach+tecs\guide.html
title: アプリケーションの開発方法
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: アプリケーションの開発方法"
---

# アプリケーションの開発方法

# アプリケーションの開発方法

ここでは， mruby アプリケーションの開発方法について説明します．
開発環境やビルド方法については，ビルド方法 を参照してください．

## サンプルアプリケーション

asp3/workspace/mruby_app に mruby のサンプルプログラムが入っています.
基本的に，このディレクトリでプログラムを書いていきます．

デフォルトは，*led_sample.rb* となっています．

## アプリケーションファイルの指定

mruby on GR-PEACH+TECS では，アプリケーションファイルの指定をCDLというファイルによってコンフィグレーションを行います．
TECS CDL については，TECS コンポーネント記述言語 (TECS CDL) を参照してください．

asp3/workspace/build の VM1.cdl にてアプリケーションを指定しています．
アプリケーションを変更する場合は，`$(MRUBY_APP_DIR)/led_sample.rb` の行を，任意のアプリケーション名に修正し,　**make** を実行してください．

例えば， `$(MRUBY_APP_DIR)/rtos_sample.rb` とすると，*rtos_sample.rb* が実行されます．
VM1.cdl
```
import(<bridge.cdl>);cellnMruby::tMrubyMruby{mrubyFile="$(MRUBY_LIB_DIR)/RTOS.rb ""$(MRUBY_LIB_DIR)/LED.rb ""$(MRUBY_APP_DIR)/led_sample.rb";<---(アプリケーションの指定)cInit=VM_TECSInitializer.eInitialize;cSerialPort=SerialPort1.eSerialPort;};celltTaskMrubyTask1{cTaskBody=Mruby.eMrubyBody;attribute=C_EXP("TA_ACT");priority=10;stackSize=4096;};
```

---

Source: [[index]]
