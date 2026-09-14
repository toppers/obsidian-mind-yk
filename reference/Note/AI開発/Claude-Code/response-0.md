---
date: 2026-08-04
description: "WSL2 の Ubuntu で apt の chromium-browser が snap ラッパーのため入らない問題の対処 — Debian リポジトリ追加 / xtradeb PPA / ungoogled-chromium と WSLg の確認手順"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

Ubuntu の WSL2 では `apt` の `chromium-browser` が snap ラッパーになっており、WSL2 では snapd が動かないため直接インストールできません。

## Chromium を WSL2 で動かす方法

### 方法1: Debian のリポジトリを使う（最もシンプル）

```bash
# Debian のリポジトリを追加
echo "deb http://deb.debian.org/debian bookworm main" | sudo tee /etc/apt/sources.list.d/debian.list
wget -qO- https://ftp-master.debian.org/keys/release-12.asc | sudo tee /etc/apt/trusted.gpg.d/debian-bookworm.asc

sudo apt update
sudo apt install -y chromium
```

### 方法2: snap を使わない PPA を使う

```bash
sudo add-apt-repository ppa:xtradeb/apps
sudo apt update
sudo apt install -y chromium
```

### 方法3: ungoogled-chromium

```bash
sudo add-apt-repository ppa:xtradeb/ungoogled-chromium
sudo apt update
sudo apt install -y ungoogled-chromium
```

## 起動

```bash
chromium --no-sandbox &
```

Windows 11 の WSLg が有効であれば、自動的にウィンドウが表示されます。

## WSLg の確認

```bash
# これが表示されれば WSLg 有効
echo $DISPLAY   # :0 など
ls /tmp/.X11-unix/
```

**`--no-sandbox` が必要な理由**: WSL2 の Linux カーネルは一部の namespace 機能が制限されており、Chromium のサンドボックスが動作しないためです。

## Related

- [[response-4]] — インストール後の起動オプションとエラー対処表
- [[response-5]] — `cannot open display` になる場合の DISPLAY / WSLg 確認