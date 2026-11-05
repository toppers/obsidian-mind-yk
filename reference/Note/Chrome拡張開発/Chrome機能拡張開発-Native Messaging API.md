---
date: 2026-05-15
description: "Chrome拡張の Native Messaging API の使い方 — サンドボックス外のネイティブホストと通信し、ローカルファイル読み書きやハードウェアアクセスを可能にする3要素"
tags:
  - reference
  - chrome-extension
---

Google Chromeの拡張機能におけるNative Messaging APIの使い方について説明します。

Native Messaging APIは、Chrome拡張機能がユーザーのコンピュータ上で動作するローカルのネイティブアプリケーション（以下、ネイティブホスト）と直接通信するための仕組みです。これにより、ブラウザのサンドボックス環境だけでは実現できない機能（ローカルファイルの読み書き、特定のハードウェアへのアクセス、他のローカルアプリとの連携など）を拡張機能から利用できるようになります。

Native Messagingを利用するには、主に以下の3つの要素が必要です。

1. **Chrome拡張機能:** ネイティブホストにメッセージを送受信する主体。
    
2. **ネイティブホスト (Native Messaging Host):** 拡張機能と通信するローカルの実行可能プログラム。
    
3. **ホストマニフェストファイル:** ネイティブホストの場所や、どの拡張機能との通信を許可するかを定義するJSONファイル。
    

**使い方の大まかな流れ:**

**ステップ1: ネイティブホスト (Native Messaging Host) の作成**

- **目的:** 拡張機能からのメッセージを標準入力 (stdin) で受け取り、処理結果を標準出力 (stdout) にJSON形式で返すプログラムを作成します。
    
- **言語:** Python, C++, C#, Java, Node.jsなど、標準入出力とJSON処理ができる言語なら何でも構いません。
    
- **通信プロトコル:**
    
    - 送受信するメッセージはJSON形式です。
        
    - 各メッセージの前には、メッセージ本体の長さ (バイト数) を示す **32ビットのリトルエンディアン** の整数を付加する必要があります。
        
    - **受信 (stdin):** 最初の4バイトでメッセージ長を読み取り、その長さ分のJSONデータを読み込みます。
        
    - **送信 (stdout):** 送信するJSONメッセージのバイト長を計算し、その長さを4バイトのリトルエンディアンで書き込んだ後、JSONメッセージ本体を書き込みます。
        

**簡単なPythonの例 (メッセージを受信してそのまま返す):**

Python

```
import sys
import json
import struct

# メッセージ読み込み関数
def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    message_length = struct.unpack('@I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

# メッセージ送信関数
def send_message(message_content):
    encoded_content = json.dumps(message_content).encode('utf-8')
    encoded_length = struct.pack('@I', len(encoded_content))
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()

# メインループ
while True:
    received_message = get_message()
    # ここで受け取ったメッセージに応じた処理を行う
    # 例: 受け取ったメッセージをそのまま返す
    send_message(received_message)
```

**ステップ2: ホストマニフェストファイル (JSON) の作成**

- **目的:** Chromeに対して、ネイティブホストの名前、説明、実行ファイルの場所、そしてどの拡張機能からの接続を許可するかを教えます。
    
- **ファイル名:** 任意ですが、通常はネイティブホスト名に関連付けます (例: `com.my_company.my_application.json`)。
    
- **内容:**
    
    JSON
    
    ```
    {
      "name": "com.my_company.my_application", // ネイティブホストの一意な名前（通常は逆ドメイン名形式）
      "description": "My Application Native Host", // 説明
      "path": "/path/to/your/native/host/executable", // ネイティブホスト実行ファイルの絶対パス (Windowsでは \ を \\ にエスケープ)
      "type": "stdio", // 通信方法 (現在は stdio のみ)
      "allowed_origins": [
        "chrome-extension://YOUR_EXTENSION_ID_HERE/" // 通信を許可する拡張機能のID (必ず / を付ける)
        // 必要であれば複数の拡張機能IDを追加
      ]
    }
    ```
    
    - `YOUR_EXTENSION_ID_HERE` は、開発中の拡張機能IDに置き換えます。拡張機能管理ページ (`chrome://extensions/`) で確認できます (デベロッパーモードをONにする必要があります)。
        
