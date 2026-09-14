---
date: 2026-06-18
description: "TECSにおける呼び口配列の書き方 — CDL宣言構文（動的・固定サイズ）、組上げ記述、Cコードでの呼び出しパターン（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 呼び口配列の書き方を教えて

呼び口配列は、同じシグニチャを持つ呼び口を配列として宣言します。

## CDLでの宣言

```cdl
celltype tMyCell {
    call sMySignature cArr[];       // 動的サイズ（組上げ記述の件数で決まる）
    call[3] sMySignature cFixed;    // 固定サイズ（3要素）
};
```

## 組上げ記述（結合）

各添数を異なる受け口に結合できます：

```cdl
cell tMyCell MyCell {
    cArr[0] = Cell0.ePort;
    cArr[1] = Cell1.ePort;
    cArr[2] = Cell2.ePort;
};
```

## TCD表記

呼び口名に添数を添えて表記します：

```
+------------------+
| tMyCell          |
|   cArr[0] ------>|----> |> ePort (Cell0)
|   cArr[1] ------>|----> |> ePort (Cell1)
|   cArr[2] ------>|----> |> ePort (Cell2)
+------------------+
```

## Cコードでの使用

```c
// 配列サイズの取得
int32_t n = N_CALL_ARRAY(cArr);

// 全要素を順に呼び出す
for (int i = 0; i < n; i++) {
    cArr_funcName(i, arg);    // 第1引数が添数
}

// 特定要素の呼び出し
cArr_funcName(0, arg);
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)
- tecs_html wiki: [実装モデル](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-implementation-model.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-呼び口配列とは何か]] | [[TECS仕様書(html版)-受け口配列の書き方を教えて]] | [[TECS仕様書(html版)-目次]]
