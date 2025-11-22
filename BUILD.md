# X自動投稿アプリ ビルド手順書 (v1.6)

このドキュメントでは、Pythonスクリプト (`main.py`) を配布可能なアプリケーション（Zipパッケージ）に変換する手順を説明します。

## 前提条件

- Python 3.10以上がインストールされていること
- 必要なライブラリがインストールされていること (`pip install -r requirements.txt`)

---

## 1. 自動ビルド（推奨）

各OS用に用意されたスクリプトを実行するだけで、ブラウザのダウンロードからZip圧縮まで全自動で行われます。

### Windows の場合
プロジェクトフォルダ内の `X_Auto_Poster_Win_Source` フォルダにある **`setup_and_build.bat`** をダブルクリックして実行してください。

- **処理内容**:
    1. 必要なライブラリのインストール
    2. ブラウザ (Chromium/Firefox) のダウンロード (`dist/browsers`)
    3. PyInstallerによるexe化
    4. 配布用Zipファイルの作成
- **生成物**: `Output\X_Auto_Poster_v1.6.0.zip`

### Mac (macOS) の場合
ターミナルでプロジェクトフォルダに移動し、**`build_mac.sh`** を実行してください。

```bash
chmod +x build_mac.sh
./build_mac.sh
```

- **処理内容**:
    1. 仮想環境(venv)のセットアップ
    2. ブラウザのダウンロード
    3. PyInstallerによる.app化（ブラウザをアプリ内に同梱）
    4. 配布用Zipファイルの作成
- **生成物**: `X_Auto_Poster_Mac_v1.6.0.zip`

---

## 2. 手動ビルド（上級者向け）

スクリプトを使わずに手動でビルドする場合の手順です。

### 共通: ブラウザの準備
まず、Playwright用のブラウザをローカルにダウンロードする必要があります。

```bash
# ブラウザ保存先を指定してインストール
# (Windowsは set, Macは export)
set PLAYWRIGHT_BROWSERS_PATH=./dist/browsers
playwright install chromium firefox
```

### Windows (手動)
```bash
pyinstaller --noconfirm --onefile --windowed --name "X_Auto_Poster" --clean --add-data "settings.json;." --add-data "personas.json;." --add-data "accounts.csv;." --hidden-import=customtkinter --hidden-import=google.generativeai main.py
```
**重要**: ビルド後、`dist` フォルダ内の `X_Auto_Poster.exe` と同じ場所に `browsers` フォルダをコピーしてください。

### Mac (手動)
```bash
pyinstaller --noconfirm --onefile --windowed --name "X_Auto_Poster" --clean --add-data "settings.json:." --add-data "personas.json:." --add-data "accounts.csv:." --hidden-import=customtkinter --hidden-import=google.generativeai main.py
```
**重要**: ビルド後、`dist/X_Auto_Poster.app/Contents/MacOS/` の中に `browsers` フォルダをコピーしてください。

---

## 3. 配布パッケージの構成

最終的に配布するZipファイルは、以下の構成になっている必要があります。

### Windows版 (Zip構成)
```
X_Auto_Poster_v1.6.0/
├── X_Auto_Poster.exe      (アプリ本体)
├── browsers/              (ブラウザフォルダ: 必須)
├── manual.html            (マニュアル)
└── 最初に読んで下さい.txt   (説明書)
```
※ `accounts.csv` や `settings.json` は初回起動時に自動生成されるか、exeに内包されたものが使われますが、編集用として同梱しても構いません。

### Mac版 (Zip構成)
```
X_Auto_Poster_Mac_v1.6.0/
├── X_Auto_Poster.app      (アプリ本体: ブラウザ内蔵)
├── manual.html
└── 最初に読んで下さい.txt
```
