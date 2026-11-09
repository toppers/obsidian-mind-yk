---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\mruby-on-ev3rt+tecs\sharedmemory.html
title: 共有変数 - SharedMemory
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: 共有変数 - SharedMemory"
---

# 共有変数 - SharedMemory

# 共有変数 - `SharedMemory`

各VM間で共有変数を扱うAPIです．

## インスタンスメソッド一覧

- 
putVal　(index, val)

- 
getVal　(index)

## インスタンスメソッド

### putVal ( index, val ) -> nil

共有変数に値を入力する
**引数**
`index`  共有変数のインデックス

`val`   　値
**戻り値**
nil

**a[index] = val でも可**

### getVal ( index ) -> Fixnum

共有変数の値を出力する
**引数**
`index`  共有変数のインデックス
**戻り値**
共有変数の値

**b = a[index] でも可**
sharedmemory_sample.rb
```

```

---

Source: [[index]]
