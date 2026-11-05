---
date: 2026-10-31
description: "TOPPERS の SVN リポジトリ群（asp・asp3・fmp3・hrp3 など）を PowerShell で一括 svn update するスクリプトのメモ"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
---

# svnコマンド
```
$root = 'E:\X\mac\repos2\svn-toppers'
$dirs = 'asp','asp3','ev3rt\ev3rt','fmp','fmp3','hrmp3','hrp3','hrp3-trunk','kernel_spec','seminar','skyeye','ssp3','tethys_usb','ttsp'
foreach ($d in $dirs) {
  Write-Host "=== $d ===" -ForegroundColor Cyan
  svn update --non-interactive "$root\$d" 2>&1
}
```
## Context

## Notes

## Action Items
- [ ]

## Related
- [[tecsgen 参照リポジトリ・配布パッケージ一覧]]
