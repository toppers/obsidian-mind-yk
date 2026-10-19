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

### 3.1 TECS CDL組込型の解析

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.1節]]に従い、署名の関数の戻り値・引数とCDL内の`typedef`に現れるTECS CDL組込型を、Cヘッダの定義に依存せず解析する。対象は`void`、`bool_t`、`char_t`、`schar_t`、`uchar_t`、`int8_t`、`int16_t`、`int32_t`、`int64_t`、`int128_t`、`uint8_t`、`uint16_t`、`uint32_t`、`uint64_t`、`uint128_t`、`float32_t`、`double64_t`の17種類とする。

`cdl/signature-types.ts`はこれらを`CType`の`primitive`として生成し、型名を`primitive.name`に保持する。幅や符号の異なる型を別の型として扱い、ヘッダ由来の`typedef`がなくても`CTypeRegistry`で解決できるようにする。`defined`（未解決の型名参照）へ変換して`W-C-TYPE-UNRESOLVED`を出してはならない。

`int_t`、`uint_t`、`long_t`、`ulong_t`、`short_t`、`ushort_t`は組込型に含めない。これらはCDL内の`typedef`または`import_C`の定義を用いて通常の型名として解決し、定義が見つからない場合にのみ未解決型として診断する。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 03 モデル設計|TECSCDE-TS内部仕様 第3章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（本モジュールのプロセス配置根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
