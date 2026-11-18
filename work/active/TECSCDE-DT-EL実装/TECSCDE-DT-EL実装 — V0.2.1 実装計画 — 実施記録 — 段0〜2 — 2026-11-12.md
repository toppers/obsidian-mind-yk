---
date: 2026-11-14
description: "TECSCDE-DT-EL V0.2.1 の段0〜2の実施記録（段0の判定結果、段1の診断パネル配置・フルパス表示・#16・#17、段2のCプリプロセッサ設定）。実施記録ノートから逐語で分離した。"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
---

# TECSCDE-DT-EL — V0.2.1 実装計画 — 実施記録 — 段0〜2

[[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 実施記録 — 2026-11-12]]から、25KB 閾値のため逐語で分離した実施記録（2026-11-14）。範囲・決定・段の割り当ては[[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 2026-11-12]]を正とし、ここには再掲しない。

## 段0の実施結果（2026-11-12、判定はユーザー確認済み）

段0（コード変更のない確認）を行い、判定を2026-11-12にユーザーが確認して確定した（推奨どおり）。根拠は、仕様（外部仕様・内部仕様・監査対応ノート）の読解と、実装リポジトリ `E:\Ccur\typescript\TECSCDE-DT-EL` の該当箇所の読解。実装は動かしていない。

### (a) 取りこぼし候補の要否判定

| 旧監査 | 判定 | 根拠 |
|---|---|---|
| #25 同名セルの共存 | **要件あり（間接）。追加実装は不要** | 契約が完全修飾セル名でセルを識別する前提（DT外部仕様 05 の `array_elements` は `::Region::Cell` の形。内部仕様 監査24 の受入条件に「同名別scope」）。実装は済み（`95cca94`、実機確認済み） |
| #26 修飾付き結合先の解決 | **要件なし。V0.2.1 では実装しない** | 外部仕様に、修飾名の結合先の解決規則の記述がない。現行コード（`document-builder.ts` の `resolveTargetCell`）は、絶対名 `::N::c` は絶対に、相対名は呼び元の名前空間から外側へ探す（tecsgen に倣う）。外側で見つからなくても、同名のセルが1つだけで修飾が末尾一致するなら受ける寛容な挙動が残る |
| #24 の残り（`const` 名参照などの式評価） | **要件なし。実装しない** | 外部仕様 4.6.x は固定長 `[N]` とだけ書き、式の評価を規定しない。現行は整数定数式まで対応しており仕様以上。評価できない式は警告 `W-ARRAY-SIZE-UNRESOLVED` で単一ポートとして扱い、安全側に倒れる |
| #7 の残り（ポートの属性編集） | **不要** | 外部仕様 4.5 は、セルタイプの定義（ポート構成・シグニチャ）を「編集対象としない」とし、読み込んで参照するのみとする |
| #27a の残り（署名・公証、ZIP の自動更新） | **V0.2.1 の範囲外** | 外部仕様 02 が「配布・インストール・自動更新の方式は本書の範囲外」とする。管理は内部仕様 11B。コード署名は当面未署名（2026-09-23 決定）。決定4のとおり別の決定として扱う。ZIP の自動更新の実機検証は 11B の残件 |
| #27b Intel Mac | **V0.2.1 の範囲外** | 同上。決定4 |
| #28 の残り（Linux の自動更新） | **要件なし（範囲外）** | `update-electron-app` が macOS・Windows のみ対応のため非対応。外部仕様は配布を範囲外とする |

**旧監査の記述の矛盾（解消、2026-11-12）**: #25 の行（外側へ探す）が現行で、#26 の行（末尾一致）は古い記述だった（コードで確認）。項目表の #26 を現行に合わせて直した。

### (b) 受け口の配列（旧監査 #23 の残り）: 三者監査 #20・#24 の契約で足りるか

**判定: 足りる。旧監査の「設計が未決」は、実態は「実装が契約に未対応」である。**

- 契約（内部仕様 監査20・監査24、外部仕様 監査対応 19-28）は、**受け口も全参照添字から要素数を決める**と定めている（「可変長EPortは全参照添字を必要数へ含める」「受け口は全参照添字を含める」）。方式は決まっている。
- tecsgen 側に対応がある。内部仕様に `get_rhs_subscript`（結合の右辺の添字）と、`@entry_array_max_subscript`（受け口配列の最大添数）の記述がある。契約は tecsgen の振る舞いに合っている。
- 実装が未対応の箇所（読解、**未実行**）:
  - `cst.ts` の結合の解析は、右辺が `field_expression`（`c.e`）のときだけ結合として扱う。右辺に添字が付く `c.e[2]` は `field_expression` にならず、**属性代入として扱われる可能性がある**（inferred、未検証）。
  - `JoinAssignDecl` に、右辺の添字を持つ項目がない。`Join` モデルも `eportName` だけで、受け口の添字を持たない。旧監査の「結合記述が受け口側の添字を持たない」は、この実装側の事実を指す。
