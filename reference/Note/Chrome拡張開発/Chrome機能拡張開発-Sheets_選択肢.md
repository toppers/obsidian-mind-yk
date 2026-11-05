---
date: 2026-05-15
description: "指定IDの Google Spreadsheets の全ワークシート名を select の選択肢にし、指定シートの API_KEY 列の値を取得する Chrome拡張の実装例"
tags:
  - reference
  - chrome-extension
  - google-sheets
---

以下の仕様のChrome機能拡張を実装してください。

1. 指定IDのGoogle Spreadsheetsの全てのワークシート名を選択肢とするselectをもつフォームを持つ。1. 指定IDのGoogle Spreadsheetsの指定名のワークシートのAPI_KEY列の値を取得する

はい、承知いたしました。 指定された仕様を満たすChrome拡張機能の実装について、基本的な構成とコードの例を示します。

**注意点:**

- **Google Cloud Platformの設定:** この拡張機能を使用するには、Google Cloud Platformでプロジェクトを作成し、Google Sheets APIを有効にして、OAuth 2.0 クライアント ID（Chrome アプリ用）を取得する必要があります。取得したクライアントIDは`manifest.json`に設定します。
    
- **APIキー列:** 指定されたワークシートに「API_KEY」という名前のヘッダーを持つ列が存在することを前提としています。ヘッダー行は1行目にあると仮定します。
    
- **エラーハンドリング:** 簡略化のため、エラーハンドリングは最小限にしています。実際の開発では、ネットワークエラー、認証エラー、APIエラーなどを適切に処理する必要があります。
    
- **セキュリティ:** 取得したAPIキーの取り扱いには十分注意してください。
    

---

**1. `manifest.json` (拡張機能の設定ファイル)**

JSON

```
{
  "manifest_version": 3,
  "name": "Spreadsheet API Key Fetcher",
  "version": "1.0",
  "description": "Fetches API keys from a specified Google Spreadsheet.",
  "permissions": [
    "identity" // Googleアカウントでの認証に必要
  ],
  "host_permissions": [
    "https://sheets.googleapis.com/" // Google Sheets APIへのアクセス許可
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "images/icon16.png", // アイコン画像を適宜用意
      "48": "images/icon48.png",
      "128": "images/icon128.png"
    }
  },
  "oauth2": {
    "client_id": "YOUR_GOOGLE_CLOUD_OAUTH_CLIENT_ID.apps.googleusercontent.com", // ★★★ Google Cloudで取得したクライアントIDに置き換える ★★★
    "scopes": [
      "https://www.googleapis.com/auth/spreadsheets.readonly" // 読み取り専用アクセス許可
    ]
  },
  "icons": {
      "16": "images/icon16.png",
      "48": "images/icon48.png",
      "128": "images/icon128.png"
  }
}
```

- `YOUR_GOOGLE_CLOUD_OAUTH_CLIENT_ID.apps.googleusercontent.com` を、Google Cloud Consoleで取得した実際のOAuth 2.0 クライアント IDに置き換えてください。
    
- `images/` ディレクトリを作成し、適切なサイズのアイコン画像 (`icon16.png`, `icon48.png`, `icon128.png`) を配置してください。
    

---

**2. `popup.html` (ポップアップウィンドウのUI)**

HTML

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Spreadsheet API Key Fetcher</title>
  <style>
    body { font-family: sans-serif; width: 300px; padding: 10px; }
    label, input, select, button { display: block; margin-bottom: 10px; width: 95%; }
    #apiKeyResult { margin-top: 15px; word-wrap: break-word; }
    .loading { font-style: italic; color: gray; }
    .error { color: red; }
  </style>
