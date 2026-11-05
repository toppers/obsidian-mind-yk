---
date: 2026-05-15
description: "指定フォルダ以下のブックマークを Title・URL に基づき分類して別フォルダへ移動する Chrome拡張。ブックマーク自動分類.md とほぼ同内容"
tags:
  - reference
  - chrome-extension
  - bookmark
---

指定フォルダ以下に存在するBookmarkをTitle、URLに基づいて、分類して、別のフォルダに移動させる機能拡張を作成して

こんにちは！私は **YK-ChromeExt-Coding-Assistant** です。 Google Chrome拡張機能の開発支援、コード作成、解説を専門としています。あなたのアイデアを形にするお手伝いをさせてください。

「指定フォルダ内のブックマークを、タイトルやURLに基づいて自動的に分類し、適切なフォルダへ移動させる」という機能、素晴らしいですね！ブックマークの整理は大変な作業なので、これを自動化できれば非常に便利です。

ご希望の機能を実現するための **完全なコード** と **ステップバイステップのガイド** を作成します。

---

### 1. リクエストの理解と確認

まず、作成する拡張機能の概要を確認します。

- **目的:** 指定した「ソースフォルダ」内のブックマークを整理する。
    
- **方法:** ブックマークの「タイトル」または「URL」に含まれるキーワードをチェックする。
    
- **アクション:** 定義したルールに従って、特定の「ターゲットフォルダ（カテゴリ）」へ移動させる。ターゲットフォルダがない場合は自動作成する。
    

**開発に必要な情報（後ほどコード内でカスタマイズ可能です）：** 今回は例として、以下の分類ルールをコードに組み込みます。これらは後で自由に変更できます。

- URLに `youtube` や `vimeo` がある → **「Video」** フォルダへ
    
- URLに `github` や `stackoverflow` がある → **「Dev」** フォルダへ
    
- タイトルに `ニュース` や `News` がある → **「News」** フォルダへ
    

---

### 2. ソリューションの概要

この拡張機能は、以下の3つの主要ファイルで構成されます。

1. **`manifest.json`**: 拡張機能の設定ファイル。ブックマークを操作する権限（Permissions）を宣言します。
    
2. **`popup.html`**: ユーザーインターフェース。整理したい「フォルダ名」を入力し、実行ボタンを押す画面です。
    
3. **`popup.js`**: ロジックの中核。ブックマークの検索、判定、移動、フォルダ作成を行います。
    

**処理の流れ:**

1. ユーザーが対象フォルダ名（例: "未整理"）を入力してボタンを押す。
    
2. スクリプトがそのフォルダを探す。
    
3. フォルダ内のブックマークを一つずつチェックする。
    
4. ルール（キーワード）に一致したら、該当するカテゴリフォルダへ移動させる。
    

---

### 3. コードと実装手順

任意の場所に新しいフォルダ（例: `bookmark-sorter`）を作成し、以下の3つのファイルをその中に作成してください。

#### A. manifest.json

拡張機能の身分証明書です。`bookmarks` 権限が必須です。

JSON

