---
date: 2026-09-16
description: "TECSCDE-DT-EL実装 の Action Items（2026-09-16〜09-21分）。[[TECSCDE-DT-EL実装]] が再度肥大化したため verbatim 分離。物理順を保持。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - implementation
---

Action Items satellite of [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]（2026-09-21、コア再肥大化により[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Action Items — 2026-09-06〜09-15|Action Items — 2026-09-06〜09-15]]に続き分離）。09-21以降の新規Action Itemsはコア側に残る。

## Action Items（2026-09-16〜09-21）

- [x] **PropertyPanelViewの未コミット編集消失バグを修正**（2026-09-20、コミット`d008840`）。「UI詳細（パレット・プロパティパネル等の操作感）の調整と機能検証」という残課題を具体化するため`palette.ts`・`property-panel.ts`・`search-box.ts`・`navigator-panel.ts`・`diagnostics-panel.ts`とAppStoreを読み直し、実際のバグを発見: `PropertyPanelView.render()`はAppStoreの`notify()`（`setView`・`setMode`・`setTecsgenDiagnostics`等、選択中セルのデータと無関係な更新でも発火）のたびに`replaceChildren()`で全`<input>`を再構築していたが、name/属性フィールドは`"change"`（blur/Enter）でのみコミットされるため、フィールド編集中に無関係なstore更新が起きると入力途中の内容がフォーカスごと無言で消えていた（`search-box.ts`は値差分ガードで既に対策済み、`navigator-panel.ts`/`diagnostics-panel.ts`は自由入力欄が無いため対象外）。`palette.ts`の`lastCelltypeSignature`と同じ再構築スキップ方式（選択・セル/結合データの署名が変化した場合のみDOMを再構築）で解消。`tests/renderer/shell.dom.test.ts`に再現テストを追加（入力ノードの同一性・フォーカス・値の保持を検証）、**192テスト全pass**、`npm run check`green（depcruise違反0件）
- [x] **実機`electron .`での初めての対話的目視確認、および2件の実バグ発見・修正**（2026-09-20、コミット`86ea408`）。ユーザーによる実機確認は2026-09-16のtree-sitter移行以降初めて（従来の「起動確認」は`electron .`がクラッシュしないことのみを見ており、ドキュメントが実際に読み込めることは未検証だった）。
  1. **起動時にセルが1つも表示されない**: `index.html`のCSP（`script-src 'self'`）がweb-tree-sitterの`WebAssembly.instantiate()`をブロックしており、`CdlGrammar.init()`が常に例外を投げ、起動ドキュメントの読み込みが無言で失敗していた（headless/happy-domテストはCSPを検証しないため未検出）。`script-src`に`'wasm-unsafe-eval'`を追加して解消。
  2. **セルを選択してもプロパティパネルが読み取り専用、セルをドラッグしても離すと元に戻る**: 調査の結果、両方とも同一原因と判明。`main/index.ts`の起動時サンプル読み込みが`openPaths([main.cde, celltypes.cdl])`の順で呼んでいたが、`openPaths()`は「最後のパスが編集対象、他は参照専用」（`file-service.ts`）という契約——実際にセル実体を持つ`main.cde`が参照専用（`editable: false`）に、セルタイプ定義のみの`celltypes.cdl`が編集対象になっていた。全セルが`editable: false`になった結果、プロパティパネルは読み取り専用表示になり、`MoveCellsCommand.apply()`（`cell-commands.ts:126`、`if (!cell || !cell.editable) continue;`）がドラッグによる移動を静かにスキップしていた（ドラッグ自体は動くがコミットされず「元に戻る」ように見えた）。引数順を`[celltypes.cdl, main.cde]`に修正して解消——ユーザーによる再確認で選択・プロパティ編集・ドラッグ移動のいずれも正常動作を確認。
  この主プロセス（`main/index.ts`）・CSP設定のバグはどちらも自動テストで検出できない種類（Electron実機のCSP適用・実際のマウスイベント座標変換はhappy-domの対象外）——今後も主要な変更後は実機での対話的確認を欠かさないこと。
