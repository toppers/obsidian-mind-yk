---
date: 2026-10-15
description: "tecsgen-python3移植計画のフェーズP7（cmake対応と正解データの基準の切り替え）の詳細をverbatim分離したノート。25KB閾値による分割"
project: tecsgen-python3
status: active
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3移植計画 — P7 cmake対応と基準の切り替え

[[tecsgen-python3移植計画]] の P7 節を、25KB 閾値のため 2026-10-15 に逐語で分離した（内容は変えていない）。未了の項目があるため `Archive` ではなくサテライトノートとして置く。関連: [[tecsgen-python3]]。

## P7 cmake 対応と正解データの基準の切り替え（2026-10-05）

Ruby 版 tecsgen-rb（`asp3_stm32cube_TECS` の `tecsgen-rb`）の cmake 対応を移植し、正解データの基準を r3304 から tecsgen-rb へ切り替えた。計画・調査・決定は [[tecsgen-python3 cmake対応計画]]。実装は Python 版リポジトリのブランチ `ykominami/cmake-support`（2026-10-05 に PR #9 で `main` へマージ済み）。

- **cmake**: `CMakeLists.tecsgen.cmake` の生成と `CMake` API を移植（内部仕様 [[tecsgen-python3内部仕様 - 08 コード生成#8.6 CMakeLists.tecsgen.cmake（2026-10-05、tecsgen-rb の cmake 対応）|8.6]]）
- **`TransparentRPCSignaturePlugin`**: tecsgen-rb で追加されたプラグイン（r3304 には無く、`RPCPlugin`・`DataPumpHolderPlugin` が参照して失敗していた）を移植。これで `rpc`・`class`・`DataPumpHolder` が成功する。`DataPumpHolder` は、r3304 では実行されなかった `DataPumpHolderPlugin#gen_ep_func_body`（Ruby 約230行）も必要になり、移植した
- **基準の切り替え**: `test/` 158ケース（`transparent_marshaler` を除く）、p2・p3、カーネル23、配布パッケージ17 を tecsgen-rb で再採取。旧との差は `CMakeLists.tecsgen.cmake` の追加と、上の3ケースの成功化だけ。`transparent_marshaler` は tecsgen-rb に `TransparentMarshalerPlugin.rb` が無いため、r3304 の正解を残し比較の対象外にした
- **検証**: プラグインなし119/119・プラグインあり77/77 が一致（`tools/port/p4_progress.py`）。Windows 1025 passed / 78 skipped、WSL 1020 passed / 83 skipped、ruff・ty とも通過。配布パッケージは、これまで p3 記録が2件しか無く検証の対象外だった13件に記録を採り、検証の対象に加えた
- **採取ツール**: `wsl_check.sh` に `--build-src-tree`・`--src-tree`・`--exclude`・`--cases-golden` を追加。svn 以外の移植元に対応した（`tools/golden/README.md`）
- **`CMake.add_*` を呼ぶプラグイン**（2026-10-09 確認）: 標準のテストケースには無いので、利用者プラグイン（`-L`）の合成ケースで確かめ、`gen/` 13ファイルが Ruby 版（tecsgen-rb）とバイト一致した。同日、golden ケース `cmake_add` として固定した（Python 版 PR #11 で `main` にマージ済み、`11f38ef`。プラグインありの一致は 78/78） → [[tecsgen-python3 cmake対応計画 — C3 の結果#C3 の結果（2026-10-09）: `CMake.add_*` を呼ぶプラグインで Ruby 版と一致|C3 の結果]]
- **セルタイプ以外の種類のプラグイン**（2026-10-09 確認）: signature・cell・composite・multi・through・domain・class の各プラグインから `CMake.add_*` を呼んでも、Ruby 版と一致した。multi で見つけた移植のずれ（`MultiPlugin#get_plugin` が返す、ファイル名と違う名前のクラスの post_code が出ない）を修正し、golden ケース 7 件を追加した（Python 版 PR #12 で `main` にマージ済み、`9c3d635`。プラグインありの一致は 85/85） → [[tecsgen-python3 cmake対応計画 — C3 の結果#種類ごとの確認（2026-10-09）|種類ごとの確認]]
- **完了**: `asp3_stm32cube_TECS` の `Asp3Tecs.cmake` から Python 版を呼ぶ確認（C5、2026-10-06）。ブランチの `main` へのマージ（PR #9）と、`-k` の差異の修正（`ykominami/fix-kcode-differences`、PR #8 で先に取り込み済み）との取り込み順は、2026-10-05 に完了。ほかのボードの確認（C6）は 2026-10-09 に完了（H563ZI・N6570-DK は Ruby 版・Python 版で最終イメージが SHA-256 まで一致。H533・C562 は TECS を使わないため対象外）→ [[tecsgen-python3 cmake対応計画 — C6 ビルド検証]]
- **未了**（as of 2026-10-10、[[tecsgen-python3]] の残りと同じ）: 実機（書込み・起動）の確認、実際の CubeMX 生成物でのビルド、H533・C562 に TECS を展開したときの確認、`transparent_marshaler` ケースの扱いの決定
