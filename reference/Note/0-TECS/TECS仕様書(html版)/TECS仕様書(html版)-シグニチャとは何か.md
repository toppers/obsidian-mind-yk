---
date: 2026-06-18
description: "TECSにおけるシグニチャ（Signature）の定義 — コンポーネント間インタフェース、関数頭部の集合（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# シグニチャとは何か

**シグニチャ (Signature)** は、コンポーネント間インタフェースの**関数頭部の集合**です。受け口と呼び口が何の関数を提供/利用するかを定義します。C言語のヘッダファイルに近い概念です。

## 特性

- 関数名・引数・戻り値の型を定義する（実装は含まない）
- 受け口はシグニチャを実装し、呼び口はシグニチャを通じて呼び出す
- 命名慣習: `s` 接頭辞（例: `sTask`, `sInputOutput`）

## CDLでの宣言

```cdl
[context(task)]
signature sMySignature {
    ER  funcA([in] int32_t x, [out] int32_t *p);
    ER  funcB([in, size_is(n)] int8_t *buf, [in] int32_t n);
    void funcC(void);
};

[callback]
signature sCallback {
    void notify([in] int32_t event);
};
```

## 引数指定子

| 指定子 | 意味 |
|--------|------|
| `[in]` | 入力引数 |
| `[out]` | 出力引数（ポインタ） |
| `[inout]` | 入出力引数 |
| `[size_is(expr)]` | 配列のバイトサイズ |
| `[count_is(expr)]` | 配列の要素数 |
| `[string]` | ヌル終端文字列 |

## シグニチャ指定子

| 指定子 | 意味 |
|--------|------|
| `[callback]` | コールバック用（逆結合 `<=` が可能） |
| `[context(ctx)]` | 呼び出しコンテキスト（task/non-task/any） |
| `[deviate]` | 逸脱（tecsgenの検査をスキップ） |
| `[oneway]` | 一方向（戻り値なし、ブロッキングなし） |

## 出典

- tecs_html wiki: [TECS概要](C:/Users/ykomi/wiki/topics/tecs_html/wiki/concepts/tecs-overview.md) (confidence: high)
- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-受け口とは何か]] | [[TECS仕様書(html版)-呼び口とは何か]] | [[TECS仕様書(html版)-コンテキストとは何か]] | [[TECS仕様書(html版)-コールバックの書き方を教えて]] | [[TECS仕様書(html版)-目次]]
