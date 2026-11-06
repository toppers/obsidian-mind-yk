---
date: 2026-10-23
description: "TECSCDE-DT-EL内部仕様書 第6章6.5節の詳細設計（外部仕様7.5.2。2026-10-24に実装済み）— リージョン/ネームスペースのフィルタ・色分け・シグニチャ名表示を表示制御バーで切り替える。DisplayFilters型の作り替え、描画層への色の渡し方、結合スタブ、検索との連携、UI結線を定める"
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

> [!info] V0.2.0差分設計（2026-11-06）
> 本章の表示制御バーのUI配置と実装完了記録は従来版の設計・経緯です。V0.2.0ではバーと領域開閉操作を廃止し、[[TECSCDE-DT-EL内部仕様 - 02B V0.2.0画面構成]]・[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]を優先します。フィルタ・色分け・凡例・検索連携の機能は保持します。差分章は実装前の内部設計です。


Domain note split from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06 表示制御設計|TECSCDE-DT-EL内部仕様 第6章]]（2026-10-23）。外部仕様は[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能|親外部仕様7.5.2]]（DT外部仕様第7章は「同一」）。**2026-10-23〜24に実装済み**（`E:/Ccur/typescript/TECSCDE-DT-EL`、6B.10の1〜7番）。実機の目視確認は、色分けの帯・シグニチャ名の切り替え・表示制御バーまで済み。リージョン木、凡例、結合スタブ、検索との連携は未確認。

本章策定時点（2026-10-23）の第6章は「TS内部仕様と同一」とし、`DisplayFilters`の型と純関数だけが実装されていた。本章はその型を外部仕様に合わせて作り替え、**表示制御バーのUI・描画層・検索との結線**を定める。型の作り替えは破壊的変更を含む（6B.1）。2026-10-25の第6章6.4節の具体化では、本章のフィルタ設計を保ったまま検索専用ハイライトとEsc解除の規約を追加した。

## 6B.0 実装前の現状と外部仕様とのずれ（2026-10-23、ソース読解による。**すべて解消済み**）

| # | 外部仕様7.5.2 | 現状 | 本章の対応 |
|---|---|---|---|
| 1 | 表示制御バーに3種の切り替えを設ける | UIが無い。`DisplayFilters`は`app/`から一度も使われない | 6B.6、6B.7 |
| 2 | リージョン木を一覧し、**チェックを外した**リージョンのセルを非表示 | `regionFilter`が単一値で、「このリージョン配下のみ表示」という逆の意味 | 6B.1、6B.2 |
| 3 | ネームスペースは**リージョンと同じ機構**。2つ目のUIは設けない | `namespaceFilter`が別フィールドとして存在 | 6B.1（削除） |
| 4 | 色分け。同じリージョンは常に同じ色。オンなら凡例 | `colorByRegion`は保持するだけで、描画層（`CanvasView`）が読まない。凡例なし | 6B.3〜6B.5、6B.6 |
| 5 | シグニチャ名表示は**既定オン** | 既定`false`（`allVisible()`と`defaultCanvasView()`） | 6B.1 |
| 6 | 一端だけ非表示の結合は、境界に**スタブ**を付けて描く | 両端非表示でのみ消す。一端だけなら、非表示セルの位置まで線を引いたまま | 6B.5 |
| 7 | 検索はフィルタに関わらず全体が対象。ヒットが非表示なら**フィルタを一時的に緩める** | `searchDocument`は`revealed`印を付けるだけで、`jumpTo`はフィルタを緩めない | 6B.8 |

上の表は実装前の状態の記録である。7項目とも、6B.10の順に実装して解消した。

## 6B.1 `DisplayFilters`の作り替え

