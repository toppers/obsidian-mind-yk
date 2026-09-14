---
date: 2026-08-08
description: "git submodule の基本操作コマンド控え — add でのサブモジュール追加、--remote での更新、サブモジュール側コミット後に親リポジトリのポインタを更新する手順"
tags:
  - reference
  - git
  - submodule
---

# サブモジュールの追加
git submodule add https://github.com/example/repo.git libs/example
git commit -m "Add submodule: example"

# サブモジュールの更新
git submodule update --remote

# サブモジュール内での変更反映
cd libs/example
## コードを編集してコミット・プッシュ
git add .
git commit -m "Fix/update"
git push

## 親リポジトリに戻ってポインタ更新
cd ../..
git add libs/example
git commit -m "Update submodule pointer"
git push

## Related

- [[VCS-gitで履歴からファイル削除]]
- [[GitHub Action のMEMO]]