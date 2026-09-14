---
date: 2026-08-04
description: "WSL2/WSLg の Chromium でカーソルが表示されない問題への追加対処 — GTK3/GTK2 の settings.ini、.Xresources、--disable-gpu、カーソルテーマ実体の存在確認"
tags:
  - reference
  - wsl2
  - chromium
  - linux
---

Chromium は GTK を使うので、GTK のカーソル設定が必要です。

## 追加対処方法

### 方法1: GTK カーソル設定ファイルを作成

```bash
# GTK3 設定
mkdir -p ~/.config/gtk-3.0
cat > ~/.config/gtk-3.0/settings.ini << 'EOF'
[Settings]
gtk-cursor-theme-name=Adwaita
gtk-cursor-theme-size=24
EOF

# GTK2 設定
cat > ~/.gtkrc-2.0 << 'EOF'
gtk-cursor-theme-name="Adwaita"
gtk-cursor-theme-size=24
EOF
```

### 方法2: .Xresources で設定

```bash
cat > ~/.Xresources << 'EOF'
Xcursor.theme: Adwaita
Xcursor.size: 24
EOF
xrdb -merge ~/.Xresources
```

設定後に Chromium を再起動：

```bash
pkill chromium
chromium --no-sandbox &
```

### 方法3: GPU 無効で起動

```bash
chromium --no-sandbox --disable-gpu &
```

### 方法4: カーソルテーマの実体を確認

```bash
# Adwaita カーソルが実際に存在するか確認
find /usr/share/icons/Adwaita -name "cursors" -type d
find /usr/share/icons -name "cursors" -type d | head -10
```

存在するテーマ名を `XCURSOR_THEME` に設定してください。

---

方法1（GTK設定）と方法2（.Xresources）を両方試して、それでも駄目なら方法3の `--disable-gpu` を試してみてください。

## Related

- [[response-6]] — 前段の XCURSOR_THEME による対処
- [[response-8]] — GTK 設定でも駄目な場合の Wayland / VcXsrv 回避策