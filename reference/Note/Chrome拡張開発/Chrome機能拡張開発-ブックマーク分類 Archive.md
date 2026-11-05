---
date: 2026-05-15
description: "Chrome拡張『ブックマーク分類』の開発履歴 V1〜V4（初版実装、アイコン生成、URL|Title形式追加、Amazon www対応、最終的にV5へ統合される前の変遷）"
tags:
  - reference
  - chrome-extension
  - bookmark
---

V1〜V4の開発履歴（アーカイブ）。最新仕様(V5)は [[Chrome機能拡張開発-ブックマーク分類]] を参照。

以下の仕様のGoogle Chrome機能拡張を実装してください。

# TEXTエリアからURLの一覧を取得

# URLのホスト部が"note.com"、"amazon.co.jp"、その他の3種類に分割し、それぞれに指定したフォルダに登録

## ホスト部が"note.com"のURLはルートフォルダ直下の"note.com"という名前のフォルダに登録

## ホスト部が"amazon.co.jp"のURLはルートフォルダ直下の"amazon.co.jp"という名前のフォルダに登録

## ホスト部が上記以外ののURLはルートフォルダ直下の"etc"という名前のフォルダに登録

## 上記のフォルダが存在しない場合は、作成してから、URLを登録する

承知いたしました。指定された仕様に基づいてGoogle Chrome拡張機能を作成します。

この拡張機能は以下のファイルで構成されます。

1. **`manifest.json`**: 拡張機能の基本的な情報と権限を定義します。
    
2. **`popup.html`**: 拡張機能アイコンをクリックしたときに表示されるポップアップウィンドウのHTMLです。URLを入力するテキストエリアと実行ボタンが含まれます。
    
3. **`popup.js`**: ポップアップ内の動作（テキストエリアからのURL取得、バックグラウンドへの処理依頼）を制御するJavaScriptです。
    
4. **`background.js`**: ブックマークの検索、フォルダ作成、URL登録といった実際の処理を行うバックグラウンドスクリプトです。
    

---

**1. `manifest.json`**

JSON

```
{
  "manifest_version": 3,
  "name": "URL Sorter Bookmarker",
  "version": "1.0",
  "description": "Sorts URLs from a textarea into specific bookmark folders (note.com, amazon.co.jp, etc).",
  "permissions": [
    "bookmarks"
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

- **注意:** 上記の`icons`パス (`images/icon16.png`など) は仮のものです。実際に拡張機能を作成する際には、`images`というフォルダを作成し、そこに16x16, 48x48, 128x128ピクセルのアイコン画像を配置してください。
    

---

**2. `popup.html`**

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
  </style>
</head>
<body>
  <h3>Enter URLs (one per line):</h3>
  <textarea id="urlList"></textarea>
  <button id="processButton">Sort and Bookmark URLs</button>
  <div id="status"></div>

  <script src="popup.js"></script>
</body>
</html>
```

---

**3. `popup.js`**

JavaScript

```
document.addEventListener('DOMContentLoaded', function() {
  const urlListTextArea = document.getElementById('urlList');
  const processButton = document.getElementById('processButton');
  const statusDiv = document.getElementById('status');

  processButton.addEventListener('click', function() {
    const urlsRaw = urlListTextArea.value;
    const urls = urlsRaw.split('\n') // Split by newline
                      .map(line => line.trim()) // Trim whitespace
                      .filter(line => line); // Remove empty lines

    if (urls.length === 0) {
      statusDiv.textContent = 'Please enter at least one URL.';
      return;
    }

    statusDiv.textContent = 'Processing...';
    processButton.disabled = true; // Prevent double-clicking

    // Send URLs to the background script for processing
    chrome.runtime.sendMessage(
      { action: "processUrls", urls: urls },
      (response) => {
        if (chrome.runtime.lastError) {
          // Handle errors like background script not ready
          statusDiv.textContent = `Error: ${chrome.runtime.lastError.message}`;
          console.error(chrome.runtime.lastError);
        } else if (response) {
          statusDiv.textContent = response.message; // Display message from background
        } else {
          // Handle case where background script didn't send a response (unexpected)
          statusDiv.textContent = 'Processing initiated. No confirmation received.';
        }
        processButton.disabled = false; // Re-enable button
        // Optional: Clear textarea after processing
        // urlListTextArea.value = '';
      }
    );
  });
});
```

---

**4. `background.js`**

JavaScript

