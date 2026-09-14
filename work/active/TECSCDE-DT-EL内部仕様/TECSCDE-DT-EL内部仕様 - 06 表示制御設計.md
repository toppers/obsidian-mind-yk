---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第6章（表示制御設計）— TECSCDE-TS内部仕様と同一、変更なし。rendererプロセスで動作。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 6 of 11。

## 6. 表示制御設計

`ViewState`・`DisplayFilters`のクラス設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様第6章]]と**完全に同一、変更なし**。ズーム・パン・グリッド・フィルタ・検索の状態はUIに閉じた表示状態であり、Electronのプロセス境界とは無関係に本モジュール（F）はrendererプロセスで完結する。`TecscdeDocument`（第3章）とは型として分離し、`.cde`形式に含めない方針も変更なし。

詳細は[[TECSCDE-TS内部仕様]]第6章を参照。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様 第6章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
