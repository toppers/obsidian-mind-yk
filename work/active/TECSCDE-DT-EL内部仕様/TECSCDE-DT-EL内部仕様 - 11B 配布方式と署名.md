---
date: 2026-10-10
description: "配布方式・設定登録・対象OSでの実機検証を分離した状態表と署名候補。macOSはDMG＋ZIP、LinuxはDEB＋RPMの設定登録済み、実機検証は未確認として管理する。2026-11-08に監査#20を反映。"
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

> [!info] 配布方式・設定登録・実機検証の区別（2026-11-08、監査#20で整理）
> 配布形式の決定、設定ファイルへの登録、対象OSでのビルド・公開・実機検証は別の段階として扱う。状態の参照元はこの表に統一し、後段や第11章で「未実装」「Windowsのみ」という旧状態を再掲しない。
>
> | OS | 配布形式・方式 | 方式決定 | 設定登録 | 対象OSでの検証 | 節 |
> |---|---|---|---|---|---|
> | Windows | Squirrel.Windows。`maker-squirrel`、`publisher-github`（`draft: true`）、`update-electron-app` | 決定済み（2026-09-12／09-23） | 実装済みの既存記録あり | 既存の実装記録を参照。本件では再検証しない | 第11章11.2 #2 |
> | macOS | DMG＋ZIP。`maker-dmg`と`maker-zip`（DMGは初回、ZIPは自動更新用） | 決定済み（2026-10-09） | **設定登録済み**。2026-10-28登録の記録を、基準実装`main`・`86f8910`で確認 | **実機未検証として管理**。完了記録は未確認。CIの2026-10-28の注記は未実行・未検証 | 11.2.2 |
> | Linux | DEB＋RPM。`maker-deb`と`maker-rpm` | 決定済み（2026-10-10） | **設定登録済み**。2026-10-28登録の記録を、基準実装`main`・`86f8910`で確認 | **実機未検証として管理**。完了記録は未確認。CIの2026-10-28の注記は未実行・未検証 | 11.2.3 |
>
> **設定登録済み**はMakerとCIの登録をファイル上で確認したことを意味し、ジョブ実行・成果物生成・公開・インストール・起動・更新の成功を含まない。**実機未検証**は、本書で対象OSの検証完了を確認していない管理状態である。今回、対象OSでのビルド・実機検証や現在までのCI実行履歴の調査は行っていない。
>
> **コード署名**: 当面は未署名で配布する（2026-09-23決定。[[work/active/tecs/TECSCDE-DT-EL 配布アーキテクチャ決定|配布アーキテクチャ決定]]）。署名方式は未決で、Windows向けの候補を11.2.1節で比較している。macOSの署名・公証、Linuxの配布物の署名は、それぞれの後続検討事項（11.2.2、11.2.3）。

**確認した設定とチェックアウトの範囲（2026-11-08）**: 基準実装`main`・`86f8910`の`forge.config.js`にmacOS/Linuxの各Maker、`.github/workflows/release.yml`にWindows・macOS・Ubuntuのmatrixが登録されている。旧作業用チェックアウト`ykominami/TECSCDE-DT-EL-codex`・`a1f4ab9`はWindows向け設定のみであり、この差を基準実装全体の未登録・未実装とは扱わない。


#### 11.2.1 Windowsインストーラーのコード署名候補（2026-10-09、署名方式は未決。配布形式のSquirrelは決定済み）

対象は現行の Electron Forge 8／Squirrel.Windows で生成し、GitHub Actions（`windows-latest`）から GitHub Releases に公開する Windows 版とする。署名主体・費用・審査条件が未確定のため、以下は**署名方式の候補案であり、採用決定・実装済みではない**（配布形式そのもの＝Squirrelは決定済み・実装済み）。macOS/Linux 向け Maker の選定は本項の対象外。

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

#### 11.2.2 macOS向けパッケージング方式（方式決定: 2026-10-09、設定・検証状況は冒頭表）

**採用する方式: Electron Forge の `@electron-forge/maker-dmg` と `@electron-forge/maker-zip` を併用する。** DMG を初回インストール用、ZIP を macOS の自動更新用として GitHub Releases に置く構成を採用する（決定済み）。現行の Electron Forge と GitHub Releases を継続でき、Forge も DMG 配布で自動更新を行う場合は ZIP の併用を案内している。2026-10-09の決定は方式選定の記録であり、その後の設定登録は冒頭表の別段階として扱う。いずれもmacOSビルド・署名・公証・公開・実機検証の完了とは区別する。

