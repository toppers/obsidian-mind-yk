---
date: 2026-05-15
description: "Service Worker から tab.html を開き、Web API から取得したデータをフォームの SELECT にセットする実装 — manifest.json を含む3ファイル構成"
tags:
  - reference
  - chrome-extension
---

はい、承知いたしました。Chrome機能拡張で、バックグラウンドのService Workerから特定のHTMLページ（`tab.html`）を開き、そのページ内で指定したWeb APIからデータを取得してフォームのSELECT要素にセットする、という機能ですね。

このタスクを実現するために、以下の3つのファイルを作成または修正する必要があります。

1. **`manifest.json`**: Chrome機能拡張の基本的な情報、必要な権限、そしてService Workerを定義します。
    
2. **`service-worker.js`**: 機能拡張のバックグラウンドで動作し、機能拡張アイコンがクリックされたときなどに`tab.html`を開く処理を記述します。
    
3. **`tab.html`**: ユーザーインターフェースとなるHTMLファイルです。ここにSELECT要素を追加し、ページロード時にAPIからデータを取得してSELECT要素にオプションとして追加するJavaScriptコードを記述します。
    

それでは、これらのファイルを作成し、機能拡張を構築する手順をご説明します。

### 開発ステップの概要

1. `manifest.json`ファイルを作成し、必要な情報を設定します。
    
2. `service-worker.js`ファイルを作成し、`tab.html`を開くコードを記述します。
    
3. 既存の`tab.html`に、APIから取得したデータで選択肢を生成する`<select>`要素とJavaScriptコードを追加します。
    
4. これらのファイルをフォルダにまとめて、Chromeブラウザに機能拡張として読み込みます。
    

### 前提条件と注意点

- **API URL**: Web APIの名前の配列をJSON形式で返すAPIのURLが必要です。以下のコード例では、このURLを`YOUR_API_URL_HERE`というプレースホルダーにしていますので、実際のURLに置き換えてください。
    
- **APIレスポンス形式**: APIは、`["name1", "name2", "name3", ...]` のような文字列の配列をJSON形式で返すことを想定しています。
    
- **機能拡張の権限**: APIへのアクセスには、`manifest.json`で該当するURLに対するホスト権限が必要です。また、新しいタブを開くために`tabs`権限が必要です。
    
- **エラーハンドリング**: API呼び出しが失敗した場合の基本的なエラーログは追加しますが、より詳細なエラー表示などは必要に応じて追加してください。
    

---

### 1. `manifest.json` のコード

機能拡張の定義ファイルです。

JSON

```
{
  "manifest_version": 3,
  "name": "Form Options Loader",
  "version": "1.0",
  "description": "Opens a form tab and loads sheet name options from an API.",
  "permissions": [
    "tabs",
    "activeTab",
    "scripting"
    // 以下にAPIのURLと、tab.htmlのフォームの送信先URLに対するホスト権限を追加します
    // 例: "https://your-api-domain.com/*",
    // "https://script.google.com/macros/*"
  ],
  "host_permissions": [
    "https://your-api-domain.com/*",  // ★ ここをAPIのドメインに置き換えてください
    "https://script.google.com/macros/*" // ★ フォームの送信先URLのドメイン
  ],
  "background": {
    "service_worker": "service-worker.js"
  },
  "action": {
    "default_popup": "" // ポップアップなし。アイコンクリックでService Workerが起動
  }
}
```

**コードの説明:**

- `manifest_version`: マニフェストのバージョンを指定します（現在は3が推奨）。
    
- `name`, `version`, `description`: 機能拡張の基本情報です。
    
- `permissions`: 機能拡張が必要とする権限です。
    
    - `tabs`: 新しいタブを作成・操作するために必要です。
        
    - `activeTab`: ユーザーが現在アクティブなタブに関する情報を一時的に取得するために使用できますが、この特定のタスクでは`tabs`と`host_permissions`がより重要です。
        
    - `scripting`: （念のため追加していますが、このアプローチでは不要かもしれません。`tab.html`内のスクリプトはページ自身のコンテキストで実行されるため。）
        
