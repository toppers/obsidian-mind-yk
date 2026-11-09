---
date: 2026-11-08
description: "TECSCDE-DT-EL内部仕様 4H。CDLパーサ（4B）から逐語分離した4B.7〜4B.10——診断コード表、クリップボード用の断片（fragment.ts）、システム定義CDLへの拡張点、実装を読んで気づいた点。25KB閾値による分割。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

# 4H. CDLパーサの診断・断片・拡張点

Domain note of [[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]（2026-11-08、25KB閾値で4B.7〜4B.10を逐語分離。節番号は4Bのまま）。親は[[TECSCDE-DT-EL内部仕様]]。

## 4B.7 診断

`messages.ts`が生成する診断:

| コード | 内容 | 出どころ |
|---|---|---|
| `G1015` | 予期しないファイル終端 | `ERROR`ノードの内容が空のとき |
| `G1016` | 構文エラー（`syntax error near`） | `MISSING`ノード、または`ERROR`ノード。対応先が定まらなければこれに倒す |
| `W-DUP-CELL` | セル重複 | 4B.5節 |
| `W-AUTO-LAYOUT-OVERFLOW` | 採用用紙で重なりなしに収容できず、ずらし配置した自動配置セル数 | 4B.5節・4D.3節（最終結果だけを通知） |
| `W-UNRESOLVED-CELLTYPE` | セルタイプ未解決 | 4B.5節（整合性チェックの`diagnostics/integrity.ts`も同名を出す） |
| `W-MISSING-JOIN-TARGET` | 結合先が無い | 4B.5節 |
| `W-COMPOSITE-UNSUPPORTED` | 複合セルタイプの未対応構文 | **DT-ELでは使わない仕様**（第8章、3B.5）。生成関数`compositeUnsupported`は、呼び出しが無いため2026-10-22に削除した（4B.10節の5）。コード`W_CODES.COMPOSITE_UNSUPPORTED`は、「出ない」ことを確かめるテストが参照するため残す。未対応構文の通知はプロパティ欄のみ |
| `W-REQUIRE-PORT-HIDDEN` | 隠れ`require`ポート | 4B.5節 |
| `W-LAYOUT-DISCARDED`、`W-LAYOUT-PARSE-ERROR`、`W-NEWER-FORMAT` | `tool_info`の検証 | `ToolInfoValidator`（`tool-info.ts`が直接出す） |
| `W-UNRESOLVED-REF-FILE`、`W-CPP-FALLBACK`、`W-CDECL-PARSE` | 参照ファイル・cpp・Cヘッダ解析 | `app/import-resolution.ts`（7.5節、9B）と`diagnostics/integrity.ts`。ローダーは出さない |
| `W-C-TYPE-UNRESOLVED`、`W-PORT-SIGNATURE-UNRESOLVED`、`W-REGION-MISMATCH` | 型・ポート・リージョン | `document-builder.ts`。コードは`messages.ts`の`W_CODES`に集約した（2026-10-22。`tool-info.ts`の`W-NEWER-FORMAT`・`W-LAYOUT-*`も同様） |
| `W-PLUGIN-TYPE-LOAD`、`E-TECSGEN-NOT-FOUND` | tecsgenの起動失敗 | それぞれ`app/file-actions.ts`、`diagnostics/tecsgen-result-parser.ts`（パーサーの外。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計|9.7節]]） |

- tree-sitterはエラーの位置と構造しか返さず、メッセージ文言を持たない（移植したのは構文定義だけで、メッセージカタログは含まれない）。そのため構文エラーは大半を`G1016`にまとめる（tecsgen自身も大半をこの1コードで報告する）。`messages.ts`のコード体系は、外部仕様が引用する範囲の再現で、tecsgenのカタログ全体の網羅ではない。
- 診断の`location.file`は、`CdlDocumentBuilder`の段階では空で、`loadSources`が`withLocation`でファイル名を埋める。

## 4B.8 クリップボード用の断片（`fragment.ts`）

**2026-11-07、監査#2への回答による契約更新**: 旧`serializeCellsAsCdl`の「結合を含めない」契約を改め、セルと結合の不変なスナップショットを受ける`serializeClipboardAsCdl`（案）に統一する。単一セル選択では結合代入を出力せず、複数セル選択では両端が選択セル集合内の結合だけを、呼び口側の`cell`ブロックへ結合代入として出力する。セル名とポート名・配列添字を保持し、位置・リージョン情報は含めない。外部セルへの結合代入を元のセル情報から再出力しない。

