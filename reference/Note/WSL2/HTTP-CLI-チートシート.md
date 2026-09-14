---
date: 2026-07-07
description: "HTTP CLI（curl / wget）のチートシート — 認証情報をシェル履歴やプロセス一覧に残さない方法を最優先する判断基準つき"
tags:
  - reference
  - wsl2
  - cli
  - cheatsheet
---

# HTTP CLI チートシート (curl / wget)

## 判断基準(最優先)

**認証情報をシェル履歴・プロセス一覧に残さない方法を優先する。**

優先順位:

1. 対話入力(`curl -u user`(パスワード省略) / `wget --ask-password`)
2. 設定ファイル(`~/.wgetrc`、パーミッション 600)
3. コマンドライン引数に平文(`-u user:pass`)— ローカルの使い捨て用途のみ
4. URL埋め込み(`https://user:pass@host/`)— 原則使わない(履歴・ログ・Referer漏洩リスク)

---

## BASIC認証

### curl

```bash
# 推奨: パスワードを対話入力(履歴に残らない)
curl -u username https://example.com/protected/

# ユーザー名・パスワードを直接指定(履歴に残る)
curl -u username:password https://example.com/protected/

# 非推奨: URL埋め込み
curl https://username:password@example.com/protected/
```

### wget

```bash
# 推奨: パスワードを対話入力
wget --user=username --ask-password https://example.com/protected/file.zip

# ユーザー名・パスワードを直接指定(履歴に残る)
wget --user=username --password=password https://example.com/protected/file.zip

# HTTP認証に限定したい場合
wget --http-user=username --http-password=password https://example.com/protected/file.zip
```

### wget: 設定ファイル方式(繰り返し使う場合の推奨)

```bash
# ~/.wgetrc に記載
http_user = username
http_password = password
```

```bash
# 他ユーザーから読めないようにする(必須)
chmod 600 ~/.wgetrc
```

---

## リダイレクト追随

### curl

```bash
# -L / --location でリダイレクト(301, 302, 303, 307, 308)に追随
curl -L https://example.com

# 最大リダイレクト回数を指定(デフォルト30)
curl -L --max-redirs 10 https://example.com
```

注意: `-L` を付けないと `301 Moved Permanently` 等のレスポンス本文だけが返り、実際のコンテンツは取得できない。

### wget

```bash
# wgetはデフォルトでリダイレクトに追随する(最大20回)
wget https://example.com

# 最大回数を変更
wget --max-redirect=10 https://example.com
```

---

## 出力の保存

```bash
# curl: 指定ファイル名で保存
curl -L -o output.html https://example.com

# curl: リモートのファイル名のまま保存
curl -L -O https://example.com/file.zip

# wget: 指定ファイル名で保存(デフォルトはリモート名)
wget -O output.html https://example.com
```

---

## デバッグ

```bash
# curl: 詳細な通信ログ(リクエスト/レスポンスヘッダー、TLS情報)
curl -L -v https://example.com

# curl: レスポンスヘッダーを本文と一緒に表示
curl -L -i https://example.com

# curl: ヘッダーのみ取得(HEADリクエスト)
curl -I https://example.com

# wget: 詳細ログ
wget -d https://example.com
```

---

## 主なオプション対応表

| 目的 | curl | wget |
|---|---|---|
| BASIC認証(対話入力) | `-u user` | `--user=user --ask-password` |
| BASIC認証(直接指定) | `-u user:pass` | `--user=user --password=pass` |
| リダイレクト追随 | `-L` / `--location` | デフォルトで追随 |
| 最大リダイレクト回数 | `--max-redirs N` | `--max-redirect=N` |
| ファイルに保存 | `-o file` / `-O` | `-O file` / デフォルト |
| 詳細ログ | `-v` | `-d` |
| レスポンスヘッダー表示 | `-i`(本文と併記) / `-I`(ヘッダーのみ) | `-S` |

---

## よく使う組み合わせ

```bash
# BASIC認証 + リダイレクト追随 + ファイル保存(パスワード対話入力)
curl -L -u username -o output.html https://example.com/protected/

# BASIC認証付きダウンロード(.wgetrc設定済みなら認証オプション不要)
wget https://example.com/protected/file.zip
```
