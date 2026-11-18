---
date: 2026-11-14
description: "TECSCDE-DT-EL V0.2.1 の段3〜4の実施記録（段3の配列の受け口の展開、段4のtecsgen相当機能・Plugin型の取り込み）。実施記録ノートから逐語で分離した。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-DT-EL — V0.2.1 実装計画 — 実施記録 — 段3〜4

[[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 実施記録 — 2026-11-12]]から、25KB 閾値のため逐語で分離した実施記録（2026-11-14）。範囲・決定・段の割り当ては[[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 2026-11-12]]を正とし、ここには再掲しない。

## 段3の実施状況（2026-11-13 完了）

旧監査 #23 の残り、および三者監査 #20・#24 の契約に基づき、配列の受け口の要素展開と添字付き結合（固定長・可変長配列受け口の要素展開、右辺添字 `cell.port[subscript]` のパース・シリアライズ、対話的結合・要素挿入削除コマンド、および `__tool_info__("tecscde")` の `array_elements` 出力連携）を実装しました。

**`main` への取り込み（2026-11-13 追記）**: コミット `8163f0a`（fix: preserve array port subscripts and element counts、`ykominami/TECSCDE-DT-EL-agy`）。段4 のブランチ `feat/v021-stage4-internal-plugin` へ `92fe439` でマージしたうえで、`3a2af05` により `main` へ取り込んだ。段3 専用の `main` へのマージコミットは無く、段4 と一緒に入った。

### 着手条件の確認結果
段0で確認した契約（受け口も全参照添字を含めて要素数を決定する）に基づき、着手条件である tecsgen 文法における右辺添字の扱いを検証・整理しました。固定長 `[N]` の範囲外添字（例: `eFixed[99]`）や添字省略（`eFixed` や `eFixed[]`）が CDL 記述に存在する場合、解決先ポートが存在しないため `W-MISSING-JOIN-TARGET` 警告を生成し未解決結合として安全側に保持する挙動を採用しました。

### 実施した変更ファイル一覧
- `src/renderer/model/join.ts`: `Join` モデルに `entrySubscript?: number` プロパティを追加
- `src/renderer/cdl/cst.ts`: CST 走査で右辺添字式（`subscript_expression`）からの `entrySubscript` 抽出に対応
- `src/renderer/cdl/tool-info.ts`: `array_elements` の `direction: "entry"` シリアライズ・デシリアライズ対応
- `src/renderer/cdl/messages.ts`: 診断メッセージでの添字付き受け口ポート名表現対応
- `src/renderer/cdl/document-builder.ts`:
  - 固定長 `[N]` および可変長 `[]`（参照添字の最大値+1個）の受け口配列要素ポート展開
  - 右辺添字付き結合（`entrySubscript`）の解決と未解決時の `W-MISSING-JOIN-TARGET` 警告生成
- `src/renderer/cdl/serializer.ts`: 右辺添字付き結合（`c.e[subscript]`）および `array_elements` の CDL 出力対応
- `src/renderer/app/source-save-state.ts`: 受け口配列要素の追加・削除操作に伴う未保存状態（save state）の追跡
- `src/renderer/commands/join-commands.ts`: 添字付き受け口への結合生成コマンド対応
- `src/renderer/commands/port-commands.ts`: `InsertArrayPortElementCommand` / `DeleteArrayPortElementCommand` の受け口配列（可変長要素の動的追加・削除）対応
- `src/renderer/commands/cell-commands.ts`: セル削除・変更・複製時の受け口添字保持対応
- `src/renderer/commands/support.ts`: 結合コマンドサポート関数での `entrySubscript` 伝播
- `src/renderer/render/gesture-controller.ts`: キャンバス上のドラッグ結合における受け口配列要素ポートへのスナップと添字付き結合生成
- `src/renderer/render/hit-tester.ts`: 近接する配列ポート要素（3mm間隔等）からの最短距離ポート要素選択（クリック精度の改善）
- `src/renderer/render/svg-path.ts`: 受け口配列各要素ポートの個別幾何座標への結合線終端描画
- `src/renderer/render/connection-focus.ts`: 添字付き結合線のフォーカス・ハイライト対応
- `src/renderer/app/property-panel.ts`: 受け口配列ポート要素選択時のプロパティ情報表示
- 各テストファイル:
  - `tests/renderer/array-port-commands.test.ts`
  - `tests/renderer/cdl-array-ports.test.ts`
  - `tests/renderer/connection-focus.test.ts`
  - `tests/renderer/hit-tester-overlap.test.ts`（近接配列ポートの最短距離選択テスト含む）
  - `tests/renderer/join-stub.test.ts`
  - `tests/renderer/join-unit-a.test.ts`
  - `tests/renderer/tool-info.test.ts`

