---
date: 2026-08-21
description: "serena project index をTECS関連リポジトリ群に対して実行した結果控え — 成功/エラーの一覧"
tags:
  - reference
  - ai
  - agents
  - serena
---

# serena project index 実行結果

> 関連: [[serena-context]] — serena のコンテキスト一覧

```
uvx --from git+https://github.com/oraios/serena serena project index

E:\Crepo\ykominami-svn-2\tecsgen\tags\tecsgen-1.9.1
E:\Crepo\ykominami-svn-2\tecscde\trunk
E:\Crepo\ykominami-svn-2\mruby\mruby-master
E:\Crepo\ykominami-svn-2\mruby\mruby-on-asp+tecs	エラー発生
E:\Crepo\ykominami-svn-2\hrp2+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\hrp3+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\hrmp3+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\hr-tecs3
E:\Crepo\ykominami-svn-2\fmp3+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\FatFs\trunk\ff004_tecs
E:\Crepo\ykominami-svn-2\FatFs\trunk\ff004.org
E:\Crepo\ykominami-svn-2\ev3rt+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\et_robcon\trunk	エラー発生
E:\Crepo\ykominami-svn-2\BASE-PLATFORM\rtc	エラー発生
E:\Crepo\ykominami-svn-2\atk1+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\asp3+tecs\trunk	エラー発生
E:\Crepo\ykominami-svn-2\asp+tecs\trunk	エラー発生
```

## 気づき

- `tecsgen`・`tecscde`・`mruby`本体・`hr-tecs3`・`FatFs`系2件は成功。
- TECS系リポジトリの多く（mruby-on-asp+tecs, hrp2+tecs, hrp3+tecs, hrmp3+tecs, fmp3+tecs, ev3rt+tecs, et_robcon, BASE-PLATFORM/rtc, atk1+tecs, asp3+tecs, asp+tecs）は `serena project index` でエラー発生。エラー内容は未記録。

## Action Items
- [ ] エラーになったリポジトリでエラー内容を確認し、原因（TECS特有の構成か、リポジトリ個別の問題か）を切り分ける

## Related
- [[serena-context]]
- [[tecsgen]]