```
// --- Configuration ---
const TARGET_PARENT_FOLDER_ID = '1'; // '1' is usually the Bookmarks Bar, '2' is Other Bookmarks. Adjust if needed.
const FOLDER_NAMES = {
  NOTE: "note.com",
  AMAZON: "amazon.co.jp",
  ETC: "etc"
};

// --- Helper Function: Find or Create Folder ---
async function findOrCreateFolder(parentId, folderName) {
  return new Promise((resolve, reject) => {
    // Search for the folder first
    chrome.bookmarks.getChildren(parentId, (children) => {
      if (chrome.runtime.lastError) {
        return reject(`Error getting children of folder ${parentId}: ${chrome.runtime.lastError.message}`);
      }

      const existingFolder = children.find(child => child.title === folderName && !child.url); // Ensure it's a folder

      if (existingFolder) {
        console.log(`Folder "${folderName}" found with ID: ${existingFolder.id}`);
        resolve(existingFolder.id);
      } else {
        // Folder not found, create it
        console.log(`Folder "${folderName}" not found. Creating...`);
        chrome.bookmarks.create({ parentId: parentId, title: folderName }, (newFolder) => {
          if (chrome.runtime.lastError) {
            return reject(`Error creating folder "${folderName}": ${chrome.runtime.lastError.message}`);
          }
          if (!newFolder || !newFolder.id) {
             return reject(`Failed to create folder "${folderName}" - invalid response.`);
          }
          console.log(`Folder "${folderName}" created with ID: ${newFolder.id}`);
          resolve(newFolder.id);
        });
      }
    });
  });
}

// --- Main Processing Logic ---
async function processUrls(urls) {
  let processedCount = 0;
  let errorCount = 0;
  let folderIds = {};

  try {
    console.log("Starting URL processing...");

    // Ensure all target folders exist and get their IDs concurrently
    const [noteFolderId, amazonFolderId, etcFolderId] = await Promise.all([
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.NOTE),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.AMAZON),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.ETC)
    ]);
    folderIds[FOLDER_NAMES.NOTE] = noteFolderId;
    folderIds[FOLDER_NAMES.AMAZON] = amazonFolderId;
    folderIds[FOLDER_NAMES.ETC] = etcFolderId;

    console.log("Folder IDs obtained:", folderIds);

    // Process each URL sequentially to avoid overwhelming the API (optional: could parallelize)
    for (const urlString of urls) {
      try {
        const url = new URL(urlString); // Validate and parse URL
        const hostname = url.hostname.toLowerCase(); // Use lowercase for consistent matching

        let targetFolderId;
        if (hostname === FOLDER_NAMES.NOTE) {
          targetFolderId = folderIds[FOLDER_NAMES.NOTE];
        } else if (hostname === FOLDER_NAMES.AMAZON) {
          targetFolderId = folderIds[FOLDER_NAMES.AMAZON];
        } else {
          targetFolderId = folderIds[FOLDER_NAMES.ETC];
        }

        // Create the bookmark
        await new Promise((resolve, reject) => {
           chrome.bookmarks.create({
             parentId: targetFolderId,
             title: urlString, // Use the URL as the title for simplicity
             url: urlString
           }, (newBookmark) => {
             if (chrome.runtime.lastError) {
               console.error(`Error bookmarking "${urlString}": ${chrome.runtime.lastError.message}`);
               reject(chrome.runtime.lastError.message);
             } else if (!newBookmark) {
                console.error(`Failed to create bookmark for "${urlString}" - invalid response.`);
                reject('Failed to create bookmark - invalid response.');
             }
              else {
               console.log(`Bookmarked "${urlString}" in folder ID ${targetFolderId}`);
               resolve();
             }
           });
        });
        processedCount++;

      } catch (urlError) {
        // Handle invalid URLs or bookmark creation errors for a single URL
        console.error(`Skipping invalid or failed URL "${urlString}": ${urlError.message}`);
        errorCount++;
      }
    }

    console.log(`Processing complete. Processed: ${processedCount}, Errors: ${errorCount}`);
    return { success: true, message: `Processed: ${processedCount}, Skipped/Errors: ${errorCount}` };

  } catch (folderError) {
    // Handle errors during folder finding/creation (critical failure)
    console.error("Critical error during folder setup:", folderError);
    return { success: false, message: `Error setting up folders: ${folderError}` };
  }
}


// --- Event Listener for Messages from Popup ---
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "processUrls") {
    console.log("Received processUrls request with", message.urls.length, "URLs");
    // Use async function directly and send response when done
    processUrls(message.urls).then(result => {
       sendResponse(result);
    }).catch(error => {
        // Catch any unexpected errors from processUrls promise itself
        console.error("Unhandled error in processUrls:", error);
        sendResponse({ success: false, message: `Unexpected background error: ${error.message}` });
    });

    // Return true to indicate you wish to send a response asynchronously
    return true;
  }
  // Handle other potential actions here if needed
  return false; // Indicate no async response for other messages
});

// Optional: Log when the service worker starts
console.log("Background service worker started.");
```

---

**手順:**

1. **フォルダ作成:** コンピュータ上に新しいフォルダを作成します（例: `url-sorter-extension`）。
    
2. **ファイル保存:** 上記の4つのコードブロックを、それぞれのファイル名（`manifest.json`, `popup.html`, `popup.js`, `background.js`）で、作成したフォルダ内に保存します。
    
3. **アイコン作成（任意）:** `images`というサブフォルダを作成し、その中に`icon16.png`, `icon48.png`, `icon128.png`という名前でアイコン画像を用意します。もしアイコンが不要な場合は、`manifest.json`から`icons`と`action.default_icon`の行を削除しても動作します（デフォルトの拡張機能アイコンが表示されます）。
    
4. **Chromeに読み込む:**
    
    - Chromeを開き、アドレスバーに `chrome://extensions` と入力してEnterキーを押します。
        
    - 右上の「デベロッパー モード」をオンにします。
        
    - 左上に表示される「パッケージ化されていない拡張機能を読み込む」ボタンをクリックします。
        
    - ステップ1で作成したフォルダ（`url-sorter-extension`など）を選択します。
        
5. **使用:**
    
    - Chromeのツールバーに新しい拡張機能のアイコンが表示されます。
        
    - アイコンをクリックするとポップアップが開きます。
        
    - テキストエリアに、一行ずつURLを入力します。
        
    - 「Sort and Bookmark URLs」ボタンをクリックします。
        
    - 処理が実行され、ブックマークバー（または`TARGET_PARENT_FOLDER_ID`で指定した場所）の下に `note.com`, `amazon.co.jp`, `etc` フォルダが作成され（存在しない場合）、各URLが適切なフォルダにブックマークとして登録されます。
        
    - ポップアップの下部に処理結果（処理したURL数、エラー数など）が表示されます。
        

これで、指定された仕様のChrome拡張機能が実装されます。

背景色がpinkで、文字色がblackで"USBM"とう文字列を中央に配置した、16x16のPNG形式のアイコンファイルを作成してください

はい、承知いたしました。

背景色がピンク (`#FFC0CB`)、文字色が黒 (`#000000`) で、中央に "USBM" という文字列を配置した 16x16 ピクセルのPNGアイコンを作成します。