```ts
class DisplayFilters {
  private constructor(
    /** 利用者がチェックを外したリージョン。そのリージョンと全子孫が非表示（6B.2）。根は含めない。 */
    readonly hiddenRegions: ReadonlySet<RegionId>,
    readonly colorByRegion: boolean,        // 既定 false
    readonly showSignatureNames: boolean,   // 既定 true（外部仕様7.5.2。現行版の常時表示を踏襲）
  ) {}
  static allVisible(): DisplayFilters;      // new DisplayFilters(new Set(), false, true)
  get isAllVisible(): boolean;              // hiddenRegions.size === 0
  withRegionHidden(id: RegionId, hidden: boolean): DisplayFilters;
  withRegionsRevealed(ids: Iterable<RegionId>): DisplayFilters;  // 検索用（6B.8）
  withAllRegionsShown(): DisplayFilters;
  withColorByRegion(on: boolean): DisplayFilters;
  withShowSignatureNames(on: boolean): DisplayFilters;
  equals(other: DisplayFilters): boolean;
}
```

- **`regionFilter`と`namespaceFilter`を削除する。** 外部仕様7.5.2は「ネームスペース単位のフィルタはリージョンと同じ機構で提供し、独立した2つ目のUIは設けない」と定める。`Region.namespacePath`は`RegionId`と同じ文字列（`buildRegionTree`が`asRegionId(path)`を使う）なので、木の節点のチェックがそのままネームスペースの階層に一致する。AND条件の合成も不要になる。
- 型の変更は`display-filters.ts`、`view-state.ts`（`toCanvasView`）、`render/view.ts`の`defaultCanvasView()`（`showSignatureNames: true`へ）、既存テストに及ぶ。`.cde`には保存しない方針は変えない（シリアライザは参照しない）。
- 既定の変更（#5）は、現行の見た目（シグニチャ名が出ない）を変える。外部仕様どおりである。

## 6B.2 非表示リージョンの解決

`resolveHiddenRegionIds(filters, regions)`は、`hiddenRegions`の各節点について**その部分木のIDをすべて集めた和集合**を返す。

- 根（`ROOT_REGION_ID`）は常に表示する（セルは実リージョンに属する、現行実装と同じ）。`hiddenRegions`に根が入っていても無視する。
- `RegionTree`に存在しないIDは無視する（別のファイルを開いた後や、貼り付けでリージョンが変わった後の取り残し）。
- 親を非表示にすると子孫も非表示になる。UIでは、非表示の祖先を持つ節点のチェックは無効にして押せなくする（6B.6）。子を単独で表示に戻す操作は設けない（木の意味と食い違うため）。

## 6B.3 `CanvasView`の拡張

`render/view.ts`の`CanvasView`に、描画層が色を読むための面を足す。

```ts
readonly regionColors: ReadonlyMap<RegionId, string> | null;  // null = 色分けなし
```

`ViewState.toCanvasView(regions)`が、`colorByRegion`がオンなら`regionColorMap(regions)`を、オフなら`null`を設定する。描画層は`ViewState`にも`DisplayFilters`にも依存しない、という第5章の方針は変えない。`setsEqual`による変更検出（`svg-renderer.ts`）には`regionColors`の参照比較を加える（`regions`が変わらない限り同じMapを再利用する）。

## 6B.4 色の割り当て（「同じリージョンには常に同じ色」）

- 固定のパレット（暫定12色、色覚多様性に配慮した彩度の低い色。具体値は実装時に定める）を`view-state/region-colors.ts`に置く。
- リージョンIDの文字列に**FNV-1aの32ビットハッシュ**をかけ、パレットの長さで割った余りを色の番号とする。登録順や木の形に依存しないため、リージョンが増減しても、別のファイルを開いても、同じIDは同じ色になる。
- **根（`::`）は無色**（色分け対象外）。
- 衝突（異なるリージョンが同じ色になること）は許容する。色だけに依存させない、という外部仕様4.9.2の方針により、識別は凡例とセルの選択時のステータス表示で補う。12個を超えるリージョンを持つ図では衝突が起きうることを、利用者向けの文書に書く。

## 6B.5 描画層の変更

### セルの色

