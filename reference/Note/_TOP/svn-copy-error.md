---
date: 2026-08-24
description: "svn copy によるtecsgenブランチ作成コマンドと、post-commit hookのImportError失敗ログ控え"
tags:
  - reference
  - svn
  - tecsgen
---

svn copy https://dev.toppers.jp/svn/tecs/toppers/tecsgen/trunk \
          https://dev.toppers.jp/svn/tecs/toppers/tecsgen/branches/<ブランチ名> \
          -m "Create branch <ブランチ名> from trunk"
		  
		  
==========
svn copy https://dev.toppers.jp/svn/tecs/toppers/tecsgen/trunk https://dev.toppers.jp/svn/tecs/toppers/tecsgen/branches/ykominami_r3033 -m "Create branch ykominami_r3303 from trunk"
Committing transaction...
Committed revision 3304.

Warning: post-commit hook failed (exit code 1) with output:
Traceback (most recent call last):
  File "/opt/svnroot/tecs/hooks/trac-post-commit-hook", line 107, in <module>
    from trac.ticket.notification import TicketNotifyEmail
ImportError: cannot import name TicketNotifyEmail

## Related
- [[reference/Note/VCS-PROJECT-PKGMGR/svn-log|svn-log]]
