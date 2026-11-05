---
date: 2026-10-09
description: "tecsgen-python3 の Asp3Tecs.cmake の configure 以降（コンパイル・リンク）を、CubeMX の代わりの ST 公開テンプレートで NUCLEO-H563ZI と STM32N6570-DK のサンプルについて確認した記録（H533・C562 は TECS 未使用で対象外）。Ruby 版と Python 版でイメージが SHA-256 まで一致。実機・実 CubeMX 生成物は未確認"
project: tecsgen-python3
status: tracking
quarter: Q4-2026
tags:
  - work-note
  - tecs
  - tecsgen
  - plan
---

# tecsgen-python3 cmake対応計画 — C6 ビルド検証（2026-10-09）

[[tecsgen-python3 cmake対応計画]] の C5（[[tecsgen-python3 cmake対応計画#C5 の結果（2026-10-06）: Asp3Tecs.cmake から Python 版を呼ぶ|C5 の結果]]）が「確認していない」としていた、`asp3_tecs_configure`・`asp3_tecs_apply_manifest` 以降（configure、コンパイル、リンク）を確かめた。**実機（ボードへの書込みと実行）は、ボードが無く確認していない。**

## 結論

NUCLEO-H563ZI の `sample1` を、tecsgen を Ruby 版（tecsgen-rb）と Python 版（`-DASP3_TECSGEN_COMMAND`）にした 2 通りで、configure からリンクまで通した。**最終イメージ（`objcopy -O binary`）は SHA-256 まで一致**した（`7031b9ba…4cb8`、41,584 バイト）。

## 何が足りなかったか

この PC には STM32CubeMX、STM32Cube の FW パッケージ、OpenOCD、STM32CubeProgrammer が無く、ST-Link のボードも接続されていない。`Drivers/`・`cmake/stm32cubemx/`・`CMakePresets.json` などの CubeMX の生成物（`.gitignore` 対象）も無い。そのため、そのままではビルドできない（[[tecsgen-python3 cmake対応計画#C5 の結果（2026-10-06）: Asp3Tecs.cmake から Python 版を呼ぶ|C5]] の時点と同じ）。

## 方法（CubeMX の代わり）

リポジトリ `asp3_stm32cube_TECS` を WSL にコピーし（元のリポジトリは変更していない）、CubeMX の生成物の代わりに、ST が GitHub で公開しているものを置いた。

| 用途 | 出所（コミット） |
|---|---|
| `asp3_core` | `toppers/asp3_core` `6496ca7`（サブモジュールの固定コミット） |
| CMSIS デバイスヘッダ・スタートアップ・リンカスクリプト | `cmsis-device-h5` `884b8dc`（v1.7.0） |
| CMSIS コア | `cmsis-core` `01d1814` |
| HAL ドライバ | `stm32h5xx-hal-driver` `ba20038` |
| Nucleo の BSP | `stm32h5xx-nucleo-bsp` `7122a2c`（v1.3.0） |

- `Core/Inc/stm32h5xx_hal_conf.h`・`stm32h5xx_nucleo_conf.h`・`Core/Src/system_stm32h5xx.c`・`stm32h5xx_hal_msp.c`・`STM32H563xx_FLASH.ld` は上のテンプレートから複写した。`stm32h5xx_it.h` は `stm32h5xx_it.c` のハンドラ定義から作った。
- `.ioc` で `VCP=true`（バーチャル COM ポート）なので、`USE_BSP_COM_FEATURE` を `1U` にした（`main.c` が `COM_InitTypeDef` を使うため）。
- `cmake/stm32cubemx/CMakeLists.txt`（HAL・BSP・`main.c`・スタートアップ・`-T` リンカスクリプトを `H563ZI` ターゲットへ登録）と、`cmake/gcc-arm-none-eabi.cmake`（Cortex-M33、`fpv5-sp-d16`、hard float、nano.specs）を書いた。
- コピーの CRLF（119 ファイル）は LF に直した。`tecsgen` は `tecsgen-rb` へのシンボリックリンクにした（Windows のチェックアウトでは壊れた 10 バイトのファイルになる。Linux のチェックアウトと同じ状態）。
- 環境: WSL、`arm-none-eabi-gcc` 13.2.1、CMake の Unix Makefiles（`ninja` は depot_tools のラッパーで本体が無いため）。
- 実行: `cmake -S . -B build/{rb,py} -DCMAKE_TOOLCHAIN_FILE=… -DCMAKE_BUILD_TYPE=Debug [-DASP3_TECSGEN_COMMAND=<tecsgen>]` → `cmake --build`。Ruby 版は `Asp3Tecs.cmake` の従来の経路（`tecsgen.rb`）、Python 版は C5 で足した `ASP3_TECSGEN_COMMAND` の経路。

## 結果

| 項目 | 結果 |
|---|---|
| configure | 両方成功（`asp3_core` の cfg の実行を含む） |
| コンパイル・リンク | 両方成功（`Built target H563ZI`。警告は newlib の `_read`・`_write` などのスタブのみ） |
| `generated/` のファイル一覧 | 111 ファイルで同一（`tecsgen.rbdmp` は除く） |
| `generated/` の内容 | 109 ファイルが一致。`kernel_cfg.c`・`kernel_cfg.h`・`cfg1_out.c`・`offset.h` を含む。残り 2 ファイルは下の「差の原因」 |
| セクション・シンボル・サイズ | 完全に一致（`text 41332`・`data 16`・`bss 17408`、`nm -n` が同一） |
| 最終イメージ | `SOURCE_DATE_EPOCH` を固定してクリーンビルドした両方で、`objcopy -O binary` が **SHA-256 まで一致** |
| TECS 生成物のオブジェクト | `*_tecsgen.c.obj` 15 個の `.text` が全て一致 |

## 差の原因（いずれも tecsgen の差ではない）

- **最終イメージの 3 バイト**（固定前）: ビルド時刻 `__TIME__`（`16:35:58` と `16:37:14`）。`SOURCE_DATE_EPOCH` を固定すると消える。
- **`CMakeLists.tecsgen.cmake` と `Makefile.templ` の 2 ファイル**: 標準 CDL のサブディレクトリ（`$(TECSPATH)/mruby`・`rpc`・`TLSFMalloc`・`DataPumpHolder`・`posix`・`TECSInfo`）を並べる順序だけが違う。tecsgen は `Dir.foreach( $tecspath )`（Python 版は `os.listdir`）の**生の列挙順**をそのまま使う。Ruby 版は ext4 上のコピー（`mruby sMalloc.cdl rpc TLSFMalloc DataPumpHolder …` のハッシュ順）、Python 版の `tecs/` は `/mnt/e` 上でファイル名順。**同じ `tecs/` に対して Ruby 版を実行すると、Python 版と同じ順になる**ことを確認した（ディレクトリが違うことによる差）。同じ名前のヘッダが複数のディレクトリにあれば `-I` の順で結果が変わるが、今回は影響しなかった（イメージが一致）
- **`cfg1_out`（中間の ELF）**: ビルドディレクトリ名（`build/rb` と `build/py`）がデバッグ情報に入るため

## ほかの 3 ボード（2026-10-09）

TECS（`Asp3Tecs.cmake`・tecsgen）を使うのは、**NUCLEO-H563ZI と STM32N6570-DK だけ**（`README.md`「TECS: NUCLEO-H563ZI と STM32N6570-DK で既定有効」。H533・C562 への展開は予定）。

| ボード | `Asp3Tecs.cmake` / tecsgen | 結果 |
|---|---|---|
| NUCLEO-H533RE | **使わない**（`CMakeLists.txt` に `asp3_tecs_*` が無く、`asp3_add_syssvc` の通常の C のシステムサービス） | 対象外 |
| NUCLEO-C562RE | **使わない**（同上。STM32CubeMX2・CMSIS-Toolbox の別系統） | 対象外 |
| STM32N6570-DK（`FSBL`） | `ASP3_ENABLE_TECS` が既定 ON | **確認した**（下） |

### STM32N6570-DK（FSBL）

H563ZI と同じ方法で、Ruby 版と Python 版（`-DASP3_TECSGEN_COMMAND`）の configure からリンクまでを通した。

- **代用品**: `cmsis-device-n6` `81fe2fe`（v1.4.0）、`stm32n6xx-hal-driver` `d88071e`（v1.4.0）、`cmsis-core`。`FSBL/Inc/stm32n6xx_hal_conf.h`（雛形のモジュールをすべて有効化）、`stm32n6xx_it.h`（ハンドラ定義から生成）、`Src/system_stm32n6xx.c`（`system_stm32n6xx_fsbl.c`）、`Src/stm32n6xx_hal_msp.c`、スタートアップ（`startup_stm32n657xx_fsbl.s`）、リンカスクリプト（`STM32N657XX_AXISRAM2_fsbl.ld`）、`gcc-arm-none-eabi.cmake`（`-mcpu=cortex-m55 -mfpu=fpv5-d16 -mfloat-abi=hard -mcmse`）、`FSBL/mx-generated.cmake`（`stm32cubemx` と `STM32_Drivers`）。USBX・FatFs・`board_*` はリポジトリに追跡されているものをそのまま使った
- **代用品側の調整**: `mx-generated.cmake` の `target_link_libraries` は、後続の行（plain 形式）に合わせて plain 形式にした（キーワード形式だと「混在」で configure が失敗する）。実プロジェクトのコードは旧名のマクロ `RCC_USBPHY2REFCLKSOURCE_HSE_DIRECT` を使うが、HAL v1.4.0 では `RCC_USBPHY2CLKSOURCE_HSE_DIRECT` に改名されているため、コンパイル定義で互換を取った（両方に同じ条件）
- **結果**:

| 項目 | 結果 |
|---|---|
| configure・コンパイル・リンク | 両方成功（`Built target N6570DK_FSBL`） |
| `generated/` | 161 ファイルで一覧が同一。159 ファイルが一致、残り 2 ファイル（`CMakeLists.tecsgen.cmake`・`Makefile.templ`）は H563 と同じ、`$(TECSPATH)` のサブディレクトリの並び順だけの差（順序を無視した集合は一致） |
| セクション・シンボル・サイズ | 完全に一致（`text 134168`・`data 476`・`bss 71500`） |
| 最終イメージ（`SOURCE_DATE_EPOCH` 固定のクリーンビルド） | **SHA-256 まで一致**（`6fd3542e…cbe9`、135,520 バイト） |

実際の N6570-DK で必要な手順（BOOT スイッチ、`scripts/run_n6.sh`、OpenOCD での SRAM ロード）は実施していない。

## 確認していないこと

- **実機**: ボードがなく、書込み・起動・シリアル出力は未確認（H563ZI も N6570-DK も）
- **実際の CubeMX の生成物**: 上は ST の公開テンプレートで代用した。tecsgen にとっては入力（ヘッダ・インクルードパス）が同じなら生成物は決まるので、Ruby 版との比較には影響しないが、`main.c` 周りの HAL 初期化が本物の CubeMX と同じとは限らない
- **H533・C562 に TECS を展開したとき**: 現状は TECS を使わないので対象外。展開したら、同じ方法で確認する
- **ビルドスクリプトの保存**: 設定と実行のスクリプトは、スクラッチパッドと WSL の `~/p2work/asp3build`（`repo/`・`dl/`・`build/{rb,py}`）にあり、リポジトリには入れていない

## Related

- [[tecsgen-python3 cmake対応計画]] — 本体
- [[tecsgen-python3]] — 親ノート