- したがって、段3 の実装は着手できる。着手前に確認する点は、tecsgen の文法で右辺の添字が許される条件（固定長の範囲外、省略の可否）。契約は範囲外の添字を規定していない（外部仕様 4.6.x の7）。

### 確認結果（ユーザー、2026-11-12）

1. (a) の判定は、案どおり確定した。実装する項目は無い。
2. 旧監査の #25 と #26 の矛盾は、コードで確認して直した（上記）。
3. 段3 の着手条件は、**tecsgen の文法で右辺の添字が許される条件（固定長の範囲外、省略の可否）の確認**とする。

## 段1の実施状況（2026-11-12）

診断パネルの独立行配置（実測10項目分の上限・自動表示）、ファイルダイアログの選択ディレクトリ完全パス、監査 #16・#17 を実装しました。#17 の短い項目名は不具合の説明であり、外部・内部の監査対応17の契約に従って主ファイル未確定時にも参照追加を許可します。

レビューで #17 の二段目の再帰解決に残る探索コンテキストと失敗時不適用の問題を修正し、再レビューで残指摘なしを確認しました。最終 `npm run check` は成功しました（87 test files passed / 1 skipped、882 tests passed / 5 skipped、build成功、dependency-cruiser違反なし）。段1は完了です。

可視Electronの検証fixtureで、診断12件が独立領域に10項目分で表示されること、件数ボタンで閉じるとキャンバスが拡大すること、選択ディレクトリの日本語を含む完全パスが省略せず折り返されることを確認しました。ファイルI/Oはfixtureで代替し、実ユーザー設定は読み書きしていません。証跡はcodexワークスペースの `tests/verification/stage1-visible-{open,closed,path}.png` と `stage1-check.log`、寸法・スクロール・状態保持は `stage1-diagnostics.electron.cjs` です。GUI操作のsynthetic入力成功表示のみを根拠にせず、操作後の画像で確認しています。2回目起動のChromiumキャッシュ作成拒否ログはありますが、画面・寸法検証は成功しています。
#16・#17 の操作検証は `tests/verification/stage1-sources.electron.cjs` で、可視Electron・実AppShell・OS一時ディレクトリの実CDLファイルを使用しました。MainとRefを読み込み、Refのcountを42へ未保存編集し、実際の「消去」ボタンのDOM clickでMainだけを消去しました。Refの本文・count=42・dirtyを保持し、primary=nullからextra.cdlを参照追加し、そのnested.cdlも再帰追加することを確認しました。追加後もRefの本文・dirtyとprimary=nullを保持し、実ref.cdlへの書出し内容が消去前の編集済み本文と一致し、元main.cdlは変更されないことをassertしました（exit 0）。証跡は `stage1-sources-{before,cleared,added}.png` と `stage1-sources.stdout.log`、実データは同ログのTEMP_EVIDENCE_DIRECTORYです。

Orcaのネイティブクリックは、このsource fixtureでは `window_not_focused`（restore-window指定でも前面化不可）となりました。反復を止め、可視レンダラ上の実ボタンhandlerをDOM clickで実行し、capturePage画像とモデル・実ファイルのassertを照合しました。参照追加はproductionのaddAsReferenceを直接呼び、OSのフォルダ選択ダイアログやCtrlキー配送そのものはこのfixtureでは検証していません。既存dirtyを保全し、commit/push/tagは行っていません。診断4列化（監査#52）はこの段の範囲外です。

## 段2の実施状況（2026-11-12 完了）

内部仕様 09E（[[TECSCDE-DT-EL内部仕様 - 09E V0.2.1 Cプリプロセッサ設定と失敗詳細]]）および外部仕様（[[TECSCDE-DT外部仕様 - Cプリプロセッサ設定と失敗詳細(V0.2.1用)]]）に基づき、C プリプロセッサ設定（`cppPath`・`cppArgs`）の永続化・解決・ファイル選択ダイアログ連携、および `import_C` 実行時の失敗詳細表示（決定理由・フルパス・未検出・非0終了理由）を実装しました。

