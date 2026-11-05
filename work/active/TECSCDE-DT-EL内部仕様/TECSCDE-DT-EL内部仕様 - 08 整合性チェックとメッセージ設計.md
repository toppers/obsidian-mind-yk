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

`Diagnostic`へ`source: DiagnosticSource`を追加する。`tree-sitter`は`ERROR`／`MISSING`ノードから生成するG-code相当の構文エラーだけを表し、S-code相当の意味エラーは生成しない。文言はCSTの文脈から構成するため、tecsgenのメッセージカタログとの完全一致を要件としない。`input`は入力側の制約によるエラー用の発生源だが、非UTF-8入力（2026-10-21）と旧世代の`__location_information__`形式（2026-10-22。読み込んで無視する）がいずれもエラーでなくなったため、**現行実装は`input`の診断を生成しない**（第7章7.8節）、`consistency`は図・参照解決の警告、`tecsgen`は第9章で取り込むtecsgen自身のG-code／S-codeと原文メッセージを表す。

本モジュール（H）はrendererプロセスで動作し、`DiagnosticsCollector.report()`はB（CDLパーサ、renderer内）だけでなく、**第9章の`TecsgenGateway.generate()`がIPC経由で受け取ったmainプロセスの実行結果**からも呼ばれる。発生源は区別して保持するが、表示先は同じ一覧・件数表示・ジャンプ機構へ集約する。

警告コード表・ジャンプ機構は[[TECSCDE-TS内部仕様]]第8章8.3・8.4節と同一。ただし複合セルタイプが存在すること自体は警告にしない（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 04 コンポーネント図の表現|DT外部仕様4.7節]]、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|DT外部仕様第9章]]）。未対応構文の存在通知は診断一覧ではなく、選択した外側セルのプロパティ欄にのみ表示する。判定方法と表示契約は[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B章]]で定める。

**`W-COMPOSITE-UNSUPPORTED`はDT-ELでは使わない**（2026-10-21、実装の確認を含む）。TS内部仕様8.3節の警告コード表にある同コード（「複合セルタイプを含む」）は、DT-ELでは**採用しない**——本節の方針が表を上書きする。実装の`cdl/messages.ts`には、コード`W_CODES.COMPOSITE_UNSUPPORTED`だけが残る（「複合型の存在では警告が出ない」ことを確かめるテストが参照するため）。生成関数`compositeUnsupported()`は呼び出しが無かったので、2026-10-22に削除した。診断一覧に出ることはない。この差——親仕様（外部仕様4.7.2・9.2）は「対応していない旨を警告する」、DT外部仕様4.7・9は「存在自体は警告にしない」——は、DT版が複合セルタイプに対応する方針を採ったために生じた（TS内部仕様8.3の表は親仕様側の文書で、DT-ELでは変更しない）。

tecsgenの起動に関する診断は、起動失敗の種類ごとの`E-TECSGEN-NOT-FOUND`・`E-TECSGEN-NO-PERMISSION`・`E-TECSGEN-TIMEOUT`・`E-TECSGEN-OUTPUT-OVERFLOW`・`E-TECSGEN-LAUNCH-FAILED`と、非0終了でエラー行が無いときの`E-TECSGEN-FAILED`（いずれもerror。「実行(Generate)」の実行結果から。2026-10-22に起動失敗の種類を追加）と、CDLを開くときのPlugin生成型の取り込みが失敗したときの`W-PLUGIN-TYPE-LOAD`（warning。開く処理は続行する）と、起動時のtecsgenの版の確認による`W-TECSGEN-VERSION-OLD`・`W-TECSGEN-VERSION-UNKNOWN`（いずれもwarning。2026-10-22設計、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認|第9C章]]）で、いずれもコード表（TS内部仕様8.3節）には無いDT-EL固有のコードである。詳細と外部仕様との差分は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章9.7節]]。

参照先を解決できない場合は既存の`W-UNRESOLVED-REF-FILE`を用いる。`import_C`のCプリプロセッサが見つからない、または起動に失敗して内蔵C宣言解析へ切り替えた場合は`W-CPP-FALLBACK`を追加し、フォールバックしたことと`#include`／`#ifdef`を反映できない可能性を利用者へ提示する。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様 第8章（一次情報源、本章はこれと同一）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（本章への新しい診断発生源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
