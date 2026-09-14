---
date: 2026-06-18
description: "TECSにおけるコールバックの書き方 — [callback]シグニチャ、逆結合（<=）のCDL構文とTCD表記（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# コールバックの書き方を教えて

TECSのコールバックは `[callback]` 指定子を持つシグニチャと逆結合（`<=`）を使います。通常の結合とは呼び口と受け口の方向が逆になります。

## 1. シグニチャに [callback] を付ける

```cdl
[callback]
signature sCallback {
    void notify([in] int32_t event);
};
```

## 2. セルタイプに呼び口（コールバック登録側）と受け口（コールバック受取側）を宣言

```cdl
// サービス提供側（コールバックを呼び出す側）
celltype tService {
    entry  sMyService eService;
    call   sCallback  cCb;      // コールバック呼び口
};

// 呼び元（コールバックを受け取る側）
celltype tClient {
    entry  sCallback  eCb;      // コールバック受け口
    call   sMyService cService;
};
```

## 3. 組上げ記述で逆結合（<=）を使う

```cdl
cell tService Service {
    cCb <= Client.eCb;         // 逆結合：サービスの呼び口 <= クライアントの受け口
};

cell tClient Client {
    cService = Service.eService;
};
```

## TCD表記

逆結合は受け口から呼び口へ向かう矢印（`<====`）で表します：

```
+------------------+  sCallback  +------------------+
| tClient          |             | tService         |
|          eCb <|===<============|= cCb             |
|   cService ----->|------------>|> eService        |
+------------------+             +------------------+
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-シグニチャとは何か]] | [[TECS仕様書(html版)-結合とは何か]] | [[TECS仕様書(html版)-目次]]