以下の内容を `icon16.png` というファイル名で保存してください。フォントのサイズや描画の都合上、特に16x16という小さいサイズでは、文字がやや読みにくくなる可能性がある点はご了承ください。

Python

```
# TOOL CODE START
# Create a 16x16 PNG icon with pink background, black text "USBM" centered.
from PIL import Image, ImageDraw, ImageFont
import io

# Define parameters
img_width = 16
img_height = 16
background_color_rgb = (255, 192, 203) # Pink
text_color_rgb = (0, 0, 0)           # Black
text = "USBM"
output_filename = "icon16.png" # Filename to save

# Create image
image = Image.new("RGB", (img_width, img_height), background_color_rgb)
draw = ImageDraw.Draw(image)

# --- Font Selection ---
# Using the default bitmap font is often best for tiny sizes for clarity,
# though it might not look 'smooth'. Trying TrueType can be blurry.
try:
    font = ImageFont.load_default()
    # For load_default(), anchor often doesn't work well. Calculate manually.
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    # Calculate top-left corner for centering
    x = (img_width - text_width) / 2
    # Adjust y slightly up because default font baseline is often low
    y = (img_height - text_height) / 2 - 1
    # Ensure coordinates are integers
    draw.text((int(x), int(y)), text, fill=text_color_rgb, font=font)
except Exception as e:
    print(f"Error loading default font: {e}. Drawing fallback text.")
    # Very basic fallback if font loading fails
    fallback_font_size = 8 # Arbitrary small size
    try:
       # Attempting a generic truetype if possible
       font = ImageFont.truetype("arial.ttf", fallback_font_size) # Example, might fail
    except IOError:
       font = ImageFont.load_default() # Fallback to default again

    # Recalculate and draw if font changed
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (img_width - text_width) / 2
    y = (img_height - text_height) / 2
    draw.text((int(x), int(y)), text, fill=text_color_rgb, font=font)


# Save the image
image.save(output_filename)

print(f"Created {output_filename}")
# TOOL CODE END
```

**上記のコードを実行すると、実行環境のカレントディレクトリに `icon16.png` というファイル名でアイコンが生成されます。**

このファイルを、先に作成したChrome拡張機能のフォルダ（例: `url-sorter-extension`）内の `images` フォルダ（もしなければ作成してください）に配置してください。

`manifest.json` の `icons` および `action.default_icon` のパス設定が正しければ、拡張機能を再読み込み（または更新）すると、このアイコンが表示されるようになります。

背景色がpinkで、文字色がblackで"USBM"とう文字列を中央に配置した、16x16、48x48、128x128のPNG形式のアイコンファイルを3種類分作成してください

はい、承知いたしました。

背景色がピンク (`#FFC0CB`)、文字色が黒 (`#000000`) で、中央に "USBM" という文字列を配置した 16x16, 48x48, 128x128 ピクセルのPNGアイコンファイルを3種類作成します。

- **16x16:** 小さいサイズのため、シンプルなピクセルフォントで描画します。
    
- **48x48, 128x128:** 一般的なサンセリフフォント（Arialなど、利用可能な場合）を使用して描画します。フォントサイズはアイコンサイズに合わせて調整します。
    

以下のPythonコードを実行すると、`images`というフォルダを作成し、その中に3つのアイコンファイル (`icon16.png`, `icon48.png`, `icon128.png`) を生成します。

Python

```
# TOOL CODE START
# Create 16x16, 48x48, 128x128 PNG icons with pink background, black text "USBM" centered.
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Creates a square PNG icon with specified properties."""
    img_width = size
    img_height = size
    background_color_rgb = (255, 192, 203) # Pink
    text_color_rgb = (0, 0, 0)           # Black
    text = "USBM"
    output_dir = "images" # Output directory name

    # Create image
    image = Image.new("RGB", (img_width, img_height), background_color_rgb)
    draw = ImageDraw.Draw(image)

    font = None
    try:
        if size <= 16:
            # --- For 16x16: Use default bitmap font ---
            font = ImageFont.load_default()
            # Calculate bounding box for manual centering
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Calculate top-left corner for centering, adjust baseline slightly up
            x = (img_width - text_width) / 2
            y = (img_height - text_height) / 2 - 1
            draw.text((int(x), int(y)), text, fill=text_color_rgb, font=font)
            print(f"Using default font for {filename} (size {size}).")

        else:
            # --- For larger sizes: Try TrueType fonts ---
            # Estimate font size (adjust multiplier as needed, 0.5 works reasonably)
            font_size = int(size * 0.5)
            font_found = False
            # List of common sans-serif fonts to try
            common_fonts = ["arial.ttf", "dejavusans.ttf", "verdana.ttf", "tahoma.ttf"]

            for font_name in common_fonts:
                 try:
                     font = ImageFont.truetype(font_name, font_size)
                     font_found = True
                     print(f"Using font '{font_name}' for {filename} (size {size}).")
                     break # Stop searching once a font is found
                 except IOError:
                     # Font not found, try the next one
                     continue

            if font_found:
                # Use anchor='mm' for automatic centering with TrueType
                draw.text((img_width / 2, img_height / 2),
                          text,
                          fill=text_color_rgb,
                          font=font,
                          anchor="mm") # Middle-middle anchor
            else:
                 # --- Fallback if no TrueType fonts found ---
                 print(f"Warning: Could not find common TrueType fonts for {filename} (size {size}). Falling back to default font.")
                 font = ImageFont.load_default()
                 # Manual centering required for default font fallback
                 bbox = draw.textbbox((0, 0), text, font=font)
                 text_width = bbox[2] - bbox[0]
                 text_height = bbox[3] - bbox[1]
                 x = (img_width - text_width) / 2
                 # No baseline adjustment needed for scaled default? Test.
                 y = (img_height - text_height) / 2
                 # Note: Default font scaled up might look very blocky
                 # We might need ImageDraw.Image.resize for a better effect if scaling default.
                 # For simplicity, just draw it directly for now.
                 draw.text((int(x), int(y)), text, fill=text_color_rgb, font=font)

    except Exception as e:
        print(f"Error processing font or drawing for {filename}: {e}")
        # Draw very basic text as final fallback if anything else fails
        print(f"Drawing fallback text for {filename}")
        draw.text((img_width * 0.1, img_height * 0.1), text, fill=text_color_rgb) # Draw offset from corner

    # Ensure the output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        # Save the image
        image.save(filepath)
        print(f"Successfully created {filepath}")
    except Exception as e:
        print(f"Error saving file {filename}: {e}")


# --- Create the icons ---
create_icon(16, "icon16.png")
create_icon(48, "icon48.png")
create_icon(128, "icon128.png")

print("\nIcon creation process finished.")
# TOOL CODE END
```

