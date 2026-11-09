---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\rtos.html
title: RTOS機能 - RTOS
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: RTOS機能 - RTOS"
---

# RTOS機能 - RTOS

# RTOS機能 - `RTOS`

RTOS機能に関するAPIです．

## 特異メソッド一覧

- 
RTOS.delay( msec )

- 
RTOS.usec

- 
RTOS.msec

## 特異メソッド

### RTOS.delay ( msec ) -> nil

指定された時間遅延する （指定された時間後に実行が再開される）．
**引数**
msec  遅延時間 (ミリ秒)
**戻り値**
nil

### RTOS.usec -> Fixnum

性能評価用システム時刻の参照．
**引数**
なし
**戻り値**
性能評価用システム時刻の現在値 （マイクロ秒）

### RTOS.msec-> Fixnum

システム時刻の参照．
**引数**
なし
**戻り値**
システム時刻の現在値 （ミリ秒）
rtos_sample.rb
```

```

---

Source: [[index]]
