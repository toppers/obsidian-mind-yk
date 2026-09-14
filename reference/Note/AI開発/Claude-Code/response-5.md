---
date: 2026-08-04
description: "$DISPLAY 未設定で Chromium が起動しない問題の切り分け — DISPLAY/WAYLAND_DISPLAY 確認、wsl --update と --shutdown、手動設定、Wayland 起動、WSLg の動作確認"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

エラーの原因は `$DISPLAY` が未設定で X サーバーが見つからない状態です。

## 確認と対処

### Step 1: DISPLAY の状態を確認

```bash
echo $DISPLAY
echo $WAYLAND_DISPLAY
```

**何も表示されない場合** → WSLg が起動していません。

### Step 2: WSLg を有効にして再起動

Windows 側の **PowerShell（管理者）** で実行：

```powershell
wsl --update
wsl --shutdown
```

その後 Ubuntu を起動し直してから再確認。

### Step 3: DISPLAY を手動設定して試す

```bash
export DISPLAY=:0
chromium --no-sandbox &
```

### Step 4: Wayland で起動する（Windows 11 推奨）

WSLg は Wayland ベースなので、こちらも試す：

```bash
chromium --no-sandbox --ozone-platform=wayland &
```

または両方指定：

```bash
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
chromium --no-sandbox &
```

### Step 5: WSLg の動作確認

```bash
# WSLg が正常なら /tmp/.X11-unix が存在する
ls /tmp/.X11-unix/

# weston (WSLg のコンポジター) が動いているか確認
ps aux | grep weston
```

---

**最も多い原因**: WSL を `wsl --shutdown` せずに使い続けていると WSLg のソケットが古くなります。一度シャットダウンして再起動するのが最速の解決策です。

## Related

- [[response-4]] — 起動オプションとエラー対処表
- [[response-0]] — WSL2 への Chromium インストール手順