- **配置場所:** このマニフェストファイルをOS固有の場所に配置する必要があります。
    
    - **Windows:** レジストリに登録します。
        
        - キー: `HKEY_CURRENT_USER\Software\Google\Chrome\NativeMessagingHosts\com.my_company.my_application` または `HKEY_LOCAL_MACHINE\Software\Google\Chrome\NativeMessagingHosts\com.my_company.my_application`
            
        - 値: (既定) にホストマニフェストファイルのフルパスを設定。
            
    - **macOS:**
        
        - ユーザー単位: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.my_company.my_application.json`
            
        - システム全体: `/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.my_company.my_application.json`
            
    - **Linux:**
        
        - ユーザー単位: `~/.config/google-chrome/NativeMessagingHosts/com.my_company.my_application.json`
            
        - システム全体: `/etc/opt/chrome/native-messaging-hosts/com.my_company.my_application.json`
            

**ステップ3: Chrome拡張機能側の実装**

- **`manifest.json` の編集:**
    
    - `permissions` に `"nativeMessaging"` を追加します。
        
    
    JSON
    
    ```
    {
      "manifest_version": 3,
      "name": "My Native Messaging Extension",
      "version": "1.0",
      "permissions": [
        "nativeMessaging"
      ],
      "background": {
        "service_worker": "background.js"
      }
      // 他の設定...
    }
    ```
    
- **JavaScript (例: `background.js`) での通信:**
    
    - **接続:** `chrome.runtime.connectNative(ネイティブホスト名)` を使用して、ネイティブホストへの持続的な接続ポートを作成します。ネイティブホスト名はホストマニフェストで定義した `name` (例: `"com.my_company.my_application"`) です。
        
    - **メッセージ送信:** 作成したポートの `port.postMessage(メッセージオブジェクト)` を使います。
        
    - **メッセージ受信:** ポートの `port.onMessage.addListener(コールバック関数)` でメッセージを待ち受けます。
        
    - **切断:** `port.onDisconnect.addListener(コールバック関数)` で切断時の処理を行います。
        

**簡単なJavaScriptの例:**

JavaScript

```
// background.js

const hostName = "com.my_company.my_application";
let port = null;

function connect() {
  console.log("Connecting to native host:", hostName);
  port = chrome.runtime.connectNative(hostName);

  port.onMessage.addListener((message) => {
    console.log("Received message from native host:", message);
    // ネイティブホストからの応答を処理
  });

  port.onDisconnect.addListener(() => {
    if (chrome.runtime.lastError) {
      console.error("Disconnected due to an error:", chrome.runtime.lastError.message);
    } else {
      console.log("Disconnected from native host");
    }
    port = null; // ポートをリセット
    // 必要に応じて再接続処理など
  });
  console.log("Connected to native host.");
}

// 拡張機能起動時などに接続を開始
connect();

// 例: ボタンクリックなどでメッセージを送信する関数
function sendMessageToHost(message) {
  if (port) {
    console.log("Sending message to native host:", message);
    port.postMessage(message);
  } else {
    console.error("Not connected to native host.");
    // 必要なら再接続を試みる
    connect();
    // 少し待ってから再送するなど
    setTimeout(() => {
        if (port) {
           port.postMessage(message);
        }
    }, 1000);
  }
}

// 使用例 (例えば5秒後にメッセージを送る)
setTimeout(() => {
    sendMessageToHost({ text: "Hello from extension!" });
}, 5000);

// 単発のメッセージを送る場合 (接続を維持しない)
// chrome.runtime.sendNativeMessage(hostName, { text: "One-time message" }, (response) => {
//   if (chrome.runtime.lastError) {
//     console.error("Error sending one-time message:", chrome.runtime.lastError.message);
//   } else {
//     console.log("Received one-time response:", response);
//   }
// });
```

**デバッグのヒント:**

- **拡張機能のエラー:** `chrome://extensions/` で拡張機能の詳細を開き、「エラー」を確認します。
    
- **ネイティブホストのログ:** ネイティブホストプログラム内でファイルにログを出力するように実装するとデバッグが容易になります。
    
- **Chromeの標準エラー出力:** ネイティブホストが標準エラー (stderr) に出力した内容は、Chromeのターミナル/コンソールに出力されることがあります (起動方法による)。
    
- **マニフェストファイルのパスと内容:** ホストマニフェストファイルの配置場所、JSONの構文、`path` や `allowed_origins` の値が正しいか確認します。特に拡張機能IDの末尾の `/` を忘れないようにします。
    
- **実行権限:** ネイティブホストの実行ファイルに実行権限があるか確認します (Linux/macOS)。
    

Native Messagingは強力な機能ですが、設定や実装が少し複雑です。公式ドキュメントやサンプルを参考に、ステップバイステップで進めてみてください。

**公式ドキュメント:** [https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging?hl=ja](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging?hl=ja)