---
date: 2026-09-22
description: "TECSCDE-DT-EL内部仕様書 第7C章（読み込み経路の統合）— 第11章11.2節#7〜#11（前回セッション復元・ファイルブラウザからの参照専用追加・消去ボタン・tecsgenオプション形式ファイルの一括読み込み・import自動追跡との統一）の設計。7.6節（第7B章）の続きとして新設（2026-09-22）。"
project: TECS
quarter: Q3-2026
status: active
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

Domain note new from [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章]]の続き（7.7節）として新規追加（2026-09-22）。[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|第11章]]11.2節#7〜#11（いずれもユーザー要望・2026-09-22追加、「ファイルの発見経路によらず統一的に管理する」という共通テーマ）の設計をまとめる。

> [!info] #8/#10/#11の実装前提（2026-09-22追記）
> 本章が「既存のresolveImports()」と呼ぶ対象は、執筆当時は型定義のみで具体アルゴリズムが未確定だった。同日中に[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章]]・[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]が具体設計を確定した。本章の記述（7.7.2・7.7.4・7.7.5節）は変更していない——7D/7E章がその実装前提を満たす。

## 7.7 読み込み経路の統合 — 2026-09-22追加

決定事項（2026-09-22、ユーザー確認）: #8「ファイルブラウザで選択したファイルを既存の編集対象へ追加する」は**参照専用として追加し、既存の編集対象(editable)は変えない**（11.2節#8の解釈(a)）。この決定により、#11「import自動追跡との統一」は自然な形で解ける——手動追加を[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|第7D章]]／[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|第7E章]]の`resolveImports`と同じパイプラインに乗せることで、発見経路（手動選択／import自動追跡）によらず同一のデータ構造・重複抑止規則で管理できる（7.7.5節）。

### 7.7.1 前回セッションの復元（#7）

[[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章7.6.6節]]の`AppSettings`（ルートフォルダの永続化）に、開いていたファイル集合を追加する。

```ts
// main/app-settings.ts の AppSettings 拡張
export interface AppSettings {
  readonly fileBrowserRoot?: string;
  readonly lastSession?: {
    readonly editablePath: string;
    readonly referencePaths: readonly string[];
  };
}
```

**保存タイミング**: 7.6.6節の「都度保存」方針を踏襲する。編集対象(editable)または参照(references)集合が変化するたび——ファイルブラウザでの`openFromPath`（7.6.4節）・7.7.2節の`addAsReference`・7.7.3節の新規作成・起動時オープン（第7章7.4節）——に保存する。「終了時にまとめて保存」を採らない理由も7.6.6節と同じ（異常終了時にも直前の状態を残すため）。

**復元の優先順位**: 起動時、`pendingOpenPath`（第7章7.4節、コマンドライン引数・ファイル関連付け）を最優先とする。次に`lastSession`があればそれを使う。どちらも無い場合のみ`public/samples`の固定ファイルへフォールバックする（既存の最終フォールバックを維持）。

**復元失敗時**: 7.6.6節の`restoreRoot`と同じ方針——記憶されたパスが存在しない・読めない場合はエラーにせず、次善のフォールバック（`lastSession`が読めなければ`samples`）へ進む（3.5.1節「解決できない場合は黙って進める」と同じ考え方）。

```ts
// main/index.ts（did-finish-loadハンドラ、第7章7.4節app:bootstrapの供給元を拡張）
const settings = await loadAppSettings();
const initialSources = pendingOpenPath
  ? await loadFromPath(pendingOpenPath)
  : settings.lastSession
    ? await loadLastSession(settings.lastSession).catch(() => loadSamples())
    : loadSamples();
```

`app:bootstrap`のIPC自体（起動後1回だけプッシュ供給、第7章7.4節）は変わらない。供給するソーステキスト群の生成元が3経路（CLI引数／前回セッション／samples）に増えるのみ。

### 7.7.2 ファイルブラウザからの参照専用追加（#8）

決定(a): 参照専用として追加し、既存のeditableは変えない。

**UI操作**: ツリー上のファイルをクリック（既存、7.6.4節`openFromPath` = 編集対象として開く）に加え、**Ctrl+クリックで「参照専用として追加」**とする。

> [!note] UI操作の選定について（inferred・未検証）
> [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様3.5.1節]]に新設する画面規定候補。右クリックメニューも代替案として考えられるが、階層ツリーの各行に対する二値の操作としてはCtrl+クリックが実装コストが低く、既存の「クリック＝開く」を変更せずに済む。最終的なキー割当・ラベルは実装時に確定する。

**重複判定**: 11.2節#8の決定どおり、選択したファイルが既に読み込み済み（editableまたはreferencesのいずれかと同一の正規化済み絶対パス）であれば無視する（第7章7.5節の`import`重複抑止と同じキー）。

**実現方式（#11との統合、7.7.5節）**: 新規クラスは設けず、`import`自動追跡と全く同じ読み込みパイプライン（第7章7.5節`FileService.resolveImports()`）を、手動選択したファイルを起点として1回実行する。`ImportRequest`に絶対パス指定の種別を追加する。