### 単体テスト・ビルド・境界チェック検証結果
- **単体テスト**: 113 test files passed / 1 skipped、1160 tests passed / 5 skipped（`tests/perf/cdl-parse.bench.test.ts` はベンチマークのためスキップ、`npx vitest run --maxWorkers=4` で全件成功）
- **型チェック / ビルド**: レンダラー型チェック（`tsconfig.renderer.json`）、レンダラー esbuild バンドル（`dist/renderer/renderer.js` 603.5kb）、メイン型チェック・コンパイル（`tsconfig.main.json`）ともに全成功
- **境界チェック (`depcruise`)**: 依存関係違反 0 件（151 modules, 556 dependencies cruised）

### 実機 Electron 検証（一時ディレクトリ隔離環境）
V0.2.1 実装計画の方針（「完了は実機で確かめて判定する。実ユーザー設定を汚さないよう一時ディレクトリ等で隔離する」）に従い、`LOCALAPPDATA` および `USERDATA` を `mkdtempSync` で生成した一時ディレクトリに隔離した状態で可視 BrowserWindow と実 AppShell を起動し、以下の動作を自動検証しました：
1. **初期ドキュメントの読み込みと要素展開描画**:
   - シグニチャ `sSig`、固定長受け口配列 `eFixed[3]`、可変長受け口配列 `eVar[]`、呼び口 `c1`, `c2`、添字付き結合 `c1 = Server.eFixed[2]`, `c2 = Server.eVar[1]` を含む CDL を `app:bootstrap` 経由で読み込み。
   - `#canvas` 内の SVG において、`Server` セルに `eFixed` の 3 要素（`subscript="0"`, `"1"`, `"2"`）と `eVar` の 2 要素（`subscript="0"`, `"1"`）が正確な幾何位置に個別ポートとして展開描画されていることを確認。
2. **結合線終端座標の一致**:
   - 描画された結合線 polyline の終端座標が、`eFixed[0]` ではなく目的の `eFixed[2]` のポート中心位置に正しく接続されていることを確認。
3. **近接ポート要素選択とプロパティパネル表示**:
   - 3mm 間隔で近接配置された `eVar[1]` ポートのクリック選択により、プロパティパネル（`#property-panel`）に該当ポートの要素情報（セル名 `Server`、ポート名 `eVar`、添字 `1`）が正常表示されることを確認。
4. **Insert キーによる可変長受け口配列の動的要素挿入**:
   - `eVar[1]` 選択状態での `Insert` キー押下イベントにより、`InsertArrayPortElementCommand` が実行され、可変長受け口配列 `eVar` の要素数が 3 個（`subscript="0"`, `"1"`, `"2"`）に増加して再描画されることを確認。
5. **CDL シリアライズと配置情報出力の整合性**:
   - ドキュメント保存処理により書き出された CDL テキストにおいて、結合記述に右辺添字 `Server.eFixed[2]` および `Server.eVar[1]` が正しく保持・出力され、`__tool_info__("tecscde")` 内に `"array_elements"`（`"direction": "entry"`, `"port": "eVar"`, `"element_count": 3`）が正しく出力されていることを確認。

検証完了後、一時検証スクリプトおよび一時隔離ディレクトリをクリーンアップし、作業ツリーを正常な状態に保ちました。段3は完了です。

## 段4の実施状況（2026-11-13 完了）

内部仕様 9D.6（[[TECSCDE-DT-EL内部仕様 - 09D tecsgen連携とPlugin生成型の取り込み]] 第6節）、外部仕様 8.5（[[TECSCDE-DT外部仕様 - 08 情報・バージョン・設定]] 第5節）、および三者監査 #60 に基づき、tecsgen 相当機能・仮想ファイル・Plugin型の取り込み（情報ダイアログでの Plugin 型取り込み方式選択と永続化、Web Worker による `MrubyBridgePlugin`・`MrubyBridgeCellPlugin` の内部生成処理、未対応プラグイン警告、および仮想定義ファイルの読み取り専用表示）を実装しました。

