---
date: 2026-05-31
tags: [tecs, interface]
type: concept
status: active
description: "[[tecs-overview]]におけるインタフェース定義。呼び口・受け口の型を定義し、関数の集合として表現される。"
---

# シグニチャ (Signature)

シグニチャは、TECSコンポーネントのインタフェースを定義する記述単位です。

## 概要

- 関数の集合として定義
- [[tecs-port]]（呼び口・受け口）の型として使用
- [[tecs-celltype]] に含まれる

## 構文例

```cdl
signature sTask {
    ER activate(void);
    ER_UINT cancelActivate(void);
    ER terminate(void);
};
```

## See Also

- [[tecs-celltype]]
- [[tecs-port]]
- [[tecs-cdl]]

## Counter-Arguments and Gaps

特になし。