```ts
// shared/ipc-types.ts の ImportRequest 拡張（第7章7.5節）
interface ImportRequest {
  readonly kind: 'import' | 'import_C' | 'manual'; // 'manual' を追加
  readonly specifier: string; // kind: 'manual' の場合は絶対パスそのもの
}
```

```ts
// renderer/app/file-actions.ts
export async function addAsReference(store: AppStore, gateway: FileGateway, path: string): Promise<void> {
  if (store.hasDocument(path)) return; // 重複は無視（#8決定）
  const resolved = await gateway.resolveImports(store.editablePath, [{ kind: 'manual', specifier: path }], {
    importPaths: [],
  });
  applyResolvedReferences(store, resolved); // 選択ファイル自身とその再帰的import先を全てreferencesへ追加
}
```

`kind: 'manual'`は、`FileService.resolveImports()`内でパスの正規化・存在確認のみ行い（`base_dir`・`import_path`探索を経由しない——絶対パスが直接指定されているため）、以降の処理（UTF-8読み取り、モジュールBでの再帰的import解決、循環・重複抑止）は既存の`import`と完全に共有する。手動追加したファイル自身がさらに`import`していれば、その参照先も連鎖的にreferencesへ加わる——import自動追跡と同じ挙動になる（7.7.5節）。

未保存確認（7.6.4節`confirmDiscardChanges`）は不要——既存のeditableを置き換えないため。

### 7.7.3 消去ボタン（#9）— 新規作成の別名

決定（ユーザー確認済み）: [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.2節]]の新規作成（既定用紙の空図、ファイル名は保存まで未確定）と同一機能の別名として設計する。DT-EL実装には現状これに相当するツールバー操作が存在しないため（11.2節#9）、本節が初めて設計する。

```ts
// renderer/app/file-actions.ts
export async function newDocument(store: AppStore, gateway: FileGateway): Promise<void> {
  if (store.isDirty()) {
    const proceed = await gateway.confirmDiscardChanges(); // 7.6.4節と同じダイアログを再利用
    if (!proceed) return;
  }
  store.resetToBlank(); // 5.2節: 既定用紙、editable未確定（filePath: null）
}
```

**配線**: [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|第7B章7.6.5節]]と同様、ツールバーに`data-action="clear"`ボタンを追加し、`runAction`に`case 'clear':`を追加して`newDocument()`を呼ぶ。利用者向けラベルは要望どおり「消去」とするが、内部の関数名は外部仕様の用語（新規作成 = new）に揃える（既存の命名規則`openFromPath`/`chooseRoot`と同様、動作を表す名前とする）。

**影響範囲**: `references`集合・ファイルブラウザの展開状態（7.6.3節`expanded`/`children`）はクリアしない——消去は編集対象(editable)のみを空にする操作であり、参照ファイル一覧やツリーの展開状態はアプリケーション実行中の状態として維持する（3.5.1節「ツリーの展開状態はアプリケーション実行中の状態としてのみ保持する」と同じ扱い）。

**7.7.1節との関係**: 消去後に`lastSession`へ保存する`editablePath`は無し（未保存の新規作成はパスを持たないためセッション復元の対象外）。references集合は維持されたまま保存する。

### 7.7.4 tecsgenオプション形式ファイルの一括読み込み（#10）

> [!note] 位置づけ
> 本節はDT-EL固有の拡張として設計する。[[TECSCDE-DT外部仕様]]（言語非依存の親仕様）へ昇格するかどうかは未定——想定利用シーン（tecsgenビルド用Makefile等の実引数列をそのまま流用する運用）自体が未検証(inferred)のため、外部仕様は変更せず本書の範囲に留める。

**①ファイル形式・拡張子**: 新拡張子`.tecsgen-opts`を定義する（仮称、**inferred・命名は未確定**）。内容はtecsgenのコマンドライン引数をそのまま記述したプレーンテキスト（`-I <path>` / `--import-path=<path>` / CDLファイルパスの列挙、空白・改行区切り、`#`始まりの行はコメント）。

```ts
// main/file-service.ts の listDirectory() フィルタを変更（第7B章7.6.1節）
.filter((e) => e.isDirectory() || /\.(cde|cdl|tecsgen-opts)$/i.test(e.name))
```

**クリック時の分岐**: `FileBrowserView`（7.6.3節）はクリックされたファイルの拡張子で処理を分ける——`.cde`/`.cdl`は既存の`openFromPath`（7.6.4節）、`.tecsgen-opts`は本節の`loadOptionsFile`へ。

**②編集対象の決定**: 新規メソッド`FileService.parseTecsgenOptionsFile(path)`がテキストを解析し、列挙されたCDLファイル群・`-I`/`--import-path`の値・`cpp`指定（あれば）を返す。CDLファイルが複数列挙されている場合は、[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様5.3節]]・[[TECSCDE外部仕様]]8.1.2節の「最後に列挙されたファイルを編集対象とする」規則をそのまま適用する。

