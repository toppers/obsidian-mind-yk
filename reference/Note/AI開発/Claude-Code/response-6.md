---
date: 2026-08-04
description: "WSLg/X11 で Chromium のカーソルが透明になる問題の対処 — adwaita-icon-theme-full 導入、XCURSOR_THEME/XCURSOR_SIZE 設定、.bashrc への永続化"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

WSLg/X11 でカーソルテーマが未設定のためカーソルが透明になる典型的な問題です。

## 対処方法

### Step 1: カーソルテーマをインストール

```bash
sudo apt install -y adwaita-icon-theme-full x11-xserver-utils
```

### Step 2: カーソルを設定してから起動

```bash
export XCURSOR_THEME=Adwaita
export XCURSOR_SIZE=24
xsetroot -cursor_name left_ptr
chromium --no-sandbox &
```

### Step 3: 永続化（.bashrc に追記）

```bash
cat >> ~/.bashrc << 'EOF'
export DISPLAY=:0
export XCURSOR_THEME=Adwaita
export XCURSOR_SIZE=24
EOF
source ~/.bashrc
```

### それでも表示されない場合

```bash
# xcursor-themes パッケージも追加
sudo apt install -y xcursor-themes

# または DMZ-White テーマを試す
export XCURSOR_THEME=DMZ-White
xsetroot -cursor_name left_ptr
chromium --no-sandbox &
```

---

**原因**: WSLg の X11 互換レイヤーはデフォルトのカーソルテーマを持たないため、カーソルが invisible（透明）になります。`XCURSOR_THEME` を設定することで解決します。

## Related

- [[response-7]] — XCURSOR で駄目な場合の GTK / .Xresources 設定
- [[response-8]] — さらに駄目な場合の Wayland 直接起動 / VcXsrv