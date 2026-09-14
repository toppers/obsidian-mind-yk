---
date: 2026-06-18
description: "TECSにおけるRPC（リモートプロシージャコール）の書き方 — リージョン間スループラグイン[through()]を使った結合のCDL構文（html版）"
tags:
  - reference
  - tecs
  - tecs-仕様書
source: tecs_html wiki
---

# RPCの書き方を教えて

TECSのRPC（リモートプロシージャコール）は、異なるリージョン（保護ドメイン・アドレス空間）間の呼び口→受け口結合を**スループラグイン** (`[through(Plugin)]`) を経由して実現します。

## スループラグインを使った結合

```cdl
// 組上げ記述でスルー結合を使用
cell tClient Client {
    [through(RPCPlugin, "option")]
    cServer = ServerCell.eService;
};
```

## リージョンの定義

```cdl
[linkunit]
region rClient {
    cell tClient Client {
        [through(RPCPlugin)]
        cService = rServer::ServerCell.eService;   // 別リージョンのセル参照
    };
};

[linkunit]
region rServer {
    cell tServer ServerCell {
        // サービス提供側
    };
};
```

## リージョン間スループラグイン

リージョン属性 `[in_through]` / `[out_through]` を使って、リージョン境界を越える結合にプラグインを自動適用することもできます：

```cdl
region rGuardedRegion {
    [in_through(GuardPlugin, )]
    [out_through()]
    region rInner {
        cell tGuarded GuardedCell {
            cSysLog = ServerSysLog.eSysLog;
        };
    };
};
```

## TCD表記

リージョン境界を越える結合は境界を示す線で区切り、スループラグインを経由する経路として示します：

```
[rClient]                 [through(RPC)]             [rServer]
| Client.cService |------//===================//---->|> eService (Server)
```

## 出典

- tecs_html wiki: [CDL言語リファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/cdl-reference.md) (confidence: high)
- tecs_html wiki: [TCDリファレンス](C:/Users/ykomi/wiki/topics/tecs_html/wiki/topics/tcd-reference.md) (confidence: high)

## 関連

[[TECS仕様書(html版)-結合とは何か]] | [[TECS仕様書(html版)-TECSコンポーネント図の書き方を教えて]] | [[TECS仕様書(html版)-目次]]
