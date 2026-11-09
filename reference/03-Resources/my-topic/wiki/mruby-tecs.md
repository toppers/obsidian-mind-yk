---
date: 2026-05-31
tags: [tecs, mruby, ruby, embedded]
type: concept
status: active
description: "mrubyをTECSコンポーネントと連携させる仕組み。ev3rt・GR-PEACH向けの実装が存在する。"
---

# mruby+TECS

mruby+TECSは、軽量Rubyのmrubyと[[tecs-overview]]を連携させる仕組みです。

## 実装

- [[mruby-ev3rt-tecs]] — mruby on ev3rt+tecs（LEGO Mindstorms EV3向け）
- [[mruby-gr-peach-tecs]] — mruby on GR-PEACH+tecs（GR-PEACH向け）

## [[tecs-plugin]]

- [[plugin-mruby-bridge]] — MrubyBridgePlugin
- [[plugin-mruby-info-bridge]] — MrubyInfoBridgePlugin

## See Also

- [[tecs-overview]]
- [[asp3-tecs]]

## Counter-Arguments and Gaps

特になし。
