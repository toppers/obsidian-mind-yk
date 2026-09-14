---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第8章（整合性チェックとメッセージ設計）— TECSCDE-TS内部仕様と同一、変更なし。rendererプロセスで動作し、mainプロセスのtecsgen実行結果もIPC経由の入力として受け取る。"
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

Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 8 of 11。

## 8. 整合性チェックとメッセージ設計

`Diagnostic`値クラス・`DiagnosticsCollector`クラスの基本設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様第8章]]を踏襲する。ただし[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|TECSCDE-DT外部仕様第9章]]に合わせ、診断の発生源を明示する。

```ts
type DiagnosticSource = 'tree-sitter' | 'input' | 'consistency' | 'tecsgen';
```

`Diagnostic`へ`source: DiagnosticSource`を追加する。`tree-sitter`は`ERROR`／`MISSING`ノードから生成するG-code相当の構文エラーだけを表し、S-code相当の意味エラーは生成しない。文言はCSTの文脈から構成するため、tecsgenのメッセージカタログとの完全一致を要件としない。`input`は非UTF-8入力と旧世代の`__location_information__`形式、`consistency`は図・参照解決の警告、`tecsgen`は第9章で取り込むtecsgen自身のG-code／S-codeと原文メッセージを表す。

本モジュール（H）はrendererプロセスで動作し、`DiagnosticsCollector.report()`はB（CDLパーサ、renderer内）だけでなく、**第9章の`TecsgenGateway.generate()`がIPC経由で受け取ったmainプロセスの実行結果**からも呼ばれる。発生源は区別して保持するが、表示先は同じ一覧・件数表示・ジャンプ機構へ集約する。

警告コード表・ジャンプ機構は[[TECSCDE-TS内部仕様]]第8章8.3・8.4節と同一。

参照先を解決できない場合は既存の`W-UNRESOLVED-REF-FILE`を用いる。`import_C`のCプリプロセッサが見つからない、または起動に失敗して内蔵C宣言解析へ切り替えた場合は`W-CPP-FALLBACK`を追加し、フォールバックしたことと`#include`／`#ifdef`を反映できない可能性を利用者へ提示する。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様 第8章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（本章への新しい診断発生源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
