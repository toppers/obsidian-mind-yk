---
date: 2026-05-12
name: project-todoa
description: E:\Ccur\webapp\todoa の TODOアプリ — Next.js 16 + Prisma 6 + SQLite 構成
tags:
  - reference
  - project
  - nextjs
metadata: 
  node_type: memory
  type: project
  originSessionId: b1d245eb-b617-4322-aee7-d47735d43d49
---

Next.js 16.2.6 (App Router) + React 19 + Tailwind CSS v4 + Prisma 6.19.3 + SQLite で構築したTODOアプリ。

**Why:** ゼロから新規作成。2026-05-12 に初期実装完了。

**How to apply:** このプロジェクトでコードを変更する際は以下の構成を念頭に置く。

## 主要ファイル
- `app/page.tsx` — Server Component。`searchParams: Promise<{filter?:string}>` を await してフィルタ処理
- `app/actions.ts` — Server Actions (createTodo, toggleTodo, deleteTodo, updateTodo, clearCompleted, getCounts)
- `lib/db.ts` — Prisma Client シングルトン
- `prisma/schema.prisma` — Todo モデル (id, title, completed, order, createdAt)
- `components/TodoForm.tsx` — Client Component, useActionState + useFormStatus
- `components/TodoItem.tsx` — Client Component, useTransition for async actions
- `components/FilterBar.tsx` — Client Component, useSearchParams (Suspenseでwrap必須)
- `components/TodoList.tsx` — Server Component

## 注意点
- Prisma 7 は SQLite の url 設定が破壊的変更のため、**Prisma 6** を使用
- Tailwind v4 は `@import "tailwindcss"` (従来の @tailwind ディレクティブなし)
- Next.js 15+ では searchParams/params は Promise 型、await が必要
- useActionState は react (react-dom ではない) からインポート (React 19)
- E: ドライブがネットワークドライブのため初回コンパイルは遅い(~30s)

## Dev server
`npm run dev` → http://localhost:3000
