---
date: 2026-05-15
description: "拡張機能アイコンのクリックでウィンドウを表示する3方式 — 最も一般的なポップアップ表示ほか、それぞれの特徴と実装方法"
tags:
  - reference
  - chrome-extension
---

はい、承知いたしました。Chrome拡張機能で、拡張機能のアイコンをクリックしたときにウィンドウを表示する方法について解説します。

主な方法として、以下の3つが考えられます。それぞれの特徴と実装方法を説明します。

1. **ポップアップ (Popup) を表示する**: 最も一般的で簡単な方法です。アイコン直下に小さなウィンドウを表示します。
    
2. **新しいウィンドウ (Window) を開く**: 独立した新しいブラウザウィンドウを生成します。サイズや種類を細かく指定できます。
    
3. **新しいタブ (Tab) で開く**: 現在のウィンドウに新しいタブを追加して、そこにコンテンツを表示します。
    

---

### 方法1: ポップアップ (Popup) を表示する

アイコンをクリックした際に、その下に小さなHTMLページを表示する方法です。多くの拡張機能で採用されている最も手軽な方法です。

#### 特徴

- 実装が非常に簡単です。
    
- ウィンドウの外側をクリックすると自動的に閉じます。
    
- 一時的な情報の表示や簡単な操作に適しています。
    

#### 実装手順

##### 1. `manifest.json` を編集する

`action` キーの中に `default_popup` を追加し、表示したいHTMLファイルを指定します。

**`manifest.json`**

JSON

```
{
  "manifest_version": 3,
  "name": "ポップアップ表示サンプル",
  "version": "1.0",
  "description": "アイコンクリックでポップアップを表示します。",
  "action": {
    "default_icon": "icon.png",
    "default_title": "ここをクリック",
    "default_popup": "popup.html"
  },
  "icons": {
    "48": "icon.png"
  }
}
```

##### 2. ポップアップ用のHTMLファイルを作成する

`manifest.json`で指定したHTMLファイルを作成します。このHTMLには、CSSやJavaScriptを通常通り読み込ませることができます。

**`popup.html`**

HTML

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ポップアップ</title>
  <style>
    body {
      width: 200px; /* ポップアップの幅を指定 */
      font-family: sans-serif;
    }
    h1 {
      font-size: 16px;
    }
  </style>
</head>
<body>
  <h1>こんにちは！</h1>
  <p>これはポップアップウィンドウです。</p>
</body>
</html>
```

##### 3. アイコンファイルを準備する

`manifest.json`で指定したアイコンファイル（例: `icon.png`）をプロジェクトフォルダに配置します。

これだけで、拡張機能のアイコンをクリックすると`popup.html`が表示されるようになります。

---

### 方法2: 新しいウィンドウ (Window) を開く

アイコンをクリックした際に、`chrome.windows.api` を使って独立した新しいウィンドウを生成します。

#### 特徴

- ウィンドウのサイズ、位置、種類（ノーマル、ポップアップ、パネルなど）を自由にカスタマイズできます。
    
- より複雑なUIや、長時間表示させておく必要がある機能に適しています。
    
- バックグラウンドスクリプト（Service Worker）からの制御が必要です。
    

#### 実装手順

##### 1. `manifest.json` を編集する

バックグラウンドスクリプトを登録し、ウィンドウを操作するための権限を要求します。**この方法では `default_popup` は指定しません。**

**`manifest.json`**

JSON

```
{
  "manifest_version": 3,
  "name": "新しいウィンドウ表示サンプル",
  "version": "1.0",
  "description": "アイコンクリックで新しいウィンドウを開きます。",
  "background": {
    "service_worker": "background.js"
  },
  "permissions": [
    "windows"
  ],
  "action": {
    "default_icon": "icon.png",
    "default_title": "新しいウィンドウを開く"
  },
  "icons": {
    "48": "icon.png"
  }
}
```

##### 2. バックグラウンドスクリプトを作成する

アイコンクリックイベントを監視し、クリックされたら `chrome.windows.create()` を呼び出して新しいウィンドウを生成します。

**`background.js`**

JavaScript

```
chrome.action.onClicked.addListener((tab) => {
  chrome.windows.create({
    url: 'window.html', // 新しいウィンドウで開くHTMLファイル
    type: 'popup',      // ウィンドウの種類 'normal' や 'panel' も選択可
    width: 400,         // ウィンドウの幅
    height: 300         // ウィンドウの高さ
  });
});
```

##### 3. ウィンドウ用のHTMLファイルを作成する

新しいウィンドウに表示するコンテンツを作成します。

**`window.html`**

HTML

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>新しいウィンドウ</title>
</head>
<body>
  <h1>独立したウィンドウです</h1>
  <p>このウィンドウは自由にリサイズできます。</p>
</body>
</html>
```

##### 4. アイコンファイルを準備する

方法1と同様に、アイコンファイル（例: `icon.png`）を配置します。

---

### 方法3: 新しいタブで開く

アイコンをクリックした際に、`chrome.tabs.api` を使って新しいタブでHTMLページを開きます。

#### 特徴

- ユーザーにとって馴染み深いタブUIでコンテンツを提供できます。
    
- ブラウザの履歴にも残ります。
    
- 実装は比較的簡単です。
    

#### 実装手順

##### 1. `manifest.json` を編集する

この方法もバックグラウンドスクリプトを使用します。**`default_popup` は指定しません。** `tabs` 権限は多くの場合不要ですが、明示的に記述することもできます。

**`manifest.json`**

JSON

```
{
  "manifest_version": 3,
  "name": "新しいタブ表示サンプル",
  "version": "1.0",
  "description": "アイコンクリックで新しいタブを開きます。",
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_icon": "icon.png",
    "default_title": "新しいタブを開く"
  },
  "icons": {
    "48": "icon.png"
  }
}
```

##### 2. バックグラウンドスクリプトを作成する

アイコンクリックイベントを監視し、`chrome.tabs.create()` を呼び出します。

**`background.js`**

JavaScript

```
chrome.action.onClicked.addListener((tab) => {
  chrome.tabs.create({
    url: 'page.html' // 新しいタブで開くHTMLファイル
  });
});
```

##### 3. タブ用のHTMLファイルを作成する

**`page.html`**

HTML

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>拡張機能ページ</title>
</head>
<body>
  <h1>新しいタブで開かれました</h1>
  <p>これは拡張機能の専用ページです。</p>
</body>
</html>
```

##### 4. アイコンファイルを準備する

同様に、アイコンファイル（例: `icon.png`）を配置します。

### まとめ

どの方法を選ぶかは、拡張機能の目的によって決まります。

|**方法**|**特徴**|**適した用途**|**実装の容易さ**|
|---|---|---|---|
|**ポップアップ**|アイコン直下に表示。自動で閉じる。|簡単な設定、一時的な情報表示、クリップボードへのコピーなど|★★★（最も簡単）|
|**新しいウィンドウ**|独立したウィンドウ。サイズや種類が自由。|高機能なツール、ダッシュボード、メディアプレーヤーなど|★★☆（やや複雑）|
|**新しいタブ**|通常のブラウザタブとして表示。|ヘルプページ、設定画面、詳細な情報の表示など|★★☆（比較的簡単）|

まずは最も簡単な「ポップアップ」から試してみて、機能が複雑になったり、より広い表示領域が必要になったりした場合に「新しいウィンドウ」や「新しいタブ」を検討するのがおすすめです。