```ts
// main/file-service.ts に追加
export interface TecsgenOptionsFile {
  readonly cdlFiles: readonly string[]; // 列挙順。最後の要素が編集対象候補
  readonly importPaths: readonly string[]; // -I/--import-path の値
  readonly cpp?: string;
}

async parseTecsgenOptionsFile(path: string): Promise<TecsgenOptionsFile> {
  const text = await fs.promises.readFile(path, 'utf-8');
  // 空白・改行区切りのトークン化、`-I`/`--import-path=`の値をimportPathsへ、
  // それ以外の非オプショントークン（`-`で始まらない）をcdlFilesへ分類する。
  // 引用符の扱い等パース規則の詳細は実装時に確定。
}
```

**③`-I`/`--import-path`の受け渡し**: 既存の`ImportResolutionOptions.importPaths`（第7章7.5節）へそのまま渡す。CDLファイル自身の`__tool_info__`が持つ`import_path`・`base_dir`は5.1節の方針どおり書き換えず、オプションファイル由来の`importPaths`は追加の探索候補として重ねる（既定順序: CDL自身の`import_path`を先に試し、見つからなければオプションファイル由来を試す——第7章7.5節の既存探索順序に追加ステップとして挿入する）。

**④#8との統合**: 列挙されたCDLファイルのうち最後の1つを`openFromPath`（編集対象として開く、未保存確認込み）、残りを7.7.2節の`addAsReference`で参照専用として追加する。いずれも「既読み込み済みなら無視」規則（#8決定）が適用される。

```ts
// renderer/app/file-actions.ts
export async function loadOptionsFile(store: AppStore, gateway: FileGateway, path: string): Promise<void> {
  const parsed = await gateway.parseTecsgenOptionsFile(path);
  const [last, ...rest] = [...parsed.cdlFiles].reverse();
  for (const refPath of rest.reverse()) {
    await addAsReference(store, gateway, refPath); // 7.7.2節
  }
  if (last) await openFromPath(store, gateway, last, { extraImportPaths: parsed.importPaths }); // 7.6.4節を拡張
}
```

`openFromPath`（7.6.4節）は`extraImportPaths`を受け取れるようオプション引数を追加し、`FileGateway.resolveImports`呼び出しへ引き渡す。

### 7.7.5 import自動追跡との統一（#11）

7.7.2節の設計により、11.2節#11(b)「発見経路（手動選択／import自動追跡）によらず同じ内部データ構造（documents/referencesの集合）で管理する」は**既に満たされる**——手動追加(`addAsReference`)は`kind: 'manual'`という種別が増えるだけで、`FileService.resolveImports()`以降の解決・重複抑止パイプラインは完全に共有される。

#11(c)「編集可否も統一する」は**対象外のまま据え置く**（ユーザー確認済み）——[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様8.1節]]が既に定める「編集可否は定義元ファイルで決まる」規定は変更しない。手動追加・import自動追跡いずれで読み込まれたファイルも、常に参照専用（読み取り専用）として扱う。

残るは#11(a)「ツリー上での参照ファイルの表示」——[[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様3.5.1節]]が「実装時の検討事項」として明示的に未規定のまま残していた項目。本節で設計する。

```ts
// renderer/app/file-browser-panel.ts の render() を拡張（第7B章7.6.3節）
render(): void {
  // 既存: store.filePath と一致するノードへ「編集中」の強調クラスを付与
  // 追加: store.references の各パスと一致するノードへ「参照読み込み済み」の強調クラス（editableとは異なる見た目）を付与
  // 両方に該当するノードは無い（editableとreferencesは排他集合、第8章8.1節）
}
```

視覚的な区別（色・アイコン等）の具体は実装時に確定する（3.5.1節が委ねている「表示可否・様式」の範囲内であり、本書はクラス名の区別のみを規定する）。

## Related

- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07B ファイルブラウザ設計|TECSCDE-DT-EL内部仕様 第7B章（本節が前提とするファイルブラウザ基本設計）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07D インポート自動追跡|TECSCDE-DT-EL内部仕様 第7D章（本章#8/#10/#11が実装前提とするresolveImports()の具体設計）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07E インポート解決の統合|TECSCDE-DT-EL内部仕様 第7E章（同、renderer側統合）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 07 ファイルI-O設計|TECSCDE-DT-EL内部仕様 第7章（7.5節、7D/7E章の分離元）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様 - 11 未決事項と実装単位案|TECSCDE-DT-EL内部仕様 第11章（11.2節#7〜#11、本節が解消する決定記録）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 03 画面構成|TECSCDE-DT外部仕様 第3章（3.5.1節、Ctrl+クリック追加の画面規定）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 05 ファイル操作|TECSCDE-DT外部仕様 第5章（5.3節、参照専用追加経路の記述更新）]]
- [[work/active/TECSCDE-DT外部仕様/TECSCDE-DT外部仕様 - 08 CDL 連携|TECSCDE-DT外部仕様 第8章（8.1節、編集可否ルールの一次情報源）]]
- [[work/active/TECSCDE-DT-EL内部仕様/TECSCDE-DT-EL内部仕様|TECSCDE-DT-EL内部仕様（目次）]]

---
