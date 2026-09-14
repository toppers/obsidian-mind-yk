---
date: 2026-06-18
description: "git svn で変換した tecsgen リポジトリに対し、SVNの tags 配下と同名の git tag を作らせる依頼プロンプト。svnクライアントは ~/bin/svny を使う"
tags:
  - reference
  - tecs
  - git
  - prompt
---

カレントディレクトリ直下の`.git`は、`git svn`を用いて、Subversionのリポジトリを、Gitリポジトリに変換したもである。
リモートリポジトリの`tags`ディレクトリ下のサブディレクトリ名と同名のgitの`tag`を作成して、対応するコミットを指すようにして。
ここで、Subversioのリモートリポジトリは`https、Subversioのリモートリポジトリは`https://dev.toppers.jp/svn/tecs/toppers/tecsgen`である。
ただし、svnクライアントとして、シェルスクリプト`~/bin/svny`を利用して。
シェルスクリプト‘svny`内にユーザ名、パスワードの値を埋め込んであり、svnクライアントを--usernameオプション、--passwordオプションを指定して呼び出す。