**実行後:**

1. コードを実行した場所に `images` というフォルダが作成されます。
    
2. `images` フォルダの中に以下の3つのファイルが生成されます。
    
    - `icon16.png` (16x16ピクセル)
        
    - `icon48.png` (48x48ピクセル)
        
    - `icon128.png` (128x128ピクセル)
        

これらのファイルをChrome拡張機能のプロジェクトフォルダ内の `images` フォルダに配置（または上書き）してください。拡張機能をChromeで再読み込みすると、新しいアイコンが適用されます。

**注意:** 48x48および128x128アイコンに使用されるフォントは、実行環境にインストールされている一般的なフォント（Arial, DejaVu Sans, Verdana, Tahoma）に依存します。これらのフォントが見つからない場合は、警告が表示され、16x16と同様のシンプルなフォント（ただし拡大表示されるため粗く見えます）で代替されます。

URLが"<URL> | 説明文"という形式の文字列として与えられるものとし、<URL>の部分がブックマークのURL、説明文がブックマークのタイトルとして作り直して

承知いたしました。入力形式を `<URL> | <説明文>` とし、`<URL>` をブックマークのURL、`<説明文>` をブックマークのタイトルとして登録するように `background.js` を修正します。

`popup.html` の説明文も少し変更して、ユーザーに新しい形式を伝えます。

---

**1. `popup.html` (修正)**

`<h3>` タグ内のテキストを変更します。

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

**2. `background.js` (修正)**

`processUrls` 関数内のループ処理を変更し、各行を `|` で分割してURLとタイトルを取得するようにします。

JavaScript

```
// --- Configuration ---
const TARGET_PARENT_FOLDER_ID = '1'; // '1' is usually the Bookmarks Bar, '2' is Other Bookmarks. Adjust if needed.
const FOLDER_NAMES = {
  NOTE: "note.com",
  AMAZON: "amazon.co.jp",
  ETC: "etc"
};

// --- Helper Function: Find or Create Folder ---
// (No changes needed in this function)
async function findOrCreateFolder(parentId, folderName) {
  return new Promise((resolve, reject) => {
    chrome.bookmarks.getChildren(parentId, (children) => {
      if (chrome.runtime.lastError) {
        return reject(`Error getting children of folder ${parentId}: ${chrome.runtime.lastError.message}`);
      }
      const existingFolder = children.find(child => child.title === folderName && !child.url);
      if (existingFolder) {
        console.log(`Folder "${folderName}" found with ID: ${existingFolder.id}`);
        resolve(existingFolder.id);
      } else {
        console.log(`Folder "${folderName}" not found. Creating...`);
        chrome.bookmarks.create({ parentId: parentId, title: folderName }, (newFolder) => {
          if (chrome.runtime.lastError) {
            return reject(`Error creating folder "${folderName}": ${chrome.runtime.lastError.message}`);
          }
          if (!newFolder || !newFolder.id) {
             return reject(`Failed to create folder "${folderName}" - invalid response.`);
          }
          console.log(`Folder "${folderName}" created with ID: ${newFolder.id}`);
          resolve(newFolder.id);
        });
      }
    });
  });
}

// --- Main Processing Logic (MODIFIED) ---
async function processUrls(lines) { // Renamed input from urls to lines
  let processedCount = 0;
  let errorCount = 0;
  let skippedCount = 0; // Count lines skipped due to format issues
  let folderIds = {};

  try {
    console.log("Starting URL processing...");

    // Ensure all target folders exist and get their IDs concurrently
    const [noteFolderId, amazonFolderId, etcFolderId] = await Promise.all([
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.NOTE),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.AMAZON),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.ETC)
    ]);
    folderIds[FOLDER_NAMES.NOTE] = noteFolderId;
    folderIds[FOLDER_NAMES.AMAZON] = amazonFolderId;
    folderIds[FOLDER_NAMES.ETC] = etcFolderId;

    console.log("Folder IDs obtained:", folderIds);

    // Process each line from the input
    for (const line of lines) {
      // --- MODIFICATION START: Parse the line ---
      const parts = line.split('|'); // Split by pipe character

      if (parts.length < 2) {
        console.warn(`Skipping line due to missing '|' separator: "${line}"`);
        skippedCount++;
        continue; // Skip to the next line
      }

      const urlString = parts[0].trim(); // First part is URL
      // Join the rest in case the title itself contains '|'
      const titleString = parts.slice(1).join('|').trim();

      if (!urlString || !titleString) {
         console.warn(`Skipping line due to empty URL or title after parsing: "${line}"`);
         skippedCount++;
         continue; // Skip to the next line
      }
      // --- MODIFICATION END: Parse the line ---

      try {
        // Validate the URL part
        const url = new URL(urlString);
        const hostname = url.hostname.toLowerCase(); // Use lowercase for consistent matching

        let targetFolderId;
        if (hostname === FOLDER_NAMES.NOTE) {
          targetFolderId = folderIds[FOLDER_NAMES.NOTE];
        } else if (hostname === FOLDER_NAMES.AMAZON) {
          targetFolderId = folderIds[FOLDER_NAMES.AMAZON];
        } else {
          targetFolderId = folderIds[FOLDER_NAMES.ETC];
        }

        // Create the bookmark using parsed URL and Title
        await new Promise((resolve, reject) => {
           chrome.bookmarks.create({
             parentId: targetFolderId,
             // --- MODIFIED: Use parsed title and url ---
             title: titleString,
             url: urlString
             // --- END MODIFIED ---
           }, (newBookmark) => {
             if (chrome.runtime.lastError) {
               console.error(`Error bookmarking "${urlString}" (Title: "${titleString}"): ${chrome.runtime.lastError.message}`);
               reject(chrome.runtime.lastError.message);
             } else if (!newBookmark) {
                console.error(`Failed to create bookmark for "${urlString}" - invalid response.`);
                reject('Failed to create bookmark - invalid response.');
             } else {
               console.log(`Bookmarked "${urlString}" (Title: "${titleString}") in folder ID ${targetFolderId}`);
               resolve();
             }
           });
        });
        processedCount++;

      } catch (urlError) {
        // Handle invalid URLs from new URL() or bookmark creation errors for a single line
        console.error(`Skipping line due to error for "${line}": ${urlError.message}`);
        errorCount++;
      }
    } // End of loop through lines

    const message = `Processed: ${processedCount}, Skipped (Format): ${skippedCount}, Errors (URL/Bookmark): ${errorCount}`;
    console.log(`Processing complete. ${message}`);
    return { success: true, message: message };

  } catch (folderError) {
    // Handle errors during folder finding/creation (critical failure)
    console.error("Critical error during folder setup:", folderError);
    return { success: false, message: `Error setting up folders: ${folderError}` };
  }
}


// --- Event Listener for Messages from Popup ---
// (No changes needed in this listener)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "processUrls") {
    console.log("Received processUrls request with", message.urls.length, "lines"); // urls actually contains lines now
    processUrls(message.urls).then(result => { // Pass the lines to processUrls
       sendResponse(result);
    }).catch(error => {
        console.error("Unhandled error in processUrls:", error);
        sendResponse({ success: false, message: `Unexpected background error: ${error.message}` });
    });
    return true; // Indicate async response
  }
  return false;
});

// Optional: Log when the service worker starts
console.log("Background service worker started (v2 - with Title parsing).");

```