セルの塗り（`.cell-rect`の`fill`）は編集可否（`.readonly`）、枠は未解決（`.unresolved`）に使われている。そこで**リージョンの色は、セルの左端に沿う細い帯**として描く。

- `CellRenderer`は`ctx.view.regionColors`が非`null`で、かつ`cell.regionId`に色があるとき、セル矩形の左端に幅`REGION_TAB_MM`（暫定2mm）、高さがセルと同じ`<rect class="region-tab">`を、`fill`に色を指定して追加する。色が無い（根、または色分けなし）ときは追加しない。
- 状態を表すクラス（`readonly`、`unresolved`、`system-defined`）には触れない。

### 結合のスタブ（外部仕様7.5.2）

- 両端が可視なら通常どおり、両端が非表示なら完全に非表示（現行どおり）。
- **一端だけが非表示のとき**、可視側の端点から折れ線に沿って`STUB_LEN_MM`（暫定4mm）だけを描き、先端に結合方向と直交する短い横線（`STUB_TICK_MM`、暫定2mm）を添える。クラスは`join-stub`とし、`<title>`に非表示側のセル名とリージョンを入れる（ホバーで見える）。
- 実装は`svg-path.ts`に純関数`truncatePolyline(points, lengthMm)`を追加し、`JoinRenderer`が`ctx.sourceHidden` / `ctx.targetHidden`を受けて切り替える。`SvgRenderer.reconcileJoins`が両端の非表示を判定して渡す。ラベル（シグニチャ名）はスタブには付けない。
- **ヒットテスト（実装で確定、2026-10-24）**: `HitTester`は`CanvasView.hiddenRegionIds`を読み、(1) 非表示リージョンのセルを、ポート・セル本体・矩形選択のいずれでも対象から外す（それまでは見えないセルを掴めた）。(2) 一端が非表示の結合は、スタブの部分の線分だけを対象にし、当たった線分の番号は`joinStub`の`segmentIndices`で元の結合の番号へ戻す。選択枠もスタブの部分だけを描く。純関数は`truncatePolyline`・`stubTick`・`joinStub`（`render/svg-path.ts`）。

## 6B.6 表示制御バーのUI

外部仕様3.1.2の「表示制御バー」を、ツールバーの直下に`#display-bar`として追加する（`index.html`）。

| 部品 | 内容 |
|---|---|
| 「リージョン」ボタン | 押すと下にポップオーバー（リージョン木）を開く。1つ以上を非表示にしているときは「リージョン（N件非表示）」と表示する |
| 「色分け」チェック | `colorByRegion`の切り替え |
| 「シグニチャ名」チェック | `showSignatureNames`の切り替え（既定オン） |

**リージョン木のポップオーバー（`app/region-filter-panel.ts`、新規）**

- `RegionTree`を`::`区切りの階層で表示する。各節点に「チェックボックス」「リージョン名（末尾の要素）」「所属セル数」。根は表示しない。
- チェックを外す／入れる操作は`store.setView(view.withFilters(filters.withRegionHidden(id, hidden)))`を呼ぶ。祖先が非表示の節点のチェックは無効にして薄く表示する（6B.2）。
- 「すべて表示」ボタンは`withAllRegionsShown()`。
- 色分けがオンのとき、各節点に色見本を付ける（凡例を兼ねる、下記）。
- 木はドキュメント変更のたびに再構築するが、チェック状態は`hiddenRegions`から導くので失われない。
- ポップオーバー外のクリックかEscで閉じる。

**凡例（`app/region-legend.ts`、新規）**

色分けがオンのとき、`#canvas-area`の左下に`#region-legend`を重ねて表示する（ナビゲータは右下）。一覧は「色見本＋リージョン名」で、**非表示のリージョンは含めない**。オフのときは`hidden`にする。キャンバスのスクロールには追従させない（`position: absolute`）。

