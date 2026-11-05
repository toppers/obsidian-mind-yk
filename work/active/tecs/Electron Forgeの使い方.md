---
date: 2026-09-12
description: "Electron Forgeの基本的な使い方（インストール、npm start/package/make/publish、forge.config.jsのmakers/plugins/publishers構造、自動更新の組み込み方）の参考ノート。実際のTECSCDE-DT-ELでの導入詳細は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]参照。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - reference
---

# Electron Forgeの使い方

## Context

[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]で比較した配布ツールのうち、TECSCDE-DT-ELが採用した**Electron Forge**の一般的な使い方をまとめた参考ノート。**本ノートの内容は一般論**——TECSCDE-DT-ELで実際に採った構成は末尾「TECSCDE-DT-ELでの実際の構成」の節、および一次情報源の[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]を参照。

## インストール

新規プロジェクト:
```bash
npm init electron-app@latest my-app -- --template=vite-typescript
```

既存プロジェクトへの後付け:
```bash
npx @electron-forge/cli import
```
既存の`package.json`・エントリポイント構成を検出し、依存関係と`forge.config.js`を自動生成しようとする。ビルド構成（esbuild等の自前スクリプト）が複雑な場合は自動検出が失敗することがあり、その際は手動セットアップが必要。

## 基本コマンド

```bash
npm start          # 開発モードで起動（electron . 相当）
npm run package    # OS向けの実行ファイル一式を生成（配布はしない、動作確認用）
npm run make       # packageの結果からインストーラ（.exe/.dmg/.deb等）を生成
npm run publish    # makeの結果を配布先（GitHub Releases等）へアップロード
```

## 設定ファイル `forge.config.js`

```js
module.exports = {
  packagerConfig: {
    asar: true,
    icon: './assets/icon',
  },
  rebuildConfig: {},
  makers: [
    { name: '@electron-forge/maker-squirrel', config: {} },      // Windows
    { name: '@electron-forge/maker-zip', platforms: ['darwin'] }, // macOS
    { name: '@electron-forge/maker-deb', config: {} },           // Linux (deb)
    { name: '@electron-forge/maker-rpm', config: {} },           // Linux (rpm)
  ],
  plugins: [
    { name: '@electron-forge/plugin-auto-unpack-natives', config: {} },
    { name: '@electron-forge/plugin-fuses', config: { /* Fuse設定 */ } }, // セキュリティ強化
  ],
  publishers: [
    {
      name: '@electron-forge/publisher-github',
      config: { repository: { owner: '<owner>', name: '<repo>' }, prerelease: false },
    },
  ],
};
```

- **Makers**: `make`で何を生成するかをOSごとに指定
- **Plugins**: ビルド過程に処理を差し込む（バンドラ統合、ネイティブモジュール展開、セキュリティ設定等）
- **Publishers**: `publish`のアップロード先（GitHub Releases、S3、Bitbucket等）

## 自動更新の組み込み

Forge自体は自動更新機能を持たないため、以下のいずれかと組み合わせる（比較は[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]参照）。

- `update-electron-app`（Electron公式の薄いラッパー、GitHub Releases前提）
- `electron-updater`（electron-builder用だが単独利用も可能、より柔軟な配信先設定）

いずれもForgeの`publisher-github`でリリースを公開し、アプリ側の更新チェックがそのリリースを参照する組み合わせになる。

## TECSCDE-DT-ELでの実際の構成（2026-09-12、一次情報源: [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]）

導入前に想定していた構成と、実際に採った構成は次の点で異なった:

- **esbuildビルドの統合**: `packagerConfig.beforeCopy`フックではなく、`hooks.prePackage`フックで既存の`npm run build`（tsc+esbuild）をそのまま呼び出す形にした（`import → dirname(fileURLToPath(...))`のESM構成、`execSync`使用）。理由・詳細は`E:\Ccur\typescript\TECSCDE-DT-EL\forge.config.js`のコメント参照
- **Makerは`@electron-forge/maker-squirrel`（Windows）のみ**を導入。macOS/Linux向けMaker・`plugin-fuses`・`publisher-github`は範囲外のまま（実機検証できない・自動更新は別タスクのため）
- **`electron-squirrel-startup`ガード**を`main/index.ts`に追加（Squirrelのインストール/アンインストールイベントでの早期終了、`createRequire`経由でCJSパッケージを読む）
- 導入時に3件の環境固有の問題を発見・解消（gitフェッチ禁止による`overrides`、`electron-winstaller`の上流バグ、`@electron/packager`のNode 26非対応）。詳細は[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]Action Items参照
- **preloadのESM/`sandbox: false`設定（[[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|preload ESM・sandbox決定]]）がasar化後も維持されるかは、この導入セッションでは未検証のまま**——`electron-forge make`でSetup.exe生成までは確認したが、実際にインストール/起動してレンダラ・preload・contextBridgeが動作するところまでは確認していない（開発時の`electron .`起動確認とは別の検証項目）

## Related

- [[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]] — Forgeを含むツール比較（姉妹ノート）
- [[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]] — Forgeでの署名設定箇所（姉妹ノート）
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — 本ノートの一次情報源（実際の導入・発見した問題・Action Items）
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章11.2節#2]] — 対応する未決事項（パッケージングはForgeで決定済み、公開/署名は引き続き未決）

