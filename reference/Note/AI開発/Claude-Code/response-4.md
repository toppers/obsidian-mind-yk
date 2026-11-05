---
date: 2026-08-04
description: "WSL2 での Chromium 起動コマンドとオプション — --no-sandbox / --disable-gpu / --user-data-dir の使い分けと、起動しない場合のよくあるエラーと対処表"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

```bash
chromium --no-sandbox
```

これが WSL2 での基本的な起動コマンドです。追加で便利なオプション：

```bash
# バックグラウンドで起動（ターミナルをブロックしない）
chromium --no-sandbox &

# プロファイルディレクトリを指定（権限エラー回避）
chromium --no-sandbox --user-data-dir=/home/$USER/.config/chromium

# GPU アクセラレーション無効（描画問題が出る場合）
chromium --no-sandbox --disable-gpu

# まとめて指定
chromium --no-sandbox --disable-gpu --user-data-dir=/home/$USER/.config/chromium &
```

起動しない場合のよくあるエラーと対処：

| エラー                                 | 対処                                             |
| -------------------------------------- | ------------------------------------------------ |
| `cannot open display`                  | `echo $DISPLAY` を確認、WSLg が有効か確認        |
| `Running as root without --no-sandbox` | `--no-sandbox` を追加                            |
| 画面が真っ黒                           | `--disable-gpu` を追加                           |
| `libGL error`                          | `sudo apt install -y mesa-utils libgl1-mesa-glx` |

## Related

- [[response-0]] — WSL2 への Chromium インストール手順
- [[response-5]] — `cannot open display` の詳細な切り分け手順