</head>
<body>
  <h2>Spreadsheet API Key Fetcher</h2>

  <label for="spreadsheetId">Spreadsheet ID:</label>
  <input type="text" id="spreadsheetId" placeholder="Enter Google Spreadsheet ID">
  <button id="loadSheetsButton">Load Worksheets</button>

  <label for="worksheetSelect">Select Worksheet:</label>
  <select id="worksheetSelect" disabled>
    <option value="">-- Enter ID and Load --</option>
  </select>

  <button id="fetchApiKeyButton" disabled>Fetch API Key</button>

  <div id="status"></div>
  <div id="apiKeyResult"></div>

  <script src="popup.js"></script>
</body>
</html>
```

---

**3. `popup.js` (ポップアップの動作ロジック)**

JavaScript

```
const spreadsheetIdInput = document.getElementById('spreadsheetId');
const loadSheetsButton = document.getElementById('loadSheetsButton');
const worksheetSelect = document.getElementById('worksheetSelect');
const fetchApiKeyButton = document.getElementById('fetchApiKeyButton');
const statusDiv = document.getElementById('status');
const apiKeyResultDiv = document.getElementById('apiKeyResult');

let authToken = null; // 認証トークンを保持

// 1. 認証トークンを取得する関数
function getAuthToken(interactive) {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: interactive }, (token) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
      } else {
        authToken = token;
        resolve(token);
      }
    });
  });
}