---

**変更点:**

1. **`popup.html`:**
    
    - `<h3>` タグの説明を「Enter Data (one per line):」に変更。
        
    - 入力形式を示す `<small>` タグを追加 (`Format: URL | Title`)。
        
2. **`background.js` (`processUrls` 関数内):**
    
    - 入力パラメータ名を `urls` から `lines` に変更（より意味的に正確なため）。
        
    - ループ内で各 `line` を `|` で分割。
        
    - 分割結果が2未満（`|` がない）の場合、警告を出力してその行をスキップ (`skippedCount` を増加)。
        
    - 分割した最初の部分を `urlString`、残りを結合して `titleString` として取得し、それぞれ `trim()` する。
        
    - `urlString` または `titleString` が空の場合も警告を出してスキップ (`skippedCount` を増加)。
        
    - `chrome.bookmarks.create` を呼び出す際に、`title` プロパティに `titleString` を、`url` プロパティに `urlString` を渡すように変更。
        
    - エラーハンドリングとログ出力を調整し、どの行で問題が発生したかわかりやすくした。
        
    - 処理結果のメッセージに `Skipped (Format)` カウントを追加。
        

**再読み込み:**

これらのファイルを保存した後、Chrome拡張機能管理画面 (`chrome://extensions`) で拡張機能を再読み込みしてください。これで、新しい入力形式に対応したバージョンが利用可能になります。

以下の仕様のGoogle Chrome機能拡張を実装してください。

# TEXTエリアからURLの一覧を取得

# URLのホスト部が"note.com"、"amazon.co.jp"か"www.amazon.co.jp"、その他の3種類に分割し、それぞれに指定したフォルダに登録

## ホスト部が"note.com"のURLはルートフォルダ直下の"note.com"という名前のフォルダに登録

## ホスト部が"amazon.co.jp"か"www.amazon.co.jp"のURLはルートフォルダ直下の"amazon.co.jp"という名前のフォルダに登録

## ホスト部が上記以外ののURLはルートフォルダ直下の"etc"という名前のフォルダに登録

## 上記のフォルダが存在しない場合は、作成してから、URLを登録する

承知いたしました。以前の状態（URL | タイトル形式ではなく、URLのみを入力し、URL自体をタイトルとしてブックマークする）に戻し、Amazonの条件のみを変更したChrome拡張機能を実装します。

**仕様の再確認:**

1. **入力:** TEXTエリアにURLを1行ずつ入力。
    
2. **処理:**
    
    - ホスト名が `note.com` のURL → `note.com` フォルダへ。
        
    - ホスト名が `amazon.co.jp` または `www.amazon.co.jp` のURL → `amazon.co.jp` フォルダへ。
        
    - 上記以外のURL → `etc` フォルダへ。
        
3. **フォルダ:** 対象フォルダがなければ作成する。
    
4. **ブックマーク:** URLをURLとして、**URL自身をタイトルとして**登録する。
    

---

**1. `manifest.json`** (変更なし)

JSON

```
{
  "manifest_version": 3,
  "name": "URL Sorter Bookmarker V3", // Version name slightly updated for clarity
  "version": "1.1", // Version updated
  "description": "Sorts URLs from a textarea into specific bookmark folders (note.com, amazon.co.jp/www.amazon.co.jp, etc).",
  "permissions": [
    "bookmarks"
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

- `name` と `version` を少し変更しましたが、機能的な必須変更ではありません。
    
- `images` フォルダとアイコンファイル (`icon16.png`, `icon48.png`, `icon128.png`) は前回作成したものが存在すると仮定します。
    

---

**2. `popup.html`** (タイトル形式の記述を削除し、元のシンプルな形に戻す)

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
  </style>
</head>
<body>
  <h3>Enter URLs (one per line):</h3>
  <textarea id="urlList"></textarea>
  <button id="processButton">Sort and Bookmark URLs</button>
  <div id="status"></div>

  <script src="popup.js"></script>
</body>
</html>
```

