---
date: 2026-05-05
description: "WSL2 の保守コマンド — 15日以上アクセスの無いキャッシュファイルの削除ほか"
tags:
  - reference
  - wsl2
---

# キャッシュ削除
$ sudo find ~/.cache -type f -atime +15 -delete

$ sudo find ~/.cache -type f -atime +15 -delete

$ wsl —shutdown
$ optimize-vhd -Path C:¥Users¥<自分のユーザー名>¥AppData¥Local¥Packages¥CanonicalGroupLimited.Ubuntu24.04LTS_79rhkp1fndgsc¥LocalState¥ext4.vhdx -Mode full

# Docker DesktopのDisk Imageデータ削除
## 仮想ドライブファイル(.vhd)の削除
- Docker Desktopアプリの左下：Troubleshoot選択
- Clean / Purge data
- WSL2 , Delete
## Disk Imageの移動
- Settings -> Resources -> Disk Image location 別の大容量ドライブへ移動
- デフォルト　C:\Users\<自分のユーザ名>\AppData\Local\Docker\wsl\disk
# RAM不足
- .wslconfig
	- [wsl2]
	- memory=48GB
	- swap=16GB