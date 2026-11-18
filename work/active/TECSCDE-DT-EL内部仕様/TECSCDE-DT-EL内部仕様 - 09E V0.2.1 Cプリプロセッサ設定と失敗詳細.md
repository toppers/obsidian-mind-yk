---
date: 2026-11-11
description: "V0.2.1におけるCプリプロセッサ設定(cppPath, cppArgs)の永続化・解決・ファイルダイアログ連携と、決定理由・フルパス・失敗詳細(未検出・非ゼロ終了・タイムアウト)の構造化伝達の内部設計。"
project: TECS
quarter: Q4-2026
status: accepted
tags:
  - work-note
  - tecs
  - tecscde
  - spec
  - architecture
---

# 9E. V0.2.1 Cプリプロセッサ設定と失敗詳細

[[TECSCDE-DT-EL内部仕様]] 第2章（モジュール構成）、第7D章（インポート自動追跡）、第8章（メッセージ設計）、第9章（tecsgen連携設計）、第9D章（V0.2.0設定基盤）の追加設計です。根拠は [[TECSCDE-DT外部仕様 - Cプリプロセッサ設定と失敗詳細(V0.2.1用)]] です。

---

## 9E.1 モジュール構成と責務

| モジュール / ファイル | プロセス | 責務 |
|---|---|---|
| `shared/ipc-types.ts` | 共通型 | `CppResult` 失敗詳細フィールド・決定理由 (`originReason`)・フルパス (`fullPath`)、`ToolSettingsView`/`ToolSettingsUpdate` 拡張 |
| `main/app-settings.ts` | main | `settings.json` の `cppPath`・`cppArgs` の永続化 |
| `main/tool-settings.ts` | main | C プリプロセッサ設定の解決（CDL指定 ＞ 設定値 ＞ PATH上の `*gcc` ＞ 既定値）、決定理由判定、フルパス特定、実行ファイル参照ダイアログ |
| `main/tecsgen-runner.ts` | main | `preprocess()` におけるコマンド実行、タイムアウト制御、構造化エラー（`failureKind`, `failureDetail`）、決定理由およびフルパスの返却 |
| `main/ipc.ts` | main | `settings:chooseCppPath`（ファイル選択ダイアログ）等の IPC ハンドラ登録 |
| `preload/index.mts` | preload | `contextBridge` を通じた API の型安全な公開（`chooseCppPath()` 等） |
| `renderer/gateways/` | renderer | `TecsgenGateway`, `SettingsGateway` 経由の薄いプロキシ |
| `renderer/app/import-resolution.ts` | renderer | `ingestImportC()` におけるフォールバック判定と `cppFallback` 診断への決定理由・フルパス・詳細引渡し |
| `renderer/cdl/messages.ts` | renderer | 決定理由（ユーザ直接指定/自動検出/フォールバック）およびフルパスを含む `cppFallback` の診断生成 |
| `renderer/app/information-dialog.ts` | renderer | 情報ダイアログでの CPP 設定表示（有効コマンド、決定理由、フルパス）および入力・「参照…」ボタン（ファイルダイアログ呼び出し）・保存 UI |

---

## 9E.2 DTO・型定義の拡張（`src/shared/ipc-types.ts`）

### 1. `CppOriginReason` および `CppResult` の構造化エラー拡張
プリプロセッサ実行ファイルの決定理由、フルパス、および失敗理由をレンダラー側へ確実に伝えるため、`originReason`、`fullPath`、`failureKind`、`failureDetail` を追加します。

```ts
/** V0.2.1: Cプリプロセッサ実行ファイルの決定理由 */
export type CppOriginReason = "ユーザ直接指定" | "自動検出" | "フォールバック";

export interface CppResult {
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number | null;
  readonly executableFound: boolean;
  /** V0.2.1: 実行ファイルの決定理由 */
  readonly originReason?: CppOriginReason;
  /** V0.2.1: 解決された実行ファイルへのフルパス（未解決の場合は未検出表記） */
  readonly fullPath?: string;
  /** V0.2.1: 失敗の分類 */
  readonly failureKind?: "not-found" | "failed" | "timeout" | "launch-failed"; // launch-failed: 引数形式不正・権限なしなどの起動失敗（終了コードなし）。2026-11-17、8-3
  /** V0.2.1: 失敗の具体的詳細（終了コード、stderrの抜粋、エラーメッセージ等） */
  readonly failureDetail?: string;
}
```

### 2. ツール設定の型拡張
`ToolSettingsView` および `ToolSettingsUpdate` に CPP 関連プロパティを追加します。

