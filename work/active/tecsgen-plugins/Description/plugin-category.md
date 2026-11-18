---
date: 2026-10-17
description: "TOPPERS各カーネル（JSP・ASP・ASP3・HRP・HRP2・HRP3・HRMP3・FMP・FMP3等）とTECSプラグイン指定子の対応分類表"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecsgen
  - plugin
verbatim: true
---
| TECS対応 | カーネル | 文｜指定子    | TECS対応   | カーネル       | 文｜指定子    | TECS対応   | カーネル        | 文｜指定子    |          |         |     |      |     |
| ------ | ---- | -------- | -------- | ---------- | -------- | -------- | ----------- | -------- | -------- | ------- | --- | ---- | --- |
|        | JSP  |          | o        | ASP        |          | o        | ASP3        | generate |          |         |     |      |     |
| o      | HRP  | domain   | generate | through    | o        | HRP2     | EV3RT(HRP2) | domain   | generate | through |     | HRP3 |     |
|        |      |          | o        | HRMP-      | domain   | class    | generate    |          | HRMP3    |         |     |      |     |
|        | FDMP |          | o        | FMP        | class    | generate |             | FMP3     |          |         |     |      |     |
|        |      |          |          |            |          |          |             |          |          |         |     |      |     |
|        |      |          |          | SSP        |          |          |             |          |          |         |     |      |     |
|        |      |          |          |            |          |          |             |          |          |         |     |      |     |
|        |      |          |          | PARX       |          |          |             |          |          |         |     |      |     |
|        | FI4  |          |          |            |          |          |             |          |          |         |     |      |     |
|        |      |          |          |            |          |          |             |          |          |         |     |      |     |
| o      | ATK1 | generate |          | ATK2       |          |          |             |          |          |         |     |      |     |
|        |      |          |          | A-RTEGEN   |          |          |             |          |          |         |     |      |     |
|        |      |          |          | A-COMSTACK |          |          |             |          |          |         |     |      |     |
|        |      |          |          | A-WDGSTACK |          |          |             |          |          |         |     |      |     |
|        |      |          |          | A-OSBENCH  |          |          |             |          |          |         |     |      |     |
|        |      |          |          | AKTSP      |          |          |             |          |          |         |     |      |     |
|        |      |          |          |            |          |          |             |          |          |         |     |      |     |
|        |      |          |          | 非カーネル      |          |          |             |          |          |         |     |      |     |
|        |      |          | o        | 繰り返し生成     | generate |          |             |          |          |         |     |      |     |
|        |      |          |          |            |          |          |             |          |          |         |     |      |     |
|        |      |          | o        | RPC        | generate | through  |             |          |          |         |     |      |     |
|        |      |          | o        | トレース       | through  |          |             |          |          |         |     |      |     |
|        |      |          | o        | mruby      | generate |          |             |          |          |         |     |      |     |
|        |      |          | o        | Cインタフェース   | generate |          |             |          |          |         |     |      |     |
|        |      |          | o        | C/C++IF生成  | generate |          |             |          |          |         |     |      |     |
|        |      |          |          |            |          |          |             |          |          |         |     |      |     |
|        |      |          | o        | データ連携      | generate |          |             |          |          |         |     |      |     |
|        |      |          | o        | TECSInfo   | generate |          |             |          |          |         |     |      |     |

## Related

- [[work/active/tecsgen-plugins/tecsgen-plugins|tecsgen-plugins]]