- [x] **2026-09-20の実機対話的確認（4ラウンド）**: 保存・Undo/Redo・結合作成・tecsgen実行・Cut/Copy/Paste・検索・診断パネルを一通り確認し、計5件の実バグを発見・修正（保存インジケータ視認性、既定メニューによるCtrl+C/X/Vの横取り、clipboard未定義、Generate後の診断が認識できない、診断メッセージ文言）。コミット`f83ce0f`・`86ec0ff`。詳細は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜|Progress Log — 2026-09-16〜]]参照。194テスト全pass。
- [x] **`public/samples/main.cde`のテストfixture汚染リスクを解消**（2026-09-21、コミット`c5e7728`）。09-20の対話的テスト中、実機保存が同ファイルを上書きしテストスイート28件が一時破壊された（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装 — Progress Log — 2026-09-16〜|Progress Log]]参照）ことを受け、fixtureを`tests/fixtures/main.cde`へ複製し、直接読んでいた13テストファイルの参照先を差し替え。`public/samples/main.cde`はアプリのライブサンプル専用に戻り、実機保存がテストに影響しなくなった（`celltypes.cdl`は参照専用で保存対象外のため対応不要）。194テスト全pass、`npm run check`green。
- [x] **大規模CDLでのパース性能実測、tree-sitterバインディング選択（内部仕様11.2節#5）の未検証状態を解消**（2026-09-21、コミット`test(perf)`）。`tests/perf/cdl-parse.bench.test.ts`（既定skip、`RUN_CDL_BENCH=1`で実行）を新設し、150〜6000セル・100〜4000結合で`CdlDocumentLoader.loadSources()`のフルパイプライン時間を計測。6000セル・4000結合（現実のtecsgen CDL図では想定しづらい規模）でも中央値約75ms、スケーリングはほぼ線形で崖なし。web-tree-sitter（WASM）から`node-tree-sitter`（ネイティブ、mainプロセス移設が必要）へ切り替える性能上の根拠は無いと判断し、①WASM案のまま確定（詳細: [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|内部仕様第11章11.2節#5]]）。
- [x] **ズームが左上を基準にずれるバグを発見・修正**（2026-09-21、コミット`566de2e`）。[[work/active/tecs/TECSCDE-DT-EL ズーム・パン対話的確認チェックリスト|ズーム・パン確認チェックリスト]]でのユーザー対話的確認により発覚（当初「shiftキー+ホイールでズーム」と報告されたが、確認の結果`ctrlキー+ホイール`——実装通りの操作だった）。原因: 用紙（A4横277×190mm）がビューポートより小さい（低〜中倍率で頻発）場合、`pan-scroll.ts`の`scrollForPanCenter`がスクロール範囲なしと判定して`scrollLeft`/`scrollTop`を常に0にクランプし、`#canvas-scroll`にCSS中央寄せが無かったためSVGが左上に張り付いていた——`view-state.ts`の`zoomAt`が計算するポインタ固定点自体は数式上正しいのに画面に反映されていなかった。`index.html`の`#canvas-scroll`に`display: flex; justify-content: safe center; align-items: safe center;`を追加し解消（コンテンツが実際にオーバーフローする軸のスクロール計算には影響しない）。**この挙動は[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 07 表示機能|外部仕様7.1.2]]が名指しで禁止する現行版（Ruby/GTK）の既知バグ「左上基準でずれる」動作の再発だった**——同時に、Ctrl+ホイールでのポインタ固定点ズームも同節が新規要件として規定している通りに実装されていることを確認。194テスト全pass、`npm run check`green（この種のレイアウトバグはheadlessテストでは検出できない）。
- [x] **「ズーム比率が100%から変化しない」という報告を調査、バグではなくUI表記の誤解と判明**（2026-09-21）。ツールバーの「−」「100%」「＋」の並びのうち「100%」は現在倍率のライブ表示ではなく`data-action="zoomReset"`（クリックで100%へリセット）ボタンの固定ラベルだった。実際のライブ倍率表示は画面下部ステータスバーの`#status-zoom`のみで、デバッグログ（`[DEBUG wheel]`/`[DEBUG refreshStatus]`、調査後に削除済み）でズーム値が正しく更新されている（例: `0.51315...` = `1/1.1^7`、Ctrl+ホイール7回分と整合）ことも確認済み。副産物として、Electron既定で有効なネイティブCtrl+ホイール/ピンチのページ全体光学ズーム（自前のCtrl+ホイールズームとは別機構、`preventDefault()`で止まらない）を`webContents.setVisualZoomLevelLimits(1, 1)`で無効化（コミット`affd8f3`）——実際に競合を確認したわけではないが、二重解釈の芽を予防的に摘む対応。194テスト全pass、`npm run check`green。
- [x] **ツールバーのズームUI（−/100%/＋ボタン）が外部仕様のスライダ規定から逸脱していることを確認・記録**（2026-09-21）。[[work/active/TECSCDE外部仕様/TECSCDE外部仕様 - 03 画面構成#3.2.1 座標系と用紙|外部仕様3.2.1]]は倍率コントロールを「整数値のスライダ」と規定しているが、実装はスライダを持たずボタン3つ組のみ。この判断が明文化された記録は見つからず、いつ・なぜボタン方式になったかは不明（[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|内部仕様11.5節#9]]に記録）。スライダを追加するか、この逸脱を正式な設計決定として確定するかは未着手。