- `host_permissions`: 機能拡張が特定のURLに対して`Workspace`などの操作を行うために必要です。APIのURLとフォームの送信先URLのドメインに対する権限を追加してください。`*`はサブドメインやパスの任意の部分を意味します。
    
- `background`: Service Workerを設定します。`service_worker`にService Workerのファイル名を指定します。
    
- `action`: ブラウザのアドレスバーの横に表示される機能拡張アイコンの動作を定義します。`default_popup`を空にすることで、アイコンクリック時に`action.onClicked`イベントがService Workerに通知されるようになります。
    

### 2. `service-worker.js` のコード

機能拡張のバックグラウンドで動作し、`tab.html`を開く処理を行います。

JavaScript

```
// 機能拡張アイコンがクリックされたときに新しいタブを開く
chrome.action.onClicked.addListener(() => {
  // 機能拡張内のtab.htmlのパスを取得して新しいタブで開く
  chrome.tabs.create({
    url: chrome.runtime.getURL('tab.html')
  });
});
```

**コードの説明:**

- `chrome.action.onClicked.addListener()`: 機能拡張アイコンがクリックされたときに実行されるリスナー関数を登録します。
    
- `chrome.tabs.create({ url: ... })`: 新しいタブを作成します。
    
- `chrome.runtime.getURL('tab.html')`: 機能拡張のディレクトリ内にある`tab.html`ファイルの完全なURLを取得します。これにより、機能拡張のコンテキストでHTMLファイルが開かれます。
    

### 3. `tab.html` の修正コード

元の`tab.html`に、`sheetName`用のSELECT要素と、APIからデータを取得して選択肢を追加するJavaScriptコードを追加します。

HTML

```
<!DOCTYPE html>
<html>
<head>
  <title>Form Options</title>
  <style>
    body {
      font-family: sans-serif;
      padding: 10px;
    }
    label {
      display: block;
      margin-bottom: 5px;
    }
  </style>
</head>
<body>
  <form action="https://script.google.com/macros/s/REDACTED-GAS-DEPLOYMENT-ID/exec" method="GET">
    <h2>Select Action:</h2>
    <label>
      <input type="radio" name="cmd" value="new_gss"> New Google Sheets
    </label>
    <label>
      <input type="radio" name="cmd" value="new_docs"> New Google Docs
    </label>
    <label>
      <input type="radio" name="cmd" value="new_docs_date"> New Google Docs with Date
    </label>
    <label>
      <input type="radio" name="cmd" value="new_chomemo"> New Chome Memo
    </label>
    <label>
      <input type="radio" name="cmd" value="current_date"> Get Current Date
    </label>
    <label>
      <input type="radio" name="cmd" value="redirect"> Redirect to Link
    </label>
    <label>
      <input type="radio" name="cmd" value="link"> Open Specific Link
    </label>
    <label>
      <input type="radio" name="cmd" value="web_api"> Call Web API
    </label>

    <br>

    <h2>Select Sheet Name:</h2>
    <label for="sheetNameSelect">Sheet Name:</label>
    <select id="sheetNameSelect" name="sheetName">
      <option value="">Loading...</option> </select>

    <br>

    <input type="submit" value="Submit">
  </form>

  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const sheetNameSelect = document.getElementById('sheetNameSelect');
      // ★ ここにWeb APIのURLを指定してください
      const apiUrl = 'YOUR_API_URL_HERE';

      // APIからシート名のリストを取得
      fetch(apiUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
          }
          return response.json();
        })
        .then(data => {
          // SELECT要素の既存のオプションをクリア
          sheetNameSelect.innerHTML = '';

          if (Array.isArray(data)) {
            // 取得した配列を元にオプションを追加
            data.forEach(name => {
              const option = document.createElement('option');
              option.value = name;
              option.textContent = name;
              sheetNameSelect.appendChild(option);
            });
          } else {
             // データが配列でない場合のエラー処理
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "Error loading names";
            sheetNameSelect.appendChild(option);
            console.error('API did not return an array:', data);
          }
        })
        .catch(error => {
          console.error('Error fetching API names:', error);
           // エラー発生時の表示
          sheetNameSelect.innerHTML = ''; // 読み込み中表示をクリア
          const option = document.createElement('option');
          option.value = "";
          option.textContent = "Error loading names";
          sheetNameSelect.appendChild(option);
        });
    });
  </script>
</body>
</html>
```