```
{
  "manifest_version": 3,
  "name": "Bookmark Auto Sorter",
  "version": "1.0",
  "description": "指定フォルダのブックマークをルールに基づいて自動分類します。",
  "permissions": [
    "bookmarks"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

_(注: アイコン画像がない場合は `icons` の項目を削除しても動作します)_

#### B. popup.html

シンプルで使いやすい操作画面です。

HTML

```
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <style>
    body { width: 300px; padding: 15px; font-family: sans-serif; }
    h2 { font-size: 16px; margin-top: 0; }
    input { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
    button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
    button:hover { background-color: #45a049; }
    #status { margin-top: 10px; font-size: 12px; color: #666; }
  </style>
</head>
<body>
  <h2>ブックマーク自動整理</h2>
  <p>整理元のフォルダ名:</p>
  <input type="text" id="sourceFolder" value="その他のブックマーク" placeholder="例: その他">
  <button id="sortBtn">整理を開始</button>
  <div id="status"></div>
  <script src="popup.js"></script>
</body>
</html>
```

#### C. popup.js

ここが最も重要なプログラム部分です。分類ルールは `categoryRules` 変数で管理しています。

JavaScript

```
document.addEventListener('DOMContentLoaded', () => {
  const sortBtn = document.getElementById('sortBtn');
  const statusDiv = document.getElementById('status');

  // 分類ルールの定義 (ここを自由にカスタマイズしてください)
  // キー: ターゲットフォルダ名
  // 値: マッチさせるキーワードの配列 (URLまたはタイトルに含まれているか)
  const categoryRules = {
    "Video": ["youtube", "vimeo", "netflix", "ニコニコ"],
    "Dev": ["github", "stackoverflow", "qiita", "zenn", "script"],
    "News": ["news", "ニュース", "yahoo", "cnn"],
    "Shopping": ["amazon", "rakuten", "メルカリ"]
  };

  sortBtn.addEventListener('click', async () => {
    const sourceFolderName = document.getElementById('sourceFolder').value;
    
    if (!sourceFolderName) {
      updateStatus("フォルダ名を入力してください。", "red");
      return;
    }

    updateStatus("処理中...", "blue");

    try {
      // 1. ソースフォルダ（整理元）を探す
      const sourceNodes = await chrome.bookmarks.search({ title: sourceFolderName });
      
      // フォルダが見つからない、またはフォルダではない場合
      const sourceFolder = sourceNodes.find(node => !node.url); 
      
      if (!sourceFolder) {
        updateStatus(`フォルダ「${sourceFolderName}」が見つかりませんでした。`, "red");
        return;
      }

      // 2. フォルダ内のブックマークを取得
      const children = await chrome.bookmarks.getChildren(sourceFolder.id);
      let moveCount = 0;

      for (const bookmark of children) {
        // フォルダ自体は移動させない（URLプロパティがあるものがブックマーク）
        if (!bookmark.url) continue;

        // 3. 分類先を判定
        const targetCategory = determineCategory(bookmark);

        if (targetCategory) {
          // 4. ターゲットフォルダを取得または作成して移動
          const targetFolderId = await getOrCreateFolderId(targetCategory, sourceFolder.parentId);
          await chrome.bookmarks.move(bookmark.id, { parentId: targetFolderId });
          moveCount++;
        }
      }

      updateStatus(`完了！ ${moveCount} 個のブックマークを移動しました。`, "green");

    } catch (error) {
      console.error(error);
      updateStatus("エラーが発生しました: " + error.message, "red");
    }
  });

  // ブックマークのタイトルやURLからカテゴリを判定する関数
  function determineCategory(bookmark) {
    const textToCheck = (bookmark.title + " " + bookmark.url).toLowerCase();

    for (const [category, keywords] of Object.entries(categoryRules)) {
      // いずれかのキーワードが含まれていれば、そのカテゴリを返す
      if (keywords.some(keyword => textToCheck.includes(keyword.toLowerCase()))) {
        return category;
      }
    }
    return null; // 該当なし
  }

  // 指定された名前のフォルダIDを取得する（なければ作成する）関数
  async function getOrCreateFolderId(title, parentId) {
    // 同じ親フォルダ内に、同じ名前のフォルダがあるか検索
    const children = await chrome.bookmarks.getChildren(parentId);
    const existingFolder = children.find(node => node.title === title && !node.url);

    if (existingFolder) {
      return existingFolder.id;
    } else {
      // なければ作成
      const newFolder = await chrome.bookmarks.create({
        parentId: parentId,
        title: title
      });
      return newFolder.id;
    }
  }

  function updateStatus(message, color) {
    statusDiv.textContent = message;
    statusDiv.style.color = color || "black";
  }
});
```

---

### 4. 導入と実行方法

1. **Chromeを開く:** Google Chromeブラウザを開きます。
    
2. **拡張機能ページへ:** アドレスバーに `chrome://extensions/` と入力してEnterキーを押します。
    
3. **デベロッパーモード:** 画面右上の「デベロッパーモード」スイッチを **オン** にします。
    
4. **読み込み:** 「パッケージ化されていない拡張機能を読み込む」ボタンをクリックします。
    
5. **フォルダ選択:** 先ほど作成した `bookmark-sorter` フォルダを選択します。
    
6. **テスト:**
    
    - ブックマークバーに適当なテスト用フォルダ（例：「未整理」）を作り、YouTubeやGithubなどのブックマークをいくつか入れておきます。
        
    - 拡張機能のアイコンをクリックし、「未整理」と入力して「整理を開始」を押してください。
        

### ポイントと注意点

- **非同期処理 (`async/await`):** ブックマークの操作は時間がかかる可能性があるため、JavaScriptの `async/await` 構文を使って、処理が順番に行われるように制御しています。
    
- **安全策:** このコードは「フォルダ」自体は移動させず、「URLを持つブックマーク」のみを移動対象としています。
    
- **カスタマイズ:** `popup.js` の `categoryRules` を編集することで、あなたの好みの分類ルール（仕事用、趣味用など）を簡単に追加できます。
    

---

このコードで基本的な機能は網羅されています。 もし、「特定のURLドメインだけを対象にしたい」や「移動ではなくコピーにしたい」などの追加要望があれば教えてください。

**次は、あなたの特定の分類ルール（どのようなカテゴリを作りたいか）に合わせて、`categoryRules` の部分を一緒に調整しましょうか？**