---
date: 2026-11-09
description: "三者監査29〜38の内部仕様契約補足。既決要件と現行コードの差を区別する。"
project: TECS
quarter: Q4-2026
status: active
tags: [work-note, tecs, tecscde, spec]
---

# TECSCDE-DT-EL内部仕様 - 監査対応 29-38 保存と画面

[[TECSCDE-DT-EL内部仕様]]の補足。[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面]]と対になる。

2026-11-09の確定契約・実装境界を記す。関連する旧時点の実装記録を、今回のコードの適合確認として扱わない。既存の決定と未決事項（TBC）を維持し、未決を完成済みにしない。仕様を修正してもソース修正が必要な項目は未実装のままである。

## 監査29

**主ファイル保存で、セル・結合レイアウトの定義元による選別が不統一**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査29]]に対応する。

CdlSerializer.serializeSourceはsourceKeyに一致するeditableセルだけを選別し、主ファイル分岐も同じ処理へ統合します。serialize(doc)を残す場合は主キーを明示して委譲し、template数1以下の特例で選別を省きません。cellList/ports/array_elementsは選別した所有セルから、joinListと結合代入は同じ集合の呼び口所有者から作ります。対象sourceTemplateだけを用い、templateなしでも範囲を広げません。SaveAsは旧sourceKeyで抽出して新pathへ書き、7Jの実保存状態と照合します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/serializer.ts:124` — `if (sourceKey === doc.editingFileName) return CdlSerializer.serialize(doc);`
- `src/renderer/cdl/serializer.ts:168` — `.filter((c) => c.editable && (doc.sourceTemplates.size <= 1 || c.locale === doc.editingFileName))`
- `src/renderer/cdl/serializer.ts:201` — `if (!sourceCell?.editable) continue; // 5.4.1: 編集可能セル由来の結合のみ書き出す`

**受入条件**: 主Aと参照Bの両方変更、AにB定義/経路混入なし／A→B結合はAだけ、B→AはBだけ／templateなし/一個/SaveAs/削除原文と再読込検証

参照: [[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約]]、[[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]、[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定]]。

## 監査30

**読み取り専用セル由来の結合作成・バー移動を拒否しない**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査30]]に対応する。

GestureControllerの結合開始とバー操作開始で呼び口側所有セルを解決し、editableでない場合は編集状態へ入れません。CreateJoinCommand・MoveJoinBarCommandもapply時に同じ条件を再検査し、UIを通らない古いコマンドや再生でも読取専用ソースを変更しないno-opにします。Deleteのポート起点処理も呼び口所有者単位で可否を確認します。既存4Gの相手が読取専用でも可能な自動経路再計算を、手動バー操作の許可へ流用しません。拒否は履歴/dirtyを増やしません。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/commands/join-commands.ts:34` — `if (!source || !target) return doc;`
- `src/renderer/commands/join-commands.ts:104` — `return doc.withJoin(join.moveBar(this.barIndex, this.newFixed));`

**受入条件**: readonly source→editable target作成/バー移動拒否／editable source→readonly targetは可能／apply直接実行/編集可否変化/UndoRedo/no-op

参照: [[TECSCDE-DT-EL内部仕様 - 03 モデル設計]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]、[[TECSCDE-DT-EL内部仕様 - 04G 再配置コマンド設計]]。

## 監査31

**セルタイプ未選択・接続済み呼び口の操作が、要求された案内なしで終わる**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査31]]に対応する。

GestureControllerのnewCell分岐でactiveCelltypeName欠落を明示判定し、既存hostの軽い通知経路へ理由を渡してAddCellCommandを発行しません。cport分岐はjoinIdの有無と修飾キーを判定し、接続済みでは通知とShift時のポート選択だけを行います。現在のSelectionState.emptyへの一律変更を止め、選択規則との接続を具体化します。通知はCommand.apply外で行い履歴再生で再表示せず、IME/入力欄/モーダル等の共通入力境界を通った操作だけに反応します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/render/gesture-controller.ts:143` — `if (hit.kind === "none" && celltypeName) {`
- `src/renderer/render/gesture-controller.ts:162` — `// 既に結合済みの呼び口はハイライトのみ（結合モードには入らない、外部仕様6.4.1）。`

**受入条件**: 型未選択の空白クリックで軽い案内/図不変／接続済みcall通常/Shiftと未接続callの分岐／UndoRedoや入力欄操作で通知/履歴増加なし