**`main` への取り込み（2026-11-13 追記）**: 前提の内部 `MrubyBridgePlugin` 処理系は `f9e32a5`（`feat/v021-stage4-internal-plugin`）、本体（Worker、`PluginTypeProvider`、`pluginTypeSource` 設定、`W-PLUGIN-UNSUPPORTED`・`W-PLUGIN-TYPE-LOAD`）は `435a99a`。`3a2af05`（Merge branch 'feat/v021-stage4-internal-plugin'）で `main` へ取り込んだ。取り込み後の `main` で `npm run check` は終了コード 0（ビルド成功、117 ファイル成功・1 スキップ、1196 テスト成功・5 スキップ、dependency-cruiser 違反なし、159 モジュール・587 依存）。push・`v0.2.1` タグは未実施。

### 着手条件の確認結果
着手条件である tecsgen 1.9.1 の出力ゴールデン（55 ファイル）との照合テスト（`tests/renderer/internal-tecsgen-golden.test.ts`）を実行し、TypeScript 実装の生成物（CDL、ヘッダ、C ソース）が tecsgen 1.9.1 本体の出力と完全一致（55/55 一致）することを確認しました。

### 実施した変更ファイル一覧
- `src/shared/ipc-types.ts`: `PluginTypeSource`（`"external"` | `"internal"`）型、`ToolSettings.pluginTypeSource`、`ToolSettingsUpdate.pluginTypeSource` の追加
- `src/main/app-settings.ts`: `AppSettings` / `AppSettingsPatch` に `pluginTypeSource` を追加、永続化（`settings.json`）対応
- `src/main/tool-settings.ts`: `getPluginTypeSource()`、更新ハンドラ、IPC 連携の追加
- `src/renderer/tecsgen/internal/processor.ts`: `mruby.cdl` 等の内部仮想ファイル解決・生成、生成 CDL・仮想ヘッダ等のマッピング
- `src/renderer/tecsgen/internal/worker.ts` (新規): Web Worker 内で `InternalTecsgenProcessor` を駆動するワーカーエントリーポイント
- `src/renderer/tecsgen/plugin-type-provider.ts` (新規): `PluginTypeProvider` インターフェース、`ExternalPluginTypeProvider`（外部 tecsgen 実行）、`InternalPluginTypeProvider`（Web Worker 駆動）の抽象化・実装
- `src/renderer/app/file-actions.ts`: 読み込みパイプライン（`openFromPath` / `applyOpenResult`）で設定された `pluginTypeSource`（`external` / `internal`）に応じて `PluginTypeProvider` を選択・実行。`internal` 選択時は `window.tecscde.cdl.loadGrammarAssets()` で取得した WASM アセットを Worker に渡して Tree-sitter を初期化し、生成された仮想 CDL をロードして型解決。未対応プラグインへの `W-PLUGIN-UNSUPPORTED` 警告発行
- `src/renderer/app/definition-source.ts`: `plugin:/` プレフィックスを持つ仮想ファイルの解決、および `plugin:/... — 仮想ソース（読み取り専用）` タイトルでの読み取り専用ソース表示対応
- `src/renderer/app/information-dialog.ts`: 情報ダイアログに「Plugin 型取り込み」セクション（方式選択: 外部 tecsgen / 内部処理、プラグイン一覧表: `MrubyBridgePlugin`, `MrubyBridgeCellPlugin` 版 1.9.1、保存ボタン）を追加
- `src/renderer/app/import-resolution.ts`: `plugin:/` 仮想パスのインポート除外・スキップ処理
- `src/renderer/app/shell.ts`: `SettingsGateway` 連携による情報ダイアログ初期化・アクションハンドラ接続
- `src/renderer/app/store.ts`: ドキュメント保存・再読込制御およびプラグイン型ソース設定更新時の不要な再読込抑止
- `src/renderer/cdl/messages.ts`: `W-PLUGIN-UNSUPPORTED` 警告メッセージ生成
- `src/renderer/index.html`: 情報ダイアログ内プラグイン設定 HTML テンプレート追加
- `src/renderer/main.ts`: 本番起動時の `SettingsGateway` 注入
- `scripts/build-renderer.mjs`: `tecsgen-worker.ts` を `dist/renderer/tecsgen-worker.js` へバンドルする設定追加
- 各テストファイル:
  - `tests/main/app-settings.test.ts`: `pluginTypeSource` の初期値（`external`）、更新、永続化テスト
  - `tests/main/tool-settings.test.ts`: `ToolSettingsService` の `pluginTypeSource` 取得・更新テスト
  - `tests/renderer/information-dialog.dom.test.ts`: 情報ダイアログの DOM 表示、選択切り替え、保存、プラグイン一覧表示テスト
  - `tests/renderer/internal-tecsgen-golden.test.ts`: tecsgen 1.9.1 出力との 55 ファイル完全一致テスト
  - `tests/renderer/plugin-type-provider.test.ts` (新規): Provider の型解決、Worker 通信、エラーハンドリング単体テスト
  - `tests/renderer/file-actions-plugin-types.test.ts` (新規): `file-actions` 経由での内部・外部プロバイダ切り替えおよび型解決テスト

