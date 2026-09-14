---
date: 2026-05-15
description: "TEXTエリアから「URL | 説明文」形式の一覧を取得し、zenn.dev/qiita.com/note.com/amazon.co.jp/その他の5種に分類、重複チェック付きでブックマーク登録する Chrome拡張の最新仕様(V5)と実装"
tags:
  - reference
  - chrome-extension
  - bookmark
---

最新仕様(V5)。V1〜V4の開発履歴（初版、アイコン生成、URL|Title形式追加、Amazon www対応など）は [[Chrome機能拡張開発-ブックマーク分類 Archive]] を参照。

仕様を追加があります。

以下の仕様のGoogle Chrome機能拡張を実装してください。

# TEXTエリアからURLの一覧を取得。ここで得られるURLは、"<URL> | 説明文"という形式の文字列として与えられるものとし、<URL>の部分がブックマークのURL、説明文がブックマークのタイトルとする

## ホスト部が"zenn.dev"のURLが重複しなければ、ルートフォルダ直下の"zenn.dev"という名前のフォルダに登録

## ホスト部が"qiita.com"のURLが重複しなければ、はルートフォルダ直下の"qiita.com"という名前のフォルダに登録

## ホスト部が"note.com"のURLが重複しなければ、ルートフォルダ直下の"note.com"という名前のフォルダに登録

## ホスト部が"amazon.co.jp"か"www.amazon.co.jp"のURLが重複しなければ、ルートフォルダ直下の"amazon.co.jp"という名前のフォルダに登録

## ホスト部が上記以外ののURLは重複しなければ、ルートフォルダ直下の"etc"という名前のフォルダに登録

## 上記のフォルダが存在しない場合は、作成してから、URLを登録する

承知いたしました。仕様を追加し、各ターゲットフォルダ内でURLが重複しない場合にのみブックマークを追加するように修正します。また、`zenn.dev` と `qiita.com` の分類も追加します。

**最終仕様 V5:**

1. **入力:** TEXTエリアに `<URL> | <説明文>` 形式で1行ずつ入力。
    
2. **解析:** 各行から `<URL>` 部分をブックマークURL、`<説明文>` 部分をブックマークタイトルとして取得。
    
3. **分類 & 重複チェック:**
    
    - URLのホスト名が `zenn.dev` → `zenn.dev` フォルダ内に**同じURLがなければ**登録。
        
    - URLのホスト名が `qiita.com` → `qiita.com` フォルダ内に**同じURLがなければ**登録。
        
    - URLのホスト名が `note.com` → `note.com` フォルダ内に**同じURLがなければ**登録。
        
    - URLのホスト名が `amazon.co.jp` または `www.amazon.co.jp` → `amazon.co.jp` フォルダ内に**同じURLがなければ**登録。
        
    - 上記以外のURL → `etc` フォルダ内に**同じURLがなければ**登録。
        
4. **フォルダ:** 対象フォルダがなければ作成する。
    
5. **ブックマーク:** 解析したURLとタイトルで登録する（重複しない場合のみ）。
    

---

**1. `manifest.json`** (バージョン番号、説明を更新)

JSON

```
{
  "manifest_version": 3,
  "name": "URL Sorter Bookmarker V5", // Name reflecting final spec
  "version": "1.3", // Version updated
  "description": "Sorts 'URL | Title' inputs into specific bookmark folders (zenn, qiita, note, amazon, etc.) avoiding duplicates within each folder.", // Description updated
  "permissions": [
    "bookmarks" // Required permission
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "images/icon16.png",
      "48": "images/icon48.png",
      "128": "images/icon128.png"
    }
  },
  "background": {
    "service_worker": "background.js"
  },
  "icons": {
    "16": "images/icon16.png",
    "48": "images/icon48.png",
    "128": "images/icon128.png"
  }
}
```

- `images` フォルダとアイコンファイルは存在すると仮定します。
    

---

