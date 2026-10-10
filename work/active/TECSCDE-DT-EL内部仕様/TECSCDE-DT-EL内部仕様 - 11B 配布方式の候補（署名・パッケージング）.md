---
date: 2026-10-10
description: "TECSCDE-DT-EL内部仕様 第11章 11.2.1〜11.2.3 — Windowsインストーラーのコード署名候補、macOS／Linux向けパッケージング方式。25KB閾値で第11章から逐語分離"
project: TECS
quarter: Q4-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
---

Domain note split from [[TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案]] (2026-10-10, 25KB threshold). 本文は第11章の 11.2.1〜11.2.3 を逐語で移動したもの。上位: [[TECSCDE-DT-EL内部仕様]]。関連: [[Electronアプリのコード署名]]・[[Electronアプリの配布・自動更新ツール]]。

#### 11.2.1 Windowsインストーラーのコード署名候補（2026-10-09、未決）

対象は現行の Electron Forge 8／Squirrel.Windows で生成し、GitHub Actions（`windows-latest`）から GitHub Releases に公開する Windows 版とする。署名主体・費用・審査条件が未確定のため、以下は**候補案であり採用決定・実装済みではない**。macOS/Linux 向け Maker の選定は本項の対象外。

| 候補 | 適用条件と運用上の論点 | 現行配布方式への影響 |
| --- | --- | --- |
| Azure Artifact Signing（旧 Trusted Signing） | Microsoft の Public Trust 対象として日本の**組織**は申請可能。Azure サブスクリプション、組織確認、証明書プロファイル、署名権限が必要。個人向け Public Trust は現時点で米国・カナダ限定。月額料金と組織確認の所要時間を申請前に確認する。 | GitHub Actions から署名可能。現行の Squirrel／GitHub Releases を維持できる。 |
| SignPath Foundation | OSI 承認ライセンスなどの OSS 条件と審査を満たす場合に利用可能。ソースから検証可能なビルド、各リリースの**手動承認**などが必要。採用可否は審査次第。 | 無料の署名候補だが、タグ push だけで完結する無人リリースには承認工程を追加する。 |
| 民間認証局の OV／EV コード署名証明書 | 発行者確認、証明書費用、秘密鍵の安全な保管と CI からの利用方法を検討する。EV でも SmartScreen 警告の即時解消は保証されない。 | 現行の Squirrel／GitHub Releases を維持できる。証明書の保管方法に応じて CI 設定が変わる。 |
| Microsoft Store の MSIX 配布 | Store 経由の MSIX は Microsoft による再署名を利用できる。Store で EXE/MSI を配布する場合は発行者による署名が必要。 | 現行の Squirrel `Setup.exe`／GitHub Releases 配布から方式を変更する別案。 |
| 自己署名証明書 | ビルド・検証手順の開発には利用できるが、一般ユーザーの Windows に信頼される公開配布用署名にはならない。 | 本番の署名候補からは除外する。 |

**選定条件:** 署名主体が日本の組織か個人かを確定し、各サービスの審査資格、継続費用、秘密鍵の管理、GitHub Actions での運用、リリース承認者を比較する。公開 OSS として SignPath Foundation の条件を満たすかも確認する。署名方式の決定後も、SmartScreen の評価は別途蓄積されるため、署名だけで警告が消えるとは規定しない。

**実装・検証条件:** 現行方式を維持する候補では、Forge の `packagerConfig.windowsSign`（アプリ本体）と Squirrel maker の `windowsSign`（インストーラー生成時）の双方を設定し、公開前に `Setup.exe` とインストール後のアプリ実行ファイルを `signtool verify /pa /v` で検証する。タイムスタンプを付け、署名または検証に失敗した成果物は publish しない。Squirrel の `*.nupkg`／`RELEASES` 内の署名対象は採用方式で実際の生成物を確認する。

