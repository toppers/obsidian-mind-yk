---
date: 2026-05-14
description: "Simon Willison の記事「Using Claude Code: The Unreasonable Effectiveness of HTML」と Thariq Shihipar の X ポストへのリンク"
tags:
  - reference
  - claude-code
---

Thariq Shihipar
[Using Claude Code: The Unreasonable Effectiveness of HTML](https://simonwillison.net/2026/May/8/unreasonable-effectiveness-of-html/)

[XユーザーのThariqさん: 「Using Claude Code: The Unreasonable Effectiveness of HTML」 / X](https://x.com/trq212/status/2052809885763747935)

「PR を HTML artifact としてレビューして。  
diff を表示し、重要度ごとに色分けし、余白に注釈を付けて」

# 実際の利用例

記事内では：

- Linux exploit 解説
- PR レビュー
- 技術文書
- コード解析
- 可視化レポート

などを HTML artifact として生成した例が紹介されています。

特に：

```
curl https://example.com | llm -m gpt-5.5 \  -s "Explain this in HTML with interactive UI"
```

のような使い方が紹介されています。
## 「LLM の出力を UI として扱う」

という思想が重要です。

# プログラマー視点で重要な点

特に実務ではかなり応用できます。

例えば：

## コードレビュー

HTML + CSS + JS で：

- 差分
- blame
- complexity
- security issue
- dependency graph

をまとめて可視化できる。

## ログ解析

AI に：

```
ログを HTML dashboard 化して
```

と指示すると、

- エラー分類
- 時系列
- フィルタ
- collapsible trace

など付きで出力可能。

## ドキュメント生成

単なる Markdown README ではなく：

- searchable
- interactive
- diagram-rich

な docs を AI が直接生成可能。