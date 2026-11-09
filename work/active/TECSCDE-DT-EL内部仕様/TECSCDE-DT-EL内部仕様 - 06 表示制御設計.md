---
date: 2026-09-05
description: "TECSCDE-DT-EL内部仕様書 第6章（表示制御設計）— TS内部仕様を基礎とし、6.4節で検索ハイライト描画・Esc解除を具体化。表示フィルタは第6B章を優先。rendererプロセスで動作。"
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
> V0.2.0のactiveOnly・結合強調・リージョン矩形モード、表示制御バー廃止に伴うUI移行は[[TECSCDE-DT-EL内部仕様 - 06C V0.2.0表示と配置]]を優先します。差分章は実装前の内部設計です。


Domain note split from [[TECSCDE-DT-EL内部仕様]] (2026-09-05). Chapter 6 of 11。

## 6. 表示制御設計

`ViewState`・`DisplayFilters`のクラス設計は、[[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様第6章]]を基礎とする。**検索ハイライトと解除処理は本章6.4節、表示フィルタは第6B章の具体化を優先する。** ズーム・パン・グリッド・フィルタ・検索の状態はUIに閉じた表示状態であり、Electronのプロセス境界とは無関係に本モジュール（F）はrendererプロセスで完結する。`TecscdeDocument`（第3章）とは型として分離し、`.cde`形式に含めない方針も変更なし。

本章・第6B章で具体化した事項以外の詳細は[[TECSCDE-TS内部仕様]]第6章を参照。

> [!note] 実装での設計更新（2026-09-09）
> - **パン（Pan）の実現**: SVG レベルでの `transform`/`viewBox` 操作ではなく、シェル（モジュールG）側の HTML スクロールコンテナ（`pan-scroll.ts`、`panCenter`(mm) ⇔ `scrollLeft/Top`(px)）で実現。描画層の `CanvasView` は `panCenter` を読まない。

> [!note] 表示フィルタの詳細設計（2026-10-23）
> `DisplayFilters`（6.5節）の型の作り替え、表示制御バーのUI、色分け・凡例、結合スタブ、検索との連携は[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計|第6B章]]に定めた。6.5節について、TS内部仕様の記述より第6B章を優先する。

### 6.4 検索ハイライトと解除（2026-10-25具体化）