**コードの説明:**

- `<label for="sheetNameSelect">`と`<select id="sheetNameSelect" name="sheetName">`: `sheetName`という名前の新しいSELECT要素を追加しました。初期状態では「Loading...」というオプションが表示されます。
    
- `<script>`タグ: ページがロードされた後に実行されるJavaScriptコードを含みます。
    
- `document.addEventListener('DOMContentLoaded', ...)`: HTMLドキュメントが完全にロードおよびパースされた後にコードを実行するためのイベントリスナーです。
    
- `const sheetNameSelect = document.getElementById('sheetNameSelect');`: 追加したSELECT要素を取得します。
    
- `const apiUrl = 'YOUR_API_URL_HERE';`: **ここに、Web APIの実際のURLを貼り付けてください。**
    
- `Workspace(apiUrl)`: 指定されたURLからデータを非同期に取得します。
    
- `.then(response => { ... })`: `Workspace`が成功した場合に実行されます。レスポンスが正常（HTTPステータスコード200番台）か確認し、問題なければJSONとしてパースします。
    
- `.then(data => { ... })`: JSONのパースが成功した場合に実行されます。
    
    - `sheetNameSelect.innerHTML = '';`: 既存の「Loading...」などのオプションをクリアします。
        
    - `if (Array.isArray(data))`: 取得したデータが配列であることを確認します。
        
    - `data.forEach(name => { ... })`: 配列の各要素（Web APIの名前を想定）に対してループ処理を行います。
        
    - `const option = document.createElement('option'); ... sheetNameSelect.appendChild(option);`: 新しい`<option>`要素を作成し、`value`と`textContent`に取得した名前を設定し、SELECT要素に追加します。
        
- `.catch(error => { ... })`: `Workspace`またはJSONパース中にエラーが発生した場合に実行されます。コンソールにエラーを出力し、SELECT要素にエラーメッセージを表示します。
    

### 機能拡張のインストール方法

1. 上記の3つのコード (`manifest.json`, `service-worker.js`, 修正した`tab.html`) を、すべて同じ新しいフォルダ内に保存します。ファイル名は上記の通りにしてください。
    
2. `manifest.json`と`tab.html`内のプレースホルダー (`YOUR_API_URL_HERE` や `host_permissions`) を実際の情報に置き換えてください。
    
3. Chromeブラウザを開き、アドレスバーに `chrome://extensions/` と入力して拡張機能ページを開きます。
    
4. ページの右上にある「デベロッパーモード」のトグルスイッチをオンにします。
    
5. 左上に表示される「パッケージされていない拡張機能を読み込む」ボタンをクリックします。
    
6. 先ほど作成したフォルダを選択します。
    
7. 機能拡張が読み込まれ、リストに表示されます。アイコンがブラウザのアドレスバーの横に表示されるようになります。
    

機能拡張のアイコンをクリックすると、新しいタブで`tab.html`が開かれ、指定したAPIからデータが読み込まれて「Select Sheet Name」のドロップダウンにオプションが追加されるはずです。

もし何か不明な点や、特定の箇所でエラーが発生した場合は、お気軽にご質問ください。コーディングのお手伝いをさせていただきます。