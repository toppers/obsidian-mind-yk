---
date: 2026-05-31
tags: [tecs, plugin, c-language]
type: concept
status: active
description: "C言語から[[tecs-overview]]コンポーネントを呼び出すためのブリッジプラグイン。"
---

# C2TECSBridgePlugin

C2TECSBridgePluginは、C言語コードから[[tecs-cell]]を呼び出すためのブリッジプラグインです。

対になるプラグイン `TECS2CBridgePlugin`（TECS受け口 → C関数呼び出し、逆方向）と併せて、詳細仕様は [[CInterfaceBridgePlugin(説明用にAIが作成)|C2TECSBridgePlugin・TECS2CBridgePlugin 仕様書]]（TECS外部仕様書シリーズ、2026-08-14完成）参照。

## See Also

- [[tecs-plugin]]
- [[plugin-mruby-bridge]] — 実運用例（`MrubyBridge-ASP3/test.cdl`）が接続する mruby ブリッジ本体

## Counter-Arguments and Gaps

詳細は [[CInterfaceBridgePlugin(説明用にAIが作成)]] へ移行済み。
