---
date: 2026-08-11
description: "settings.json の Stop フック定義の抜粋 — pmb.hookclient の lesson-followcheck / autowrite / capture-exploration を PowerShell で叩き、加えてダッシュボード用イベントを JSONL 記録"
tags:
  - reference
  - claude-code
  - hooks
  - pmb
---

    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "& C:/Users/ykomi/AppData/Roaming/uv/tools/pmb-ai/Scripts/python.exe -m pmb.hookclient lesson-followcheck --window 30 --quiet",
            "shell": "powershell"
          }
        ]
      },
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "& C:/Users/ykomi/AppData/Roaming/uv/tools/pmb-ai/Scripts/python.exe -m pmb.hookclient autowrite --window 30 --quiet",
            "shell": "powershell"
          }
        ]
      },
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "& C:/Users/ykomi/AppData/Roaming/uv/tools/pmb-ai/Scripts/python.exe -m pmb.hookclient capture-exploration --quiet",
            "shell": "powershell"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "node -e \"const f=require('fs'),p=require('path'),dir=p.join(require('os').homedir(),'.claude');if(!f.existsSync(p.join(dir,'.dashboard-live'))){process.exit(0)}process.stdin.resume();let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const e=JSON.parse(d);const line=JSON.stringify({type:e.hook_event_name,tool:e.tool_name,sessionId:e.session_id,timestamp:Date.now()})+'\\n';f.appendFileSync(p.join(dir,'.dashboard-events.jsonl'),line)}catch(err){}})\""
          }
        ]
      }
    ],

## Related

- [[reference/Note/AI開発/Claude-Code/MCP/PMB/使い方|PMB の使い方]] — このフックが叩いている pmb.hookclient 側のツール群
