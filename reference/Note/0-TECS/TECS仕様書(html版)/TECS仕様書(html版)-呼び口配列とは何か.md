---
date: 2026-06-18
description: "TECSにおける呼び口配列（Call Array）の定義 — 複数の受け口に個別に結合できる配列型呼び口、CDL構文と使用場面（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 呼び口配列とは何か

**呼び口配列 (Call Array)** は、同じシグニチャを持つ呼び口を**配列**として宣言したものです。各要素を異なる受け口に個別に結合できます。

## 特性

- 各添数（インデックス）ごとに異なる受け口に結合できる
- TCD図では呼び口名に添数を添えて表記（例: `cArr[0]`, `cArr[1]`）
- Cコードでは `N_CALL_ARRAY(cArr)` マクロで配列の大きさを取得できる
- 動的サイズ（`[]`）と固定サイズ（`[n]`）の両方を宣言できる

## CDLでの宣言

```cdl
celltype tMyCell {
    call sMySignature cArr[];        // 動的サイズ（組上げ記述で決まる）
    call[3] sMySignature cFixed;     // 固定サイズ（3要素）
};
```

## 組上げ記述（結合）

```cdl
cell tMyCell MyCell {
    cArr[0] = Cell0.ePort;
    cArr[1] = Cell1.ePort;
    cArr[2] = Cell2.ePort;
};
```

## Cコードでの使用

```c
// 呼び口配列のサイズを取得
int32_t n = N_CALL_ARRAY(cArr);

// 各要素を呼び出す
for (int i = 0; i < n; i++) {
    cArr_funcName(i, arg);   // 添数を渡して特定要素を呼び出す
}
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)
- tecs_html wiki: [実装モデル](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-implementation-model.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-呼び口とは何か]] | [[TECS仕様書(html版)-呼び口配列の書き方を教えて]] | [[TECS仕様書(html版)-受け口配列とは何か]] | [[TECS仕様書(html版)-目次]]