参照: [Microsoft の署名方式比較](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options)、[Artifact Signing の開始手順](https://learn.microsoft.com/en-us/azure/artifact-signing/quickstart)、[SignPath Foundation の条件](https://signpath.org/terms)、[Electron Forge の Windows 署名設定](https://www.electronforge.io/guides/code-signing/code-signing-windows)、[SmartScreen の評価](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)。

#### 11.2.2 macOS向けパッケージング方式（2026-10-09、候補選定済み・未実装）

**採用する方式: Electron Forge の `@electron-forge/maker-dmg` と `@electron-forge/maker-zip` を併用する。** DMG を初回インストール用、ZIP を macOS の自動更新用として GitHub Releases に置く構成を第一候補として選定した。現行の Electron Forge と GitHub Releases を継続でき、Forge も DMG 配布で自動更新を行う場合は ZIP の併用を案内している。この決定は**パッケージング方式の選定のみ**であり、macOS ビルド・署名・公証・公開・実機検証を完了した意味ではない。

| 候補 | 特徴 | 判定 |
| --- | --- | --- |
| Electron Forge の DMG＋ZIP | DMG で初回配布、ZIP で macOS の自動更新に対応する。既存の Forge／GitHub Releases を利用できる。 | **採用** |
| Electron Forge の ZIP のみ | 配布物は少ないが、利用者が展開してアプリを配置する必要がある。 | 今回は採用しない |
| Electron Forge の PKG＋ZIP | インストールウィザードやインストールスクリプトが必要な場合に適する。自動更新用の ZIP は別途必要。 | 今回は採用しない |
| electron-builder による DMG＋ZIP | 複数形式を一元設定できるが、既存の Forge 設定・公開処理からの移行が必要。 | 今回は採用しない |
| Mac App Store 配布 | Store 専用ビルド、Sandbox、Apple Distribution 署名、審査が必要で、現行の GitHub Releases とは別経路になる。 | 今回は採用しない |

**後続の検討・検証事項:** `forge.config.js` への maker 追加、macOS 用 GitHub Actions ジョブ、x64／arm64（または universal）の配布方法、Developer ID 署名と公証、DMG からのインストール、ZIP を用いた自動更新を個別に設計・検証する。これらは本決定では確定しない。現時点の `forge.config.js` と release workflow は Windows の Squirrel 配布のみで、macOS の配布物は未生成。

参照: [Forge DMG maker](https://www.electronforge.io/config/makers/dmg)、[Forge ZIP maker](https://www.electronforge.io/config/makers/zip)、[Forge PKG maker](https://www.electronforge.io/config/makers/pkg)、[Forge の自動更新](https://www.electronforge.io/advanced/auto-update)、[Forge の macOS 署名・公証](https://www.electronforge.io/guides/code-signing/code-signing-macos)、[Electron の Mac App Store ガイド](https://www.electronjs.org/docs/latest/tutorial/mac-app-store-submission-guide)。

#### 11.2.3 Linux向けパッケージング方式（2026-10-10、候補選定済み・未実装）

**採用する方式: Electron Forge の `@electron-forge/maker-deb` と `@electron-forge/maker-rpm` を併用する。** DEB と RPM を Linux 向け配布物として生成する方針とする。既存の Forge に maker を追加する構成で、両形式の利用者を対象にできる。この決定は**パッケージング方式の選定のみ**であり、Linux 向けビルド・公開・インストール検証を完了した意味ではない。

| 候補 | 特徴 | 判定 |
| --- | --- | --- |
| Electron Forge の DEB＋RPM | 既存の Forge で Debian 系・RPM 系の両形式を生成できる。 | **採用** |
| Electron Forge の DEB のみ | Debian 系への配布に絞る構成で、RPM 系向けの配布物は生成しない。 | 今回は採用しない |
| Electron Forge の RPM のみ | RPM 系への配布に絞る構成で、Debian 系向けの配布物は生成しない。 | 今回は採用しない |
| Snap | Snap の配布基盤を利用する方式。Forge の DEB／RPM maker とは別の配布・更新経路になる。 | 今回は採用しない |
| Flatpak | Flatpak の配布基盤を利用する方式。Forge の DEB／RPM maker とは別の配布・更新経路になる。 | 今回は採用しない |

**後続の検討・検証事項:** `forge.config.js` への maker 追加、Linux 用 GitHub Actions ジョブ、ビルド対象アーキテクチャ、DEB／RPM の生成と対応ディストリビューションでのインストール・起動、GitHub Releases への公開方法を設計・検証する。Linux 向け自動更新の方式は別途検討する。現時点の配布設定は Windows の Squirrel のみで、Linux の配布物は未生成。

参照: [Forge DEB maker](https://www.electronforge.io/config/makers/deb)、[Forge RPM maker](https://www.electronforge.io/config/makers/rpm)、[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]、[[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]]。
