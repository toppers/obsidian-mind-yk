---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\tlsf+tecs\index.html
title: TLSF+TECS
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: TLSF+TECS"
---

# TLSF+TECS

# TLSF+TECS

TLSF+TECSは，「TLSF」をTECSでコンポーネント化した動的メモリアロケータです．

TLSFコンポーネントは，内部変数として独自のヒープ領域を保持しているため，タスク毎に独立してメモリ管理を行えます．

ただし，複数のタスクで同時に同じTLSFコンポーネントを使用する場合は，排他制御が必要です．

使用例:

mrubyのマルチVM機能 ( mruby-on-ev3rt+tecs-package-beta2.0.1 ~)

リンク:

TLSF (Two-Level Segregate Fit) -Memory Allocator for Real-Time-

課題

to be filled in

目次:

---

Source: [[index]]
