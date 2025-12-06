# X Auto Poster Project Context

## 1. プロジェクトの核心 (Core Identity)

### 目的 (Purpose)
*   **社内非エンジニアへの配布**: コマンドライン操作や環境構築ができない社内スタッフでも、簡単にX（旧Twitter）の自動投稿を行えるようにする。
*   **複数アカウントの運用自動化**: `accounts.csv` で管理された多数のアカウントに対し、ログイン状態を保持しながら効率的に投稿を行う。

### ビジョン (Vision)
*   **「誰でも使えるシンプルさ」**: 複雑な設定を排除し、GUI（Tkinter）だけで完結する直感的な操作性を提供する。
*   **「人間らしい振る舞い」**: ランダムな待機時間やAIによる文章生成を組み合わせ、機械的な挙動を避けることでアカウントの安全性を確保する。

### ターゲットユーザー
*   社内の非エンジニアスタッフ。
*   「黒い画面（ターミナル）」を使わずに自動化の恩恵を受けたい層。

---

## 2. 技術スタックとアーキテクチャ (Technical Stack & Architecture)

### コア技術
*   **言語**: Python 3.12+
*   **GUI**: `tkinter`, `customtkinter` (モダンなUIデザイン)
*   **ブラウザ操作**: `playwright` (Firefoxエンジンを使用)
*   **AI**: `google-generativeai` (Gemini API)
*   **パッケージング**: `PyInstaller`

### アーキテクチャの特徴
1.  **ブラウザ分離方式 (v1.9.0以降)**:
    *   アプリ本体の軽量化のため、ブラウザバイナリは同梱せず、初回起動時にユーザーのドキュメントフォルダへ自動ダウンロードする。
    *   保存先: `~/Documents/X_Auto_Poster/Browsers` (Mac) / `Documents/X_Auto_Poster/Browsers` (Win)

2.  **ローカルファースト (Local First)**:
    *   設定、アカウント情報、ブラウザのCookie（プロファイル）は全てローカルディスクに保存し、外部サーバーには送信しない。

3.  **クロスプラットフォーム**:
    *   Windows / macOS 両対応。OSごとのパスや挙動の差異はコード内で吸収する。

---

## 3. 機能要件詳細 (Functional Specifications)

### 動作設定
*   **ヘッドレスモード**: **デフォルトOFF**（画面表示あり）。
    *   ユーザーが動作を目視確認できるようにするため、デフォルトではブラウザを表示して実行する。設定でON（非表示）に変更可能。
*   **ブラウザ**: **Firefox** を採用（Chromium系と比較して自動化検知対策として有利なため）。

### 投稿機能
*   **通常投稿**: テキスト＋画像（最大4枚）。
*   **AI生成投稿**: Gemini APIを使用し、ペルソナ（口調・興味）に基づいた投稿文を生成。
*   **スマートスケジュール**: 投稿間にランダムな待機時間を設け、人間らしい挙動を模倣する。

### アカウント管理
*   CSVによる一括管理。
*   Playwrightの `storage_state` を活用し、2回目以降はログイン処理をスキップ（永続化）。

---

## 4. 開発・ビルド・リリース運用 (DevOps)

### ビルド (Build)
*   **ローカルビルド**: GitHub Actionsではなく、開発者のローカル環境でビルドを行う。
*   **Mac**: `build_mac.sh` -> `.app` -> Zip
*   **Windows**: `setup_and_build.bat` -> `.exe` -> Zip
    *   *重要*: Windows版は `multiprocessing` の無限ループ対策として `sys.argv` パッチが適用されている。

### リリース (Release)
*   **配布場所**: GitHub Releases。
*   **パッケージ**: Windows版とMac版のZipファイルをアップロード。
*   **注意点**: Windows版Zip内のマニュアルPDFは、文字化け回避のため `Manual.pdf` にリネームして格納する。

### ランディングページ (LP)
*   **URL**: `https://un907.github.io/X_Auto_Poster/`
*   **運用**: `distribution_site/` フォルダを編集し、GitHub Actions経由で自動デプロイ。

---

## 5. 経緯と文脈 (Historical Context)

### 初期〜v1.8
*   「社内配布用」として開発開始。
*   ブラウザ同梱によるファイルサイズ肥大化が課題だった。

### v1.9.0
*   **軽量化**: ブラウザ分離方式の実装により、配布サイズを劇的に削減。
*   **安定化**: Windowsでのビルド不具合（無限ループ）やインストーラーの問題を解決。
*   **LP**: NetlifyからGitHub Pagesへ移行し、運用コストを削減。

### v1.9.1 (Current - Mac版のみ)
*   **Mac版修正**: PyInstallerでバンドルされた.app環境でブラウザインストールが失敗する問題を修正。
*   **Playwright API直接呼び出し**: `sys.executable -m playwright` ではなく `compute_driver_executable()` を使用。
*   **Firefox統一**: ブラウザをFirefoxに統一（context.mdの記載と一致）。
*   **パス修正**: `PROFILES_DIR` / `IMAGES_DIR` 定数を直接使用するよう7箇所を修正。

---

## 6. システム運用ルール (System Rules for AI Agent)
1.  **言語**: 全て日本語（会話、思考、ファイル内容）で行う。
2.  **コンテキスト管理**:
    *   成功時（ユーザーの良い反応時）に `context.md` を更新する。
    *   更新単位: ブランチ、コミット、セッション、指示。
    *   **情報の継承**: AIが入れ替わっても、このファイルを読めば「何を作るべきか」「なぜそうなっているか」が完全に理解できるように記述する。
