---
date: 2026-09-06
description: "bash（Git Bash/mintty）向けfzfシェル統合の設定手順 — fzf --bashで生成した~/.fzf.bashによるCtrl-T/Ctrl-R/Alt-C/Tab補完の有効化"
tags:
  - reference
  - cli
  - bash
---

~/.fzf.bash（= C:\Users\ykomi\.fzf.bash）を作成しました。ローカルにインストール済みのfzfバイナリが持つ組み込みコマンド fzf --bash でスクリプトを生成したので、外部からのダウンロードは行っていません。

msys64-2/git/.git_profile:287 に既にある

[ -f ~/.fzf.bash ] && source ~/.fzf.bash

がこのファイルを検知して読み込むようになるので、これで次回シェルを開いた時から有効になります。動作確認します。

  Ran 2 shell commands

__fzf_history__ 関数が正しく読み込まれていることを確認できました（Ctrl-Rの中身）。念のためキーバインドの割り当ても確認します（_log: command not found は git_profile が単体では unix/log-functions を解決できないための無関係なエラーで、通常のシェル起動時は問題ありません）。

  Searched for 2 patterns, ran 2 shell commands

Ctrl-T（fzf-file-widget）とCtrl-R（__fzf_history__）のキーバインドがスクリプト内に正しく含まれていることを確認できました（155〜183行目あたり）。

完了内容

1. fzf --bash（ローカルインストール済みfzf 0.74.3の組み込みコマンド）で bash用シェル統合スクリプトを生成
2. C:\Users\ykomi\.fzf.bash として保存（939行）
3. 既存の msys64-2/git/.git_profile:287 の

[ -f ~/.fzf.bash ] && source ~/.fzf.bash

がこのファイルを検知するようになったので、新しいbashシェルを開けば自動的に有効になります

有効になる機能

- Ctrl-T : カレントディレクトリ以下のファイルをfzfで検索し、コマンドラインに挿入
- Ctrl-R : コマンド履歴をfzfであいまい検索
- Alt-C : ディレクトリをfzfで検索して cd
- **<Tab> 補完（vim **<Tab> など）

既存の fbr / fshow / fd / fssh などの自前関数と共存します。

確認方法: 新しいターミナル（Git Bash / mintty）を開いて Ctrl-R を押し、履歴のインクリメンタル検索が起動するか試してください。

## Related
- [[fzf]]
- [[fzf-インストール状況]]
- [[fzf-PowerShell]]