```ts
export interface ToolSettingsView {
  // --- 既存の tecsgen / CDL設定 ---
  readonly tecsgenPath: string;
  readonly effectiveCommand: string;
  readonly tecspath?: string;
  readonly cdlFilesRoot?: string;
  readonly revision: number;

  // --- V0.2.1: Cプリプロセッサ設定 ---
  readonly cppPath?: string;
  readonly cppArgs?: string;
  readonly effectiveCppCommand: string;
  readonly effectiveCppFullPath: string;
  readonly cppOrigin: "cdl" | "settings" | "path" | "default";
  readonly cppOriginReason: CppOriginReason;
}

export interface ToolSettingsUpdate {
  readonly tecsgenPath?: string;
  readonly cdlFilesRoot?: string;
  // --- V0.2.1: 更新用 ---
  readonly cppPath?: string;
  readonly cppArgs?: string;
}
```

---

## 9E.3 メインプロセス設計

### 1. ファイル選択ダイアログのハンドラ（`ipc.ts`, `tool-settings.ts`）
「参照…」ボタン押下時にネイティブファイル選択ダイアログを表示します。

```ts
// main/tool-settings.ts
export async function chooseCppPath(currentPath?: string): Promise<string | null> {
  const defaultDir = currentPath && existsSync(currentPath)
    ? dirname(currentPath)
    : undefined;

  const result = await dialog.showOpenDialog({
    title: "C プリプロセッサ実行ファイルの選択",
    defaultPath: defaultDir,
    filters: process.platform === "win32"
      ? [
          { name: "実行可能ファイル (*.exe;*.cmd;*.bat)", extensions: ["exe", "cmd", "bat"] },
          { name: "すべてのファイル (*.*)", extensions: ["*"] },
        ]
      : [{ name: "すべてのファイル (*)", extensions: ["*"] }],
    properties: ["openFile"],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  return result.filePaths[0];
}
```

### 2. コマンドライン・フルパス・決定理由の解決（`tool-settings.ts`）
優先順位に従い、実行コマンド、フルパス、および決定理由（`originReason`）を決定します。

**CDL 固有の指定（`cdlCppCommand`）の出どころ（2026-11-17 決定）**: `.tecsgen-opts` の `-c`／`--cpp` があれば、それを渡し、なければ CDL の `__tool_info__` の `cpp` を渡す。`.tecsgen-opts` を開いたときの `cpp` は、`OpenResult` に載せて、`import_C` の解決（`resolveAllImports`、Ctrl+クリックの追加を含む）まで届ける。値は引数込みの完全なコマンドとして扱い、`cppArgs` は付けない。**実装済み（v0.2.6 段2、2026-11-17、コミット `b4fa6e1`、ブランチ `v0.2.6-stage2`・未マージ、三者相違一覧 8-4）**: `OpenResult.cpp`（`.tecsgen-opts` を開く経路・セッション復元・起動時の引数で設定）を`applyOpenResult`が`resolveAllImports`へ渡す。Ctrl+クリックの追加（`addAsReference`）は、今開いている `.tecsgen-opts` を読み直して`cpp`を得る（Generate と同じく呼ぶたびに再解析）。`import-resolution.ts`は、追加したCDL自身の`__tool_info__`の`cpp`より`.tecsgen-opts`の`cpp`を優先する。


