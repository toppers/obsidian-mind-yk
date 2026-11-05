---
date: 2026-10-14
description: "tecsgen-python3移植計画のうち解消済みの「現状の問題（2026-09-26確認、同日修正済み）」の節をverbatim分離したアーカイブ。25KB閾値による分割"
project: tecsgen-python3
status: tracking
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3移植計画 Archive — 現状の問題

[[tecsgen-python3移植計画]] の「現状の問題」の節を、25KB 閾値のため verbatim で分離したもの（2026-10-14）。すべて 2026-09-26 に修正済み。

## 現状の問題（2026-09-26 確認 → 同日修正済み）

- ~~ノートに書かれたパス `E:/Ccur/python3/tecsgen-python` は存在しない~~ → 実体は `E:/Ccur/python3/tecsgen-python3`（リモートは `ykominami/tecsgen-python`。2026-09-28 に `ykominami/tecsgen-python3` へ改名）。関連ノート5件のパスを修正済み
- `pyproject.toml` を修正済み
  - 配布名を `tecsgen-python3`、import パッケージを `tecsgen`（`src/tecsgen/`）に改名。CLI 完全互換の決定（[[tecsgen-python3 P0基本方針決定]]）に合わせ、コマンド名を `tecsgen` にした
  - description の誤記「Ptyhon」を修正
  - `my`・`tuff` を削除。PyPI 上の無関係なパッケージだった（中身は数行の無害なコードと確認）。`ruff` の誤記と判断し、`pytest`・`ruff`・`ty` を dev 依存（`[dependency-groups]`）へ移した
  - 依存に入っていなかった `yklibpy` の `[tool.uv.sources]` 指定を削除
  - hatchling がパッケージを見つけられるよう `[tool.hatch.build.targets.wheel]` を追加
- `example.py` を修正済み。インデントが崩れ、DLL パスの文字列が途中で改行されていて動かなかった。また `Language(int)` 方式は非推奨で、Windows では `OverflowError` になる（`unsigned long` が32ビットのため）。PyCapsule を渡す方式に変えた。DLL の場所は環境変数 `TECSGEN_CDL_DLL` で上書きできる
- `.venv` を作り直した。ディレクトリ名が `tecsge-python3` だった頃に作られたもので、スクリプトのパスが古いままだった
- 確認: `uv run example` でサンプル CDL をエラーなくパースできた。pytest 1件 pass、`ruff check`・`ruff format --check`・`ty check` はすべて問題なし
