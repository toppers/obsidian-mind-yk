---
date: 2026-06-22
description: "PowerShell から外部ツールを呼ぶ Start-Process の書き方 — 引数の埋め込みと標準出力のリダイレクト"
tags:
  - reference
  - powershell
---

Start-Process -FilePath "mytool.exe" -ArgumentList "-i `"$InputFile`"" -RedirectStandardOutput $OutputFile -NoNewWindow -Wait


Start-Process -FilePath "mytool.exe" -ArgumentList "-i `"$InputFile`"", "-o `"$OutputFile`"" -NoNewWindow -Wait

# ==============================================================================
# 設定パラメーター
# ==============================================================================
$TargetDir  = "C:\path\to\your\directory"  # 対象ディレクトリ
$FilePattern = "*.txt"                     # 検索パターン
$NewExtension = "log"                      # 変更後の拡張子（ドット不要）
$ExePath     = "cmd.exe"                   # 実行プログラムのパス（例としてcmd）

# ==============================================================================
# 処理実行部
# ==============================================================================
# 1. 指定ディレクトリからパターンに合致するファイルを再帰的に取得
Get-ChildItem -Path $TargetDir -Filter $FilePattern -Recurse -File | ForEach-Object {
    
    # 2. 入力ファイルのフルパスを取得
    $InputFile = $_.FullName
    
    # 3. 拡張子を変更した出力ファイルのフルパスを生成
    $OutputFile = [System.IO.Path]::ChangeExtension($InputFile, $NewExtension)
    
    # 4. 指定プログラムの実行（ここでは例として /c echo で疑似処理し、結果を出力ファイルへ保存）
    # ※実際のプログラムに合わせて引数（Arguments）部分を調整してください。
    Start-Process -FilePath $ExePath -ArgumentList "/c echo Processing $InputFile", ">", "`"$OutputFile`"" -NoNewWindow -Wait
    
    Write-Host "処理完了: $InputFile -> $OutputFile"
}