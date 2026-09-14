---
date: 2026-08-19
description: "PowerShellでのgrep相当パイプライン(Select-String)の使い方メモ — Claude CodeはGrepツールを使う旨の補足付き"
tags:
  - work-note
---

❯ PowerShell で grep で"qmd" を検索した結果を、パイプラインでつないで、"index"というパターンが一致するものを取り出す方法をおしえて

PowerShellでの grep → grep パイプライン

1. PowerShell純正コマンドレット Select-String を使う方法（推奨）

PowerShellには grep に相当する Select-String（エイリアス sls）があります。これを2段階でパイプすれば、「"qmd"を含む行の中からさらに"index"を含む行」を絞り込めます。

# カレントディレクトリ配下のファイルから "qmd" を検索し、
# その結果からさらに "index" にマッチする行だけを抽出
Get-ChildItem -Recurse -File | Select-String -Pattern "qmd" | Select-String -Pattern "index"

# 拡張子を絞る場合（例: .ts ファイルのみ）
Get-ChildItem -Recurse -Include *.ts | Select-String -Pattern "qmd" | Select-String -Pattern "index"

ポイント:
- Select-String はデフォルトで大文字小文字を区別しません（区別したい場合は -CaseSensitive）
- パターンは正規表現として解釈されます。リテラル文字列として扱いたいなら -SimpleMatch を付ける
- 出力オブジェクトは MatchInfo 型ですが、2つ目の Select-String にパイプすると自動的に文字列化（ファイル名・行番号込み）されてから再マッチするので、そのまま連結できます

2. 本物の grep（GNU grep / Git Bash付属）がPATHにある場合

Windowsでも Git for Windows などで grep.exe が入っていれば、bashと同じ書き方がPowerShell上でもそのまま動きます（grep.exe は単なる実行ファイルなので | パイプは通常のプロセス間パイプとして機能します）。

grep -r "qmd" . | grep "index"

# 行番号・ファイル名付きで見たい場合
grep -rn "qmd" . | grep "index"

3. ripgrep（rg）がある場合（高速・おすすめ）

rg "qmd" | Select-String "index"
# もしくは rg 自体を2段にする
rg "qmd" . | rg "index"

4. そもそも1回のコマンドで済ませる方法（AND条件）

2段パイプではなく、「"qmd" と "index" の両方を含む行」を1回の正規表現で書くこともできます（可読性はやや落ちますが高速です）:

Get-ChildItem -Recurse -File | Select-String -Pattern "(?=.*qmd)(?=.*index)"

---

このqmdプロジェクトに当てはめる具体例（例: src/ の中で "qmd" と "index" の両方を含む行を探す）:

Get-ChildItem -Recurse -Path .\src -Include *.ts | Select-String -Pattern "qmd" | Select-String -Pattern "index"

なお、私（Claude Code）自身がコード検索する際は Select-String/grep を直接叩くのではなく専用の Grep ツールを使うようにしています。実際にこのプロジェクトで検索してほしい場合は、そのまま「〇〇を検索して」と言ってもらえれば Grep ツールで実行します。


## Related
- [[reference/Note/AI開発/Claude-Code/MCP/Search-Tool-List|Search Tool List]]
