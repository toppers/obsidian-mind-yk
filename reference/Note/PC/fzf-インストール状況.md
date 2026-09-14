---
date: 2026-09-06
description: "この機器（msys64-2）でのfzfインストール状況控え — Scoop導入版0.74.3、シェル統合未設定、fbr/fshow/fd/fsshなど自前fzf関数の一覧"
tags:
  - reference
  - cli
---

fzfはインストール済みです。

/c/Users/ykomi/scoop/shims/fzf

Scoop経由でインストールされています（scoop install fzf）。バージョンを確認する場合:

  Ran 1 shell command

バージョンは 0.74.3 です。

このdotfiles環境（msys64-2）でシェル統合（Ctrl-R / Ctrl-T / Alt-C）が設定済みかどうか確認したい場合は、.bashrcやsetting.d/settingにfzfのkey-bindings読み込みがあるか調べられます。必要であれば見てみましょうか？

✻ Churned for 24s · done 10:16

❯ 調べて

  Searched for 4 patterns, read 2 files, listed 2 directories, ran 2 shell commands

調べた結果をまとめます。

fzf導入・統合の状況

インストール: Scoopで導入済み（C:\Users\ykomi\scoop\apps\fzf\0.74.3）。ただしこのScoop版フォルダには fzf.exe と install.json / manifest.json しかなく、公式のkey-bindings/completionスクリプトは同梱されていません（Git管理下のfzfリポジトリをインストールした場合と違い、Scoopパッケージはシェル統合ファイルを含まない）。

シェル統合の設定: msys64-2/git/.git_profile:287 に

[ -f ~/.fzf.bash ] && source ~/.fzf.bash

という行があり、~/.fzf.bash が存在すれば読み込む仕組みは用意されています。しかし実際に確認したところ ~/.fzf.bash は存在しません。つまり Ctrl-R（履歴検索）/ Ctrl-T（ファイル検索）/ Alt-C（cd）のキーバインドは現状有効になっていません。

独自のfzfラッパー関数（同じく msys64-2/git/.git_profile 内、220〜287行目）は使えます:

┌───────────────────────────┬─────────────────────────────────────────────┐
│           関数            │                    用途                     │
├───────────────────────────┼─────────────────────────────────────────────┤
│ fbr                       │ ローカルブランチをfzfで選んでチェックアウト │
├───────────────────────────┼─────────────────────────────────────────────┤
│ （233行目付近の無名関数） │ 全ブランチ（remote含む）をfzf-tmuxで選択    │
├───────────────────────────┼─────────────────────────────────────────────┤
│ fshow                     │ git log --graph をfzfでインクリメンタル検索 │
├───────────────────────────┼─────────────────────────────────────────────┤
│ fd                        │ ディレクトリをfzfで検索して移動用に返す     │
├───────────────────────────┼─────────────────────────────────────────────┤
│ （265行目）               │ git worktree list をfzfで選択               │
├───────────────────────────┼─────────────────────────────────────────────┤
│ fssh                      │ ~/.ssh/config のHostをfzfで選んでSSH接続    │
└───────────────────────────┴─────────────────────────────────────────────┘

その他、関連スクリプト:
- win/ps1/fzfps1.ps1（今いるディレクトリ）: 同ディレクトリの *.ps1 をfzfで選ぶPowerShellラッパー
- unix/bin2/fzf1: wsl-ubuntu用、dirlist.txt からディレクトリ選択してcd
- msys64/bin1/fzfx: win/bat1/*.bat をfzfで選んで実行

足りないもの: key-bindings/completionによる Ctrl-R / Ctrl-T / Alt-C が未設定です。有効化したい場合、公式fzfのgit repoから shell/key-bindings.bash などを取得して ~/.fzf.bash として設置するか、msys64-2/git/.git_profile の該当行を対応するパスに書き換える必要があります。設定してほしければ言ってください。
## Related
- [[fzf]]
- [[fzf-PowerShell]]
- [[fzf-bashrc]]
