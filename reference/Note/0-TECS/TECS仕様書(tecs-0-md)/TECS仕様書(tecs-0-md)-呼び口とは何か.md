---
date: 2026-06-18
description: "TECSウィキ（tecs-0-md）クエリ回答 — 呼び口（call port）とは何か。セルが他のセルの機能を利用するための口。同じシグニチャを持つ受け口のみと結合できる"
tags:
  - reference
  - tecs
  - wiki-query
---

# TECS仕様書(tecs-0-md)-呼び口とは何か

呼び口（call port）は、**セルが他のセルの機能を利用するための口**である。シグニチャに対応付けられ、呼び口名を持つ。同じシグニチャを持つ受け口のみと結合できる。

---

## 定義

- セルが他のセル（自セルも可）の機能を利用するための口
- シグニチャに対応付けられ、呼び口名を持つ
- 通常は必ずいずれかの受け口と結合しなければならない
- `optional` 指定で未結合のままにできる（ただし実行時に結合確認が必要）
- コンポーネント図では**線分**（セル外側に伸びる）で表す

## 呼び口関数

呼び口に対応するシグニチャの関数で、セルタイプコードから呼び出し可能な関数。tecsgenが生成したマクロ経由で使用する。

```c
ER ret = cCall_func(arg1);       // 非シングルトン
ER ret = cCall_func(idx, arg1);  // 受け口関数内（idx引き継ぎ）
```

## CDLでの記述例

```
celltype tA {
    call  tMySignature  cMyCall;    // 呼び口: シグニチャ tMySignature
};
```

## 合流・分流の制約

- **合流（複数の呼び口→1つの受け口）**: 可能
- **分流（1つの呼び口→複数の受け口）**: 不可（呼び口配列で代替）

---

**Sources used:**
- [呼び口・受け口（call/entry port）](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/concepts/tecs-port.md) (confidence: high) — 呼び口の定義・optional指定・合流分流
- [TECSコンポーネント実装](C:/Users/ykomi/wiki/topics/tecs-0-md/wiki/topics/tecs-component-implementation.md) (confidence: high) — 呼び口関数の呼び出し

**Knowledge gaps:**
- なし
