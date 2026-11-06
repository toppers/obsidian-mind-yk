---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第4章（編集コマンドとUndo-Redo設計）— Command/Historyクラスはrendererで動作しTECSCDE-TS内部仕様と同一。Copy/Paste/CutのみOSクリップボード連携を追加。"
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
> V0.2.0のactiveセル最上段配置は[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置#6C.4 activeセルの最上段への移動|6C.4]]で追加します。表示のみの変更は編集履歴へ入れません。差分章は実装前の内部設計です。


Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 4 of 11。

## 4. 編集コマンドとUndo-Redo設計

`Command`抽象クラス（`apply`のみ、`invert()`は持たない）、`History`クラス（replay計算・past/future操作のカプセル化）、および大半のコマンドクラス（`AddCellCommand`・`MoveCellCommand`・`DeleteCommand`・`CreateJoinCommand`等）は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様第4章]]と**完全に同一、変更なし**。第2章2.3節のとおり本モジュール（D）はrendererプロセスで動作する。

### 4.1 差分: `CopyCommand`/`PasteCommand`/`CutCommand`のOSクリップボード連携

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様6.7節]]が採用したOSクリップボード連携を、コマンドクラスと`AppStore`に反映する。以下は**現行の実装**（`src/renderer`の`commands/clipboard-commands.ts`、`app/store.ts`、`app/clipboard-actions.ts`、`gateways/clipboard-gateway.ts`、`cdl/fragment.ts`と、`preload/index.mts`、`main/ipc.ts`の読解。2026-10-21に当初のスケッチから更新。テストは読んでいない）。

**ClipboardGateway**（renderer）: OSクリップボードの読み書きは**非同期**。preloadが`window.tecscde.clipboard`を公開し、実体は`ipcMain`のハンドラ（`clipboard:writeText`／`clipboard:readText`）がmainプロセスで`clipboard`モジュールを呼ぶ（第2章2.4節）。

```ts
class ClipboardGateway {
  writeText(text: string): Promise<void> { return window.tecscde.clipboard.writeText(text); }
  readText(): Promise<string> { return window.tecscde.clipboard.readText(); }
}
```

**コマンド**:

```ts
class CopyCommand extends Command {
  readonly kind = 'Copy';
  constructor(private readonly cellIds: readonly CellId[], private readonly clipboard: Pick<ClipboardGateway, 'writeText'>) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    // 履歴を作らない特殊なコマンド。書き込みの完了は待たない（fire-and-forget）
    void this.clipboard.writeText(serializeCellsAsCdl(doc, this.cellIds)); // cellブロックのみのCDL断片（外部仕様6.7節）
    return doc; // ドキュメントは変更しない
  }
}

class PasteCommand extends Command {
  readonly kind = 'Paste';
  constructor(
    private readonly appClipboard: readonly Cell[],            // コピー時点のCellスナップショット
    private readonly osClipboardText: string | undefined,       // 呼び出し側が先に読み取り済み
    private readonly targetSourceKey?: string,                  // 貼り付け先の定義元ファイル
  ) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    // アプリ内クリップボードが空の場合のみ、OSクリップボードのCDL断片を試みる
    if (this.appClipboard.length > 0) return pasteFromAppClipboard(doc, this.appClipboard, this.targetSourceKey);
    if (this.osClipboardText === undefined) return doc;
    const fragment = tryParseCdlFragment(this.osClipboardText); // 解析できなければ何もしない（外部仕様6.7節）
    return fragment ? pasteFromCdlFragment(doc, fragment, this.targetSourceKey) : doc;
  }
}

class CutCommand extends Command {
  readonly kind = 'Cut';
  constructor(private readonly cellIds: readonly CellId[], private readonly joinIds: readonly JoinId[]) { super(); }
  apply(doc: TecscdeDocument): TecscdeDocument {
    return new DeleteCommand(this.cellIds, this.joinIds).apply(doc); // カスケード削除のみ。クリップボードには触れない
  }
}
```

**呼び出し側（`AppStore`とモジュールG）**: 副作用と非同期の読み取りは、すべてコマンドの外に置く。

| 操作 | 実装 | 内容 |
|---|---|---|
| コピー | `AppStore.copySelection(clipboard)` | 選択セルを`appClipboard`へスナップショットし、`CopyCommand.apply()`を**`dispatch`を通さず直接1回だけ**呼ぶ（履歴を作らない） |
| カット | `AppStore.cutSelection(clipboard)` | スナップショットを取り、`serializeCellsAsCdl`の結果を`void clipboard.writeText(…)`で**先に1回だけ**書いたうえで、`dispatch(new CutCommand(…))`し、選択を空にする（1つのUndo単位） |
| 貼り付け | `pasteFromClipboard(store, clipboard)`（`app/clipboard-actions.ts`、非同期）→ `AppStore.pasteClipboard(text)` | まず`await clipboard.readText()`で読み取り、解決済みの文字列を渡す。`pasteClipboard`は、選択が編集可能セル1つで、その定義元ファイルがあれば`targetSourceKey`にして`dispatch(new PasteCommand(…))`する |