> [!note] セル選択時の所属リージョン表示
> 外部仕様4.9.2は、凡例のほかに「セルを選択したとき所属リージョンをステータス表示に示す」ことも定める。ステータスバーとプロパティパネルの側の設計であり、本章の対象外とする。[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧|差分一覧]]で別途扱う。

## 6B.7 ストアとシェルへの結線

- 状態は既存の`AppStore.view`（`ViewState.filters`）にある。新しい状態は増やさない。
- `Shell`が`#display-bar`の2つのチェックを`store.setView(...)`に結び、`store.subscribe`でチェックの表示を状態に合わせる。
- **別のファイルを開く、または「消去」したとき、`hiddenRegions`を空に戻す**（`withAllRegionsShown()`）。IDが旧ドキュメントのものになるため。`colorByRegion`と`showSignatureNames`は保つ。
- 保存対象に含めない（外部仕様7.5.2）。アプリ設定（`app-settings`）にも保存しない。起動のたびに既定に戻る。

## 6B.8 検索との連携（外部仕様7.4.2）

- `searchDocument`は引き続き表示フィルタに関わらずモデル全体を対象とする。
- `SearchBoxView.jumpTo(index)`が、ヒットしたセル（結合なら両端のセル）の**リージョンと祖先を**`hiddenRegions`から外す（`filters.withRegionsRevealed(ids)`）。その結果リージョン木のチェックも更新される。これが「フィルタを一時的に緩める」の実体で、元に戻す操作は設けない（利用者が木で再び外す）。
- 緩めた事実は一覧の`revealed`印（既存）で見える。
- 実装: `regionsToReveal(doc, hit)`（`view-state/search.ts`）が外すIDを返し、`SearchBoxView.jumpTo`が`withRegionsRevealed`を呼ぶ。祖先を含めるのは、祖先が非表示だと子孫も隠れるため（6B.2）。結合のヒットは両端のセルについての和集合。

検索ハイライトの具体的な描画方式・描画状態の受け渡し・Escによる解除・検証項目は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06 表示制御設計#6.4 検索ハイライトと解除（2026-10-25具体化）|第6章6.4節]]に定める。Escで検索を解除しても、本章のフィルタ緩和は元に戻さない。

## 6B.9 テスト

`tests/renderer/`に追加・更新する（既存の`display-filters`系を含む）。

1. `DisplayFilters`: 既定値（シグニチャ名がオン）、`withRegionHidden`の不変性、`withRegionsRevealed`。
2. `resolveHiddenRegionIds`: 部分木の和集合、根を含まない、未知のIDの無視、親子の両方を外した場合。
3. `regionColorMap`: 同じIDは常に同じ色、根は色なし、IDの登録順に依存しない。
4. `CellRenderer`: `regionColors`が`null`のとき`region-tab`が無い、あるときに色が付く、`readonly`などのクラスが変わらない。
5. `truncatePolyline`: 長さが線全体より短い・長い場合、直角に曲がる点をまたぐ場合。
6. `SvgRenderer.reconcileJoins`: 両端可視、一端非表示（スタブ）、両端非表示（消える）。
7. `SearchBoxView.jumpTo`: 非表示リージョンのヒットで`hiddenRegions`から外れる。
8. `RegionFilterPanel`: チェックの操作が`setView`へ届く、非表示の祖先を持つ節点が無効になる（happy-domで検証可能）。

実機でしか確かめられないもの（ポップオーバーの位置、凡例の重なり、スタブの見え方）は、ズーム・パン確認（[[work/active/tecs/TECSCDE-DT-EL ズーム・パン対話的確認チェックリスト|チェックリスト]]）と同じ方式で目視確認の項目に加える。

## 6B.10 実装順（すべて実装済み、DT-ELリポジトリのコミット）

