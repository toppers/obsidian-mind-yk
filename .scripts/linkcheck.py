"""Obsidian の wikilink を解決規則に沿って検査する。

コードブロック / インラインコードは除外する（[[ を含むコード片の誤検出を防ぐ）。
解決は Obsidian の規則に合わせ、以下のいずれかに当たれば OK とする:
  - vault 内のいずれかのファイルの basename（拡張子なし）に一致
  - vault 内のいずれかのファイル名（拡張子つき）に一致
  - vault ルートからの相対パス（拡張子あり/なし）に一致
"""
import re
import sys
from pathlib import Path

VAULT = Path(sys.argv[1])
SKIP_DIRS = {".git", ".obsidian", ".claude", ".serena", ".agents", "node_modules"}

stems, names, paths = set(), set(), set()
for p in VAULT.rglob("*"):
    if not p.is_file():
        continue
    if any(part in SKIP_DIRS for part in p.parts):
        continue
    rel = p.relative_to(VAULT).as_posix()
    stems.add(p.stem)
    names.add(p.name)
    paths.add(rel)
    paths.add(rel[: -len(p.suffix)] if p.suffix else rel)

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"!?\[\[([^\[\]]+?)\]\]")

bad = []
total = 0
for p in sorted(VAULT.rglob("*.md")):
    if any(part in SKIP_DIRS for part in p.parts):
        continue
    in_fence = False
    for lineno, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = INLINE_CODE.sub("", line)
        for m in LINK.finditer(line):
            # 表の中では別名区切りが \| とエスケープされる。先に | で切ってから
            # 末尾の \ を落とさないと、正しいリンクを壊れ扱いしてしまう。
            target = m.group(1).split("|")[0].rstrip("\\").split("#")[0].strip()
            if not target:
                continue
            total += 1
            if target in stems or target in names or target in paths:
                continue
            bad.append((p.relative_to(VAULT).as_posix(), lineno, target, m.group(0)))

print(f"wikilink 総数(コード除外後): {total} / 解決不能: {len(bad)}\n")
for src, lineno, target, raw in bad:
    print(f"{src}:{lineno}\t{target}\t{raw}")
