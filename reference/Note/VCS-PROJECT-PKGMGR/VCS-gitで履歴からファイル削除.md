---
date: 2026-03-29
description: "git filter-repo で履歴から特定ファイル（config/settings2.json）を削除し force push する手順。対象は bmx リポジトリ"
tags:
  - reference
  - git
---

remote.origin.url=git@github.com:ykominami/bmx.git

git filter-repo --path config/settings2.json --invert-paths

git push --force --all
git push --force --tags
