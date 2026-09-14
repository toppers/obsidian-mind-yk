---
date: 2026-08-15
description: "serena MCP の context list コマンド出力控え — 対応コンテキスト一覧（claude-code・codex・ide 等）とカスタムコンテキスト作成手順"
tags:
  - reference
  - ai
  - agents
  - serena
---

# serena context list

> 関連: [[AI-Agents|AI エージェント]] / [[agent-skill|Agent Skill 調査メモ]]

```
 serena context list
agent                (internal)
antigravity          (internal)
chatgpt              (internal)
claude-code          (internal)
codebuddy             (internal)
codex                (internal)
context.template     (internal)
copilot-cli          (internal)
desktop-app          (internal)
grok                 (internal)
ide                  (internal)
jb-ai-assistant      (internal)
jb-copilot-plugin    (internal)
junie                (internal)
oaicompat-agent      (internal)
vscode               (internal)
```

### 補足: カスタムコンテキストの作成

新しいコンテキストテンプレートを作成したい場合は、以下のコマンドを使用できる。

```
serena context create <新しいコンテキスト名>
```

## Related

- [[AI-Agents]]
- [[agent-skill]]
- [[serena-実行結果]] — `serena project index` をTECS関連リポジトリ群に実行した結果控え
