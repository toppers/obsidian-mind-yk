---
date: 2026-05-15
description: "フォーム入力を URL パラメータへ組み立て、HTTPS の GET/PUT で指定URLに送信する Chrome拡張の実装手順"
tags:
  - reference
  - chrome-extension
---

Google Chromeの拡張機能で、フォーム入力をURLパラメータとして組み立ててHTTPSのGET/PUTメソッドで指定URLに送信する機能ですね。

実装手順は以下の通りです。

## 1. 拡張機能の作成

### 1.1. マニフェストファイル (manifest.json) の作成

拡張機能の設定を記述する`manifest.json`を作成します。

JSON

```
{
  "manifest_version": 3,
  "name": "Form to URL Parameter",
  "version": "1.0",
  "description": "フォーム入力をURLパラメータとして送信",
  "permissions": [
    "activeTab",
    "storage",
    "scripting"
  ],
  "action": {
    "default_popup": "popup.html"
  }
}
```

- `permissions`: 拡張機能に必要な権限を記述します。
    
    - `activeTab`: 現在開いているタブへのアクセス権
        
    - `storage`: 拡張機能の設定データ保存権
        
    - `scripting`: スクリプト実行権
        

### 1.2. ポップアップ画面 (popup.html) の作成

拡張機能のUIとなるポップアップ画面`popup.html`を作成します。

HTML

```
<!DOCTYPE html>
<html>
<head>
  <title>Form to URL Parameter</title>
</head>
<body>
  <h1>Form to URL Parameter</h1>
  <form id="myForm">
    <label for="url">URL:</label><br>
    <input type="text" id="url" name="url" size="50"><br><br>

    <label for="method">Method:</label><br>
    <select id="method" name="method">
      <option value="GET">GET</option>
      <option value="PUT">PUT</option>
    </select><br><br>

    <div id="formFields">
      </div>

    <button type="button" id="addFormField">Add Field</button>
    <button type="submit">Send</button>
  </form>

  <script src="popup.js"></script>
</body>
</html>
```

### 1.3. スクリプト (popup.js) の作成

ポップアップ画面の処理を行う`popup.js`を作成します。

JavaScript

```
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('myForm');
  const urlInput = document.getElementById('url');
  const methodSelect = document.getElementById('method');
  const formFields = document.getElementById('formFields');
  const addFormFieldButton = document.getElementById('addFormField');

  // フォームフィールド追加
  addFormFieldButton.addEventListener('click', function() {
    const div = document.createElement('div');
    div.innerHTML = `
      <input type="text" name="fieldName" placeholder="Field Name">
      <input type="text" name="fieldValue" placeholder="Field Value">
      <button type="button" class="removeFormField">Remove</button>
    `;
    formFields.appendChild(div);

    // 削除ボタン
    const removeButton = div.querySelector('.removeFormField');
    removeButton.addEventListener('click', function() {
      formFields.removeChild(div);
    });
  });

  // 送信処理
  form.addEventListener('submit', function(event) {
    event.preventDefault();

    const url = urlInput.value;
    const method = methodSelect.value;
    const params = new URLSearchParams();

    // フォームフィールドの値を取得
    const fieldInputs = formFields.querySelectorAll('input[name="fieldName"]');
    const valueInputs = formFields.querySelectorAll('input[name="fieldValue"]');
    for (let i = 0; i < fieldInputs.length; i++) {
      const name = fieldInputs[i].value;
      const value = valueInputs[i].value;
      params.append(name, value);
    }

    // URL作成
    const queryString = params.toString();
    const fullUrl = url + (queryString ? `?${queryString}` : '');

    // 送信
    fetch(fullUrl, { method })
      .then(response => {
        // レスポンス処理
        console.log(response);
      })
      .catch(error => {
        console.error(error);
      });
  });
});
```

## 2. 拡張機能のインストール

1. Chromeのアドレスバーに`chrome://extensions/`と入力して拡張機能管理画面を開く
    
2. 「デベロッパーモード」をオンにする
    
3. 「パッケージ化されていないものを読み込む」をクリック
    
4. 作成した拡張機能のフォルダを選択
    

## 3. 拡張機能の使用

1. 拡張機能のアイコンをクリックしてポップアップを開く
    
2. URL、Method、フォームフィールドを入力
    
3. 「Send」ボタンをクリック
    

## その他

- エラー処理やUIの改善は適宜行ってください。
    
- `fetch` APIの`body`にJSON文字列を設定することで、PUTメソッドでJSONデータを送信できます。
    

ご不明な点がありましたらお気軽にご質問ください。