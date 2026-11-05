---
date: 2026-08-04
description: "Wayland 直接起動でカーソル問題が解決した後の永続化手順 — .bashrc の DISPLAY 設定を削除して WAYLAND_DISPLAY を設定し、chromium-wsl エイリアスを登録する"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

方法Bで解決しましたね。永続化しておきましょう。

```bash
# .bashrc の DISPLAY 設定を Wayland 用に更新
sed -i 's/export DISPLAY=:0//' ~/.bashrc

cat >> ~/.bashrc << 'EOF'
export WAYLAND_DISPLAY=wayland-0
EOF
source ~/.bashrc
```

Chromium の起動コマンドも固定：

```bash
chromium --no-sandbox --ozone-platform=wayland &
```

毎回入力するのが面倒なら alias を追加：

```bash
echo "alias chromium-wsl='chromium --no-sandbox --ozone-platform=wayland'" >> ~/.bashrc
source ~/.bashrc

# 以後これだけで起動
chromium-wsl &
```

## Related

- [[response-8]] — 解決に至った方法B（Wayland 直接起動）の提示元