```ts
export interface DetectedExecutable {
  readonly name: string;
  readonly fullPath: string;
}

export function findGccOnPath(envPath = process.env.PATH ?? ""): DetectedExecutable | null {
  const dirs = envPath.split(delimiter).filter(Boolean);
  const extensions = process.platform === "win32"
    ? (process.env.PATHEXT ?? ".EXE;.CMD;.BAT;.COM").split(";").map((e) => e.toLowerCase())
    : [""];

  // 1. 完全一致の gcc / gcc.exe を先に探す
  for (const dir of dirs) {
    for (const ext of extensions) {
      const candidate = join(dir, `gcc${ext}`);
      if (isExecutable(candidate)) {
        return { name: "gcc", fullPath: candidate };
      }
    }
  }

  // 2. 拡張子除き末尾が gcc の実行ファイル（例: arm-none-eabi-gcc.exe）
  const GCC_STEM_REGEX = /^.*gcc$/i;
  for (const dir of dirs) {
    try {
      const entries = readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isFile()) continue;
        const lastDot = entry.name.lastIndexOf(".");
        const stem = lastDot >= 0 ? entry.name.slice(0, lastDot) : entry.name;
        if (GCC_STEM_REGEX.test(stem)) {
          const fullPath = join(dir, entry.name);
          if (isExecutable(fullPath)) {
            return { name: entry.name, fullPath };
          }
        }
      }
    } catch {
      // ディレクトリ読み取り不可はスキップ
    }
  }
  return null;
}

export interface ResolvedCppCommand {
  readonly command: string;
  readonly executable: string;
  readonly fullPath: string;
  readonly origin: "cdl" | "settings" | "path" | "default";
  readonly originReason: CppOriginReason;
}

export function resolveCppCommand(
  cdlCppCommand: string | undefined,
  savedSettings: AppSettings,
): ResolvedCppCommand {
  // 1. CDL 固有指定
  if (cdlCppCommand && cdlCppCommand.trim().length > 0) {
    const trimmed = cdlCppCommand.trim();
    const exe = trimmed.split(/\s+/)[0];
    return {
      command: trimmed,
      executable: exe,
      fullPath: isAbsolute(exe) ? exe : (findOnPath(exe) ?? exe),
      origin: "cdl",
      originReason: "ユーザ直接指定",
    };
  }

  // オプション設定値（未設定＝undefined のときだけ既定値 `-E -DTECSGEN` を使う。2026-11-14 変更）。
  // 空文字で保存された場合は、利用者が意図して付けなかったものとして、オプションを渡さない。
  const args = (savedSettings.cppArgs ?? DEFAULT_CPP_ARGS).trim();   // DEFAULT_CPP_ARGS = "-E -DTECSGEN"
  const buildCommand = (executable: string) => (args && args.length > 0 ? `${executable} ${args}` : executable);

  // 2. 明示設定 (settings.json)
  if (savedSettings.cppPath && savedSettings.cppPath.trim().length > 0) {
    const exe = savedSettings.cppPath.trim();
    const resolvedPath = isAbsolute(exe) ? exe : (findOnPath(exe) ?? exe);
    return {
      command: buildCommand(exe),
      executable: exe,
      fullPath: resolvedPath,
      origin: "settings",
      originReason: "ユーザ直接指定",
    };
  }

  // 3. PATH上の自動検出
  const detected = findGccOnPath();
  if (detected) {
    return {
      command: buildCommand(detected.name),
      executable: detected.name,
      fullPath: detected.fullPath,
      origin: "path",
      originReason: "自動検出",
    };
  }

  // 4. フォールバック
  const fallbackFound = findOnPath("gcc");
  return {
    command: buildCommand("gcc"),
    executable: "gcc",
    fullPath: fallbackFound ?? "未検出 (PATH上)",
    origin: "default",
    originReason: "フォールバック",
  };
}
```

### 3. プロセス実行とエラー抽出（`tecsgen-runner.ts`）
`preprocess(headerPath, resolvedCpp: ResolvedCppCommand, includeDirs)` は、実行ファイルと引数を分離して安全に起動し、結果に決定理由とフルパスを付加します。

- **未検出（ENOENT）**:
  `executableFound = false, originReason = resolvedCpp.originReason, fullPath = resolvedCpp.fullPath, failureKind = "not-found", failureDetail = `'${resolvedCpp.executable}' が見つかりません``
- **非ゼロ終了（`exitCode !== 0`）**:
  `executableFound = true, originReason = resolvedCpp.originReason, fullPath = resolvedCpp.fullPath, failureKind = "failed"`
  `stderr` の先頭から主要なエラー行を最大 200 文字に要約して `failureDetail` とする（例: `終了コード 1: fatal error: kernel.h: No such file or directory`）。
- **タイムアウト（30秒超過）**:
  `originReason = resolvedCpp.originReason, fullPath = resolvedCpp.fullPath, failureKind = "timeout", failureDetail = "30秒以内に完了しなかったためタイムアウトしました"`
- **起動できない（2026-11-17、三者相違一覧 8-3。実装済み、v0.2.6 段2、コミット `15e811d`）**: 引数形式不正（`splitCommand`の引用符の閉じ忘れ）と、数値の終了コードを持たない起動失敗（権限なし `EACCES`・`EPERM` など）。
  `executableFound = true, exitCode = null, failureKind = "launch-failed", failureDetail = "コマンドの引数の形式が不正です（引用符が閉じていません）"` または `"EACCES: <メッセージ>"`。**存在しない終了コード 1 を作らない**。数値の終了コードで終わったものだけを `failed` とする。

---

## 9E.4 レンダラープロセス設計

### 1. インポート解決での診断生成（`import-resolution.ts`, `messages.ts`）
`ingestImportC()` は `CppResult` を受け取り、失敗（`usedFallback === true`）時に決定理由、フルパス、および失敗詳細を付与して `cppFallback` を呼び出します。

