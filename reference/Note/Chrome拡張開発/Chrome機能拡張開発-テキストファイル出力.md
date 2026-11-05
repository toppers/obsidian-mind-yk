---
date: 2026-05-15
description: "ブックマークをテキストファイルへ書き出す Chrome拡張 — ブックマークの階層（ツリー）構造をどうテキスト化するかが要点"
tags:
  - reference
  - chrome-extension
  - bookmark
---

ブックマークをテキストファイルとして書き出す機能ですね。これもChrome拡張機能で非常に役立つ機能の一つです。

前回の「ファイルの出力」の知識に、新しく「ブックマーク情報の取得」というステップを組み合わせることで実現できます。ブックマークはフォルダの中にフォルダが入る「階層構造（ツリー構造）」になっているため、それをうまくテキスト化する処理がポイントになります。

それでは、ステップバイステップで実装方法を解説します。

---

### ソリューションの概要

1. **権限の追加:** `manifest.json` にブックマークを読み取るための権限を追加します。
    
2. **ブックマークの取得:** `chrome.bookmarks.getTree` APIを使用して、すべてのブックマーク情報を取得します。
    
3. **テキストへの変換:** 取得したデータは複雑な階層構造なので、これを読みやすいテキスト形式（インデント付きのリストなど）に変換します。
    
4. **保存:** 前回同様、`chrome.downloads` を使ってファイルとして出力します。
    

---

### コードと実装手順

#### ステップ 1: manifest.json の更新

`permissions` 配列に `"bookmarks"` を追加します。これがないとブックマーク情報にアクセスできません。

JSON

```
{
  "manifest_version": 3,
  "name": "ブックマーク保存拡張機能",
  "version": "1.0",
  "permissions": [
    "downloads",
    "bookmarks" 
  ],
  "action": {
    "default_popup": "popup.html"
  }
}
```

#### ステップ 2: popup.html

実行用のボタンを用意します。

HTML

```
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { width: 250px; padding: 10px; text-align: center; }
    button { padding: 10px; cursor: pointer; width: 100%; }
  </style>
</head>
<body>
  <h3>ブックマーク出力</h3>
  <button id="exportBtn">ブックマークを保存する</button>

  <script src="popup.js"></script>
</body>
</html>
```

#### ステップ 3: popup.js

ここがメインのロジックです。階層構造をテキスト化するために「再帰関数（自分自身を呼び出す関数）」を使用しています。

JavaScript

```
const exportButton = document.getElementById('exportBtn');

// ブックマークのノードを再帰的に処理してテキスト化する関数
function processBookmarkNodes(nodes, depth = 0) {
    let result = "";
    // 階層の深さに応じてインデント（空白）を作る
    const indent = "  ".repeat(depth);

    for (const node of nodes) {
        if (node.url) {
            // URLがある場合（＝ブックマークそのもの）
            result += `${indent}- [Page] ${node.title} : ${node.url}\n`;
        } else {
            // URLがない場合（＝フォルダ）
            // ルートフォルダなどは名前がない場合があるので空文字チェック
            const folderName = node.title ? `[Folder] ${node.title}` : "[Root]";
            result += `${indent}${folderName}\n`;
            
            // 子ノード（フォルダの中身）がある場合は、さらに深く探索する（再帰処理）
            if (node.children) {
                result += processBookmarkNodes(node.children, depth + 1);
            }
        }
    }
    return result;
}

exportButton.addEventListener('click', () => {
    // 1. ブックマークツリー全体を取得
    chrome.bookmarks.getTree((bookmarkTreeNodes) => {
        
        // 2. ツリー構造をテキストデータに変換
        const textData = processBookmarkNodes(bookmarkTreeNodes);

        // 3. ファイル保存の準備（前回と同じ流れ）
        const blob = new Blob([textData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        // 4. ダウンロード実行
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        chrome.downloads.download({
            url: url,
            filename: `bookmarks_${timestamp}.txt`, // ファイル名に日時を入れると便利です
            saveAs: true
        });
    });
});
```

---

### コードの解説

- **`chrome.bookmarks.getTree(callback)`**: Chromeに保存されているすべてのブックマークを、根っこ（ルート）から丸ごと取得します。
    
- **再帰関数 `processBookmarkNodes`**: ブックマークは「フォルダの中にまたフォルダがある」という構造をしています。
    
    - `node.children` がある場合はフォルダなので、さらにその中身に対して `processBookmarkNodes` を実行します。
        
    - これを繰り返すことで、どんなに深い階層のブックマークもすべてテキスト化できます。
        
    - `depth` 変数を使ってインデント（字下げ）を行うことで、出力されたテキストファイルが見やすくなります。
        

### 出力イメージ（bookmarks_xxxx.txt）

このコードを実行すると、以下のようなテキストファイルが生成されます。

Plaintext

```
[Root]
  [Folder] ブックマーク バー
    - [Page] Google : https://www.google.com/
    [Folder] 仕事用
      - [Page] GitHub : https://github.com/
  [Folder] その他のブックマーク
    - [Page] レシピサイト : https://...
```

---

これで、ご自身のPC上のブックマークをテキストファイルとしてバックアップできるようになりました。

**次のステップとして、こちらはいかがでしょうか？**

- テキスト形式ではなく、他のプログラムでも読み込みやすい **JSON形式 (`.json`)** で保存するように変更する。
    
- すべてのブックマークではなく、**「特定のフォルダ（例えば『仕事用』フォルダなど）」だけ** を抽出して保存する。
    

ご希望があれば、コードを調整いたします！