// 2. ワークシート名を取得する関数
async function loadWorksheets() {
  const spreadsheetId = spreadsheetIdInput.value.trim();
  if (!spreadsheetId) {
    setStatus('Please enter a Spreadsheet ID.', 'error');
    return;
  }
  if (!authToken) {
    setStatus('Authenticating...', 'loading');
    try {
      await getAuthToken(true); // 初回はインタラクティブに認証
      setStatus('Authentication successful. Loading sheets...', 'loading');
    } catch (error) {
      setStatus(`Authentication failed: ${error.message}`, 'error');
      console.error('Authentication failed:', error);
      return;
    }
  }

  setStatus('Loading worksheets...', 'loading');
  worksheetSelect.innerHTML = '<option value="">-- Loading... --</option>';
  worksheetSelect.disabled = true;
  fetchApiKeyButton.disabled = true;
  apiKeyResultDiv.textContent = '';

  const url = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}?fields=sheets(properties(title))`;

  try {
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });

    if (!response.ok) {
        // トークンが無効になっている可能性があるので再認証を試みる
        if (response.status === 401) {
            console.log('Token might be invalid. Attempting to remove cached token and retry.');
            await new Promise((resolve, reject) => {
                chrome.identity.removeCachedAuthToken({ token: authToken }, resolve);
            });
            authToken = null; // トークンをクリア
            setStatus('Token expired. Re-authenticating...', 'loading');
            await getAuthToken(true); // 再度インタラクティブに認証
            if(authToken) {
                setStatus('Re-authenticated. Retrying load worksheets...', 'loading');
                loadWorksheets(); // 再試行
            } else {
                 setStatus('Re-authentication failed.', 'error');
            }
            return; // 再試行するのでここで終了
        }
      throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    worksheetSelect.innerHTML = '<option value="">-- Select Worksheet --</option>'; // デフォルトオプション
    if (data.sheets && data.sheets.length > 0) {
      data.sheets.forEach(sheet => {
        const option = document.createElement('option');
        option.value = sheet.properties.title;
        option.textContent = sheet.properties.title;
        worksheetSelect.appendChild(option);
      });
      worksheetSelect.disabled = false;
      fetchApiKeyButton.disabled = false; // シートが読み込めたらAPIキー取得ボタンを有効化
      setStatus('Worksheets loaded successfully.', '');
    } else {
      worksheetSelect.innerHTML = '<option value="">-- No worksheets found --</option>';
      setStatus('No worksheets found in this spreadsheet.', 'error');
    }
  } catch (error) {
    setStatus(`Error loading worksheets: ${error.message}`, 'error');
    worksheetSelect.innerHTML = '<option value="">-- Error Loading --</option>';
    worksheetSelect.disabled = true;
    fetchApiKeyButton.disabled = true;
    console.error('Error fetching worksheets:', error);
     // 認証エラーの場合、キャッシュされたトークンを削除することも検討
    if (error.message.includes('401') || error.message.includes('403')) {
        console.log('Potential auth error, consider removing cached token.');
        // chrome.identity.removeCachedAuthToken({ token: authToken }, () => {});
    }
  }
}

// 3. APIキーを取得する関数
async function fetchApiKey() {
  const spreadsheetId = spreadsheetIdInput.value.trim();
  const selectedSheet = worksheetSelect.value;

  if (!spreadsheetId || !selectedSheet) {
    setStatus('Please select a spreadsheet and worksheet.', 'error');
    return;
  }
  if (!authToken) {
     setStatus('Not authenticated. Please load worksheets first.', 'error');
     return;
  }

  setStatus('Fetching API Key...', 'loading');
  apiKeyResultDiv.textContent = '';
  fetchApiKeyButton.disabled = true; // 処理中はボタンを無効化

  try {
    // a) ヘッダー行を取得して 'API_KEY' 列のインデックスを見つける
    const headerRange = `'${selectedSheet}'!1:1`; // 1行目を取得
    const headerUrl = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${encodeURIComponent(headerRange)}`;
    let apiKeyColumnIndex = -1;

    const headerResponse = await fetch(headerUrl, {
      headers: { 'Authorization': `Bearer ${authToken}` }
    });
    if (!headerResponse.ok) throw new Error(`HTTP error! status: ${headerResponse.status} ${headerResponse.statusText}`);
    const headerData = await headerResponse.json();

    if (headerData.values && headerData.values[0]) {
      apiKeyColumnIndex = headerData.values[0].findIndex(header => header.trim().toUpperCase() === 'API_KEY');
    }

    if (apiKeyColumnIndex === -1) {
      throw new Error("'API_KEY' column not found in the first row.");
    }

    // 列インデックスをアルファベット表記に変換 (0->A, 1->B, ...)
    let columnName = '';
    let tempIndex = apiKeyColumnIndex;
    while (tempIndex >= 0) {
        columnName = String.fromCharCode(65 + (tempIndex % 26)) + columnName;
        tempIndex = Math.floor(tempIndex / 26) - 1;
    }


    // b) 'API_KEY' 列の値を取得 (ヘッダー行を除く)
    const dataRange = `'${selectedSheet}'!${columnName}2:${columnName}`; // 例: 'Sheet1'!C2:C
    const dataUrl = `https://sheets.googleapis.com/v4/spreadsheets/${spreadsheetId}/values/${encodeURIComponent(dataRange)}`;

    const dataResponse = await fetch(dataUrl, {
        headers: { 'Authorization': `Bearer ${authToken}` }
    });
     if (!dataResponse.ok) {
        // ヘッダー取得時と同様にトークン失効の可能性を考慮
        if (dataResponse.status === 401) {
             console.log('Token might be invalid during data fetch. Attempting to remove cached token and retry.');
            await new Promise((resolve, reject) => {
                chrome.identity.removeCachedAuthToken({ token: authToken }, resolve);
            });
            authToken = null; // トークンをクリア
            setStatus('Token expired. Re-authenticating...', 'loading');
            await getAuthToken(true);
             if(authToken) {
                 setStatus('Re-authenticated. Retrying fetch API Key...', 'loading');
                 fetchApiKey(); // 再試行
             } else {
                 setStatus('Re-authentication failed.', 'error');
             }
            return;
        }
        throw new Error(`HTTP error! status: ${dataResponse.status} ${dataResponse.statusText}`);
    }
    const apiKeyData = await dataResponse.json();

    if (apiKeyData.values && apiKeyData.values.length > 0) {
      // 最初の空でないキーを取得（もしくは全てのキーをリスト表示なども可能）
      const firstKey = apiKeyData.values.flat().find(key => key && key.trim() !== '');
      if (firstKey) {
        apiKeyResultDiv.textContent = `Found API Key: ${firstKey}`; // ★★★ 取得したキーの表示方法注意 ★★★
        setStatus('API Key fetched successfully.', '');
      } else {
        apiKeyResultDiv.textContent = 'API_KEY column found, but no values detected (excluding header).';
        setStatus('', '');
      }
      // 全てのキーをリスト表示する場合:
      // const allKeys = apiKeyData.values.flat().filter(key => key && key.trim() !== '');
      // apiKeyResultDiv.innerHTML = 'Found API Keys:<br>' + allKeys.join('<br>');
    } else {
      apiKeyResultDiv.textContent = 'API_KEY column found, but no values detected (excluding header).';
      setStatus('', '');
    }

  } catch (error) {
    setStatus(`Error fetching API Key: ${error.message}`, 'error');
    apiKeyResultDiv.textContent = '';
    console.error('Error fetching API Key:', error);
    // 認証エラーの場合、キャッシュされたトークンを削除することも検討
    if (error.message.includes('401') || error.message.includes('403')) {
        console.log('Potential auth error, consider removing cached token.');
        // chrome.identity.removeCachedAuthToken({ token: authToken }, () => {});
    }
  } finally {
    fetchApiKeyButton.disabled = false; // 処理完了後、ボタンを再度有効化
  }
}

