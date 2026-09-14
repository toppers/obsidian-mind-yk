---
date: 2026-09-06
description: "fzf（あいまい検索CLI）の基本的な使い方まとめ — パイプ連携、シェル統合キーバインド、補完機能、検索構文、Windows/MSYS2向け活用例"
tags:
  - reference
  - cli
---
fzf（fuzzy finder）は汎用のあいまい検索ツールです。基本的な使い方をまとめます。

基本

fzf
だけで実行すると、カレントディレクトリ以下のファイル一覧がリスト表示され、インクリメンタル検索できます。矢印キーやCtrl-j/Ctrl-kで選択、Enterで確定、選んだ結果が標準出力に渡されます。

パイプと組み合わせる

fzfは「標準入力のリストを絞り込んで選んだ行を標準出力に返す」フィルタとして使うのが基本です。

# コマンド履歴から選んで実行
history | fzf

# git のブランチを選んでチェックアウト
git branch | fzf | xargs git checkout

# プロセスを選んで kill
ps aux | fzf | awk '{print $2}' | xargs kill

シェル統合（bash/zsh）

fzfをインストールすると使えるキーバインド（.bashrcや.zshrcで読み込み設定している場合）:

- Ctrl-R : コマンド履歴をあいまい検索
- Ctrl-T : カレントディレクトリ以下のファイルをあいまい検索し、コマンドラインに挿入
- Alt-C : ディレクトリをあいまい検索して cd

# .bashrc / .zshrc に追記（インストール方法による）
source /usr/share/fzf/key-bindings.bash
source /usr/share/fzf/completion.bash

補完機能

** を使うと対象コマンドの引数でfzf補完が使えます。

vim **<Tab>      # ファイルをあいまい検索して選択
cd **<Tab>       # ディレクトリを検索
kill **<Tab>     # プロセスを検索
ssh **<Tab>      # known_hosts から検索

よく使うオプション

fzf --height 40%          # 画面の下40%に表示（全画面にしない）
fzf --reverse             # リストを上から表示
fzf --preview 'cat {}'    # 選択項目のプレビュー表示
fzf -m                    # 複数選択（Tabでマーク）
fzf --query "foo"         # 初期検索文字列を指定

検索構文（あいまい検索の絞り込み）

- foo bar : fooとbar両方を含む（AND）
- foo | bar : どちらか（OR）
- 'foo : 完全一致（先頭に'）
- ^foo : 先頭一致
- foo$ : 末尾一致
- !foo : fooを含まない（否定）

実用例（このdotfiles環境向け）

Windows/MSYS2環境なら、Git Bashやmintty上で使うことが多いはずです。よくある活用パターン：

# ghqで管理しているリポジトリに fzf で移動
cd $(ghq list -p | fzf)

# git log をあいまい検索してコミットを確認
git log --oneline | fzf --preview 'git show --color=always {1}'

# 環境変数一覧から選んでコピー
env | fzf

インストール状況を確認したい場合は which fzf や fzf --version で確認できます。もしこの環境で未導入なら、win/bin1/ や msys64-2/bin1/ あたりにfzf連携のラッパースクリプトを追加する構成が、このdotfilesの流儀に合いそうです。

# [[fzf-インストール状況]]

## Related
- [[fzf-インストール状況]]
- [[fzf-PowerShell]]
- [[fzf-bashrc]]
