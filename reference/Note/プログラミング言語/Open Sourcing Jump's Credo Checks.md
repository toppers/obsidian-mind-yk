---
title: "Open Sourcing Jump's Credo Checks"
source: "https://tylerayoung.com/2026/04/13/credo-checks/?utm_medium=email&utm_source=elixir-radar"
author:
  - "[[タイラー・ヤング]]"
published:
created: 2026-07-31
description: "Jump open-sources jump_credo_checks — 14 Credo static-analysis checks for Elixir that run on every PR and block merges. Walks through the author's favorites: always-true LiveView assertions, function-level else, and other defects that escape code review."
tags:
  - "clippings"
---
[カンファレンス講演](https://tylerayoung.com/category/conference-talks/) [プログラミング](https://tylerayoung.com/category/programming/) [作業](https://tylerayoung.com/category/work/) [について](https://tylerayoung.com/about/) [すべてのカテゴリ](https://tylerayoung.com/categories/)

## Open Sourcing Jumpの信条チェック

[プログラミング](https://tylerayoung.com/category/programming) [関数型プログラミング](https://tylerayoung.com/category/functional-programming) [エリクサー](https://tylerayoung.com/category/elixir)

Jumpの開発者エクスペリエンスチームにおける私の仕事の大部分は、コード品質の向上に重点を置いており、Credo¹チェックの作成は [その](#1-what-is-credo) 重要な部分を占めています。

本日、Jump は、コミュニティの他のメンバーにも役立つ可能性のある、社内で構築したすべての Credo チェックをオープンソース化します。Credo には、 [`Jump.CredoChecks`](https://hex.pm/packages/jump_credo_checks/) 本番コードとテストの両方で発生する可能性のある問題とその修正方法に関する、非常に独断的な (こんにちは、私に会ったことありますか? 👋) 知識が数多く含まれています。これらのチェック (社内デザインシステムから適切な UI コンポーネントを使用していることを確認するなど、社内でのみ関心のある多くのチェックに加えて) は、すべての PR で実行され、いずれかが失敗した場合はマージがブロックされます。

初回リリースには14項目のチェック項目がありますが、その中でも特に気に入っている項目をいくつかご紹介しましょう。（もちろん、 残りの項目については [詳細なドキュメントを参照してください。）](https://hexdocs.pm/jump_credo_checks/)

## 私のお気に入り

### AssertElementSelectorCanNeverFail

このコードはコードレビューで何度も見落とされてきました。

```elixir
test "my LiveView", %{conn: conn} do
  {:ok, view, _html} = live(conn, ~p"/")
  assert element(view, "button", "Log in")
end
```

そこでの問題は、それが *常に* `LiveViewTest.element/{2,3}` 真である ということです。要素が欠落している場合、空のリストが返されます。代わりに、を使用する必要があります 。 `LiveViewTest.has_element?/{2,3}`

### AvoidFunctionLevelElse

あるリファクタリングで、偶然にもこうなってしまった。

```elixir
def my_fun(arg) do
  with {:ok, whatever} <- other_fun(arg),
       ... do
     whatever
  else
    {:error, reason} -> handle_error(reason)
  end
end
```

…これを：

```elixir
def my_fun(arg) do
  other_fun(arg)
else
  {:error, reason} -> handle_error(reason)
end
```

`else` 関数の最上位レベルに が あることを知っていたか? 私は知りませんでした。これは最上位レベルの を補完するために存在し `rescue` 、関数が例外を発生させ *ない* `other_fun/1` 場合にのみ実行されます。ただし、上記の例では、関数がタプルを返さないとき`:error` (例外が発生するとき) はいつでもクラッシュします `TryClauseError` 。

それは法律的な構文ではあるが、実際には *ほとんど* 役に立たない。

### DoctestIExExamples

`iex>` や `@doc` でそれを 見ると、コードが実際にテストされており、構造化されていない例よりも信頼性が高いと確信できます。この Credo チェックは、対応するテストファイルが モジュールに対して `@moduledoc` 実際に を呼び出すことを確認することで、それを保証します。 `doctest`

### LiveViewFormCanBeRehydrated

`phx-change` LiveViewのフォーム状態回復に関するルールは、シンプルであると同時に、非常に簡単にミスを犯してしまう可能性があります。このルールは、フォーム回復に必要な前提条件であるIDとハンドラーが 少なくとも満たされていることを保証することで、ささやかな保護層を追加します。

### TopLevelAliasImportRequire

LLM は、関数の本体に 、 、 および ステートメントを挿入するのが大好きです。これにより、それらがモジュールのルートにのみ存在することが保証さ `alias` れ `import` ます 。 `require`

### VacuousTest

実際の運用コードを実行していないと思われるテストについて警告します。LLM（ライフサイクルマネージャー）は、特にテスト対象が難しい場合に、このようなテストを生成する傾向があります。

### WeakAssertion

「ああ、よかった」という主張を見ると心が痛む `refute is_nil(...)` 。「無限にある可能性のある値のうち、1つを排除できた」と思う。

似たような逸品: `assert is_binary(...)` 。これは空文字列でしょうか? 何か特別な内容があるのでしょうか?この文字列については、存在するということ以外 *何* も言えないのでしょうか? 本当に?!

このチェックは、より適切な主張を促します。読者に 値 *について何か説明してください！*

## ご意見をお聞かせください

チェック機能を試してみたら、 [BlueSky](https://bsky.app/profile/tylerayoung.com) か [Mastodonで](https://fosstodon.org/@tylerayoung) 感想を聞かせてください。良い点、悪い点、改善点など、何でも構いません。私たちのチームにとって役立ったように、皆さんにとっても役立つことを願っていますが、もしそうでない場合は、どのように改善できるかぜひ教えてください。

### 1\. クレドとは何ですか？

[Credoは](https://github.com/rrrene/credo) 、Elixirにおける静的解析を行うための最も人気のあるツールです。

## Related

- [[プログラミング言語-記事索引]]
