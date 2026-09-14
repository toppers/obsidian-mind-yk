---
date: 2026-08-04
description: "WSLg の XWayland でカーソルテーマが効かない既知問題の回避策 — /usr/share/icons/default の system-wide 設定、Wayland 直接起動、VcXsrv を X サーバーとして使う方法"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

WSLg の XWayland 上での既知の問題です。別のアプローチを試します。

## 方法A: デフォルトカーソルテーマを system-wide で設定

```bash
sudo mkdir -p /usr/share/icons/default
sudo tee /usr/share/icons/default/index.theme << 'EOF'
[Icon Theme]
Inherits=Adwaita
EOF
```

その後 Chromium を再起動。

## 方法B: Wayland モードで起動

WSLg は Wayland ベースなので、X11 ではなく Wayland で直接起動：

```bash
unset DISPLAY
export WAYLAND_DISPLAY=wayland-0
chromium --no-sandbox --ozone-platform=wayland &
```

## 方法C: VcXsrv（X サーバー）を使う

WSLg の代わりに Windows 側で VcXsrv を使う方法です。

1. Windows で **VcXsrv** をインストール（winget で可能）：
   ```powershell
   winget install marha.VcXsrv
   ```

2. VcXsrv を起動（`XLaunch` → Multiple windows → Display 0 → Disable access control にチェック）

3. WSL2 側で：
   ```bash
   export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
   chromium --no-sandbox &
   ```

---

**根本原因**: WSLg の XWayland はカーソルを Windows の RDP カーソルとして扱うため、Linux 側のカーソルテーマが反映されないケースがあります。方法B（Wayland直接）か方法C（VcXsrv）が最も確実です。

## Related

- [[response-7]] — 先に試した GTK / .Xresources による対処
- [[response-9]] — 方法B（Wayland 直接起動）で解決した後の永続化