**貼り付けの規則**（`pasteFromAppClipboard`／`pasteFromCdlFragment`）:
- **共通**: セルタイプが解決できないセルは作らない。名前は`deriveCellName`で新規に割り当て、結合は引き継がない。生成するセルは`editable: true`、`locale`は貼り付け先（`targetSourceKey`、無ければ編集中のファイル）。
- **アプリ内クリップボード**: 元の位置から10mm（`PASTE_OFFSET_MM`）ずらし、大きさ・属性を引き継ぐ。所属リージョンは元のものを引き継ぐが、貼り付け先ファイルにそのスコープが無ければルートにする（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.3節]]）。
- **OSクリップボードのCDL断片**: 断片は位置・リージョン・結合を持たない（`cdl/fragment.ts`）ので、所属はルート、大きさは既定値、位置は(20, 20)mm（`PASTE_ANCHOR_MM`）から10mm刻みで斜めに並べる。

> [!note] 当初のスケッチからの更新（2026-09-11、2026-10-21 に整理）
> 当初（2026-09-05）のスケッチは、`ClipboardGateway`を同期の`writeText(): void`／`readText(): string`とし、preloadが`clipboard`を直接ブリッジする想定で、`PasteCommand`が`apply()`内で読み取り、`CutCommand`が`apply()`内で書き込む設計だった。実装で次のとおり変わった（[[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|決定記録]]）。
> - **`ClipboardGateway`は非同期でipcMain経由**: 実機確認で、preloadに公開される`electron`モジュールには`clipboard`が含まれないと分かった（ESM／CJSを問わず）。そのため`file`・`tecsgen`と同じく`ipcRenderer.invoke`→`ipcMain.handle`の経路になり、読み書きは`Promise`を返す。
> - **`PasteCommand`は`ClipboardGateway`を持たない**: `Command.apply()`は純粋な同期処理なので、非同期の読み取りはコマンドの外（`clipboard-actions.ts`）で済ませ、解決済みの文字列（`string | undefined`）を受け取る。
> - **`CutCommand`は副作用を持たない**: `History.current`が`past`を先頭から再生（replay）する設計のため、`apply()`に書き込みがあると再描画のたびに再実行される。書き込みは`AppStore.cutSelection`が`apply()`を通さず1回だけ行い、`CutCommand`は`DeleteCommand`と同じ純粋なモデル削除（`kind`が`Cut`であるだけの違い）。`CopyCommand`は履歴に入らないので、この問題は起きない。
> - 実装コメントは、非同期化の理由に「Electron 44でclipboardモジュールが非同期化された」ことも挙げるが、ここでは検証していない。上の「preloadから使えない」ことが、現行の経路の直接の理由である。

### 4.7 結合の自動経路と他セルの回避（2026-10-24、親外部仕様7.3.2）

結合の経路を自動生成・再計算するとき、他のセルの矩形と重ならない候補を優先する。軽量な範囲に限り、すべての交差を除く保証はしない（親外部仕様7.3.2。4.6.2の「要件としない」を、同じく将来課題としていた7.3.2で一部実現したもの）。

- **入口**: `autoRouteBars(from, fromEdge, to, toEdge, obstacles = [])`（`model/geometry.ts`）。`obstacles`は他のセルを含む全セルの矩形（`RectMm`、`Cell`が構造的に満たす）。呼び出しは、読み込み時に保存済みの経路が無い結合（`cdl/document-builder.ts`）、`CreateJoinCommand`、`rerouteJoin`（セル移動・整列・ポート辺変更に伴う再計算、`commands/support.ts`）の3か所で、いずれも`doc.cellValues()`を渡す。保存済みの経路は従来どおり再計算しない。
- **既定の経路**: 従来どおりのL字（ポートから`DIST_PORT_MM`だけ出て、1回曲がり、受け口側へ入る）。ポート直後の点（`p1`）から`p2`までの区間が、どの矩形の内部も横切らなければ、これを返す。**障害物が無い、または邪魔にならないときの結果は従来と同一**（再計算のたびに経路が変わらない）。
- **候補**: 既定が矩形を横切るときだけ、(1) もう一方のL字、(2) コの字（中間の垂直線`x`、または水平線`y`を置く5区間の経路）を加える。`x`・`y`は、`p1`と`p2`の中間と、各矩形の外側`DIST_PORT_MM`の位置（いずれも`alignRound`で1mmに丸める）。
- **選択**: 区間が内部を横切る矩形の数が最小のもの。同数なら短いもの。既定より改善する候補が無ければ既定を返す。縁に沿う・接するだけは交差に数えない。ポートから出る・入る短い区間は数えない。
- **制約**: 水平・垂直のバーのみ（外部仕様10.3 #4）。コの字の経路は5本のバーになるが、保存・読み込み・バー移動（先頭と末尾は移動不可）は本数に依存しない。他の矩形の外側に置いた線が別の矩形を横切ることはあり、その場合は交差の少ない方が選ばれる。
- **テスト**: `auto-route.test.ts`（純関数）、`route-avoidance.test.ts`（読み込み・結合作成・セル移動・再計算）。共有フィクスチャの`cController1.cLog`は、従来`cSensor1`を貫く直線だった（保存済みの経路が無いため）。回避の導入で経路が変わり、座標を決め打ちしていた`hit-tester.test.ts`・`gesture-controller.test.ts`は、経路から最長の途中バーの中点を求める形に改めた。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（一次情報源、Copy/Paste/Cut以外は同一）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様 第6章後半（OSクリップボード連携の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（ClipboardGatewayの設計根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
