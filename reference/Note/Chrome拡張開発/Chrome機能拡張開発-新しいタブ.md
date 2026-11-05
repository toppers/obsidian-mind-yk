---
date: 2026-05-15
description: "popup.html ではなく新しいタブを開いて書き込む方法2種 — バックグラウンドスクリプトからの chrome.tabs.create() ほか"
tags:
  - reference
  - chrome-extension
---

Chrome拡張機能で、`popup.html` ではなく新しいタブを開いてそこに書き込むには、主に以下の2つの方法があります。

**方法1: バックグラウンドスクリプトから `chrome.tabs.create()` を使用する**

この方法は、拡張機能のアイコンがクリックされたときや、何らかのイベントが発生したときに新しいタブを開く場合に適しています。

1. **マニフェストファイル (`manifest.json`) の設定:**
    
    - `manifest_version` を `3` に設定している場合、`background` プロパティに `service_worker` を指定します。
        
    - `manifest_version` が `2` の場合は、`background` プロパティに `scripts` を指定します。
        
    - `permissions` に `"tabs"` を追加します。
        
    
    JSON
    
    ```
    {
      "manifest_version": 3,
      "name": "New Tab Writer",
      "version": "1.0",
      "description": "新しいタブに書き込む拡張機能",
      "permissions": [
        "tabs"
      ],
      "background": {
        "service_worker": "background.js" // manifest_version 3 の場合
        // "scripts": ["background.js"],   // manifest_version 2 の場合
        "persistent": false             // manifest_version 2 の場合
      },
      "action": {
        "default_popup": "" // ポップアップを使用しないことを明示
      }
    }
    ```
    
2. **バックグラウンドスクリプト (`background.js`) の作成:**
    
    - `chrome.action.onClicked.addListener()` を使用して、拡張機能のアイコンがクリックされたときの処理を定義します。
        
    - `chrome.tabs.create()` を使用して新しいタブを開き、書き込みたい HTML ファイルの URL を指定します。
        
    
    JavaScript
    
    ```
    chrome.action.onClicked.addListener((tab) => {
      chrome.tabs.create({ url: 'new_tab_content.html' });
    });
    ```
    
3. **新しいタブに表示する HTML ファイル (`new_tab_content.html`) の作成:**
    
    - このファイルに、書き込みたい内容や JavaScript コードを記述します。
        
    
    HTML
    
    ```
    <!DOCTYPE html>
    <html>
    <head>
      <title>新しいタブ</title>
    </head>
    <body>
      <h1>ここに書き込みたい内容</h1>
      <textarea id="myTextArea"></textarea>
      <script src="new_tab_script.js"></script>
    </body>
    </html>
    ```
    
4. **新しいタブで実行する JavaScript ファイル (`new_tab_script.js`) の作成 (任意):**
    
    - `new_tab_content.html` 内の要素を操作したり、動的な処理を行ったりする場合に作成します。
        

**方法2: コンテンツスクリプトから `window.open()` を使用する (推奨されません)**

コンテンツスクリプトは、特定のウェブページに挿入されて実行されるスクリプトです。この方法を使うと、拡張機能のポップアップからではなく、コンテンツスクリプトが動作しているウェブページから新しいタブを開くことになります。一般的には、拡張機能のアイコンクリックなどのアクションに応じて新しいタブを開きたい場合は、方法1を使用する方が適切です。

1. **マニフェストファイル (`manifest.json`) の設定:**
    
    - `permissions` に `"tabs"` または `<all_urls>` を追加します。
        
    - `content_scripts` で、コンテンツスクリプトを挿入するウェブページを指定します。
        
    
    JSON
    
    ```
    {
      "manifest_version": 3,
      "name": "New Tab Writer (Content Script)",
      "version": "1.0",
      "description": "コンテンツスクリプトから新しいタブに書き込む拡張機能",
      "permissions": [
        "tabs"
        // "<all_urls>" // 特定のURLに限定しない場合
      ],
      "content_scripts": [
        {
          "matches": ["<all_urls>"], // または特定のURLパターン
          "js": ["content.js"]
        }
      ],
      "action": {
        "default_popup": "popup.html" // ポップアップはトリガーとして使用
      }
    }
    ```
    
2. **ポップアップ HTML (`popup.html`) の作成:**
    
    - 新しいタブを開くためのボタンなどを配置します。
        
    
    HTML
    
    ```
    <!DOCTYPE html>
    <html>
    <head>
      <title>ポップアップ</title>
    </head>
    <body>
      <button id="openNewTabButton">新しいタブを開く</button>
      <script src="popup.js"></script>
    </body>
    </html>
    ```
    
3. **ポップアップ JavaScript (`popup.js`) の作成:**
    
    - ボタンがクリックされたときに、現在のタブにメッセージを送信する処理を記述します。
        
    
    JavaScript
    
    ```
    document.addEventListener('DOMContentLoaded', () => {
      const openNewTabButton = document.getElementById('openNewTabButton');
      openNewTabButton.addEventListener('click', () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          chrome.tabs.sendMessage(tabs[0].id, { action: 'openNewTab' });
        });
      });
    });
    ```
    
4. **コンテンツスクリプト (`content.js`) の作成:**
    
    - ポップアップからのメッセージを受信し、`window.open()` を使用して新しいタブを開きます。
        
    
    JavaScript
    
    ```
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'openNewTab') {
        window.open('new_tab_content.html', '_blank');
      }
    });
    ```
    
5. **新しいタブに表示する HTML ファイル (`new_tab_content.html`) の作成:**
    
    - 方法1と同様です。
        

**どちらの方法を選ぶべきか:**

- 拡張機能のアイコンクリックなど、拡張機能自体のアクションに応じて新しいタブを開きたい場合は **方法1** を選択してください。
    
- 現在のウェブページの内容に基づいて新しいタブを開きたいなど、特定のウェブページとの連携が必要な場合は **方法2** を検討できますが、一般的には方法1の方がシンプルで推奨されます。
    

**注意点:**

- `manifest.json` ファイルの記述ミスがあると、拡張機能が正常に動作しません。
    
- `chrome.tabs.create()` で開く HTML ファイルは、拡張機能のパッケージ内に含める必要があります。`chrome.runtime.getURL()` を使用して、拡張機能内のファイルの絶対パスを取得できます。例: `chrome.tabs.create({ url: chrome.runtime.getURL('new_tab_content.html') });`
    

上記の手順に従うことで、`popup.html` ではなく、新しいタブを開いてそこに自由に内容を書き込むChrome拡張機能を作成できます。