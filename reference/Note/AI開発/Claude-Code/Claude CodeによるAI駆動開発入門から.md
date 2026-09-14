---
date: 2026-05-22
description: "書籍「Claude CodeによるAI駆動開発入門」(平川知秀・技術評論社)を追った実演ログ。ultrathink 付きの依頼から Plan モードに入り、Next.js App Router + Prisma/SQLite の TODO アプリ計画が生成されるまで"
tags:
  - reference
  - claude
  - claude-code
  - plan-mode
---

「Claude CodeによるAI駆動開発入門-平川知秀-技術評論社」

❯ TODOアプリをNext.js(App Router)を使用して作って ultrathink

● Planモードで設計を確認してから実装します。

  Searched for 1 pattern, listed 1 directory (ctrl+o to expand)

● Entered plan mode
  Claude is now exploring and designing an implementation approach.

● User answered Claude's questions:
  ⎿  · データの永続化方法を選んでください → Prisma + SQLite（推奨）
     · TODOの機能範囲を選んでください → 標準（推奨）

● 選択を確認しました。プラン文書を作成します。

● Updated plan
  ⎿  /plan to preview
  
   Plan: Next.js App Router TODOアプリ

 Context

 空のE:\Ccur\webapp\todoaディレクトリにTODOアプリをゼロから構築。
 Next.js 15 App Router + Server Actions + Prisma/SQLite で永続化。

 Stack

 - Next.js 15 (App Router)
 - TypeScript
 - Tailwind CSS v3
 - Prisma 6 + SQLite (ローカルDB)
 - Server Actions (mutations)

 機能

 - TODO追加 / 削除 / 完了トグル
 - タイトルインライン編集（ダブルクリック）
 - All / Active / Completed フィルタ（searchParams）
 - 「完了済みを削除」ボタン
 - 残件数表示

 ---
 ファイル構成

 todoa/
 ├── prisma/
 │   └── schema.prisma          ← Todoモデル (id, title, completed, order, createdAt)
 ├── lib/
 │   └── db.ts                  ← Prisma Client シングルトン
 ├── app/
 │   ├── layout.tsx             ← Root layout (metadata, Inter font)
 │   ├── globals.css            ← Tailwind base + カスタムCSS
 │   ├── page.tsx               ← Server Component: fetch + render
 │   └── actions.ts             ← Server Actions
 └── components/
     ├── TodoForm.tsx            ← Client: 入力フォーム
     ├── TodoList.tsx            ← Server: リスト描画
     ├── TodoItem.tsx            ← Client: toggle / edit / delete
     └── FilterBar.tsx          ← Client: フィルタナビ

 ---
 Data Model

 model Todo {
   id        String   @id @default(cuid())
   title     String
   completed Boolean  @default(false)
   order     Int      @default(0)
   createdAt DateTime @default(now())
 }

 ---
 Server Actions (app/actions.ts)

 ┌───────────────────────────┬─────────────────────────────────────────┐
 │          Action           │                  処理                   │
 ├───────────────────────────┼─────────────────────────────────────────┤
 │ getTodos(filter)          │ all/active/completed でフィルタして返す │
 ├───────────────────────────┼─────────────────────────────────────────┤
 │ createTodo(formData)      │ 新規作成, revalidatePath('/')           │
 ├───────────────────────────┼─────────────────────────────────────────┤
 │ toggleTodo(id, completed) │ 完了状態を反転                          │
 ├───────────────────────────┼─────────────────────────────────────────┤
 │ deleteTodo(id)            │ 削除                                    │
 ├───────────────────────────┼─────────────────────────────────────────┤
 │ updateTodo(id, title)     │ タイトル更新                            │
 ├───────────────────────────┼─────────────────────────────────────────┤
 │ clearCompleted()          │ 完了済み一括削除                        │
 └───────────────────────────┴─────────────────────────────────────────┘

 ---
 Component 設計

 app/page.tsx (Server Component)

 - searchParams.filter を読みフィルタ適用
 - getTodos(filter) でDB取得
 - 全コンポーネントを組み合わせてレンダリング

 components/TodoForm.tsx (Client Component)

 - 制御されたinput
 - Server Action createTodo を直接バインド
 - useFormStatus でsubmit中は無効化

 components/TodoItem.tsx (Client Component)

 - checkbox → toggleTodo 呼び出し
 - ダブルクリック → inline edit state → blur/Enter で updateTodo
 - 削除ボタン → deleteTodo 呼び出し
 - 完了時: テキストに打ち消し線 + グレーアウト

 components/FilterBar.tsx (Client Component)

 - useSearchParams + usePathname でアクティブタブ判定
 - <Link> で ?filter=all/active/completed に遷移

 components/TodoList.tsx (Server Component)

 - todos を受け取り TodoItem を列挙
 - 空の場合はemptyメッセージを表示

 ---
 実装手順

 1. npx create-next-app@latest . --typescript --tailwind --eslint --app --no-git --no-src-dir --import-alias "@/*"
 --yes
 2. npm install @prisma/client + npm install -D prisma

! git init
  ⎿  Initialized empty Git repository in E:/Ccur/webapp/todoa/.git/

❯ TODOアプリをNext.js(App Router)を使用して作って ultrathink

● Planモードで設計を確認してから実装します。

  Searched for 1 pattern, listed 1 directory (ctrl+o to expand)

● Entered plan mode
  Claude is now exploring and designing an implementation approach.

● User answered Claude's questions:
  ⎿  · データの永続化方法を選んでください → Prisma + SQLite（推奨）
     · TODOの機能範囲を選んでください → 標準（推奨）

● 選択を確認しました。プラン文書を作成します。

