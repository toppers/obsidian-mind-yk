---
date: 2026-05-15
description: "フォームの隠しフィールドを公開鍵で暗号化する Chrome拡張の検討 — 公開鍵の入手方法（拡張に埋め込むか外部取得か）を確認する段階で止まっている"
tags:
  - reference
  - chrome-extension
  - crypto
---

おもしろそうな拡張機能ですね！フォームの仕様、ばっちり承知しました。

ただ、いくつか確認させてください。

1. **公開鍵の入手方法**: 隠しフィールドで暗号化するために、公開鍵をどのように取得する予定ですか？拡張機能に埋め込むのか、それとも別の方法で取得するのでしょうか？
    
2. **現在時刻の形式**: 現在時刻はどのような形式でJSONに含めますか？ (例: ISO 8601形式 "2025-04-15T10:11:00Z"、UNIXタイムスタンプなど)
    
3. **メールアドレスの取得方法**: ユーザーのメールアドレスはどのように取得しますか？ChromeのIdentity APIを利用する、または拡張機能内で入力してもらうなどの方法が考えられます。
    

これらの点が明確になると、より具体的な実装方法をご提案できます。どんなアイデアをお持ちですか？ぜひ教えてください！

1.公開鍵は拡張機能に埋め込みます

2.現在時刻はUNIXタイムスタンプを使用します

3.メール阿どれは拡張機能に埋め込みます。

了解しました！公開鍵とメールアドレスは拡張機能に埋め込み、現在時刻はUNIXタイムスタンプでJSONに含めるんですね。

それでは、実装の基本的な流れとコード例をご提案します。

**基本的な流れ:**

1. **マニフェストファイル (manifest.json) の作成:** 拡張機能の名前、バージョン、必要な権限などを定義します。
    
2. **HTMLファイルの作成:** ユーザーインターフェースとなるフォームを作成します。
    
3. **JavaScriptファイルの作成:** フォームの送信処理、JSONデータの作成、暗号化処理、隠しフィールドへの設定を行います。
    
4. **(必要に応じて) バックグラウンドスクリプトの作成:** 拡張機能のライフサイクル管理や、より複雑な処理を行う場合に利用します。今回はフォームの処理がメインなので、必須ではありません。
    

**コード例:**

まずは、必要な情報をJavaScriptファイルに定義しておきましょう。

JavaScript

```
const publicKeyPEM = "-----BEGIN PUBLIC KEY-----\nYOUR_PUBLIC_KEY_HERE\n-----END PUBLIC KEY-----\n"; // 実際の公開鍵に置き換えてください
const embeddedEmail = "your_embedded_email@example.com"; // 実際のメールアドレスに置き換えてください
const actionURL = "https://example.com/a";
```

次に、HTMLファイル (例えば `popup.html`) でフォームを作成します。

HTML

```
<!DOCTYPE html>
<html>
<head>
  <title>My Chrome Extension</title>
</head>
<body>
  <form id="myForm" action="" method="POST">
    <div>
      <label for="command">Command:</label>
      <input type="text" id="command" name="command">
    </div>
    <div>
      <label for="api_name">API Name:</label>
      <input type="text" id="api_name" name="api_name">
    </div>
    <input type="hidden" id="object" name="object">
    <button type="submit">Submit</button>
  </form>
  <script src="popup.js"></script>
</body>
</html>
```

そして、JavaScriptファイル (`popup.js`) でフォームの送信処理などを実装します。ここでは、[jsrsasign](https://kjur.github.io/jsrsasign/) などのJavaScript暗号化ライブラリを使用すると便利です。まず、ライブラリをHTMLに読み込ませるか、拡張機能に含める必要があります。ここではCDN経由で読み込む例を示します。

HTML

```
<!DOCTYPE html>
<html>
<head>
  <title>My Chrome Extension</title>
</head>
<body>
  <form id="myForm" action="" method="POST">
    <div>
      <label for="command">Command:</label>
      <input type="text" id="command" name="command">
    </div>
    <div>
      <label for="api_name">API Name:</label>
      <input type="text" id="api_name" name="api_name">
    </div>
    <input type="hidden" id="object" name="object">
    <button type="submit">Submit</button>
  </form>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jsrsasign/8.0.20/jsrsasign-all-min.js"></script>
  <script src="popup.js"></script>
</body>
</html>
```

そして、`popup.js` の内容は以下のようになります。

JavaScript

```
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('myForm');
  form.action = actionURL;

  form.addEventListener('submit', function(event) {
    event.preventDefault();

    const command = document.getElementById('command').value;
    const apiName = document.getElementById('api_name').value;
    const currentTime = Math.floor(Date.now() / 1000); // UNIXタイムスタンプ

    const objectData = {
      email: embeddedEmail,
      timestamp: currentTime
    };
    const objectString = JSON.stringify(objectData);

    // jsrsasignライブラリを使って公開鍵で暗号化
    try {
      const publicKey = KEYUTIL.getKey(publicKeyPEM);
      const encryptedDataHex = KJUR.crypto.Cipher.encrypt(objectString, publicKey, 'RSA');
      const encryptedDataBase64 = btoa(String.fromCharCode.apply(null, new Uint8Array(hextobin(encryptedDataHex))));

      document.getElementById('object').value = encryptedDataBase64;
      form.submit(); // フォームを送信
    } catch (error) {
      console.error("Encryption error:", error);
      alert("Encryption failed. Please try again.");
    }
  });
});
```

最後に、`manifest.json` ファイルを作成します。

JSON

```
{
  "manifest_version": 3,
  "name": "My Form Extension",
  "version": "1.0",
  "description": "Submits a form with encrypted data.",
  "permissions": [],
  "action": {
    "default_popup": "popup.html"
  }
}
```

**注意点:**

- **公開鍵の安全性:** 拡張機能に公開鍵を埋め込む場合、その公開鍵を使って暗号化されたデータは、拡張機能のコードを見れば誰でも復号できてしまう可能性があります。これは、クライアントサイドでの暗号化の一般的な限界です。より安全な方法としては、サーバーサイドで公開鍵を管理し、API経由で取得するなどの方法が考えられます。今回はご指定の仕様に沿って実装しています。
    
- **jsrsasignライブラリ:** 上記の例では `jsrsasign` を使用していますが、他のJavaScript暗号化ライブラリも利用可能です。
    
- **エラーハンドリング:** 暗号化処理でエラーが発生した場合の処理を追加しています。
    
- **実際の公開鍵とメールアドレス:** `publicKeyPEM` と `embeddedEmail` のプレースホルダーは、必ず実際の値に置き換えてください。
    

このコード例を元に、Chrome拡張機能を開発できます。開発者モードを有効にしたChromeに、作成した `manifest.json`、`popup.html`、`popup.js` などのファイルをフォルダごと読み込むことで、拡張機能を試すことができます。

何か他に質問や、さらに具体的な実装に関するご要望があれば、遠慮なくお尋ねください！