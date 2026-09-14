---
date: 2026-05-15
description: "React で Chrome拡張を作るためのOSSテンプレート/フレームワーク3選（2026年時点）— Manifest V3 対応と HMR 最適化を基準に選定"
tags:
  - reference
  - chrome-extension
  - react
---

Chrome機能拡張をReactで実装する場合のオープンソースとして公開されているテンプレートを教えて

Reactを使用してChrome拡張機能を開発する際、2026年現在で最も推奨されるオープンソースのテンプレートおよびフレームワークを、特性別に3つ厳選して紹介します。

現在は単なる「テンプレート」よりも、Manifest V3への対応やHMR（ホットリロード）が高度に最適化された「フレームワーク」を利用するのが主流です。

---

## 1. 推奨テンプレート・フレームワーク比較

|名称|特徴|最適なケース|
|---|---|---|
|**WXT (Web Extension Toolbox)**|**2026年現在の本命。** 高速なViteベースで、ディレクトリ構造からManifestを自動生成。|開発効率と最新ツールチェーンを重視する場合|
|**Plasmo**|Reactフレンドリーな「拡張機能版Next.js」。ストレージや認証の統合が強力。|Reactの作法で大規模な拡張機能を開発したい場合|
|**Chrome Extension Boilerplate (Jonghakseo)**|シンプルかつスター数が多い（5k+）。ピュアなVite + React構成。|フレームワークに縛られず、標準的な構成で始めたい場合|

---

## 2. 各テンプレートの詳細と導入方法

### ① WXT (Next-gen Framework)

Viteを採用しており、ビルドが非常に高速です。`.wxt`ディレクトリで設定が完結するため、`manifest.json`を手動で細かく管理するストレスから解放されます。

- **GitHub:** [wxt-dev/wxt](https://github.com/wxt-dev/wxt)
    
- **具体的な導入方法:**
    
    Bash
    
    ```
    npx wxt@latest init my-extension
    # テンプレート選択で "React" を指定
    cd my-extension
    npm install
    npm run dev
    ```
    
- **根拠:** ブラウザ間の差異を吸収するポリフィル機能や、型安全なメッセージング機能が標準搭載されています。
    

### ② Plasmo (The Browser Extension Framework)

「It's like Next.js for browser extensions」を掲げており、Content Scriptsのインジェクション設定などをファイルシステムベースで直感的に行えます。

- **GitHub:** [PlasmoHQ/plasmo](https://github.com/PlasmoHQ/plasmo)
    
- **具体的な導入方法:**
    

Bash

````
    npx plasmo init
    # 指示に従ってプロジェクト名を入力
    cd my-project
    npm run dev
    ```
*   **根拠:** ReactコンポーネントをそのままPopupやOptionsページとして扱えるため、学習コストが極めて低いです。

### ③ chrome-extension-boilerplate-react-vite
特定のフレームワーク（WXTやPlasmo）を使わず、ViteとReact、TypeScriptの最小構成で開発したい場合に最適です。

*   **GitHub:** [Jonghakseo/chrome-extension-boilerplate-react-vite](https://github.com/Jonghakseo/chrome-extension-boilerplate-react-vite)
*   **具体的な導入方法:**
    
```bash
    git clone https://github.com/Jonghakseo/chrome-extension-boilerplate-react-vite.git
    cd chrome-extension-boilerplate-react-vite
    pnpm install
    pnpm dev
    ```
*   **根拠:** 5,000以上のスターを獲得しており、Tailwind CSSやi18nの設定も含まれているため、即座に実戦投入可能です。

---

## 3. 実装のステップ（最短成果への提案）

成果を最短で出すためのアクションプランです。

1.  **フレームワークの選定:** 迷ったら、現在最も勢いがありメンテナンスが活発な **WXT** を選択してください。
2.  **ブラウザへのロード:** 
    *   `npm run dev` 実行後、生成された `dist/chrome-mv3`（または類似）フォルダを確認。
    *   Chromeの `chrome://extensions/` を開き、「デベロッパーモード」をON。
    *   「パッケージ化されていない拡張機能を読み込む」から上記フォルダを選択。
3.  **UI開発の効率化:** 
    *   **Tailwind CSS** を併用し、デザイン時間を短縮してください。
    *   Shadow DOMを使用して、既存サイトのスタイル干渉を防ぐ設定（PlasmoやWXTなら標準機能で可能）を確認してください。



これらを使用することで、Manifest V3の複雑な仕様に悩まされることなく、Reactでの機能実装に集中できます。
````