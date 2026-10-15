---
date: 2026-05-12
name: project-todo-app
description: E:\Ccur\webapp\todo に作成したTODOウェブアプリの技術スタックと構成
tags:
  - reference
  - project
  - react
metadata: 
  node_type: memory
  type: project
  originSessionId: 0667b3b3-4962-4343-ad6a-ba4ac55145b5
---

React 18 + Vite + Tailwind CSS v3 でTODOアプリを構築。localStorageで永続化。

**Why:** ユーザーのwebapp/todoディレクトリ向けに新規作成。バックエンド不要のシンプル構成を選択。

**How to apply:** 追加機能（フィルタリング、優先度、期限等）を実装する場合はこの技術スタックを踏襲する。

## 構成
- `src/App.jsx` — todos state + localStorage同期 + CRUD関数
- `src/components/TodoInput.jsx` — 入力フォーム
- `src/components/TodoList.jsx` — リスト表示
- `src/components/TodoItem.jsx` — 1件分（チェック・削除）

## 起動
```
npm run dev  # http://localhost:5173/
```
