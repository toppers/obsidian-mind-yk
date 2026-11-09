---
date: 2026-05-31
source-type: article
source-url: E:\Crepo\ykominami-svn-2\tecsgen\trunk\doc\C2TECSBrdigePlugin.txt
title: C2TECSBridgePlugin — C言語からTECS受け口関数を呼び出すプラグイン
compiled: true
tags: [tecs, toppers, plugin, c-language]
description: "C2TECSBridgePlugin の使用方法・オプション・生成コードの詳細リファレンス"
---

# C2TECSBridgePlugin — C言語からTECS受け口関数を呼び出すプラグイン

C 言語から TECS の受け口関数を直接呼び出すセルタイプを生成するシグニチャプラグイン。

## 使用方法

```cdl
// signature sSignature, cell CellToBeCalledFromC は定義済みとする
generate(C2TECSBridgePlugin, sSignature, "prefix='Sig'" );

cell nC2TECS::tsSignature C2TECSBridge {
   cCall = CellToBeCalledFromC.eEntry;
};
```

## オプション

| オプション | 説明 |
|-----------|------|
| `header_name=name` | 生成ヘッダファイルの名前を `name.h` にする |
| `prefix=PREFIX` | 各関数名の前に PREFIX を付加 |
| `suffix=SUFFIX` | 各関数名の後ろに SUFFIX を付加 |

## 動作

`generate(C2TECSBridgePlugin, sSignature, ...)` により `nC2TECS::tsSignature` セルタイプを生成する。C言語から関数を呼び出す際、セルタイプに結合された TECS セルの受け口関数が呼ばれる。

## 関連

- [[plugin-c2tecs]]
- [[tecs-plugin]]
- [[tecs-signature]]
- [[tecs-celltype]]