---

**3. `popup.js`** (変更なし)

このファイルはテキストエリアの内容をバックグラウンドに送るだけなので、変更は不要です。

JavaScript

```
document.addEventListener('DOMContentLoaded', function() {
  const urlListTextArea = document.getElementById('urlList');
  const processButton = document.getElementById('processButton');
  const statusDiv = document.getElementById('status');

  processButton.addEventListener('click', function() {
    const urlsRaw = urlListTextArea.value;
    const urls = urlsRaw.split('\n') // Split by newline
                      .map(line => line.trim()) // Trim whitespace
                      .filter(line => line); // Remove empty lines

    if (urls.length === 0) {
      statusDiv.textContent = 'Please enter at least one URL.';
      return;
    }

    statusDiv.textContent = 'Processing...';
    processButton.disabled = true; // Prevent double-clicking

    // Send URLs to the background script for processing
    chrome.runtime.sendMessage(
      { action: "processUrls", urls: urls }, // Pass the list of url strings
      (response) => {
        if (chrome.runtime.lastError) {
          statusDiv.textContent = `Error: ${chrome.runtime.lastError.message}`;
          console.error(chrome.runtime.lastError);
        } else if (response) {
          statusDiv.textContent = response.message;
        } else {
          statusDiv.textContent = 'Processing initiated. No confirmation received.';
        }
        processButton.disabled = false; // Re-enable button
      }
    );
  });
});
```

---

**4. `background.js`** (URL|タイトル形式の解析を削除、Amazonのホスト名チェックを修正)

JavaScript

```
// --- Configuration ---
const TARGET_PARENT_FOLDER_ID = '1'; // '1' = Bookmarks Bar, '2' = Other Bookmarks
const FOLDER_NAMES = {
  NOTE: "note.com",
  AMAZON: "amazon.co.jp", // Folder name remains amazon.co.jp
  ETC: "etc"
};

// --- Helper Function: Find or Create Folder ---
// (No changes needed in this function)
async function findOrCreateFolder(parentId, folderName) {
  return new Promise((resolve, reject) => {
    chrome.bookmarks.getChildren(parentId, (children) => {
      if (chrome.runtime.lastError) {
        return reject(`Error getting children of folder ${parentId}: ${chrome.runtime.lastError.message}`);
      }
      const existingFolder = children.find(child => child.title === folderName && !child.url);
      if (existingFolder) {
        console.log(`Folder "${folderName}" found with ID: ${existingFolder.id}`);
        resolve(existingFolder.id);
      } else {
        console.log(`Folder "${folderName}" not found. Creating...`);
        chrome.bookmarks.create({ parentId: parentId, title: folderName }, (newFolder) => {
          if (chrome.runtime.lastError) {
            return reject(`Error creating folder "${folderName}": ${chrome.runtime.lastError.message}`);
          }
          if (!newFolder || !newFolder.id) {
             return reject(`Failed to create folder "${folderName}" - invalid response.`);
          }
          console.log(`Folder "${folderName}" created with ID: ${newFolder.id}`);
          resolve(newFolder.id);
        });
      }
    });
  });
}

// --- Main Processing Logic (MODIFIED) ---
async function processUrls(urls) { // Input is now explicitly a list of url strings
  let processedCount = 0;
  let errorCount = 0;
  // Removed skippedCount as we are not parsing specific formats anymore
  let folderIds = {};

  try {
    console.log("Starting URL processing...");

    // Ensure all target folders exist and get their IDs concurrently
    const [noteFolderId, amazonFolderId, etcFolderId] = await Promise.all([
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.NOTE),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.AMAZON), // Find/create 'amazon.co.jp' folder
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.ETC)
    ]);
    folderIds[FOLDER_NAMES.NOTE] = noteFolderId;
    folderIds[FOLDER_NAMES.AMAZON] = amazonFolderId;
    folderIds[FOLDER_NAMES.ETC] = etcFolderId;

    console.log("Folder IDs obtained:", folderIds);

    // Process each URL string from the input list
    for (const urlString of urls) { // Loop through url strings directly
        // Removed the URL | Title parsing logic

      try {
        // Validate the URL string
        const url = new URL(urlString);
        const hostname = url.hostname.toLowerCase(); // Get hostname

        let targetFolderId;
        // --- MODIFICATION START: Check hostname conditions ---
        if (hostname === FOLDER_NAMES.NOTE) { // Check for note.com
          targetFolderId = folderIds[FOLDER_NAMES.NOTE];
        } else if (hostname === 'amazon.co.jp' || hostname === 'www.amazon.co.jp') { // Check for amazon.co.jp OR www.amazon.co.jp
          targetFolderId = folderIds[FOLDER_NAMES.AMAZON]; // Use the amazon.co.jp folder ID
        } else { // Otherwise
          targetFolderId = folderIds[FOLDER_NAMES.ETC];
        }
        // --- MODIFICATION END ---

        // Create the bookmark using the URL string as both title and url
        await new Promise((resolve, reject) => {
           chrome.bookmarks.create({
             parentId: targetFolderId,
             // --- MODIFIED: Use urlString for both title and url ---
             title: urlString,
             url: urlString
             // --- END MODIFIED ---
           }, (newBookmark) => {
             if (chrome.runtime.lastError) {
               console.error(`Error bookmarking "${urlString}": ${chrome.runtime.lastError.message}`);
               reject(chrome.runtime.lastError.message);
             } else if (!newBookmark) {
                console.error(`Failed to create bookmark for "${urlString}" - invalid response.`);
                reject('Failed to create bookmark - invalid response.');
             } else {
               console.log(`Bookmarked "${urlString}" in folder ID ${targetFolderId}`);
               resolve();
             }
           });
        });
        processedCount++;

      } catch (urlError) {
        // Handle invalid URLs from new URL() or bookmark creation errors for a single URL
        console.error(`Skipping invalid or failed URL "${urlString}": ${urlError.message}`);
        errorCount++;
      }
    } // End of loop through urls

    // Updated status message (removed skipped count)
    const message = `Processed: ${processedCount}, Errors: ${errorCount}`;
    console.log(`Processing complete. ${message}`);
    return { success: true, message: message };

  } catch (folderError) {
    // Handle errors during folder finding/creation (critical failure)
    console.error("Critical error during folder setup:", folderError);
    return { success: false, message: `Error setting up folders: ${folderError}` };
  }
}


// --- Event Listener for Messages from Popup ---
// (No changes needed in this listener)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "processUrls") {
    console.log("Received processUrls request with", message.urls.length, "URLs");
    processUrls(message.urls).then(result => { // Pass the url list
       sendResponse(result);
    }).catch(error => {
        console.error("Unhandled error in processUrls:", error);
        sendResponse({ success: false, message: `Unexpected background error: ${error.message}` });
    });
    return true; // Indicate async response
  }
  return false;
});

// Optional: Log when the service worker starts
console.log("Background service worker started (v3 - Amazon www check).");
```

