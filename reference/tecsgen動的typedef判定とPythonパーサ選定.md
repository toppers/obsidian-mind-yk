---
date: 2026-09-26
description: "tecsgen（Ruby版）の字句解析が持つ動的typedef判定（既知シンボルをスキャナに逐次追加）をPythonで再現できるか整理。手書きレクサー/SLYは容易、Larkは要工夫、tree-sitterは外部スキャナ（DLL）が必要という結論"
tags:
  - reference
---

# tecsgen動的typedef判定とPythonパーサ選定

## Context
Ruby版[[tecsgen]]の字句解析（[[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析|内部仕様5章]]）は、`IDENTIFIER`としてマッチした語を`Namespace.is_typename?`で既知の型名かどうか都度チェックし、`TYPE_NAME`トークンへ**動的に再分類**する。型名の集合はパース中の`import_C`アクションが逐次登録していく可変状態——古典的な「C言語typedef問題」への標準解法。[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]でこの挙動をPython側でも再現できるかを検討した。

## 結論: 実装方式によって難易度が変わる

> [!success] 採用した方式（2026-09-27）
> 表の「手書きレクサー」に当たる方式を採った。Ruby 版の字句解析器を移植し、`next_token` で `typename_resolver`（P3 で `Namespace.is_typename` につなぐ）を引いて TYPE_NAME に置き換え、racc の生成済み表で駆動する → [[tecsgen-python3 構文解析方式決定]]。

| 方式 | 動的シンボル追加 | 理由 |
|---|---|---|
| **手書きレクサー（正規表現＋`re`）** | ◎ 可能・Rubyとほぼ同じ実装 | `next_token`相当の関数内で`if word in known_typenames: TYPE_NAME else: IDENTIFIER`とするだけ。可変な`set()`をパーサのアクションから追記していけばよい |
| **SLY**（PLY後継） | ◎ 可能 | トークン関数はただのPython関数なので、任意の外部状態（シンボルテーブル）を参照・更新できる。Rubyの構造をほぼそのまま移植可能 |
| **Lark**（LALR/Earley、[[reference/Racc代替のPythonパーサジェネレータ比較|関連ノート]]の第一候補） | △ 工夫が必要 | 標準の`basic`/`contextual`レクサーは事前に全トークンを分類してからパーサに渡す設計のため、パーサの意味アクションと同期して字句を書き換えるには、カスタムレクサー（`lark.lexer.Lexer`継承）か`lexer_callbacks`でIDENTIFIER後処理フックを書く必要がある。「後段でTYPE_NAMEかIDENTIFIERかを構文規則側で曖昧に受けて意味解析で判定する」設計に寄せた方が素直 |
| **tree-sitter**（[[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]]の当時の採用方針。2026-09-27 に不採用） | △〜× 標準機構では不可、要ネイティブ外部スキャナ | tree-sitterで文脈依存の字句解析をしたい場合の正式な仕組みは「external scanner」（Cで書きコンパイルする）で、これは[[reference/Racc代替のPythonパーサジェネレータ比較|前回指摘したDLL運用]]そのもの。文法定義（`grammar.js`）だけでは動的シンボルテーブル参照はできない |

## 含意（重要な論点の接続）
tree-sitterのDLL依存を避けたい動機（[[reference/Racc代替のPythonパーサジェネレータ比較]]）と、この「動的typedef判定」要求は**同じ論点で衝突する**。

- tree-sitterのままDLLなしで済ませようとすると、この字句解析の動的性は実現できない。代わりに**パーサ側で曖昧性を許容し、意味解析フェーズで型名かどうかを解決する**設計変更が必要になる。
- 一方、SLYや素朴な手書きレクサーを選べば、Ruby版の設計をほぼそのまま踏襲できる。

つまりパーサ生成系の選定は「DLL回避」と「動的typedef判定の再現しやすさ」の両軸で評価する必要があり、この2つは独立ではなく**tree-sitter一本槍だと両立しない可能性がある**という点が本ノートの核心。

## 未決定事項（TBC）
- Lark採用時、動的typedef判定をカスタムレクサーで実装するコストの見積もりは未検証
- tree-sitter継続採用の場合、意味解析フェーズでの型名解決に設計変更するコストは未検証
- [[work/active/tecsgen-python3/tecsgen-plugins-python3/tecsgen-plugins-python3|tecsgen-plugins-python3]]の`CdeclExtractor`関連実装（[[TECSCDE-DT-EL実装]]、C宣言のtypedef/struct抽出）との設計整合も未確認——DT-EL版はTypeScript側でtree-sitterを使い切っており、同種の型名判定課題をどう解いたかは要調査

## Related
- [[reference/Racc代替のPythonパーサジェネレータ比較#tree-sitterのPython利用がDLLを要する具体的な仕組み（実測手順）|tree-sitterのPython利用がDLLを要する具体的な仕組み]] — `ctypes`によるネイティブ共有ライブラリロードの実測手順（本ノートの「要ネイティブ外部スキャナ」判定の裏付け）
- [[tecsgen]] — Ruby実装版
- [[work/active/tecsgen/tecsgen内部仕様 - 05 字句解析・構文解析|tecsgen内部仕様 第5章]] — Ruby版の動的typedef判定の実装詳細
- [[work/active/tecsgen-python3/tecsgen-python3|tecsgen-python3]] — Python3移植の親ノート
- [[reference/Racc代替のPythonパーサジェネレータ比較|Racc代替のPythonパーサジェネレータ比較]] — DLL回避の観点からのパーサ生成系比較（本ノートの前提）
