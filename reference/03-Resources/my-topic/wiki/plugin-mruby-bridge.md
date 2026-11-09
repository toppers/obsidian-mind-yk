---
date: 2026-05-31
tags: [tecs, plugin, mruby]
type: concept
status: active
description: "mrubyと[[tecs-overview]]コンポーネントをブリッジするプラグイン。"
---

# MrubyBridgePlugin

MrubyBridgePluginは、[[mruby-tecs]]とTECSコンポーネントを接続するプラグインです。

## See Also

- [[tecs-plugin]]
- [[plugin-mruby-info-bridge]]
- [[mruby-tecs]]

## Counter-Arguments and Gaps

詳細リファレンスは [[work/active/tecsgen-plugins/MrubyBridgePlugin|MrubyBridgePlugin 仕様書]]（TECS外部仕様書シリーズ、2026-08-14）に作成済み——実体は5ファイル（`MrubyBridgePlugin`・`MrubyBridgeSignaturePlugin`・`MrubyBridgeCelltypePlugin`・`MrubyBridgeCompositePlugin`・`MrubyBridgeCellPlugin`）で、CDL上の付与位置によって実装クラスが自動切り替わる `MultiPlugin` ディスパッチ機構の実例。作者自身の設計メモ `tecs/mruby/mrubyBridge.txt` を一次資料として型対応表・CDL記述例を採録した。
