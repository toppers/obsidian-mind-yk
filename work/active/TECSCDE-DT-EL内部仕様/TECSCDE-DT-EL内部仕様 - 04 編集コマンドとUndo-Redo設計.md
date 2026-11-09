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

[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様6.7節]]が採用したOSクリップボード連携を、コマンドクラスと`AppStore`に反映する。2026-10-21の実装読解を土台に、**2026-11-07、監査#2への回答として、単一セルでは結合を含めず、複数セルでは選択セル間の結合を保持する契約へ更新した**。以下のスナップショット型・補助関数を含むコード例は更新後の設計であり、実装済みを意味しない。非同期IPCと履歴の再生方式は維持する。

**ClipboardGateway**（renderer）: OSクリップボードの読み書きは**非同期**。preloadが`window.tecscde.clipboard`を公開し、実体は`ipcMain`のハンドラ（`clipboard:writeText`／`clipboard:readText`）がmainプロセスで`clipboard`モジュールを呼ぶ（第2章2.4節）。

```ts
class ClipboardGateway {
  writeText(text: string): Promise<void> { return window.tecscde.clipboard.writeText(text); }
  readText(): Promise<string> { return window.tecscde.clipboard.readText(); }
}
```

**コマンド**:

```ts
// コピー時点の不変なスナップショット。単一セルの場合はjoinsが空。
interface ClipboardSnapshot {
  readonly cells: readonly Cell[];
  readonly joins: readonly Join[];
}

class CopyCommand extends Command {
  readonly kind = 'Copy';
  constructor(private readonly snapshot: ClipboardSnapshot, private readonly clipboard: Pick<ClipboardGateway, 'writeText'>) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    // 履歴を作らない特殊なコマンド。書き込みの完了は待たない（fire-and-forget）
    void this.clipboard.writeText(serializeClipboardAsCdl(this.snapshot)); // 選択セル内の結合代入もcellブロックへ含める
    return doc; // ドキュメントは変更しない
  }
}

class PasteCommand extends Command {
  readonly kind = 'Paste';
  constructor(
    private readonly appClipboard: ClipboardSnapshot,          // コピー時点のセルと内部結合
    private readonly osClipboardText: string | undefined,       // 呼び出し側が先に読み取り済み
    private readonly targetSourceKey?: string,                  // 貼り付け先の定義元ファイル
  ) { super(); }

  apply(doc: TecscdeDocument): TecscdeDocument {
    // アプリ内クリップボードが空の場合のみ、OSクリップボードのCDL断片を試みる
    if (this.appClipboard.cells.length > 0) return pasteFromAppClipboard(doc, this.appClipboard, this.targetSourceKey);
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
| コピー | `AppStore.copySelection(clipboard)` | 下記のセル数・端点条件で`ClipboardSnapshot`を1回作り、`appClipboard`とOS出力で共有する。`CopyCommand.apply()`を**`dispatch`を通さず直接1回だけ**呼ぶ（履歴を作らない） |
| カット | `AppStore.cutSelection(clipboard)` | コピーと同じスナップショットを取り、そのCDLを`void clipboard.writeText(…)`で**先に1回だけ**書いたうえで、`dispatch(new CutCommand(…))`し、選択を空にする（1つのUndo単位）。選択外へ出る結合はコピーしないが、元の図からの削除は既存のカスケード規則に従う |
| 貼り付け | `pasteFromClipboard(store, clipboard)`（`app/clipboard-actions.ts`、非同期）→ `AppStore.pasteClipboard(text)` | まず`await clipboard.readText()`で読み取り、解決済みの文字列を渡す。`pasteClipboard`は、選択が編集可能セル1つで、その定義元ファイルがあれば`targetSourceKey`にして`dispatch(new PasteCommand(…))`する |

**貼り付けの規則**（`pasteFromAppClipboard`／`pasteFromCdlFragment`）:
- **コピー範囲**: コピー時点の選択セルIDを重複除去して確定する。1個なら`joins`を空にし、自己結合もコピーしない。2個以上なら、呼び口側・受け口側のセルがともにその集合に含まれる結合をすべてスナップショットする。結合線の選択状態は条件にしない。片端が選択外の結合は含めず、セルの属性等に保持した元の結合情報から再混入させない。セルが0個ならセル群のコピーを行わない。
- **共通**: セルタイプが解決できないセルは作らない。名前は`deriveCellName`で新規に割り当てる。生成するセルは`editable: true`、`locale`は貼り付け先（`targetSourceKey`、無ければ編集中のファイル）。結合の有無はコピー時に確定したスナップショット／CDL断片に従い、貼り付け時点の選択セル数では変更しない。
- **端点の再対応**: 先に貼り付け対象の全セルを生成し、コピー元のセルID／断片内セル名から新セルへの対応表を作る。その後、保持した結合の両端を対応する新セルのポートへ付け替える。呼び口・受け口、配列添字を保持し、セル・ポート・結合のIDは複製先用に割り当てる。元の図の同名セルへ解決しない。セルタイプ未解決等で一方のセルを生成できなかった場合、または対応ポートがない場合は、その結合を生成しない。
- **経路と履歴**: 結合の経路は新セルの配置とポート位置から再計算する。セル群と結合の追加を1つの`PasteCommand`で適用し、1回のUndoでともに取り消し、Redoで同じ対応関係を復元する。スナップショットとID割り当てをコマンドの入力として固定し、履歴再生中に現在の選択やクリップボードを読み直さない。
- **アプリ内クリップボード**: 元の位置から10mm（`PASTE_OFFSET_MM`）ずらし、大きさ・属性を引き継ぐ。所属リージョンは元のものを引き継ぐが、貼り付け先ファイルにそのスコープが無ければルートにする（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 03 モデル設計|第3章3.3節]]）。
- **OSクリップボードのCDL断片**: 位置・リージョンは含めず、所属はルート、大きさは既定値、位置は(20, 20)mm（`PASTE_ANCHOR_MM`）から10mm刻みで斜めに並べる。複数セルの断片には選択セル間の結合代入を含め、解析結果もセルと結合を保持する。外部セルを参照する代入から元の図のセルへの結合を作らない。

**契約の検証条件（実装時）**:
- 単一セルは、外部セルへの結合・自己結合の有無にかかわらず、結合なしで複製される。
- A・Bを選択した場合、A→B／B→Aの結合は線を選択していなくても保持され、A・Bと選択外Cとの結合は複製されない。結合のない複数セルは結合なしで複製される。
- アプリ内・OS経由の両方で、新セル名の衝突回避後も端点と配列添字が対応し、元セルへ結ばれない。コピー後の元セル・結合の変更でスナップショットは変わらない。
- 貼り付け先で1セルを選択していても複数セル断片の内部結合は保持される。貼り付け全体のUndo／Redo、再貼り付け、片端のセルタイプ未解決でもID・結合の整合が保たれる。

> [!note] 当初のスケッチからの更新（2026-09-11、2026-10-21 に整理）
> 当初（2026-09-05）のスケッチは、`ClipboardGateway`を同期の`writeText(): void`／`readText(): string`とし、preloadが`clipboard`を直接ブリッジする想定で、`PasteCommand`が`apply()`内で読み取り、`CutCommand`が`apply()`内で書き込む設計だった。実装で次のとおり変わった（[[work/active/tecs/TECSCDE-DT-EL PasteCommand非同期クリップボード決定|決定記録]]）。
> - **`ClipboardGateway`は非同期でipcMain経由**: 実機確認で、preloadに公開される`electron`モジュールには`clipboard`が含まれないと分かった（ESM／CJSを問わず）。そのため`file`・`tecsgen`と同じく`ipcRenderer.invoke`→`ipcMain.handle`の経路になり、読み書きは`Promise`を返す。
> - **`PasteCommand`は`ClipboardGateway`を持たない**: `Command.apply()`は純粋な同期処理なので、非同期の読み取りはコマンドの外（`clipboard-actions.ts`）で済ませ、解決済みの文字列（`string | undefined`）を受け取る。
> - **`CutCommand`は副作用を持たない**: `History.current`が`past`を先頭から再生（replay）する設計のため、`apply()`に書き込みがあると再描画のたびに再実行される。書き込みは`AppStore.cutSelection`が`apply()`を通さず1回だけ行い、`CutCommand`は`DeleteCommand`と同じ純粋なモデル削除（`kind`が`Cut`であるだけの違い）。`CopyCommand`は履歴に入らないので、この問題は起きない。
> - 実装コメントは、非同期化の理由に「Electron 44でclipboardモジュールが非同期化された」ことも挙げるが、ここでは検証していない。上の「preloadから使えない」ことが、現行の経路の直接の理由である。

### 4.2 可変長配列ポートの要素挿入（2026-11-07、監査#12）

継承元のコマンド一覧に、`InsertArrayPortElementCommand(plan)`（案）を追加する。[[TECSCDE-DT-EL内部仕様 - 04E 可変長配列ポートの要素挿入|4E]]が、Insertの対象判定、固定長拒否、後続要素の再添字、結合の同一性と参照更新、配置、1操作1Undoの契約を定める。計画・新規IDはdispatch前に固定し、`apply()`は同期・副作用なしとする。拒否通知は履歴の外で行い、成功した変更だけを履歴へ入れる。現行のコードがこの追加契約を満たすかは未確認。

### 4.3 配列ポートの要素削除（2026-11-07、監査#13）

[[TECSCDE-DT-EL内部仕様 - 04F 配列ポートの要素削除|4F]]に、Deleteの結合解除優先と`DeleteArrayPortElementsCommand(plan)`（案）を追加する。選択ポートに結合があれば既存の結合削除だけを行い、すべて未結合なら要素削除へ進む。固定長・添字0の拒否は要素削除に適用し、結合解除の可否と混同しない。複数要素は元のID・添字で計画し、全対象を検証してから一括削除・再添字する。各操作を1Undoとし、拒否・no-opは履歴を増やさない。計画は固定した入力で再生し、通知は`apply()`の外で行う。実装適合は未確認。

### 4.4 再配置・全体再配置（2026-11-08、監査#11）

[[TECSCDE-DT-EL内部仕様 - 04G 再配置コマンド設計|4G]]に`RelayoutSelectedCellsCommand(plan)`と`RelayoutAllCellsCommand(plan)`（案）を追加する。前者は選択した編集可能セル、後者は選択によらず全編集可能セルを対象とし、共通の純粋な配置計算と`RelayoutCellsCommand`の一括適用を使う。対象外セルは固定障害物とし、現在用紙内で配置・関係結合の経路を計画する。1操作1Undo、拒否・変更なしは履歴なしとし、計画中や`apply()`からUI・診断を副作用更新しない。実装適合は未確認。

### 4.5 履歴位置と保存済み状態の識別（2026-11-08、監査#21）

[[TECSCDE-DT-EL内部仕様 - 07J 保存チェックポイントと未保存判定|7J]]に従い、文書世代と一意な`HistoryNodeId`で履歴位置を識別する。commitは新しいID、Undo/Redoは既存ノードへの移動とし、同じ深さの分岐へIDを再利用しない。`apply()`の再生中にIDを生成せず、既存の純粋な再生とUndo/Redoの方式は維持する。未保存判定はソース別保存状態との比較を根拠とし、履歴長やノードIDだけでcleanへ戻さない。no-op・表示のみでは編集ノードを作らず、履歴剪定でも保存済みの比較状態を保持する。現行`5cf2d85`の`History`・未保存判定はこの契約に未反映であり、7J.0の確認結果と実装受入条件に従う（2026-11-08、三者監査#3）。

### 4.7 結合の自動経路と他セルの回避（2026-10-24、親外部仕様7.3.2）

結合の経路を自動生成・再計算するとき、他のセルの矩形と重ならない候補を優先する。軽量な範囲に限り、すべての交差を除く保証はしない（親外部仕様7.3.2。4.6.2の「要件としない」を、同じく将来課題としていた7.3.2で一部実現したもの）。

- **入口**: `autoRouteBars(from, fromEdge, to, toEdge, obstacles = [])`（`model/geometry.ts`）。`obstacles`は他のセルを含む全セルの矩形（`RectMm`、`Cell`が構造的に満たす）。呼び出しは、読み込み時に保存済みの経路が無い結合（`cdl/document-builder.ts`）、`CreateJoinCommand`、`rerouteJoin`（セル移動・整列・ポート辺変更に伴う再計算、`commands/support.ts`）の3か所で、いずれも`doc.cellValues()`を渡す。保存済みの経路は従来どおり再計算しない。
- **既定の経路**: 従来どおりのL字（ポートから`DIST_PORT_MM`だけ出て、1回曲がり、受け口側へ入る）。ポート直後の点（`p1`）から`p2`までの区間が、どの矩形の内部も横切らなければ、これを返す。**障害物が無い、または邪魔にならないときの結果は従来と同一**（再計算のたびに経路が変わらない）。
- **候補**: 既定が矩形を横切るときだけ、(1) もう一方のL字、(2) コの字（中間の垂直線`x`、または水平線`y`を置く5区間の経路）を加える。`x`・`y`は、`p1`と`p2`の中間と、各矩形の外側`DIST_PORT_MM`の位置（いずれも`alignRound`で1mmに丸める）。
- **選択**: 区間が内部を横切る矩形の数が最小のもの。同数なら短いもの。既定より改善する候補が無ければ既定を返す。縁に沿う・接するだけは交差に数えない。ポートから出る・入る短い区間は数えない。
- **制約**: 水平・垂直のバーのみ（外部仕様10.3 #4）。コの字の経路は5本のバーになるが、保存・読み込み・バー移動（先頭と末尾は移動不可）は本数に依存しない。他の矩形の外側に置いた線が別の矩形を横切ることはあり、その場合は交差の少ない方が選ばれる。
- **テスト**: `auto-route.test.ts`（純関数）、`route-avoidance.test.ts`（読み込み・結合作成・セル移動・再計算）。共有フィクスチャの`cController1.cLog`は、従来`cSensor1`を貫く直線だった（保存済みの経路が無いため）。回避の導入で経路が変わり、座標を決め打ちしていた`hit-tester.test.ts`・`gesture-controller.test.ts`は、経路から最長の途中バーの中点を求める形に改めた。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 04 編集コマンドとUndo-Redo設計|TECSCDE-TS内部仕様 第4章（基礎設計。DT-ELの追加・変更は本章の各節を優先）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 06B 編集操作（後半）|TECSCDE-DT外部仕様 第6章後半（OSクリップボード連携の一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章（ClipboardGatewayの設計根拠）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

- [[TECSCDE-DT-EL内部仕様 - 監査対応 19-28 配列と配置]] — 該当する監査項目の契約補足（2026-11-09）。

- [[TECSCDE-DT-EL内部仕様 - 監査対応 29-38 保存と画面]] — 該当する監査項目の契約補足（2026-11-09）。

- [[TECSCDE-DT-EL内部仕様 - 監査対応 39-48 編集と表示]] — 該当する監査項目の契約補足（2026-11-09）。