| 候補 | 特徴 | 判定 |
| --- | --- | --- |
| Electron Forge の DMG＋ZIP | DMG で初回配布、ZIP で macOS の自動更新に対応する。既存の Forge／GitHub Releases を利用できる。 | **採用** |
| Electron Forge の ZIP のみ | 配布物は少ないが、利用者が展開してアプリを配置する必要がある。 | 今回は採用しない |
| Electron Forge の PKG＋ZIP | インストールウィザードやインストールスクリプトが必要な場合に適する。自動更新用の ZIP は別途必要。 | 今回は採用しない |
| electron-builder による DMG＋ZIP | 複数形式を一元設定できるが、既存の Forge 設定・公開処理からの移行が必要。 | 今回は採用しない |
| Mac App Store 配布 | Store 専用ビルド、Sandbox、Apple Distribution 署名、審査が必要で、現行の GitHub Releases とは別経路になる。 | 今回は採用しない |

**後続の検討・検証事項:** 設定登録の状態は冒頭表を参照し、MakerとmacOSジョブの追加自体を未着手事項として繰り返さない。対象アーキテクチャ、対象OSでのビルドとDMG／ZIP生成、Developer ID署名と公証、インストール・起動、ZIPを用いた更新、公開を個別に確認する。基準実装の署名・公証設定は未設定という記録を保持する。配布物が生成・公開されたかは、設定登録だけから断定しない。

参照: [Forge DMG maker](https://www.electronforge.io/config/makers/dmg)、[Forge ZIP maker](https://www.electronforge.io/config/makers/zip)、[Forge PKG maker](https://www.electronforge.io/config/makers/pkg)、[Forge の自動更新](https://www.electronforge.io/advanced/auto-update)、[Forge の macOS 署名・公証](https://www.electronforge.io/guides/code-signing/code-signing-macos)、[Electron の Mac App Store ガイド](https://www.electronjs.org/docs/latest/tutorial/mac-app-store-submission-guide)。

#### 11.2.3 Linux向けパッケージング方式（方式決定: 2026-10-10、設定・検証状況は冒頭表）

**採用する方式: Electron Forge の `@electron-forge/maker-deb` と `@electron-forge/maker-rpm` を併用する。** DEBとRPMをLinux向け配布物として生成する方針とする。2026-10-10の決定は方式選定の記録であり、その後のMaker・CI登録は冒頭表の別段階として扱う。方式決定や設定登録だけで、Linux向けビルド・公開・インストール検証を完了した意味にはしない。

| 候補 | 特徴 | 判定 |
| --- | --- | --- |
| Electron Forge の DEB＋RPM | 既存の Forge で Debian 系・RPM 系の両形式を生成できる。 | **採用** |
| Electron Forge の DEB のみ | Debian 系への配布に絞る構成で、RPM 系向けの配布物は生成しない。 | 今回は採用しない |
| Electron Forge の RPM のみ | RPM 系への配布に絞る構成で、Debian 系向けの配布物は生成しない。 | 今回は採用しない |
| Snap | Snap の配布基盤を利用する方式。Forge の DEB／RPM maker とは別の配布・更新経路になる。 | 今回は採用しない |
| Flatpak | Flatpak の配布基盤を利用する方式。Forge の DEB／RPM maker とは別の配布・更新経路になる。 | 今回は採用しない |

**後続の検討・検証事項:** 設定登録の状態は冒頭表を参照し、MakerとLinuxジョブの追加自体を未着手事項として繰り返さない。対象アーキテクチャ、対象OSでのビルドとDEB／RPM生成、対応ディストリビューションでのインストール・起動、GitHub Releasesへの公開を確認する。Linux向け自動更新の方式は別途検討する。配布物が生成・公開されたかは、設定登録だけから断定しない。

参照: [Forge DEB maker](https://www.electronforge.io/config/makers/deb)、[Forge RPM maker](https://www.electronforge.io/config/makers/rpm)、[[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]]、[[work/active/tecs/Electron Forgeの使い方|Electron Forgeの使い方]]。
