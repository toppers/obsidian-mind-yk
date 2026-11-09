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

> [!info] V0.2.0差分設計（2026-11-06）
> V0.2.0の設定保存後の版診断更新と未検出エラーの設定案内は[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理#9D.4 版確認と診断更新|9D.4]]で拡張します。差分章は実装前の内部設計です。


Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 8 of 11。

## 8. 整合性チェックとメッセージ設計

`Diagnostic`値クラス・`DiagnosticsCollector`クラスの基本設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様第8章]]を踏襲する。ただし[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|TECSCDE-DT外部仕様第9章]]に合わせ、診断の発生源を明示する。

```ts
type DiagnosticSource = 'tree-sitter' | 'input' | 'consistency' | 'tecsgen';
```

`Diagnostic`へ`source: DiagnosticSource`を追加する。`tree-sitter`は`ERROR`／`MISSING`ノードから生成するG-code相当の構文エラーだけを表し、S-code相当の意味エラーは生成しない。文言はCSTの文脈から構成するため、tecsgenのメッセージカタログとの完全一致を要件としない。`input`は入力側の制約によるエラー用の発生源だが、非UTF-8入力（2026-10-21）と旧世代の`__location_information__`形式（2026-10-22。読み込んで無視する）がいずれもエラーでなくなったため、**現行実装は`input`の診断を生成しない**（第7章7.8節）、`consistency`は図・参照解決の警告、`tecsgen`は第9章で取り込むtecsgen自身のG-code／S-codeと原文メッセージを表す。

本モジュール（H）はrendererプロセスで動作し、`DiagnosticsCollector.report()`はB（CDLパーサ、renderer内）だけでなく、**第9章の`TecsgenGateway.generate()`がIPC経由で受け取ったmainプロセスの実行結果**からも呼ばれる。発生源は区別して保持するが、表示先は同じ一覧・件数表示・ジャンプ機構へ集約する。

警告コード表は[[TECSCDE-TS内部仕様]]第8章8.3節を基本とする。ジャンプ機構は[[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ|8B]]で具体化し、TS内部仕様8.4の「位置だけなら提示に留める」は採用しない（2026-11-08、監査#18）。図要素がなくても解析時ソースの該当行・列へ移動する。ただし複合セルタイプが存在すること自体は警告にしない（[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 04 コンポーネント図の表現|DT外部仕様4.7節]]、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 09 エラーと警告|DT外部仕様第9章]]）。未対応構文の存在通知は診断一覧ではなく、選択した外側セルのプロパティ欄にのみ表示する。判定方法と表示契約は[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計|3B章]]で定める。

**`W-COMPOSITE-UNSUPPORTED`はDT-ELでは使わない**（2026-10-21、実装の確認を含む）。TS内部仕様8.3節の警告コード表にある同コード（「複合セルタイプを含む」）は、DT-ELでは**採用しない**——本節の方針が表を上書きする。実装の`cdl/messages.ts`には、コード`W_CODES.COMPOSITE_UNSUPPORTED`だけが残る（「複合型の存在では警告が出ない」ことを確かめるテストが参照するため）。生成関数`compositeUnsupported()`は呼び出しが無かったので、2026-10-22に削除した。診断一覧に出ることはない。この差——親仕様（外部仕様4.7.2・9.2）は「対応していない旨を警告する」、DT外部仕様4.7・9は「存在自体は警告にしない」——は、DT版が複合セルタイプに対応する方針を採ったために生じた（TS内部仕様8.3の表は親仕様側の文書で、DT-ELでは変更しない）。

tecsgenの起動に関する診断は、起動失敗の種類ごとの`E-TECSGEN-NOT-FOUND`・`E-TECSGEN-NO-PERMISSION`・`E-TECSGEN-TIMEOUT`・`E-TECSGEN-OUTPUT-OVERFLOW`・`E-TECSGEN-LAUNCH-FAILED`と、非0終了でエラー行が無いときの`E-TECSGEN-FAILED`（いずれもerror。「実行(Generate)」の実行結果から。2026-10-22に起動失敗の種類を追加）と、CDLを開くときのPlugin生成型の取り込みが失敗したときの`W-PLUGIN-TYPE-LOAD`（warning。開く処理は続行する）と、起動時のtecsgenの版の確認による`W-TECSGEN-VERSION-OLD`・`W-TECSGEN-VERSION-UNKNOWN`（いずれもwarning。2026-10-22設計、[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09C tecsgen版の確認|第9C章]]）で、いずれもコード表（TS内部仕様8.3節）には無いDT-EL固有のコードである。詳細と外部仕様との差分は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|第9章9.7節]]。

参照先を解決できない場合は既存の`W-UNRESOLVED-REF-FILE`を用いる。`import_C`のCプリプロセッサが見つからない、または起動に失敗して内蔵C宣言解析へ切り替えた場合は`W-CPP-FALLBACK`を追加し、フォールバックしたことと`#include`／`#ifdef`を反映できない可能性を利用者へ提示する。

### 8.1 配列ポート挿入の拒否通知（2026-11-07、監査#12）

