---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第3章（モデル設計）— TECSCDE-TS内部仕様を基本とし、複合セルタイプは3B章で拡張。rendererプロセスで動作。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 3 of 11。

## 3. モデル設計

`Cell`・`Port`（`CPort`/`EPort`）・`Join`・`Region`・`RegionTree`・`TecscdeDocument`のクラス設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様第3章]]と**複合セルタイプを除き同一**。第2章2.3節で述べたとおり本モジュール（C）はrendererプロセスで動作し、Node.js APIへの依存を一切持たない——これはブラウザ版（TECSCDE-TS内部仕様）から変更する理由がないことの裏付けでもある。

複合セルタイプのモデル、未対応構文フラグ、外側セルへの適用は[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B章]]で定める。

その他の詳細は[[TECSCDE-TS内部仕様]]第3章を参照。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様 第3章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（本モジュールのプロセス配置根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
