#!/usr/bin/env python3
"""folder-classify Skill 同梱スクリプト(ダミー実装)。

つねに同一の固定データ(FIXTURE)から分類結果を生成して出力する。
対象ディレクトリの実際の中身は一切見ない。

目的:
  - SKILL.md が「正」と宣言している出力契約(列構成・並び順・サマリー書式)を
    このファイルで確定させる。
  - 本実装に差し替える際は analyze() だけを実ロジックに置き換えればよい。
    render_table() / render_summary() は出力契約なので変更しない。

使い方:
  python3 analyze_folders.py <対象ディレクトリ>
"""

import sys
from pathlib import Path

DUMMY_MARKER = "(dummy: 固定データによる出力です。実ディレクトリは走査していません)"

# 分類ラベル(SKILL.md「分類観点」と1対1対応。表示順もこの順に固定)
CLASS_EMPTY = "空フォルダ"
CLASS_DIRS_ONLY = "フォルダのみ"
CLASS_FILES_ONLY = "ファイルのみ"
CLASS_MIXED = "ディレクトリ+ファイル"
CLASS_ORDER = [CLASS_EMPTY, CLASS_DIRS_ONLY, CLASS_FILES_ONLY, CLASS_MIXED]

# 固定の分類結果。各分類・各属性の組み合わせを最低1件ずつ含むゴールデンデータ。
# 列: (フォルダ名, 分類, .git, remote, .rbあり, Rubyのみ)
FIXTURE = [
    ("sandbox",        CLASS_EMPTY,      False, False, False, False),
    ("workspace",      CLASS_DIRS_ONLY,  False, False, False, False),
    ("scripts",        CLASS_FILES_ONLY, False, False, True,  True),
    ("notes",          CLASS_FILES_ONLY, False, False, False, False),
    ("my-cli-tool",    CLASS_MIXED,      True,  True,  True,  False),
    ("legacy-project", CLASS_MIXED,      True,  False, True,  True),
    ("web-app",        CLASS_MIXED,      True,  True,  False, False),
]


def analyze(target_dir: Path) -> list[tuple]:
    """分類結果の行データを返す。

    ダミー実装: target_dir を無視して FIXTURE をそのまま返す。
    本実装ではここで target_dir 直下を走査する。
    """
    return list(FIXTURE)


def mark(flag: bool) -> str:
    return "あり" if flag else "なし"


def render_table(rows: list[tuple]) -> str:
    lines = [
        "| フォルダ名 | 分類 | .git | remote | Rubyスクリプト | Rubyのみ |",
        "|---|---|---|---|---|---|",
    ]
    # 並び順: 分類(CLASS_ORDER順) -> フォルダ名昇順
    ordered = sorted(rows, key=lambda r: (CLASS_ORDER.index(r[1]), r[0]))
    for name, cls, has_git, has_remote, has_rb, ruby_only in ordered:
        lines.append(
            f"| {name} | {cls} | {mark(has_git)} | {mark(has_remote)} "
            f"| {mark(has_rb)} | {mark(ruby_only)} |"
        )
    return "\n".join(lines)


def render_summary(rows: list[tuple]) -> str:
    counts = {c: 0 for c in CLASS_ORDER}
    git = remote = rb = 0
    for _, cls, has_git, has_remote, has_rb, _ in rows:
        counts[cls] += 1
        git += has_git
        remote += has_remote
        rb += has_rb
    lines = [f"## サマリー", f"", f"- 合計: {len(rows)} フォルダ"]
    lines += [f"- {c}: {counts[c]}" for c in CLASS_ORDER]
    lines += [
        f"- .gitあり: {git}(うちremote設定あり: {remote})",
        f"- Rubyスクリプトあり: {rb}",
    ]
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) != 2:
        print("使い方: python3 analyze_folders.py <対象ディレクトリ>", file=sys.stderr)
        return 2
    target = Path(sys.argv[1])
    if not target.is_dir():
        print(f"エラー: ディレクトリが存在しません: {target}", file=sys.stderr)
        return 1

    rows = analyze(target)
    print(f"# フォルダ分類: {target} {DUMMY_MARKER}")
    print()
    print(render_table(rows))
    print()
    print(render_summary(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