### 単体テスト・ビルド・境界チェック検証結果
- **単体テスト**: 115 test files passed / 1 skipped、1166 tests passed / 5 skipped（`tests/perf/cdl-parse.bench.test.ts` はベンチマークのためスキップ、全件成功）
- **型チェック / ビルド**: レンダラー型チェック（`tsconfig.renderer.json`）、レンダラー esbuild バンドル（`renderer.js` および `tecsgen-worker.js`）、メイン型チェック・コンパイル（`tsconfig.main.json`）ともに全成功
- **境界チェック (`depcruise`)**: 依存関係違反 0 件（159 modules, 587 dependencies cruised）

### 実機 Electron 検証（一時ディレクトリ隔離環境）
V0.2.1 実装計画の方針（「完了は実機で確かめて判定する。実ユーザー設定を汚さないよう一時ディレクトリ等で隔離する」）に従い、`LOCALAPPDATA` および `USERDATA` を `mkdtempSync` で生成した一時ディレクトリに隔離した状態で実機 Electron（`node_modules/electron/dist/electron.exe`）を起動し、以下の 4 点を自動検証しました：

1. **情報ダイアログの初期表示と設定保存**:
   - 情報ダイアログを開き、`#information-plugin-type-source` の初期値が `"external"` であること、`#information-plugin-table` に `MrubyBridgePlugin`・`MrubyBridgeCellPlugin`（版 `1.9.1`）が表示されることを確認。
   - 方式を `"internal"` に切り替えて `#information-plugin-save` をクリックし、保存完了メッセージの表示、隔離ディレクトリ内の `settings.json` への `"pluginTypeSource": "internal"` 永続化、および現在開いているドキュメントが勝手に再読込されないことを確認。
2. **内部処理（`internal`）での CDL 読み込み・型解決・対象外プラグイン警告**:
   - `TECSGEN_COMMAND` に存在しないダミーコマンドを設定（外部 tecsgen を一切使用しない環境を保証）。
   - `generate(MrubyBridgePlugin, sKernel, ""); generate(OtherPlugin, sKernel, ""); region rDomainEV3 { cell nMruby::tsKernel BridgeKernel { cTECS = HRP2Kernel.eKernel; }; cell tKernel HRP2Kernel {}; };` を含む一時 CDL ファイルを読み込み。
   - Web Worker（`dist/renderer/tecsgen-worker.js`）経由で `nMruby::tsKernel` が生成・解決され、キャンバス SVG 上に `BridgeKernel` セルが描画され、`celltypeUnresolved` が `false`（赤枠警告なし）であることを確認。
   - 対象外プラグイン `OtherPlugin` に対して `#diagnostics-panel` に `[W-PLUGIN-UNSUPPORTED]` 警告が出力されることを確認。
3. **仮想定義ファイルの読み取り専用表示**:
   - 生成された `nMruby::tsKernel` のセルタイプ詳細ダイアログを開き、定義ファイルパスが `plugin:/MrubyBridgeSignaturePlugin/tmp_MrubyBridgeSignaturePlugin_0.cdl` と表示されることを確認。
   - 「定義ファイルを表示」（`[data-show-definition]`）を実行し、`.definition-file-window` ダイアログが開き、タイトルが `plugin:/MrubyBridgeSignaturePlugin/tmp_MrubyBridgeSignaturePlugin_0.cdl — 仮想ソース（読み取り専用）` と表示され、読み取り専用の `<pre>` 要素内に生成 CDL（`celltype tsKernel { ... }`）が正確に表示されることを確認。
4. **クリーンアップ**:
   - 検証完了後、一時検証スクリプトおよび一時隔離ディレクトリを完全に削除し、作業ツリーにゴミが残らないことを確認。

段4は完了です。

## Related

- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 実施記録 — 2026-11-12]] — 実施記録（索引とリリースの経緯）
- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 2026-11-12]] — 計画（範囲・決定・段）
- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 実施記録 — 段0〜2 — 2026-11-12]] — 段0〜2の実施記録
