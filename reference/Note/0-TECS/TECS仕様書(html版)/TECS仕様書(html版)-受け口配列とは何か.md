---
date: 2026-06-18
description: "TECSにおける受け口配列（Entry Array）の定義 — 複数の受け口インスタンスを持つ配列型受け口、CDL構文と使用場面（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# 受け口配列とは何か

**受け口配列 (Entry Array)** は、同じシグニチャを持つ受け口を**配列**として宣言したものです。添数（インデックス）を使って個別の受け口にアクセスできます。

## 特性

- 複数の呼び口を個別に区別して受け取ることができる
- TCD図では受け口名に添数を添えて表記（例: `eArr[0]`, `eArr[1]`）
- コールバックの多対一実装などに使用される

## CDLでの宣言

```cdl
celltype tMyCell {
    entry sMySignature eArr[];   // 受け口配列（サイズ自動決定）
};
```

## TCD表記

```
+------------------+
| tCellB           |
|   eArr[0] <|     |
|   eArr[1] <|     |
+------------------+
```

## 呼び口配列との組み合わせ（コールバック）

受け口配列と呼び口配列の添数を対応付けることで、複数の呼び元に対するコールバックを実現できます：

```cdl
// 呼び元 tCaller の定義
celltype tCaller {
    entry sCallback eCb;       // 各セルごとのコールバック受け口
    call sService cSvc;        // サービス呼び口
};

// サービス側の定義
celltype tService {
    entry sService eArr[];     // 受け口配列
    call sCallback cCbArr[];   // コールバック呼び口配列
};
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-受け口とは何か]] | [[TECS仕様書(html版)-受け口配列の書き方を教えて]] | [[TECS仕様書(html版)-呼び口配列とは何か]] | [[TECS仕様書(html版)-目次]]
