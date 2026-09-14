---
date: 2026-08-24
description: "SVN文字化けコミットメッセージの文字コード指定再取得・XML整形表示コマンド控え"
tags:
  - reference
  - svn
  - tecsgen
---

一部の日本語コミットメッセージが文字化けしています。文字コードを指定して再取得します。

  Ran 3 shell commands

XMLはUTF-8で正しく取得できました。これをPythonで整形して読みやすい形式で表示します。

  Ran 2 shell commands

❯ LANG=ja_JP.UTF-8 svn log -r 3086:3250 https://dev.toppers.jp/svn/tecs/toppers/tecsgen/trunk

  Ran 4 shell commands

XMLアプローチ(既に正しいUTF-8で取得済み)でパースし直します。

  Read 1 file, ran 1 shell command

日本語コミットメッセージも正しく文字化けせずに取得できました。r3086〜r3250 の51件のログです（コンソール出力は文字コードの都合で日本語部分が化けていたため、svn log --xml で取得しUTF-8に整形しています）。

- r3086 (2019-06-13): release 1.7.0
- r3088–3098: 一時コミット、NotifierPlugin.rb更新、MANIFEST更新
- r3141 (2020-04-08): ClassPlugin.rb をリリースに追加
- r3155–3161: release 1.8.RC1、重複ファイル名を削除
- r3164 (2020-07-30): FMPClassManager.rb を追加
- r3165–3202: release 1.8.RC2〜RC7（複数回のRC7再リリース含む）
- r3203: 一時コミット
- r3207–3211: release 1.8.RC8
- r3214 (2021-05-05): namespace対応済箇所の 'mikan' を削除
- r3215–3216: delete class_free / delete restrict_class
- r3218–3225: release 1.8.RC9〜RC10
- r3241–3250: release 1.8.RC11〜1.8.0（最終リリース、r3249/3250）

r3086が1.7.0リリース、r3249/3250が1.8.0リリースなので、この範囲はおおむね1.7.0から1.8.0への開発期間全体（2019年6月〜2022年1月）に相当します

tecsgen-1.7.0 3086
tecsgen-1.8.0 3250
tecsgen-1.9.0 3280
tecsgen-1.9.1 3302

❯ LANG=ja_JP.UTF-8 svn log -r 3250:3303 https://dev.toppers.jp/svn/tecs/toppers/tecsgen/trunk

前回と同様、コンソール文字化けを避けるため XML 経由で取得します。

  Read 1 file, ran 2 shell commands

r3250〜r3303の範囲、18件のログです。

- r3250–3251 (2022-01): release 1.8.0
- r3262 (2022-06-09): ファイルを追加
- r3263–3272 (2022-12〜2023-07): release 1.9.0Beta1〜Beta6（段階的なベータリリース）
- r3275 (2024-01-04): changes_TECS_V1.9.pptx を追加
- r3276 (2024-01-04): tecsgen V1.9.0RC1、MANIFEST を調整
- r3277 (2024-03-24): update doc
- r3280 (2025-07-14): tecsgen V1.9.0 リリース版のチェックイン
- r3302 (2026-06-07): release 1.9.1

r3250が1.8.0、r3280が1.9.0正式リリース、r3302が1.9.1リリースで、この範囲は1.8.0から1.9.1への開発期間（2022年1月〜2026年6月）に相当します。なお指定範囲の上限3303には到達しておらず、r3302が最終リビジョンでした。

## Related
- [[svn-diff]]