`tryParseCdlFragment`は`CdlDocumentBuilder.build`の結果からセル群と断片内で閉じた結合を保持する。構文エラーがあるか、`cell`が1つも無ければ`undefined`を返す（貼り付けは「何もしない」）。貼り付け先の既存セルを断片内の参照解決に使わない。単一セル選択の例外、セル名・IDの再対応、Undo／Redoは[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計#4.1 差分: `CopyCommand`/`PasteCommand`/`CutCommand`のOSクリップボード連携|第4章4.1節]]を正とする。この更新は設計であり、実装済みの記録ではない。

## 4B.9 システム定義CDLの判定（実装済み）

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|3.2節]]に従い、**rendererの`CdlDocumentLoader.loadSources()`が判定する**。`LoadOptions.systemDirs`と各`CdlSource.sourcePath`を、main・rendererで共用できる純粋関数`shared/path-under.ts`の`isUnderAny`で比較する。mainで判定結果を付けて渡す当初案は採用しない。

Plugin生成ソースをこのパス判定から除き、定義元パスが指定ディレクトリ配下の通常CDLを`systemDefined`とする。そのソースの`editable`は、呼び出し側が渡した値と`allowEditSystemDefined === true`の両方を満たす場合だけ有効にする。ソース単位で編集可否を確定してからテンプレートとセルを作り、`Cell`へ`systemDefined`と`editable`を渡す。セル単位でだけ編集不可にして、保存用テンプレートに編集不可セルを混在させない。

この判定経路は**2026-10-22に実装済み**で、2026-11-08の監査#1対応として内部03.2と現行`src/renderer/cdl/document-builder.ts`に合わせて記述を統一した。表示の追加設計や他の読み込み契約まで実装済みとするものではない。

## 4B.10 実装を読んで気づいた点

仕様と実装のずれの候補。いずれも、読解のみで、動作は確認していない。

1. ~~**`isRequire`が常に`false`**~~ → **解消（2026-10-22）**。`require`を拾う処理を足した（4B.2節の「セルタイプ」）。経緯: `collectPort`は`isRequire: false`固定（`require`は独立した`celltype_statement`のため）。一方、`loadSources`は`isRequire`のポート数を`hiddenRequirePortCount`にするので、この経路では**常に0**となり、`W-REQUIRE-PORT-HIDDEN`は出ない可能性が高い。`celltype_statement`の`require`を拾う処理が`collectCelltype`に無いことが原因（`var`／`require`／`factory`は無視する、とコメントがある）。
2. ~~**古いドキュメントコメント**~~ → **解消（2026-10-22）**（`loadSources`のコメントを更新）。経緯: `loadSources`の説明は「編集対象ファイルのcellのみeditable=trueとなり」と書くが、現行の仕様（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07C 読み込み経路の統合|7C]]）は呼び出し側が決める`editable`で、通常CDLは全て編集可能。`CdlSource.editable`のコメントも「読み込んだCDLは編集可能」となっていて、こちらは現行どおり。
3. ~~**トップレベルとネストの重複**~~ → **解消（2026-10-22）**（`visitNested`に統合。統合前も`signature`の名前の修飾に実際の差は無かった）。経緯: `build`のトップレベル`switch`と`visitNested`の`switch`が別々に同じ分岐を持ち、片方だけ直す事故が起きうる。`signature`の名前の修飾規則も、片方（トップレベル）は常に修飾なし。
4. ~~**メッセージの二重管理**~~ → **解消（2026-10-22）**（`W_CODES`に集約）。経緯: `W-C-TYPE-UNRESOLVED`などは`document-builder.ts`に直書きされ、`messages.ts`の`W_CODES`にない。
5. ~~**`compositeUnsupported`の呼び出しが無い**~~ → **解消（2026-10-22）**（関数を削除。コード定数はテスト用に残す）。経緯: `messages.ts`の`W-COMPOSITE-UNSUPPORTED`と生成関数は、`src`内に呼び出しが見当たらない（2026-10-21の検索）。DT-ELの仕様（第8章、3B.5。DT外部仕様4.7節・第9章と一致）は、複合型の存在や未対応構文を警告にしないので、仕様と実装は整合しており、残るのは未使用の定義だけ（削除してよい）。
6. ~~**ファイル名ヘッダの参照番号**~~ → **解消（2026-10-22）**（`cdl/`の主要なファイルの先頭コメントに、DT-EL内部仕様04Bへの参照を足した）。経緯: ソース先頭のコメントは「TECSCDE-TS内部仕様 2.2」「11.3」など、TS版の章番号を指す。DT-ELで章番号が違う場合に追跡しにくい（本章がDT-ELの対応表になる）。

## 関連

- [[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]] — 4B.1〜4B.6（構成要素・読み込みの流れ・CST走査・モデル組み立て・直列化）
- [[TECSCDE-DT-EL内部仕様]]

- [[TECSCDE-DT-EL内部仕様 - 監査対応 19-28 配列と配置]] — 該当する監査項目の契約補足（2026-11-09）。
