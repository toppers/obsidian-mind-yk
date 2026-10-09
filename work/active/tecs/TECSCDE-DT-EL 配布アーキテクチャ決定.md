---
date: 2026-09-23
description: "TECSCDE-DT-ELの配布設計決定 — originを非公開から公開へ変更し、toppers/tecscde-dt-el自身へupdate-electron-app + GitHub Releasesで自動更新、GitHub Actions（Node 22固定）でpublishまで自動化する。ミラーリポジトリ案は検討したが採用しなかった（当日中にorigin公開化でスコープ外に）。コード署名・macOS/Linux対応は引き続き未決。"
project: TECS
quarter: Q3-2026
status: accepted
tags:
  - decision
  - tecs
  - tecscde
---

# Decision: TECSCDE-DT-ELの配布はoriginへの直接publish＋自動更新とする

## Context

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様11.2節#2]]は、パッケージング（package/make、Electron Forge + `@electron-forge/maker-squirrel`）のみ2026-09-12に決定済みで、自動更新・コード署名・macOS/Linux向けMakerは範囲外のまま未決だった。実装（[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]、`E:\Ccur\typescript\TECSCDE-DT-EL`）は2026-09-20の実機対話的確認・279テストpassまで進み、配布の残り論点を詰める段階にある。

2026-09-23、配布設計のセッションでユーザーと以下を確認した: 対象OSはWindowsのみ（現状のmaker-squirrel維持）、コード署名は当面見送り、自動更新は`update-electron-app` + GitHub Releases、リリース自動化はGitHub Actionsまで設計する。

設計の途中、実リポジトリを確認したところ、push先の`origin`（`git@github.com:toppers/tecscde-dt-el.git`、TOPPERS組織）が**非公開（PRIVATE）**であることが判明した。`update-electron-app`の既定サービス（`update.electronjs.org`）は非公開リポジトリのリリース資産を認証なしで取得できないため、このままでは自動更新が機能しない。この時点でユーザーは「配布専用の公開ミラーリポジトリを新設する」方針を選び、いったんそちらで設計を確定させた。

**同日中に状況が変わった**: ユーザーがTOPPERS組織側で`origin`をpublicへ変更した（本人確認、2026-09-23）。これによりミラーリポジトリを新設する動機（非公開originでは`update.electronjs.org`が使えない）が消え、origin自身へ直接publishする単純な構成が可能になった。本ノートは最終的に確定したこの構成を記録する。

## Options Considered

1. **origin（`toppers/tecscde-dt-el`）へ直接publishする**（最終採用）
   - 利点: 追加リポジトリ不要。`@electron-forge/publisher-github`のpublish先をソースリポジトリ自身にできる。認証も同一リポジトリへの書き込みのため既定の`GITHUB_TOKEN`で足り、cross-repo用のPAT管理が不要。
   - 前提: originがpublicであること（2026-09-23、ユーザーがTOPPERS組織側で変更し充足）。
2. **electron-updaterのGenericServerで自前ホスト**
   - 利点: リポジトリ可視性に依存しない。
   - 欠点: 自前サーバ／ストレージの追加インフラが要り、現状の個人開発規模には見合わない。パッケージング基盤も`electron-builder`系へ乗り換える必要がありForge資産・既知gotcha対処が作り直しになる。origin公開化により動機が消えたため不採用。
3. **配布専用の公開ミラーリポジトリを新設する**（いったん採用→origin公開化により撤回）
   - 利点（当時）: ソースを非公開に保ったまま配布だけ公開できる。組織のポリシー判断を経ずに個人の裁量で開始できる。
   - 撤回理由: origin自体がpublicになったことで、ミラーリポジトリが解決するはずだった問題（非公開originからのpublic配布）が消滅した。二層構成を維持するメリットがなくなり、追加リポジトリの保守コストだけが残る。

## Decision

**選択肢1**（originへの直接publish）を採用。ユーザーがorigin可視性を変更したことで確定（2026-09-23）。

設計の詳細:

1. **リリースアーキテクチャ**: `origin`（`toppers/tecscde-dt-el`、現在public）へ`@electron-forge/publisher-github`で直接publishする。Squirrelの成果物（`Setup.exe`／`RELEASES`／`.nupkg`）はソースリポジトリのGitHub Releasesにそのまま公開される。追加のミラーリポジトリは作らない。
2. **自動更新**: `update-electron-app`を導入する。`repo`オプションは`package.json`の`repository`フィールドから自動推測させるか、明示的に`'toppers/tecscde-dt-el'`を指定する（どちらでも可、実装時に選ぶ）。originが公開であるため`update.electronjs.org`がそのまま使える。
3. **コード署名**: 当面は未署名のまま（新規決定なし）。SmartScreen警告は許容する。将来の切替ポイントは[[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]]を参照。
4. **CI/CD（GitHub Actions）**: ワークフローはソースリポジトリ（`toppers/tecscde-dt-el`）に置く。
   - トリガー: `v*`形式のタグpush。
   - runner: `windows-latest`（`maker-squirrel`がWindows専用のため）。
   - Node: **22 LTS固定**（`actions/setup-node@v4`で`node-version: '22'`を明示）——[[Gotchas - Electron Forge Packaging]]の「`@electron/packager`がこのマシンの既定Node（26系）で無期限にハングする」gotchaに基づく既知の制約。CI runnerでも同じ`@electron/packager`が動くため、既定のNode最新版ではなく22系を明示的に固定する必要がある。
   - ステップ: `npm ci` → `npm run check`（build + test + depcruise） → `npx electron-forge publish`。
   - 認証: **既定の`GITHUB_TOKEN`で足りる**（`contents: write`権限を明示的に付与すれば良い）。ミラーリポジトリ案で必要だったcross-repo用fine-grained PATの発行・Secrets登録は不要になった。
5. **バージョニング**: `package.json`の`version`（SemVer）とgitタグ`v{version}`を一致させる。初回リリースのバージョン番号自体は実装時判断とする。
6. **README**: 現状の「`electron .`起動は未検証」という記述は2026-09-20の実機確認で事実と乖離している。実装時タスクとして、検証状況の更新とエンドユーザー向けインストール／更新手順の追加を行う。

## Consequences

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|11.2節#2]]のうち自動更新の実現手段が決定済みになる。コード署名・macOS/Linux向けMakerは引き続き未決のまま残る。
- 実リポジトリ側の実装（`forge.config.js`への`publisher-github`設定追加、GitHub Actionsワークフローファイルの追加、`update-electron-app`導入、README更新）は本決定を土台にした別セッションでの実装タスクとする（未着手）。フォローアップは[[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]]のAction Itemsに記載。
- **origin可視性の変更（private→public）自体が本決定の一部として実行済み**——TOPPERS組織のリポジトリを公開にしたという事実は、コード側の変更ではなく組織側の設定変更であり、コードだけを読んでも分からない。将来「なぜこのリポジトリはpublicなのか」を確認する読者は本ノートを参照する必要がある。
- **手放したもの**: ソースコードを非公開に保つ選択肢（ミラーリポジトリ案が実現しようとしていたもの）。今後ソースを再び非公開に戻す場合は、配布アーキテクチャの再設計（ミラーリポジトリ案の再検討）が必要になる。
- 姉妹実装[[work/active/TECSCDE-DT-TA実装/TECSCDE-DT-TA実装|TECSCDE-DT-TA実装]]（Tauri版）は別エコシステム（`tauri-plugin-updater`）のため本決定の対象外——[[work/active/TECSCDE-DT-TA内部仕様/TECSCDE-DT-TA内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-TA内部仕様11.2節#5]]は引き続き未決のまま。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章11.2節#2]] — 対応する未決事項（本決定で自動更新部分を解消）
- [[work/active/tecs/Electronアプリの配布・自動更新ツール|Electronアプリの配布・自動更新ツール]] — 選定時に比較したツール一覧
- [[work/active/tecs/Electronアプリのコード署名|Electronアプリのコード署名]] — 未署名のまま据え置く判断の背景
- [[brain/Gotchas - Electron Forge Packaging|Gotchas - Electron Forge Packaging]] — CI runnerでもNode 22固定が必要な根拠
- [[work/active/TECSCDE-DT-EL実装/TECSCDE-DT-EL実装|TECSCDE-DT-EL実装]] — フォローアップ実装タスクの記録先
- [[work/active/tecs/TECSCDE-DT-EL preload ESM・sandbox決定|TECSCDE-DT-EL preload ESM・sandbox決定]] — 同じく実装着手時に判明して記録した設計決定（同形式の先例）
- [[work/active/tecs/TECS開発|TECS開発]] — 開発進捗全体