---

**手順:**

1. 上記のコードをそれぞれ対応するファイル名 (`manifest.json`, `popup.html`, `popup.js`, `background.js`) で保存します。既存のファイルを上書きしてください。
    
2. Chrome拡張機能管理画面 (`chrome://extensions`) を開きます。
    
3. デベロッパーモードがオンになっていることを確認します。
    
4. 対象の拡張機能（例: URL Sorter Bookmarker V3）を見つけて、「更新」ボタンをクリックするか、一度削除してから「パッケージ化されていない拡張機能を読み込む」でフォルダを再読み込みします。
    

これで、`amazon.co.jp` と `www.amazon.co.jp` の両方が `amazon.co.jp` フォルダに保存され、入力されたURLがそのままブックマークのタイトルとして使われる拡張機能として動作します。

指示を間違えました。

以下の仕様のGoogle Chrome機能拡張を実装してください。

# TEXTエリアからURLの一覧を取得。ここで得られるURLは、"<URL> | 説明文"という形式の文字列として与えられるものとし、<URL>の部分がブックマークのURL、説明文がブックマークのタイトルとする

## ホスト部が"note.com"のURLはルートフォルダ直下の"note.com"という名前のフォルダに登録

## ホスト部が"amazon.co.jp"か"www.amazon.co.jp"のURLはルートフォルダ直下の"amazon.co.jp"という名前のフォルダに登録

## ホスト部が上記以外ののURLはルートフォルダ直下の"etc"という名前のフォルダに登録

## 上記のフォルダが存在しない場合は、作成してから、URLを登録する

承知いたしました。指示の混同があったとのこと、失礼いたしました。

改めて、以下の最新の仕様に基づいてGoogle Chrome拡張機能を実装します。

**最終仕様:**

1. **入力:** TEXTエリアに `<URL> | <説明文>` 形式で1行ずつ入力。
    
2. **解析:** 各行から `<URL>` 部分をブックマークURL、`<説明文>` 部分をブックマークタイトルとして取得。
    
3. **分類:**
    
    - URLのホスト名が `note.com` → `note.com` フォルダへ。
        
    - URLのホスト名が `amazon.co.jp` または `www.amazon.co.jp` → `amazon.co.jp` フォルダへ。
        
    - 上記以外のURL → `etc` フォルダへ。
        
4. **フォルダ:** 対象フォルダがなければ作成する。
    
5. **ブックマーク:** 解析したURLとタイトルで登録する。
    

---

**1. `manifest.json`** (バージョン番号などを更新)

JSON

```
{
  "manifest_version": 3,
  "name": "URL Sorter Bookmarker V4", // Name reflecting final spec
  "version": "1.2", // Version updated
  "description": "Sorts 'URL | Title' inputs into specific bookmark folders (note.com, amazon.co.jp/www.amazon.co.jp, etc).", // Description updated
  "permissions": [
    "bookmarks"
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

**2. `popup.html`** (`URL | Title` 形式の説明を記載)

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

**3. `popup.js`** (変更なし)

テキストエリアの内容をそのままバックグラウンドに送信します。

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
      statusDiv.textContent = 'Please enter at least one line.'; // Message updated slightly
      return;
    }

    statusDiv.textContent = 'Processing...';
    processButton.disabled = true;

    // Send the raw lines to the background script
    chrome.runtime.sendMessage(
      { action: "processUrls", urls: lines }, // Send lines (variable name 'urls' kept for consistency with message listener)
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

**4. `background.js`** (`URL | Title` 解析と、修正されたAmazonホスト名チェックを両方実装)

JavaScript

```
// --- Configuration ---
const TARGET_PARENT_FOLDER_ID = '1'; // '1' = Bookmarks Bar, '2' = Other Bookmarks
const FOLDER_NAMES = {
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
        return reject(`Error getting children of folder ${parentId}: ${chrome.runtime.lastError.message}`);
      }
      const existingFolder = children.find(child => child.title === folderName && !child.url);
      if (existingFolder) {
        console.log(`Folder "${folderName}" found with ID: ${existingFolder.id}`);
        resolve(existingFolder.id);
      } else {
        console.log(`Folder "${folderName}" not found. Creating...`);
        chrome.bookmarks.create({ parentId: parentId, title: folderName }, (newFolder) => {
          if (chrome.runtime.lastError) {
            return reject(`Error creating folder "${folderName}": ${chrome.runtime.lastError.message}`);
          }
          if (!newFolder || !newFolder.id) {
             return reject(`Failed to create folder "${folderName}" - invalid response.`);
          }
          console.log(`Folder "${folderName}" created with ID: ${newFolder.id}`);
          resolve(newFolder.id);
        });
      }
    });
  });
}

