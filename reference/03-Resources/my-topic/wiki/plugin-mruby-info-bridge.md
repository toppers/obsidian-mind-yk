---
date: 2026-05-31
tags: [tecs, plugin, mruby]
type: concept
status: active
description: "mrubyの実行時情報をTECSと連携させるプラグイン。V1.7.0で追加。"
---

# MrubyInfoBridgePlugin

MrubyInfoBridgePluginは、mrubyの実行時情報を[[tecs-overview]]と連携させるプラグインです。V1.7.0で追加されました。

## See Also

- [[tecs-plugin]]
- [[plugin-mruby-bridge]]

## Counter-Arguments and Gaps

詳細リファレンスは [[work/active/tecsgen-plugins/MrubyInfoBridgePlugin|MrubyInfoBridgePlugin 仕様書]]（TECS外部仕様書シリーズ、2026-08-14）に作成済み——実体は3ファイル。[[plugin-mruby-bridge]] との決定的な違いは、対象セルを CDL 記述時に静的結合するか、TECSInfo API 経由で実行時に文字列パスから検索・検証してバインドするかにある。