[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入|4E.6]]の`W-ARRAY-PORT-INSERT-REJECTED`（案）はwarning・`source: 'consistency'`とし、固定長の場合は「固定長配列には要素を挿入できません。」を対象セル・ポートとともに示す。他の拒否理由も同コードの詳細として区別する。操作の呼び出し側が拒否時に一度だけ通知し、ドキュメントやUndo/Redo履歴は変更しない。コマンドの`apply()`や履歴再生から診断を追加しない。これは通知契約の追加であり、実装済みを示すものではない。

### 8.2 配列ポート要素削除の拒否通知（2026-11-07、監査#13）

[[TECSCDE-DT-EL内部仕様 - 04F 配列ポートの要素削除|4F.6]]の`W-ARRAY-PORT-DELETE-REJECTED`（案）はwarning・`source: 'consistency'`とする。固定長は「固定長配列の要素は削除できません。」、可変長の添字0は「先頭要素は削除できません」と対象付きで通知し、黙って拒否しない。複数対象の全体拒否では対象別の理由をまとめる。これは要素削除要求の拒否であり、固定長や添字0の結合解除まで一律に拒否する通知ではない。呼び出し側が一度だけ通知し、履歴再生からは追加しない。実装済みを意味しない。

### 8.3 位置付き診断のソース識別と表示（2026-11-08、監査#18）

[[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ|8B]]に従い、`Diagnostic.location`の原値を保持し、`sourceRef`と`coordinateKind`（案）を関連付ける。各producerが実際の基数・列単位を確認し、ソースID・解析時本文・実行時cwdをナビゲータへ引き渡す。任意の空ファイル名や相対名を現在の主ファイルへ解決しない。`DiagnosticNavigator`は図要素があれば既存ジャンプ、位置だけなら読み取り専用ビューの行・列へ移動する。両方あれば図ジャンプと「ソースへ」を使い分ける。取得・変換失敗はビュー内で説明し、診断ログの文字列表示だけをジャンプ成功とは扱わない。実装適合は未確認。

### 8.4 再配置結果の通知（2026-11-08、監査#11）

[[TECSCDE-DT-EL内部仕様 - 04G 再配置コマンド設計|4G.6]]の通常再配置は、ずらし配置した対象セル数を`W-AUTO-LAYOUT-OVERFLOW`で通知する。用紙内へ配置できず計画全体を拒否した場合は、`W-RELAYOUT-FAILED`（案、warning、`source: 'consistency'`）で現在用紙内に配置できない理由を示す。通知は呼び出し側で行い、操作・現在文書に紐付く結果を更新する。Undo/Redoと文書切替で警告表示を整合させ、`apply()`から重複登録しない。拒否のためにモデル・dirty・履歴を変更しない。実装適合は未確認。

### 8.5 active最上段配置の通知（2026-11-08）

[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置|6C.4]]のactiveセルの最上段への移動は、最上段以外の行へ送った対象セル数を`W-ACTIVE-TOP-OVERFLOW`（案、warning、`source: 'consistency'`）で通知する。用紙内に重ならずに置けない対象があり計画全体を拒否した場合は、`W-ACTIVE-TOP-FAILED`（案、warning、`source: 'consistency'`）で「現在の用紙内に重ならずに配置できないため、最上段への移動を行いませんでした。」と理由を示す。通知は8.4と同じく呼び出し側が計画の最終結果から一度だけ行い、Undo/Redoと文書切替で警告表示を整合させ、`apply()`から登録しない。拒否のためにモデル・dirty・履歴を変更しない。外部仕様は[[TECSCDE-DT外部仕様 - 09 エラーと警告|9.2]]。実装適合は未確認。

### 8.6 用紙指定の通知（2026-11-08）

編集対象ファイルグループの読み込み時、採用元以外のファイルが採用した用紙と異なる`paper`を宣言している場合は`W-PAPER-CONFLICT`（案、warning、`source: 'consistency'`）で、競合したファイル名と採用した値を通知する。`size`が許容値でない場合（宣言なしとして扱う）と`orientation`が許容値でない場合（横として扱う）は`W-PAPER-INVALID`（案、warning、`source: 'consistency'`）で通知する。いずれも用紙の決定を変えない。通知はロード結果の最終警告として一度だけ行い、不採用の最小用紙選択の試行（[[TECSCDE-DT-EL内部仕様 - 04D 読み込み時の最小用紙選択|4D.2]]）の途中では登録しない。外部仕様は[[TECSCDE-DT外部仕様 - 09 エラーと警告|9.2]]、決定規則は[[TECSCDE-DT外部仕様 - 05B CDLファイル一覧の作成と自動配置|5.3.x]]項目8。実装適合は未確認。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 08 整合性チェックとメッセージ設計|TECSCDE-TS内部仕様 第8章（基本設計の一次情報源。DT-ELのジャンプは8Bを優先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|TECSCDE-DT-EL内部仕様 第9章（本章への新しい診断発生源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

- [[TECSCDE-DT-EL内部仕様 - 監査対応 49-58 出力と検索]] — 該当する監査項目の契約補足（2026-11-09）。

- [[TECSCDE-DT-EL内部仕様 - 監査対応 59-69 環境と文書]] — 該当する監査項目の契約補足（2026-11-09）。