● Updated plan
  ⎿  /plan to preview

● User approved Claude's plan
  ⎿  Plan saved to: C:\Users\ykomi\.claude\plans\quirky-crunching-key.md · /plan to edit
     Plan: Next.js App Router TODOアプリ

     Context

     空のE:\Ccur\webapp\todoaディレクトリにTODOアプリをゼロから構築。
     Next.js 15 App Router + Server Actions + Prisma/SQLite で永続化。

     Stack

     - Next.js 15 (App Router)
     - TypeScript
     - Tailwind CSS v3
     - Prisma 6 + SQLite (ローカルDB)
     - Server Actions (mutations)

     機能

     - TODO追加 / 削除 / 完了トグル
     - タイトルインライン編集（ダブルクリック）
     - All / Active / Completed フィルタ（searchParams）
     - 「完了済みを削除」ボタン
     - 残件数表示

     ---
     ファイル構成

     todoa/
     ├── prisma/
     │   └── schema.prisma          ← Todoモデル (id, title, completed, order, createdAt)
     ├── lib/
     │   └── db.ts                  ← Prisma Client シングルトン
     ├── app/
     │   ├── layout.tsx             ← Root layout (metadata, Inter font)
     │   ├── globals.css            ← Tailwind base + カスタムCSS
     │   ├── page.tsx               ← Server Component: fetch + render
     │   └── actions.ts             ← Server Actions
     └── components/
         ├── TodoForm.tsx            ← Client: 入力フォーム
         ├── TodoList.tsx            ← Server: リスト描画
         ├── TodoItem.tsx            ← Client: toggle / edit / delete
         └── FilterBar.tsx          ← Client: フィルタナビ

     ---
     Data Model

     model Todo {
       id        String   @id @default(cuid())
       title     String
       completed Boolean  @default(false)
       order     Int      @default(0)
       createdAt DateTime @default(now())
     }

     ---
     Server Actions (app/actions.ts)

     ┌───────────────────────────┬─────────────────────────────────────────┐
     │          Action           │                  処理                   │
     ├───────────────────────────┼─────────────────────────────────────────┤
     │ getTodos(filter)          │ all/active/completed でフィルタして返す │
     ├───────────────────────────┼─────────────────────────────────────────┤
     │ createTodo(formData)      │ 新規作成, revalidatePath('/')           │
     ├───────────────────────────┼─────────────────────────────────────────┤
     │ toggleTodo(id, completed) │ 完了状態を反転                          │
     ├───────────────────────────┼─────────────────────────────────────────┤
     │ deleteTodo(id)            │ 削除                                    │
     ├───────────────────────────┼─────────────────────────────────────────┤
     │ updateTodo(id, title)     │ タイトル更新                            │
     ├───────────────────────────┼─────────────────────────────────────────┤
     │ clearCompleted()          │ 完了済み一括削除                        │
     └───────────────────────────┴─────────────────────────────────────────┘

     ---
     Component 設計

     app/page.tsx (Server Component)

     - searchParams.filter を読みフィルタ適用
     - getTodos(filter) でDB取得
     - 全コンポーネントを組み合わせてレンダリング

     components/TodoForm.tsx (Client Component)

     - 制御されたinput
     - Server Action createTodo を直接バインド
     - useFormStatus でsubmit中は無効化

     components/TodoItem.tsx (Client Component)

     - checkbox → toggleTodo 呼び出し
     - ダブルクリック → inline edit state → blur/Enter で updateTodo
     - 削除ボタン → deleteTodo 呼び出し
     - 完了時: テキストに打ち消し線 + グレーアウト

     components/FilterBar.tsx (Client Component)

     - useSearchParams + usePathname でアクティブタブ判定
     - <Link> で ?filter=all/active/completed に遷移

     components/TodoList.tsx (Server Component)

     - todos を受け取り TodoItem を列挙
     - 空の場合はemptyメッセージを表示

     ---
     実装手順

     1. npx create-next-app@latest . --typescript --tailwind --eslint --app --no-git --no-src-dir --import-alias "@/*"
     --yes
     2. npm install @prisma/client + npm install -D prisma
     3. npx prisma init --datasource-provider sqlite
     4. prisma/schema.prisma にTodoモデルを記述
     5. npx prisma db push (SQLiteファイル生成 + テーブル作成)
     6. lib/db.ts (Prisma singleton)
     7. app/actions.ts (Server Actions)
     8. 各Componentを実装
     9. app/page.tsx で組み立て
     10. npm run dev で動作確認

     ---
     検証

     - npm run dev → http://localhost:3000
     - TODO追加 → DB反映確認 (npx prisma studio)
     - 完了トグル → Active/Completedフィルタで件数変化を確認
     - インライン編集 (ダブルクリック→Enter)
     - 「完了済みを削除」ボタン動作
     - npm run build でビルドエラーなし確認

● 実装を開始します。まずNext.jsのスキャフォルドを作成します。

● PowerShell(Set-Location E:\Ccur\webapp\todoa && npx create-next-app@latest . --typescript --tailwind --eslint --app
            --no-git --no-src-dir --import-alias "@/*" --yes 2>&1)
  ⎿  Waiting…
─────────────────────────────────────────────────────────────────────────────────────────────── nextjs-todo-app-setup ──

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 PowerShell command

   Set-Location E:\Ccur\webapp\todoa && npx create-next-app@latest . --typescript --tailwind --eslint --app --no-git
   --no-src-dir --import-alias "@/*" --yes 2>&1
   Scaffold Next.js app in current directory

 Compound command contains cd with path operation — manual approval required to prevent path resolution bypass

## Related

- [[Claude-Code-教科書]]
- [[Claude Codeの使い方]]