**2. `popup.html`** (変更なし - V4と同じ)

入力形式の説明は変わらないため、前回のバージョンと同じです。

HTML

```
<!DOCTYPE html>
<html>
<head>
  <title>URL Sorter</title>
  <style>
    body {
      font-family: sans-serif;
      width: 300px;
      padding: 10px;
    }
    textarea {
      width: 95%;
      height: 150px;
      margin-bottom: 10px;
    }
    button {
      width: 100%;
      padding: 8px;
      cursor: pointer;
    }
    #status {
      margin-top: 10px;
      font-size: 0.9em;
      min-height: 1.2em; /* Ensure space for messages */
    }
    small {
        font-size: 0.8em;
        color: #555;
    }
  </style>
</head>
<body>
  <h3>Enter Data (one per line):</h3>
  <small>Format: URL | Title</small>
  <textarea id="urlList"></textarea>
  <button id="processButton">Sort and Bookmark URLs</button>
  <div id="status"></div>

  <script src="popup.js"></script>
</body>
</html>
```

---

**3. `popup.js`** (変更なし - V4と同じ)

テキストエリアの内容をバックグラウンドに送信する役割は変わりません。

JavaScript

```
document.addEventListener('DOMContentLoaded', function() {
  const urlListTextArea = document.getElementById('urlList');
  const processButton = document.getElementById('processButton');
  const statusDiv = document.getElementById('status');

  processButton.addEventListener('click', function() {
    const urlsRaw = urlListTextArea.value;
    const lines = urlsRaw.split('\n') // Split by newline (get lines)
                      .map(line => line.trim()) // Trim whitespace
                      .filter(line => line); // Remove empty lines

    if (lines.length === 0) {
      statusDiv.textContent = 'Please enter at least one line.';
      return;
    }

    statusDiv.textContent = 'Processing...';
    processButton.disabled = true;

    // Send the raw lines to the background script
    chrome.runtime.sendMessage(
      { action: "processUrls", urls: lines },
      (response) => {
        if (chrome.runtime.lastError) {
          statusDiv.textContent = `Error: ${chrome.runtime.lastError.message}`;
          console.error(chrome.runtime.lastError);
        } else if (response) {
          statusDiv.textContent = response.message;
        } else {
          statusDiv.textContent = 'Processing initiated. No confirmation received.';
        }
        processButton.disabled = false;
      }
    );
  });
});
```

---

**4. `background.js`** (zenn/qiitaフォルダ追加、重複チェック機能を追加)

JavaScript

