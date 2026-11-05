---
date: 2026-08-29
description: "Claude Code CLIをPowerShellスクリプトから -p(--print)非対話モードで呼び出す方法 — 変数埋め込み、--output-format json、権限モードの注意点"
tags:
  - reference
  - claude-code
---
Claude Code CLIは -p(--print)オプションを付けると非対話モードで実行でき、標準出力に結果を返してから終了します。PowerShellスクリプトから呼び出すには以下のようにします。

基本形

claude -p "このディレクトリのREADME.mdを要約して"

PowerShell変数でプロンプトを組み立てる場合

改行を含む長いプロンプトは、変数に入れてから渡すのが安全です(引用符のエスケープ事故を防げます)。

$prompt = @"
以下のファイルをレビューしてください。
- src/main.ps1
- src/utils.ps1
セキュリティ上の懸念点を箇条書きで挙げてください。
"@

claude -p $prompt

結果を変数に受け取る

$result = claude -p $prompt
Write-Output $result

出力形式を指定する(スクリプト連携向け)

--output-format json にすると、結果・セッションID・コスト等が構造化されて返るので後処理しやすくなります。

$json = claude -p $prompt --output-format json | ConvertFrom-Json
Write-Output $json.result

作業ディレクトリを指定する

Push-Location "C:\path\to\project"
try {
    claude -p "このプロジェクトのビルドエラーを直して"
} finally {
    Pop-Location
}

または --add-dir でカレントディレクトリを変えずに対象ディレクトリを追加することもできます。

モデルを指定する

claude -p $prompt --model sonnet

標準入力からプロンプトを渡す(パイプ)

Get-Content -Raw "prompt.txt" | claude -p

権限モードについて(注意)

自動実行スクリプトで確認プロンプトに毎回止められたくない場合、--permission-mode を使う方法がありますが、--dangerously-skip-permissions はサンドボックス外での破壊的操作を無条件許可してしまうため、CI等の隔離環境以外では避けるべきです。用途に応じて --allowedTools を settings.json 側で絞り込む方が安全です。

---

スクリプト全体の例(run-claude.ps1)

param(
    [Parameter(Mandatory=$true)]
    [string]$Prompt,
    [string]$WorkDir = "."
)

Push-Location $WorkDir
try {
    $json = claude -p $Prompt --output-format json | ConvertFrom-Json
    if ($json.is_error) {
        Write-Error "Claude実行エラー: $($json.result)"
        exit 1
    }
    Write-Output $json.result
} finally {
    Pop-Location
}

使い方:

.\run-claude.ps1 -Prompt "このディレクトリのファイル一覧をMarkdownで出力して" -WorkDir "C:\Users\ykomi\dotfiles\win\ps1"

必要であれば、_file_dir_list.ps1 の出力結果(CSV)を読み込んでプロンプトに埋め込むような、このリポジトリに合わせた具体的な連携スクリプトも作成できます。


## Related
- [[Claude-Code-記事索引]]