### 実施した変更ファイル一覧
- `src/shared/ipc-types.ts`: `ToolSettings`, `ToolSettingsUpdate`, `ResolvedCppCommand`, `ChooseCppPathResult` 型定義、`TecscdeApi.settings.chooseCppPath` 追加
- `src/main/app-settings.ts`: `AppSettings` / `AppSettingsPatch` に `cppPath`（string）、`cppArgs`（string）を追加・永続化対応
- `src/main/tool-settings.ts`: `findGccOnPath`（PATH探索・優先度判定）、`resolveCppCommand`（4優先順位による解決、空白パスのダブルクォート囲み、クォート付きコマンドからの実行ファイル抽出）、`chooseCppPath`（ファイルダイアログ連携）、`ToolSettingsService.resolveForPreprocess` 実装
- `src/main/tecsgen-runner.ts`: `preprocess` 戻り値に `resolvedCpp`、`errorCategory`（`unmatched_quote` / `spawn_error` / `nonzero_exit` / `empty_output`）、`exitCode`、`stderrSnippet`、`systemError` を格納
- `src/main/ipc.ts`: `settings:choose-cpp-path` ハンドラ登録、`tecsgen:preprocess` への `toolSettingsService.resolveForPreprocess` 連携
- `src/preload/index.mts`: `settings.chooseCppPath` API を contextBridge 経由で公開
- `src/renderer/gateways/settings-gateway.ts`: `SettingsGateway.chooseCppPath()` 追加
- `src/renderer/cdl/messages.ts`: `W-CPP-FALLBACK` 警告メッセージ生成関数（コマンド・フルパス・決定理由・失敗詳細を含む複数行メッセージ）
- `src/renderer/app/import-resolution.ts`: `preprocess` 呼び出しおよび詳細失敗診断（`W-CPP-FALLBACK`）の収集・集約
- `src/renderer/app/information-dialog.ts`: 情報ダイアログへの C プリプロセッサ設定セクション（有効コマンド・フルパス・決定理由・パス入力・参照ボタン・引数入力・保存ボタン）追加
- 各テストファイル:
  - `tests/main/app-settings.test.ts`
  - `tests/main/ipc.test.ts`
  - `tests/main/tecsgen-runner.test.ts`
  - `tests/main/tool-settings.test.ts`（空白入りパスのクォート処理および `splitCommand` ラウンドトリップ検証含む）
  - `tests/preload/index.test.ts`
  - `tests/renderer/gateways.test.ts`
  - `tests/renderer/import-resolution.test.ts`
  - `tests/renderer/information-dialog.dom.test.ts`

### 単体テスト・ビルド・境界チェック検証結果
- **単体テスト**: 111 test files passed / 1 skipped、1130 tests passed / 5 skipped（`tests/perf/cdl-parse.bench.test.ts` はベンチマークのためスキップ）
- **型チェック / ビルド**: レンダラー型チェック（`tsconfig.renderer.json`）、レンダラー esbuild バンドル、メイン型チェック・コンパイル（`tsconfig.main.json`）ともに全成功
- **境界チェック (`depcruise`)**: 依存関係違反 0 件（151 modules, 556 dependencies cruised）

### 実機 Electron 検証（一時ディレクトリ隔離環境）
V0.2.1 実装計画の方針（「完了は実機で確かめて判定する。実ユーザー設定を汚さないよう一時ディレクトリ等で隔離する」）に従い、`LOCALAPPDATA` および `USERDATA` を `mkdtempSync` で生成した一時ディレクトリに隔離した状態で可視 BrowserWindow と実 AppShell を起動し、以下の動作を検証しました：
1. **情報ダイアログの初期表示**:
   - `#information-cpp-effective`、`#information-cpp-meta`（フルパス、決定理由）、`#information-cpp-path`、`#information-cpp-browse`、`#information-cpp-args`（初期値 `"-E -DTECSGEN"`）が正しく配置・表示されること、および GCC 未検出時のフォールバック状態（決定理由: `フォールバック`、フルパス: `未検出 (PATH上)`）が正しく提示されることを確認。
2. **CPP 設定の保存と即時反映**:
   - `#information-cpp-path` にカスタムパス（例: `C:\dummy_tools\my-custom-gcc.exe`）、`#information-cpp-args` に `"-E -DTECSGEN"` を入力して保存を実行し、保存完了メッセージの表示、有効コマンドの即時更新、決定理由が `ユーザ直接指定` に更新されることを確認。また、隔離ディレクトリ内の `settings.json` に設定値が正しく永続化されていることを確認。
3. **`import_C` 実行時の `W-CPP-FALLBACK` 診断パネル表示**:
   - `import_C("test_header.h");` を含む一時 CDL ファイルを読み込み、プリプロセスが失敗した際、診断パネル（`#diagnostics-panel`）に `[W-CPP-FALLBACK]` 警告が表示され、その詳細テキストに実行コマンド名、フルパス、決定理由（`ユーザ直接指定` 等）、および失敗理由（実行ファイルが見つからない、または非ゼロ終了等）が正確に含まれていることを確認。

検証完了後、一時ディレクトリおよび一時検証スクリプトをクリーンアップし、作業ツリーを正常な状態に保ちました。段2は完了です。

## Related

- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 実施記録 — 2026-11-12]] — 実施記録（索引とリリースの経緯）
- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 2026-11-12]] — 計画（範囲・決定・段）
- [[TECSCDE-DT-EL実装 — V0.2.1 実装計画 — 実施記録 — 段3〜4 — 2026-11-13]] — 段3〜4の実施記録