外部要求は[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能#7.4.2 JS 版の規定|外部仕様7.4.2]]（DT外部仕様第7章から継承）。一致するセル・結合の強調を、選択状態の二重線矩形およびセル名強調から独立させる。以下はDT-ELの規範となる具体設計であり、実装済みの記録ではない。

#### 6.4.1 状態と責務

- 検索語の唯一の保持先は`AppStore.view.searchQuery: string | null`。既存の`ViewState.withSearchQuery(query)`で更新し、空文字・空白のみは`null`へ正規化する。
- 一致判定は既存の純関数`searchDocument(doc, query, hiddenRegionIds)`を用いる。セル名・セルタイプ名・結合ラベルを検索し、表示フィルタに関わらずモデル全体を対象とする。
- 描画用の`SearchHighlights`は次の読み取り専用インターフェースとし、検索結果から毎回導出する。`SearchHit.kind`に従ってIDを集合化し、結合の一致をその両端セルの一致へ置き換えない。

```ts
interface SearchHighlights {
  readonly cellIds: ReadonlySet<CellId>;
  readonly joinIds: ReadonlySet<JoinId>;
}
```

- `SearchHighlights`を`TecscdeDocument`・`SelectionState`・`DisplayFilters`に格納しない。独立した永続ストアも設けず、`.cde`・セッション設定・Undo/Redo履歴に含めない。
- `AppShell.render()`は、その描画で使うドキュメント・検索語・非表示リージョン集合から検索結果を求め、結果一覧と描画用集合を同じスナップショットに揃える。`SearchBoxView`はその結果を一覧表示・巡回に用い、描画用集合を所有しない。
- `SvgRenderer.render()`の既存の描画オプション（`joinPreview`を渡す引数）へ`searchHighlights?: SearchHighlights`を追加する。省略時は両集合が空として扱う。`ViewState.toCanvasView(regions)`の責務は変更せず、`CanvasView`へ検索語やドキュメント参照を追加しない。
- `SvgRenderer`はセル・結合ごとの一致フラグを`CellRenderer`・`JoinRenderer`へ渡す。描画層は検索処理を呼ばず、受け取った集合だけを参照する。IPC・main・preloadへの追加は不要。

#### 6.4.2 描画方式

検索一致はすべて同じ様式で強調する。「次を検索」「前を検索」で現在のヒットが変わっても、他の一致の強調を消さない。現在のヒットは結果一覧の既存の`current`クラスで示す。

| 対象 | SVGと描画規約 |
|---|---|
| セル | セル本体の矩形より各辺を0.8mm外へ広げた`<rect class="search-highlight search-highlight-cell">`。`fill="none"`、`stroke="#b45309"`（濃い琥珀色）、`stroke-width="3"`、`stroke-dasharray="6 3"`。セル本体・文字の背面に置く |
| 結合 | 通常線と同じ可視経路の`<polyline class="search-highlight search-highlight-join">`を通常線の直前に描く。`fill="none"`、`stroke="#b45309"`、`stroke-width="6"`、`stroke-linecap="round"`、`stroke-linejoin="round"`。通常線を上に重ね、両側に色付きの縁が見えるようにする |

- セルの枠は既存の`<g data-cell-id>`内、結合の強調線は既存の`<g data-join-id>`内に置く。これによりグループの移動・非表示に通常図形と一緒に追従する。
- 両者に`vector-effect="non-scaling-stroke"`を指定し、線幅を画面上のCSS pxで一定に保つ。`pointer-events="none"`・`aria-hidden="true"`とし、ヒットテスト・ドラッグ・ポート操作の対象にしない。
- 既存の選択枠・選択ハンドルは検索強調より前面へ描く。一致する対象を選択した場合は両方を表示し、検索していない対象を選択しても一致対象の強調を残す。
- セルの塗り・通常の枠線・読取専用等のクラス・リージョン色の帯・セル名強調は維持する。検索強調のために`SelectionState`を変更しない。
- 非表示セルは強調も描かない。結合は既存の可視性規約に従い、両端非表示なら強調なし、片端非表示なら通常線と同じスタブ部分だけを強調する。検索一致だけではフィルタを変更せず、ヒットへのジャンプ時に[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 06B 表示フィルタUI設計#6B.8 検索との連携（外部仕様7.4.2）|6B.8節]]に従って必要なリージョンを表示する。

#### 6.4.3 更新と差分描画

- 検索語の入力・解除、ドキュメントの編集・Undo/Redo・差し替え、フィルタ変更の通知で一致集合を再計算する。消えた要素のIDを前の描画から持ち越さない。
- `SvgRenderer`の差分更新は、一致フラグの変更をセル・結合の再描画条件に含める。モデルの参照が同じでも、検索語が変われば強調を追加・除去する。集合の内容が同じなら集合の参照が変わっただけで全要素を再生成する必要はない。
- ズーム・パン・リージョン表示の変更後も、通常図形と強調図形の座標・表示範囲を一致させる。セルのドラッグプレビューは既存グループの`transform`に追従させ、`JoinRenderer.previewBars()`では通常線と強調線の両方の`points`を更新する。プレビュー解除時も両方を確定経路へ戻す。
- ヒットへのジャンプで行う選択・パンは既存動作を維持するが、その後の選択変更と検索一致集合の更新は独立とする。

#### 6.4.4 Escによる解除（F5）

`AppShell.bindKeyboard()`がwindowの`keydown`を受け、テキスト入力欄を除外する判定およびCtrl/Metaの判定より先に次を処理する。

1. `event.key === "Escape"`かつ`event.isComposing === false`で、検索語が`null`でなければ`preventDefault()`し、`store.setView(store.view.withSearchQuery(null))`を1回呼ぶ。検索欄・キャンバス・他の入力欄のいずれにフォーカスがあっても有効とする。
2. ストア通知による再描画で、検索入力を空文字へ同期し、結果一覧・件数表示・一覧の現在位置（`cursor = -1`）・セルと結合の検索強調を除去する。
3. 選択状態・表示フィルタ・ズーム・パン・ドキュメント・dirty状態・編集履歴は変更しない。検索ジャンプで緩めたフィルタも元に戻さない（6B.8節）。
4. IME変換中のEscでは検索語を変更しない。検索語が既に`null`なら検索解除としては何もせず、不要なストア通知も行わない。
5. `stopPropagation()`・`stopImmediatePropagation()`は呼ばない。既存の結合作成・結合バー移動のキャンセルやポップオーバーの閉鎖と同じEscで成立させる。既存ハンドラを検索解除だけで抑止しない。

検索語を入力欄から空にした場合も、同じ`withSearchQuery`の正規化と再描画により一覧・検索強調を解除する。解除処理を編集コマンドとしてdispatchしない。

#### 6.4.5 受入・検証項目

1. 検索一致セルには破線枠、検索一致結合には通常線の背面の太い線が表示される。複数一致・一致なし・空の検索語を確認する。
2. 一致対象と別の対象を選択しても検索強調が残り、同じ対象を選択したときは選択枠と検索強調を区別できる。セル名強調・リージョン色・読取専用表示との同時表示を確認する。
3. 検索語変更・モデル編集・Undo/Redo・ドキュメント差し替えで、古い一致の図形が残らない。通常の図形が変化しない検索語変更も差分描画する。
4. 非表示セル・両端非表示結合に強調が出ず、片端非表示の結合はスタブだけを強調する。ジャンプ後は緩めたフィルタで通常経路と強調が一致する。
5. 検索欄・キャンバス・他の入力欄からのEsc、空の検索でのEsc、IME変換中のEscをDOMテストで確認する。解除前後の選択・フィルタ・パン・dirty状態・履歴を比較する。
6. 検索中の結合作成・結合バー移動をEscでキャンセルしたとき、検索も解除され、モデルが変更されないことを確認する。
7. 実画面で5%・100%・200%のズーム、パン、結合経路プレビューを確認し、線幅・重なり順・文字の可読性・通常操作を妨げないことを検証する。

> [!note] 設計と実装の区別
> 本節の追加時点では、検索結果一覧とジャンプ処理は既存実装にある一方、キャンバス上の検索専用ハイライトは未実装。Escによる検索状態解除はF5作業ブランチに実装・テスト済みであり、本節全体の実装完了を意味しない。

## Related

- [[work/active/TECSCDE-TS内部仕様/TECSCDE-TS内部仕様 - 06 表示制御設計|TECSCDE-TS内部仕様 第6章（基礎設計。検索は本章6.4節、フィルタは第6B章を優先）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---

- [[TECSCDE-DT-EL内部仕様 - 監査対応 49-58 出力と検索]] — 該当する監査項目の契約補足（2026-11-09）。
