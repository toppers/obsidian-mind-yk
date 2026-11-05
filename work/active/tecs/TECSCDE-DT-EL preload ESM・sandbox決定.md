---
date: 2026-09-08
description: "TECSCDE-DT-EL版のpreloadスクリプトをESM（.mjs）で書き、BrowserWindowのsandboxをfalseとする決定。実機electron .起動確認でESM/CJS不整合が露見したことが契機。"
project: TECS
quarter: Q3-2026
status: accepted
tags:
  - decision
  - tecs
  - tecscde
---

# Decision: TECSCDE-DT-EL版の preload を ESM（`.mjs`）とし、`sandbox: false` にする

## Context

2026-09-08、[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]の実機 `electron .` 起動確認で、preload スクリプトが `SyntaxError: Cannot use import statement outside a module` でロードできないと判明した。

- 原因: `package.json` が `"type": "module"` のため、TypeScript が出力する preload の `.js` は ESM。一方 Electron のサンドボックス化された preload は CommonJS コンテキストで実行されるため `import` を解釈できない。
- 契約テスト（`tests/preload/index.test.ts`、vitest が `electron` をモックして TS ソースを直接変換）はこのビルド出力形式の不整合を検出できず、実機起動でのみ露見した。
- この論点は [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|内部仕様11.2節#1]]（`sandbox: true` の採否）と直結する。

## Options Considered

1. **preload を CommonJS 出力にする**（`.cts` 化、または専用 tsconfig + `dist/preload/package.json` に `{"type":"commonjs"}`）
   - 利点: `sandbox: true`（Electron 20以降の既定、よりセキュア）を選べる余地を残す。
   - 欠点: プロジェクト全体が ESM なのに preload だけ CJS という非対称。ビルド設定が増える。
2. **preload を ESM（`.mjs`）で書き、`sandbox: false` にする**（採用）
   - 利点: プロジェクトの ESM 統一を保つ。ビルドは `.mts` 拡張子だけで完結（`.mts` は package type に関わらず CommonJS ではなく ESM `.mjs` を出力）。
   - 欠点: Electron の既定 `sandbox: true` から外れる。ESM の `electron` モジュールは preload/renderer 向けに `clipboard` を名前付きエクスポートしないため、`createRequire(import.meta.url)("electron")` で CJS 版から取得する必要がある。

## Decision

**選択肢2**（ESM preload + `sandbox: false`）。ユーザー判断（2026-09-08）。

実装:
- `src/preload/index.ts` → `src/preload/index.mts`（ESM `.mjs` を出力）
- `src/main/index.ts` の `webPreferences`: `preload` パスを `../preload/index.mjs`、`sandbox: false` を明示
- preload の `clipboard` は `createRequire(import.meta.url)("electron")` で取得（`contextBridge` / `ipcRenderer` は名前付き import のまま）
- `tests/preload/index.test.ts`: `node:module` の `createRequire` をモックして clipboard 経路を検証

## Consequences

- **[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|11.2節#1]] が解消**（`sandbox: false` に確定）。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|2.4節]]の preload コードサンプルも `.mjs` + `createRequire` に更新。
- `contextIsolation: true`・`nodeIntegration: false` は維持。renderer から Node/Electron API へ触れる経路は依然 `contextBridge` 経由のみで、サンドボックス無効化で広がる攻撃面は preload スクリプト自身（信頼済みの自作コード）に限られる。
- **手放したもの**: Electron のサンドボックス保護。将来 renderer に信頼できないコンテンツ（外部 URL・サードパーティ埋め込み等）を読み込む設計になった場合は再検討が必要。本アプリはローカルの `.cde`/`.cdl` ファイルと `tecsgen` 出力のみを扱うため、当面のリスクは低い。
- **検証済み**: `electron .` で preload ロード成功・`contextBridge.exposeInMainWorld("tecscde", ...)` 実行を確認（`Unable to load preload script` エラーが消えた）。`npm run check`（build + 47テスト + depcruise）green。
- **2026-09-15、asar化後の実機起動でも確認済み**: `electron-forge package`後の`.exe`をターミナルから起動し、DevTools Consoleで`window.tecscde`の存在とAPI呼び出し（IPC往復）を確認。preload自体のESM/asar互換性リスクは実際には問題にならなかった——起動時に別途発覚した`electron-squirrel-startup`の依存関係配置バグ（`devDependencies`にあったためpackagerのプルーニングで除外されクラッシュ）を修正した後は、preload/contextBridgeは想定通り動作した（詳細: [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]Action Items）。
- 姉妹実装 [[work/active/TECSCDE-TS実装/TECSCDE-TS実装|TECSCDE-TS実装]]（ブラウザ、Electron なし）・[[work/active/TECSCDE-DT-TA実装/TECSCDE-DT-TA実装|TECSCDE-DT-TA実装]]（Tauri、preload 相当なし）には影響しない。

## Related

- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — この決定の契機となった実機起動確認、実装の記録
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章]] — 11.2節#1 の未決事項（本決定で解消）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 02 モジュール構成とプロセス境界|TECSCDE-DT-EL内部仕様 第2章]] — preload 設計（2.4節、本決定でコード更新）
- [[work/active/tecs/TECSCDE Undo-Redo設計決定|TECSCDE Undo-Redo設計決定]] — 同じく実装着手時に判明して記録した設計決定
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