```ts
// messages.ts
export function cppFallback(
  headerPath: string,
  command: string,
  originReason?: CppOriginReason,
  fullPath?: string,
  failureKind?: "not-found" | "failed" | "timeout" | "launch-failed",
  detail?: string,
): Diagnostic {
  const metaParts: string[] = [];
  if (fullPath) metaParts.push(`フルパス: ${fullPath}`);
  if (originReason) metaParts.push(`決定理由: ${originReason}`);
  const metaLabel = metaParts.length > 0 ? `（${metaParts.join("、")}）` : "";

  let body = "";
  if (failureKind === "not-found") {
    body = `Cプリプロセッサ '${command}'${metaLabel}が見つからないため、'${headerPath}' は未展開のまま型を抽出しました（パス設定またはインストールを確認してください）`;
  } else if (failureKind === "failed") {
    body = `Cプリプロセッサ '${command}'${metaLabel}の実行が失敗したため${detail ? `（${detail}）` : ""}、'${headerPath}' は未展開のまま型を抽出しました`;
  } else {
    body = `Cプリプロセッサ '${command}'${metaLabel}を起動・実行できなかったため${detail ? `（${detail}）` : ""}、'${headerPath}' は未展開のまま型を抽出しました`;
  }

  return {
    severity: "warning",
    code: W_CODES.CPP_FALLBACK,
    message: body,
  };
}
```

### 2. 情報ダイアログ UI（`information-dialog.ts`）
情報ダイアログの「設定」セクションに「Cプリプロセッサ (CPP)」サブセクションを追加します：

- **有効コマンドの表示**:
  `<p class="cpp-effective">有効なコマンド: <code>${effectiveCppCommand}</code></p>`
  `<p class="cpp-meta">（フルパス: <code>${effectiveCppFullPath}</code>、決定理由: ${cppOriginReason}）</p>`
- **実行ファイル入力と「参照…」ボタン**:
  `<input type="text" id="setting-cpp-path" placeholder="例: arm-none-eabi-gcc (空欄でPATHから自動検出)" />`
  `<button id="btn-browse-cpp">参照…</button>`
  - ボタン押下時に `window.tecscde.settings.chooseCppPath(currentInputPath)` を呼び出し、選択された絶対パスを入力欄にセット。
- **オプション入力**:
  - 初回ダイアログ表示時（`settings.cppArgs` が未設定の場合）の入力欄初期値として `-E -DTECSGEN` を利用します。
  - **未設定（`cppArgs` が `undefined`）のときは、実行時にも既定値 `-E -DTECSGEN` を使います**（2026-11-14 変更。`DEFAULT_CPP_ARGS`、`tool-settings.ts`）。入力欄の初期値と実行時の既定値は一致します。
  - 空欄で保存された場合は `cppArgs: ""` として保持され、実行時にオプションは付与されません（利用者が意図して付けなかったものとして扱います）。
  - **変更の理由**: 旧仕様（未設定ならオプションなし）では、自動検出した `gcc` に `-E` が付かず、`gcc` がヘッダーを**コンパイル**して `unknown type name`（終了コード 1）になり、標準出力が空になり、ヘッダーの隣へ `.gch` を書き出していた（`v0.2.3` の実機で確認）。
  `<input type="text" id="setting-cpp-args" placeholder="オプションなしの場合は空欄" />`
- **保存**:
  ダイアログ内の「設定を保存」ボタン押下時に、`tecsgenPath` とともに `cppPath`・`cppArgs` をまとめて IPC 経由で更新。

---

## 9E.5 整合性と監査ルールへの準拠

1. **プロセス境界（.dependency-cruiser.cjs）**:
   - renderer から `dialog`、`child_process`、`fs` 等の Node/Electron API を直接参照せず、すべて `TecscdeApi`（IPC）を経由します。
2. **ログの1行1件原則（監査#68）**:
   - `fullPath` や `failureDetail` を含む診断メッセージに改行が含まれる場合でも、`formatDiagnostic`（`escapeSingleLine`）によって可逆エスケープされ、`tecscde-log-*.txt` の物理行が分裂しないことを保証します。
3. **シェルインジェクション防止**:
   - 任意の入力文字列に対して `shell: true` を用いず、`splitCommand` でトークン化した引数配列を `execFile` に渡します。

---

## 9E.6 関連仕様

- [[TECSCDE-DT外部仕様 - Cプリプロセッサ設定と失敗詳細(V0.2.1用)]] — 対応する外部仕様
- [[TECSCDE-DT-EL内部仕様 - 09 tecsgen連携設計]] — tecsgen / CPP 実行基盤
- [[TECSCDE-DT-EL内部仕様 - 09D V0.2.0tecsgen設定と内部処理]] — V0.2.0 設定基盤
- [[TECSCDE-DT-EL内部仕様 - 08 整合性チェックとメッセージ設計]] — メッセージ・診断カタログ