```
// --- Configuration ---
const TARGET_PARENT_FOLDER_ID = '1'; // '1' = Bookmarks Bar, '2' = Other Bookmarks
const FOLDER_NAMES = {
  // Added zenn.dev and qiita.com
  ZENN: "zenn.dev",
  QIITA: "qiita.com",
  NOTE: "note.com",
  AMAZON: "amazon.co.jp", // Folder name for amazon URLs
  ETC: "etc"
};

// --- Helper Function: Find or Create Folder ---
// (No changes needed in this function)
async function findOrCreateFolder(parentId, folderName) {
  return new Promise((resolve, reject) => {
    chrome.bookmarks.getChildren(parentId, (children) => {
      if (chrome.runtime.lastError) {
        return reject(new Error(`Error getting children of folder ${parentId}: ${chrome.runtime.lastError.message}`));
      }
      const existingFolder = children.find(child => child.title === folderName && !child.url);
      if (existingFolder) {
        console.log(`Folder "${folderName}" found with ID: ${existingFolder.id}`);
        resolve(existingFolder.id);
      } else {
        console.log(`Folder "${folderName}" not found. Creating...`);
        chrome.bookmarks.create({ parentId: parentId, title: folderName }, (newFolder) => {
          if (chrome.runtime.lastError) {
            return reject(new Error(`Error creating folder "${folderName}": ${chrome.runtime.lastError.message}`));
          }
          if (!newFolder || !newFolder.id) {
             return reject(new Error(`Failed to create folder "${folderName}" - invalid response.`));
          }
          console.log(`Folder "${folderName}" created with ID: ${newFolder.id}`);
          resolve(newFolder.id);
        });
      }
    });
  });
}

// --- Helper Function: Check for Duplicate URL in Folder ---
async function checkForDuplicate(folderId, urlToCheck) {
  return new Promise((resolve, reject) => {
    chrome.bookmarks.getChildren(folderId, (children) => {
      if (chrome.runtime.lastError) {
        // Log error but potentially resolve false to allow bookmarking attempt if search fails? Or reject?
        // Rejecting seems safer to signal the check failed.
        console.error(`Error getting children for duplicate check in folder ${folderId}: ${chrome.runtime.lastError.message}`);
        return reject(new Error(chrome.runtime.lastError.message));
      }
      const isDuplicate = children.some(child => child.url === urlToCheck);
      resolve(isDuplicate);
    });
  });
}


// --- Main Processing Logic (MODIFIED - Added zenn/qiita, duplicate check) ---
async function processUrls(lines) {
  let processedCount = 0;
  let errorCount = 0;
  let skippedFormatCount = 0; // Count lines skipped due to format issues
  let skippedDuplicateCount = 0; // Count lines skipped due to duplication
  let folderIds = {};

  try {
    console.log("Starting URL processing (V5 - URL | Title format, duplicate check)...");

    // Ensure all target folders exist and get their IDs concurrently
    // Added ZENN and QIITA folders
    const [zennFolderId, qiitaFolderId, noteFolderId, amazonFolderId, etcFolderId] = await Promise.all([
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.ZENN),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.QIITA),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.NOTE),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.AMAZON),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.ETC)
    ]);
    folderIds[FOLDER_NAMES.ZENN] = zennFolderId;
    folderIds[FOLDER_NAMES.QIITA] = qiitaFolderId;
    folderIds[FOLDER_NAMES.NOTE] = noteFolderId;
    folderIds[FOLDER_NAMES.AMAZON] = amazonFolderId;
    folderIds[FOLDER_NAMES.ETC] = etcFolderId;

    console.log("Folder IDs obtained:", folderIds);

    // Process each line from the input
    for (const line of lines) {
      // Step 1: Parse line for URL and Title
      const parts = line.split('|');
      if (parts.length < 2) {
        console.warn(`Skipping line due to missing '|' separator: "${line}"`);
        skippedFormatCount++;
        continue;
      }
      const urlString = parts[0].trim();
      const titleString = parts.slice(1).join('|').trim();
      if (!urlString || !titleString) {
         console.warn(`Skipping line due to empty URL or title after parsing: "${line}"`);
         skippedFormatCount++;
         continue;
      }

      try {
        // Step 2: Validate URL and Determine Target Folder
        const url = new URL(urlString);
        const hostname = url.hostname.toLowerCase();
        let targetFolderId;
        let targetFolderName = FOLDER_NAMES.ETC; // Default

        // Updated categorization logic
        if (hostname === FOLDER_NAMES.ZENN) {
            targetFolderId = folderIds[FOLDER_NAMES.ZENN];
            targetFolderName = FOLDER_NAMES.ZENN;
        } else if (hostname === FOLDER_NAMES.QIITA) {
            targetFolderId = folderIds[FOLDER_NAMES.QIITA];
            targetFolderName = FOLDER_NAMES.QIITA;
        } else if (hostname === FOLDER_NAMES.NOTE) {
            targetFolderId = folderIds[FOLDER_NAMES.NOTE];
            targetFolderName = FOLDER_NAMES.NOTE;
        } else if (hostname === 'amazon.co.jp' || hostname === 'www.amazon.co.jp') {
            targetFolderId = folderIds[FOLDER_NAMES.AMAZON];
            targetFolderName = FOLDER_NAMES.AMAZON;
        } else {
            targetFolderId = folderIds[FOLDER_NAMES.ETC];
            // targetFolderName remains ETC
        }

        // --- Step 3: Check for Duplicates in Target Folder ---
        let isDuplicate = false;
        try {
          isDuplicate = await checkForDuplicate(targetFolderId, urlString);
        } catch (duplicateCheckError) {
           // Log the error, count it, and skip this URL as we couldn't verify non-duplication
           console.error(`Could not check for duplicates for "${urlString}" in folder ${targetFolderName}: ${duplicateCheckError.message}`);
           errorCount++;
           continue; // Skip to next line
        }

        if (isDuplicate) {
          console.log(`Skipping duplicate URL in folder ${targetFolderName}: "${urlString}"`);
          skippedDuplicateCount++;
          continue; // Skip to the next line in the input
        }
        // --- End Step 3 ---

        // --- Step 4: Create the Bookmark (if not duplicate) ---
        await new Promise((resolve, reject) => {
           chrome.bookmarks.create({
             parentId: targetFolderId,
             title: titleString,
             url: urlString
           }, (newBookmark) => {
             if (chrome.runtime.lastError) {
               console.error(`Error bookmarking "${urlString}" (Title: "${titleString}"): ${chrome.runtime.lastError.message}`);
               reject(new Error(chrome.runtime.lastError.message));
             } else if (!newBookmark) {
                console.error(`Failed to create bookmark for "${urlString}" - invalid response.`);
                reject(new Error('Failed to create bookmark - invalid response.'));
             } else {
               console.log(`Bookmarked "${urlString}" (Title: "${titleString}") in folder ${targetFolderName} (ID ${targetFolderId})`);
               resolve();
             }
           });
        });
        processedCount++;
        // --- End Step 4 ---

      } catch (urlOrBookmarkError) {
        // Handle errors from new URL(), checkForDuplicate rejection, or bookmark creation rejection
        console.error(`Skipping line due to error for "${line}": ${urlOrBookmarkError.message}`);
        errorCount++;
      }
    } // End of loop through lines

    // Final status message including skipped format and duplicate counts
    const message = `Processed: ${processedCount}, Skipped(Format): ${skippedFormatCount}, Skipped(Duplicate): ${skippedDuplicateCount}, Errors: ${errorCount}`;
    console.log(`Processing complete. ${message}`);
    return { success: true, message: message };

  } catch (folderSetupError) {
    // Handle critical errors during folder setup (Promise.all rejection)
    console.error("Critical error during folder setup:", folderSetupError);
    return { success: false, message: `Error setting up folders: ${folderSetupError.message || folderSetupError}` };
  }
}


// --- Event Listener for Messages from Popup ---
// (No changes needed here)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "processUrls" && message.urls) {
    console.log("Received processUrls request with", message.urls.length, "lines (V5)");
    processUrls(message.urls).then(result => {
       sendResponse(result);
    }).catch(error => {
        console.error("Unhandled error in processUrls promise chain:", error);
        sendResponse({ success: false, message: `Unexpected background error: ${error.message}` });
    });
    return true; // Indicate async response
  }
  return false;
});

// Optional: Log when the service worker starts
console.log("Background service worker started (v5 - Added zenn/qiita, duplicate check).");
```

---

**手順:**

1. 上記4つのコード (`manifest.json`, `popup.html`, `popup.js`, `background.js`) を、拡張機能用のフォルダにそれぞれ正しいファイル名で保存（または上書き）してください。
    
2. Chrome拡張機能管理画面 (`chrome://extensions`) を開きます。
    
3. デベロッパーモードがオンになっていることを確認します。
    
4. 該当の拡張機能を更新するか、一度削除して再読み込みします。
    

これで、指定されたすべての分類（`zenn.dev`, `qiita.com` を含む）と、各フォルダ内でのURL重複チェック機能が実装された拡張機能として動作します。重複するURLはスキップされ、ステータスメッセージでその数が報告されます。