// --- Main Processing Logic (MODIFIED - Combined Parsing & Amazon Check) ---
async function processUrls(lines) { // Input parameter is the list of lines
  let processedCount = 0;
  let errorCount = 0;
  let skippedCount = 0; // Count lines skipped due to format issues
  let folderIds = {};

  try {
    console.log("Starting URL processing (URL | Title format)...");

    // Ensure all target folders exist and get their IDs concurrently
    const [noteFolderId, amazonFolderId, etcFolderId] = await Promise.all([
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.NOTE),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.AMAZON),
      findOrCreateFolder(TARGET_PARENT_FOLDER_ID, FOLDER_NAMES.ETC)
    ]);
    folderIds[FOLDER_NAMES.NOTE] = noteFolderId;
    folderIds[FOLDER_NAMES.AMAZON] = amazonFolderId;
    folderIds[FOLDER_NAMES.ETC] = etcFolderId;

    console.log("Folder IDs obtained:", folderIds);

    // Process each line from the input
    for (const line of lines) {
      // --- Step 1: Parse the line for URL and Title ---
      const parts = line.split('|');

      if (parts.length < 2) {
        console.warn(`Skipping line due to missing '|' separator: "${line}"`);
        skippedCount++;
        continue; // Skip to the next line
      }

      const urlString = parts[0].trim();
      const titleString = parts.slice(1).join('|').trim(); // Handle '|' in description

      if (!urlString || !titleString) {
         console.warn(`Skipping line due to empty URL or title after parsing: "${line}"`);
         skippedCount++;
         continue; // Skip to the next line
      }
      // --- End Step 1 ---

      try {
        // --- Step 2: Validate URL and Determine Target Folder ---
        const url = new URL(urlString); // Validate the URL part
        const hostname = url.hostname.toLowerCase();

        let targetFolderId;
        if (hostname === FOLDER_NAMES.NOTE) { // Check note.com
          targetFolderId = folderIds[FOLDER_NAMES.NOTE];
        } else if (hostname === 'amazon.co.jp' || hostname === 'www.amazon.co.jp') { // Check amazon.co.jp OR www.amazon.co.jp
          targetFolderId = folderIds[FOLDER_NAMES.AMAZON]; // Use the amazon.co.jp folder
        } else { // Otherwise
          targetFolderId = folderIds[FOLDER_NAMES.ETC];
        }
        // --- End Step 2 ---

        // --- Step 3: Create the Bookmark ---
        await new Promise((resolve, reject) => {
           chrome.bookmarks.create({
             parentId: targetFolderId,
             title: titleString, // Use parsed title
             url: urlString      // Use parsed URL
           }, (newBookmark) => {
             if (chrome.runtime.lastError) {
               console.error(`Error bookmarking "${urlString}" (Title: "${titleString}"): ${chrome.runtime.lastError.message}`);
               reject(chrome.runtime.lastError.message);
             } else if (!newBookmark) {
                console.error(`Failed to create bookmark for "${urlString}" - invalid response.`);
                reject('Failed to create bookmark - invalid response.');
             } else {
               console.log(`Bookmarked "${urlString}" (Title: "${titleString}") in folder ID ${targetFolderId}`);
               resolve();
             }
           });
        });
        processedCount++;
        // --- End Step 3 ---

      } catch (urlError) {
        // Handle invalid URLs from new URL() or bookmark creation errors
        console.error(`Skipping line due to error for "${line}": ${urlError.message}`);
        errorCount++;
      }
    } // End of loop through lines

    // Final status message including skipped count
    const message = `Processed: ${processedCount}, Skipped (Format): ${skippedCount}, Errors (URL/Bookmark): ${errorCount}`;
    console.log(`Processing complete. ${message}`);
    return { success: true, message: message };

  } catch (folderError) {
    // Handle critical errors during folder setup
    console.error("Critical error during folder setup:", folderError);
    return { success: false, message: `Error setting up folders: ${folderError}` };
  }
}


// --- Event Listener for Messages from Popup ---
// (No changes needed here)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // The key 'urls' in the message actually contains the 'lines' from popup.js
  if (message.action === "processUrls" && message.urls) {
    console.log("Received processUrls request with", message.urls.length, "lines (expecting URL | Title format)");
    processUrls(message.urls).then(result => { // Pass the lines array to processUrls
       sendResponse(result);
    }).catch(error => {
        console.error("Unhandled error in processUrls:", error);
        sendResponse({ success: false, message: `Unexpected background error: ${error.message}` });
    });
    return true; // Indicate async response
  }
  return false; // Explicitly return false for messages not handled or without async response
});

// Optional: Log when the service worker starts
console.log("Background service worker started (v4 - URL|Title & Amazon www check).");
```

---

**手順:**

1. 上記4つのコード (`manifest.json`, `popup.html`, `popup.js`, `background.js`) を、拡張機能用のフォルダにそれぞれ正しいファイル名で保存（または上書き）してください。
    
2. Chrome拡張機能管理画面 (`chrome://extensions`) を開きます。
    
3. デベロッパーモードがオンになっていることを確認します。
    
4. 該当の拡張機能を更新するか、一度削除して再読み込みします。
    

これで、「`<URL> | <説明文>`」形式の入力を受け付け、URLのホスト名（`note.com`, `amazon.co.jp`/`www.amazon.co.jp`, その他）に基づいて分類し、指定のタイトルとURLでブックマークを作成する拡張機能として動作します。