1. `DisplayFilters`の作り替え（6B.1、6B.2）とテスト。`CanvasView.showSignatureNames`の既定を`true`へ。（`da603e0`、2〜4と同一コミット）
2. `regionColorMap`と`CanvasView.regionColors`（6B.3、6B.4）、`CellRenderer`の帯（6B.5前半）。（`da603e0`）
3. `#display-bar`、2つのチェック、`Shell`の結線（6B.6、6B.7）。ここで色分けとシグニチャ名の切り替えが実機で動く。（`da603e0`）
4. `RegionFilterPanel`とフィルタの結線。ファイルを開いたときのリセット（`AppStore.loadDocument`、参照追加の`keepDirty`では保つ）を含む。（`da603e0`）
5. 凡例（`app/region-legend.ts`。名前は`namespacePath`で出し、非表示のリージョンは載せない）。（`50909a4`）
6. 結合スタブ（6B.5後半）と、非表示セルのヒットテスト除外。（`5fd550d`）
7. 検索との連携（6B.8）。（`3a87b29`）

## 6B.11 セル名強調（2026-10-24、親外部仕様7.4.2）

表示制御バーの3種に並ぶ4つ目の切り替え。オンでセル名を大きく表示し、セルタイプ名を隠す。オフで両方を通常表示する。検索のハイライトとは独立で、同時にオンにできる。

- **状態**: `DisplayFilters.emphasizeCellName`（既定オフ）。`withEmphasizeCellName(on)`を足し、他の切り替え（`withRegionHidden`など）で値が落ちないようにした。`CanvasView.emphasizeCellName`へ射影し、`SvgRenderer`の変更検出に含める。`.cde`には保存しない（他の切り替えと同じ）。
- **描画**: `CellRenderer`は、オンのときセル名の`<text>`に`emphasized`クラス（14px・太字、暫定）を付け、セルの中央（`dominant-baseline: middle`）に置き、セルタイプ名の`<text>`を作らない。セル名の長さがセルの幅に収まらない場合の扱い（切り詰め・縮小）は決めていない。
- **UI**: `#display-bar`に「セル名強調」のチェック（`#filter-emphasize`）。他の2つと同じく、チェックは常に`DisplayFilters`の状態に従う。
- **テスト**: `view-state.test.ts`（既定・独立・`equals`・射影）、`cell-renderer-emphasis.test.ts`（既定の表示、オン、色の帯との独立）、`shell.dom.test.ts`（実DOMのチェック）。

## 6B.12 選択時の所属リージョン表示（2026-10-26、親外部仕様4.9.2・F6）

色分け（7.5.2）だけに頼らずにリージョンが分かるよう、セルを選択したとき所属リージョンをステータスバーに示す（外部仕様4.9.2「色のみに依存させない」）。

- **関数**: `regionStatusText(doc, selection)`（`app/status-region.ts`）。選択中のセルのリージョンを集める。セルが選ばれていなければ空、1つのリージョンならそのパス（根は「ルート」）、複数にまたがれば「複数（N）」。結合の選択や文書に無いIDは数えない。
- **表示**: ステータスバーの`#status-region`（ズームの右）に「リージョン: ::N::A」の形で出す。`AppShell.refreshStatus`が描画のたびに更新する。
- **テスト**: `status-region.test.ts`（関数）、`shell.dom.test.ts`（選択の変化に連動してステータスが変わる）。

## 未決事項

- パレットの具体的な色、帯の幅（`REGION_TAB_MM` = 2mm）、スタブの長さ（`STUB_LEN_MM` = 4mm）、横線（`STUB_TICK_MM` = 2mm）は暫定値のまま。凡例・スタブ・検索の目視確認と合わせて決める。
- 12色を超えるリージョンで衝突したときに、色以外の手がかり（模様など）を足すか。
- 色分けオンのとき、読み取り専用セルの灰色の塗りと帯が見分けにくくならないか（実機確認）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06 表示制御設計|TECSCDE-DT-EL内部仕様 第6章（本章の親）]]
- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様 第6章6.5節（作り替え前の型）]]
- [[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能|親外部仕様 7.5.2]]
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — 外部仕様と内部仕様・実装の差分一覧|TECSCDE-DT-EL実装 — 差分一覧]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]