// ステータスメッセージを設定するヘルパー関数
function setStatus(message, type = '') { // type: 'loading', 'error', ''
  statusDiv.textContent = message;
  statusDiv.className = type; // CSSクラスを適用
}

// イベントリスナーの設定
loadSheetsButton.addEventListener('click', loadWorksheets);
fetchApiKeyButton.addEventListener('click', fetchApiKey);

// ポップアップが開かれたときに自動で認証を試みる (非インタラクティブ)
document.addEventListener('DOMContentLoaded', async () => {
    setStatus('Attempting to authenticate...', 'loading');
    try {
        // まず非インタラクティブに試す
        await getAuthToken(false);
        setStatus('Ready. Enter Spreadsheet ID and load sheets.', '');
    } catch (error) {
        // 非インタラクティブで失敗した場合 (初回起動など)
        console.log('Non-interactive auth failed, user interaction will be required.');
        setStatus('Authentication required. Enter Spreadsheet ID and load sheets.', '');
        // 必要であれば、ここでユーザーに認証を促すUIを表示しても良い
    }
});
```

---

**4. 使い方**

1. 上記の3つのファイル (`manifest.json`, `popup.html`, `popup.js`) と、`images` フォルダ（アイコン画像入り）を一つのフォルダにまとめます。
    
2. Chromeブラウザで `chrome://extensions/` を開きます。
    
3. 右上の「デベロッパー モード」をオンにします。
    
4. 「パッケージ化されていない拡張機能を読み込む」ボタンをクリックし、作成したフォルダを選択します。
    
5. 拡張機能のアイコンがツールバーに追加されます。
    
6. アイコンをクリックするとポップアップが開きます。
    
7. 「Spreadsheet ID」入力欄に、対象のGoogle SpreadsheetのID（URL中の `d/` と `/edit` の間の長い文字列）を入力します。
    
8. 「Load Worksheets」ボタンをクリックします。
    
    - 初回はGoogleアカウントへのアクセス許可を求める画面が表示されるので、許可してください。
        
    - Spreadsheet内のワークシート名がドロップダウンリストに読み込まれます。
        
9. ドロップダウンから目的のワークシートを選択します。
    
10. 「Fetch API Key」ボタンをクリックします。
    
11. 選択されたワークシートの「API_KEY」列にある最初の値がポップアップ内に表示されます。
    

このコードは基本的な機能を提供するものです。必要に応じて、エラーハンドリングの強化、UIの改善、取得したAPIキーの利用方法（クリップボードへのコピー機能など）を追加開発してください。