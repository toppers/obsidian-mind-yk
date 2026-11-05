---
date: 2026-07-23
description: "スキルから別スキルを順に呼び、失敗が出たら以降を中止できるかの回答 — スキルには戻り値や exit code の概念が無く、失敗をどう機械的に検出するかが設計の核心。確実さに応じて3段階"
tags:
  - reference
  - claude-code
  - skill
---

claude codeのskillで、`skill A`から`skill B``, ‘skill C‘`, `skill D` をよびだしたい。このとき、どれかで失敗が報告されたら、それ以降はskillをよびださないようにしたい。このようなことは可能か。`

可能です。ただし「どのレベルの確実さが必要か」で実装が3段階に分かれます。前提として、Skillは関数呼び出しではなくmarkdownファイルの指示をコンテキストに読み込んでClaudeが実行する仕組みなので、戻り値やexit codeという概念がSkill自体には存在しません。「失敗の報告」をどう機械的に検出するかが設計の核心になります。

**方法1: SKILL.mdの指示のみ(ソフト・非推奨)**

Skill AのSKILL.mdに「B→C→Dの順に呼び出す。各スキル完了後に成功条件Xを確認し、満たさなければ以降のスキル呼び出しを中止して報告する」と明記する方法。スキルは合成可能で、あるスキルが別のスキルを処理ステップとして呼び出せますが、遵守はLLMの判断依存です。あなたの過去の実測(cc-env)でもSkill単体の発動率は約20%で、指示ベースの制御は保証になりません。

**方法2: 実処理のスクリプト化 + 状態ファイル(推奨・確実)**

各スキルの実体をスクリプトに寄せ、Skill Aは「以下を1コマンドで実行せよ」とだけ指示する形:

```bash
set -e
bash "$CLAUDE_PROJECT_DIR/.claude/skills/b/run.sh" && \
bash "$CLAUDE_PROJECT_DIR/.claude/skills/c/run.sh" && \
bash "$CLAUDE_PROJECT_DIR/.claude/skills/d/run.sh"
```

exit code非0でシェルが短絡評価し、以降は物理的に実行されません。これが最も単純で決定論的です。B/C/Dに「Claudeの判断」が必要な場合は、共有状態ファイルを各スキルが読み書きし、オーケストレータが次に実行すべきスキルを判定するパターンが定石です。具体的には各スキルのSKILL.md冒頭に「最初に `.claude/workflow-state.json` を読み、`failed: true` なら何もせず中断を報告せよ」と書き、失敗したスキルが自分でフラグを書く構成にします。

**方法3: Hooksで強制ブロック(ハード保証)**

方法2の状態ファイルをHookで強制する形。PreToolUseフックをSkill呼び出しにマッチさせ、失敗フラグ(sentinelファイル)が存在したらexit code 2でブロックします。あなたの環境ならPowerShellで:

```powershell
# pre-skill-guard.ps1
if (Test-Path "$env:CLAUDE_PROJECT_DIR\.claude\workflow-failed") {
    [Console]::Error.WriteLine("Workflow failed earlier. Skill invocation blocked.")
    exit 2
}
exit 0
```

これならClaudeが指示を忘れても呼び出し自体が拒否されます。あなたの実測(hooks併用で発動率20%→84%)からも、確実性が要件なら最初からHooks前提で組むのが妥当です。なお、Skill呼び出しに対応する実際のツール名・matcher文字列はバージョンで変わりうるので、`claude --debug` か `/hooks` で実環境のツール名を確認してから設定してください。

確認させてください:

1. 「失敗」はスクリプトのexit codeで機械的に判定できる種類ですか?(はい→方法2で完結/いいえ=Claudeの判断が必要→方法2の状態ファイル+方法3の併用)
2. B/C/Dは既存スキルの流用ですか、それとも今回新規に設計できますか?(新規なら最初からスクリプト中心に寄せるのが楽です)