---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\button.html
title: ボタン - Battery
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: ボタン - Battery"
---

# ボタン - Battery

# ボタン - `Battery`

ボタンに関するAPIです．

## 特異メソッド一覧

- 
Button[button].pressed?

## シンボル

- 
**button**

ボタンを表わすシンボル

| 
シンボル
 | 
| 
:left
 | 
左ボタン
 | 
| 
:right
 | 
右ボタン
 | 
| 
:up
 | 
上ボタン
 | 
| 
:down
 | 
下ボタン
 | 
| 
:enter
 | 
中央ボタン
 | 
| 
:back
 | 
戻るボタン
 | 
## 特異メソッド

### Button[ button ].pressed? -> bool

ボタンの押下状態を取得する．
不正のボタン番号を指定した場合，常に `false` を返す （エラーログが出力される）．
**引数**
なし
**戻り値**
`true`  押されている状態

`false` 押されていない状態
button_sample.rb
```

```

---

Source: [[index]]