参照: [[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]、[[TECSCDE-DT-EL内部仕様 - 04 編集コマンドとUndo-Redo設計]]、[[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]]。

## 監査32

**保存済み結合経路のバー・端点整合の検証が不足**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査32]]に対応する。

ToolInfoValidator.parseTecscdeはjoin_listの各barのdir/fixed/from/toを型と有限数で検査し、loaderは全セル・ポートの最終配置確定後にvalidateSavedJoinRouteで端点・向きの整合を検証します。受理する座標許容誤差は既存のALIGN/幾何契約に沿って明示し、未決数値をここで勝手に固定しません。失敗時は該当joinだけautoRouteBarsへ渡し、破棄理由と件数を診断へ集約します。現行Array.isArrayだけの採用と無条件mapを置き換え、正常な他要素とCDL接続を保持します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/document-builder.ts:584` — `const bars: readonly Bar[] = savedBars`
- `src/renderer/cdl/tool-info.ts:360` — `Array.isArray(v.bars)`

**受入条件**: NaN/Infinity/不正dir/短い経路/先頭向き/終端ずれ／セル移動やport辺変更後の旧経路再計算／正常な他join維持、破棄件数と許容誤差境界

参照: [[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]、[[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約]]、[[TECSCDE-DT-EL内部仕様 - 05 描画・インタラクション設計]]。

## 監査33

**セル・ポート・結合レイアウト内部の未知キーを保存で失う**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査33]]に対応する。

parseTecscdeで各階層の既知項目と未知フィールドを分け、所有sourceKeyと安定したセル/ポート/結合の対応情報へ関連付けて保持します。serializerは対象定義元の現在モデルから既知値を作り、その要素に対応する未知値を先にマージして既知値で更新します。同名別ソースや再添字した別PortIdへ付属情報を誤転用せず、名前変更等はモデルの対応を使います。削除対象の既知/付属情報は出力せず、未解決で保持すべき原情報と区別します。4Cの再構成は未知値全消去を意味しないと明記します。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/cdl/serializer.ts:134` — `cellList[cell.name] = {`
- `src/renderer/cdl/serializer.ts:189` — `ports[p.name] = { edge: p.edgeSide, offset: p.offset };`

**受入条件**: cell/port/joinの階層別unknown無編集往復／既知位置変更とunknown保持、同名別source混同なし／名前変更/再添字/削除で誤転用や復活なし

参照: [[TECSCDE-DT-EL内部仕様 - 04C ファイル別保存契約]]、[[TECSCDE-DT-EL内部仕様 - 04B CDLパーサ設計]]、[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入]]。

## 監査34

**情報ボタン・版情報モーダル・コピー・設定欄のUIがない**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査34]]に対応する。

AppShellが情報ビューの1インスタンスを所有し、showModal相当で開く。版情報はpackage由来の埋込値、preloadの環境値、保存済みのtecsgen確認結果からDTO化し、コピーはClipboardGatewayへ渡す。設定欄は現在値と入力中の候補を分離し、確認は保存値を変更しない。保存失敗は入力を残して欄内で通知する。設定取得・保存・候補確認・一覧作成は各Gatewayへ委譲し、UIからfsやprocess.envへアクセスしない。モーダル中は図編集ショートカットを発行せず、Esc閉鎖は検索等の既存キャンセルと競合しないように扱う。#59の探索器や#63の版情報基盤とは責務を分ける。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/index.html:516` — `<div id="toolbar">`
- `src/renderer/app/shell.ts:257` — `runAction(action: string)`

**受入条件**: 表示全項目とコピー内容の一致、未確認/unknownを確認する。／確認失敗後も保存可、PATH非表示、閉鎖・閲覧・コピーでdoc/dirty/history不変を確認する。／モーダル表示中にキャンバス選択へのDelete/Undo等が発行されないことを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界]]、[[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]]。

## 監査35

**ファイルブラウザ・セルタイプ一覧のモードレス化が未反映**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査35]]に対応する。

