---
date: 2026-09-06
description: "PowerShellプロファイルでのfzf統合設定（PSFzfモジュール） — Ctrl+T/Ctrl+R/Tab/Alt+Cのキーバインド、自前関数xcd/xedit"
tags:
  - reference
  - cli
  - powershell
---

PowerShellプロファイルでのfzf設定

PSFzf モジュール（バージョン 2.7.12、Scoopでインストール済み: C:\Users\ykomi\scoop\modules\PSFzf）を使ってfzf統合を組んでいます。

if (Get-Module -ListAvailable -Name PSFzf) {
    Import-Module PSFzf
    Set-PsFzfOption -PSReadlineChordProvider Ctrl+t -PSReadlineChordReverseHistory Ctrl+r
    $commandOverride = [ScriptBlock]{ param($Location) Write-Host $Location }
    Set-PsFzfOption -AltCCommand $commandOverride
    Set-PSReadLineKeyHandler -Key Tab -ScriptBlock { Invoke-FzfTabCompletion }
}

内容:

┌────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  設定  │                                                  効果                                                   │
├────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Ctrl+T │ PSReadlineChordProvider —                                                                               │
│        │ カレントディレクトリ以下のファイル／ディレクトリをfzfで検索し、コマンドラインに挿入                     │
├────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Ctrl+R │ PSReadlineChordReverseHistory — コマンド履歴をfzfであいまい検索（bashのCtrl-Rと同等）                   │
├────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Alt+C  │ 通常は選択したディレクトリに cd するが、ここでは Write-Host $Location                                   │
│        │ にオーバーライドされていて、実際には移動せず選択したパスを表示するだけになっている点に注意              │
├────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Tab    │ Invoke-FzfTabCompletion — 通常のPSReadLineタブ補完をfzfベースのあいまい補完に置き換え                   │
└────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────┘

加えて、このプロファイル内には xcd / xedit という自前関数もあります：

function xcd {
    Get-ChildItem . -Recurse -Attributes Directory | Invoke-Fzf | Set-Location
}
function xedit {
    Get-ChildItem . -Recurse -Attributes !Directory | Invoke-Fzf | % { notepad $_ }
}

Invoke-Fzf（PSFzfのコア関数）でディレクトリ／ファイルを選んで、それぞれ移動・notepadで開く独自コマンドです。

まとめると

- PowerShell側: PSFzfモジュール経由でCtrl+T/Ctrl+R/Tabのfzf統合が有効（Alt+Cは意図的にcdしない挙動に変更済み）
- bash側（msys64-2 .git_profile）: ~/.fzf.bash を読み込む行はあるが、そのファイルが存在しないためkey-bindingsは未設定。ただし fbr/fshow/fd/fssh などの自前fzf関数は使える

## Related
- [[fzf]]
- [[fzf-インストール状況]]
- [[fzf-bashrc]]
