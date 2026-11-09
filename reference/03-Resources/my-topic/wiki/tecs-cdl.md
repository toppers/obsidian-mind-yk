---
date: 2026-05-31
tags: [tecs, cdl, dsl]
type: concept
status: active
description: "[[tecs-overview]]のコンポーネントを記述するためのドメイン固有言語。拡張子 .cdl、C言語文法と親和性あり。"
---

# TECS CDL (コンポーネント記述言語)

TECS CDL（Component Description Language）は、TECSコンポーネントを記述するためのドメイン固有言語です。

## 特徴

- 拡張子: `.cdl`
- 文字コード: UTF-8（7bit ASCII互換文字コードも可）
- C言語文法と親和性のある記述形式

## 記述内容（記述順）

1. 前置部 — `import` / `import_C` 等
2. [[tecs-signature]] — シグニチャ記述
3. [[tecs-celltype]] — セルタイプ記述
4. [[tecs-composite-celltype]] — 複合セルタイプ記述
5. [[tecs-cell]] — 組上げ記述（セル記述）
6. [[tecs-namespace]] — ネームスペース記述
7. [[tecs-region]] — リージョン記述

## ツール

- [[wiki-tecsgen]] — CDLファイルを入力としてインタフェースコードを生成

## Counter-Arguments and Gaps

- sjis等のマルチバイト文字コードは動作保証外
- 未記載事項が存在する（CDLref_undoc参照）