AppShellがFileBrowserViewとPaletteViewをそれぞれ1つのモードレスコンテナへ収容し、show相当を用いて背景をinertにしない。開閉とフォルダ選択を別アクションとし、隠した際にビューやストアを作り直さない。再表示は現在のdoc、型レジストリ、ルートと展開状態を描画する。FileBrowserViewの通常クリック/Ctrl追加・未保存確認とPaletteViewの配置モードへの受渡しを再利用する。通知購読は二重登録せず、dispose時だけ解除する。DOMの移設だけでファイル読込・再保存・履歴追加を行わず、両表示を開いたままパンやセル配置が継続できるよう入力境界を分ける。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/index.html:553` — `<div id="file-browser"></div>`
- `src/renderer/index.html:554` — `<div id="palette">`
- `src/renderer/app/shell.ts:260` — `void this.fileBrowser.chooseRoot()`

**受入条件**: 両ダイアログを同時に開き、パン・型選択・セル配置・Undoができることを確認する。／繰返し開閉してDOM/購読が重複せず、ツリー状態と現在の型集合が一致することを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計]]。

## 監査36

**廃止対象の表示制御バーが現役のまま**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査36]]に対応する。

index.htmlのdisplay-barとそのDOM参照を移行し、AppShellが旧バーの存在を必須として初期化しない構成にする。既存DisplayFiltersの状態と純粋な可視性・色計算を維持し、操作コントロールを移設して同じstore更新へ結線する。位置は6C.1のツールバー案を参照し、確定前の配置詳細は未決として明記する。領域開閉フラグでツールバー・プロパティ・ステータスを隠す新経路を作らない。旧バー削除によって必要な状態を初期化したり、フィルタ機能そのものを削除したりしない。古い実装記録は従来版の経緯として残し、現在UIの完了記録と区別する。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/index.html:543` — `<div id="display-bar">`
- `src/renderer/app/shell.ts:173` — `this.bindDisplayBar();`

**受入条件**: 旧バーなしでもシェルが起動し、全既存表示機能へ到達できることを確認する。／3常時領域と凡例が残り、一覧の開閉がモードレス操作に移ったことを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計]]、[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]。

## 監査37

**セルの定義元フルパス表示・読み取り専用表示ボタンがない**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査37]]に対応する。

PropertyPanelViewは単一セルの定義元情報を表示署名へ含め、選択・定義元変更に同期する。DefinitionFileViewへパスと取得モードを渡し、mainの副作用のないテキスト読込をFileGateway経由で行う。openPathのように図やセッションを変更するAPIは流用しない。本文はtextContentで描き、編集・保存・再解析をしない。削除済み、アクセス拒否、復号失敗は表示内へ通知して現在のdocを維持する。診断ジャンプの解析時本文モードとは区別し、読み取り要求が逆順完了しても最新の表示を上書きしない。縦スクロールは既存実装を保持し、横方向のTBCは変更しない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/property-panel.ts:123` — `private renderCell`
- `src/renderer/app/property-panel.ts:171` — `const attrNames = celltype?.attributeNames`

**受入条件**: 主/別ソース/生成/未保存/単一/複数選択でパスとボタンを確認する。／閲覧の失敗、非ASCIIパス、長いパス、逆順の読込完了でもdoc/dirty/historyが不変であることを確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 08B 診断位置へのソースジャンプ]]。

## 監査38

**セルタイプ詳細モーダル・定義ファイルのフルパス表示・閲覧がない**

[[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面#監査38]]に対応する。

PaletteViewの型選択と詳細表示を別の明示的な操作に分け、AppShell所有のCelltypeDetailsViewへ選択型の現行メタデータを渡す。詳細はshowModal相当とし、表示中の図編集ショートカットを抑止する。定義元パスの取得と有無判定はセルタイプのソース情報を使い、現在の主ファイルや生成用の一時パスで補完しない。通常ファイルは#37のDefinitionFileViewへディスク表示モードで渡し、内部生成型はVFSの読み取り専用モードへ渡す。仮想ソースがなければ閲覧不能と示す。本文はHTMLとして解釈せず、図上のセル作成・型定義変更・履歴追加を行わない。型集合や文書が変わった際は古い型・パスを別の型へ誤って引き継がない。

**実装要否**: ソースコードの修正は必要です。 現行コードが確定契約に未対応です。

**現行コード根拠（5cf2d85）**:

- `src/renderer/app/palette.ts:22` — `this.celltypeList.addEventListener("click"`
- `src/renderer/app/palette.ts:27` — `this.store.setMode("newCell");`

**受入条件**: 選択からの配置と詳細表示を個別に確認し、詳細では型やdocが変わらないことを確認する。／通常型/複合型/生成型/定義元なしで情報と閲覧可否を確認する。

参照: [[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]、[[TECSCDE-DT-EL内部仕様 - 03B 複合セルタイプ設計]]。

## Related

- [[TECSCDE-DT-EL内部仕様]]
- [[TECSCDE-DT外部仕様 - 監査対応 29-38 保存と画面]]
