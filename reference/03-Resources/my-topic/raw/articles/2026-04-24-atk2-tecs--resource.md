---
date: 2026-04-24
source-type: article
source-url: E:\Crepo\github-toppers\tecs-docs\docs\_build\html\atk2+tecs\resource.html
title: リソース ― tResource
compiled: true
tags: [tecs, toppers, documentation]
description: "TECS ドキュメント: リソース ― tResource"
---

# リソース ― tResource

# リソース ― `tResource`

課題

to be filled in

## 使用方法

### リソースの生成

アプリケーション開発者は `tResource` セルタイプのセルを生成することにより、リソースを生成することができます。次の例では `MyResource` という名前のリソースセルを生成し、 `MyCell` の `cResource` をメインルーチンとして結合しています。
app.cdl
```
celltypetMyCellType{callsResourcecResource;};celltMyCellTypeMyCell{};celltTaskMyResource{property="STANDARD";linkedResource="OMISSIBLE";eResource=MyCell.cResource;};
```
tMyCellType.c
```

```

## リファレンス

### セルタイプ
*celltype*`tResource`
リソースの生成を行うコンポーネントです。
*attr *int8_t` id`=C_EXP("$ID$")
リソースのIDの識別子を指定します。
*attr *char_t*` name`="$cell$"
リソースの名前を指定します。
*attr *char_t*` property`
リソースの種類を指定します。
`STANDARD`
標準リソース
`INTERNAL`
内部リソース
`LINKED`
リンクリソース
*attr *char_t*` linkedResource`
リンクリソースにおけるリンク先リソースを指定します。

### シグニチャ
*signature*`sResource`
リソースを操作するためのシグニチャ。
StatusType` get`(void)
リソースを獲得する。
StatusType` release`(void)
リソースを開放する。

---

Source: [[index]]
