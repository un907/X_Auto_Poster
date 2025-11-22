# Windowsビルド チェックリスト (v1.7 インストーラー版)

このチェックリストは、X Auto PosterのWindowsインストーラーを確実に作成するための手順書です。

## 1. 環境準備
- [ ] **Python 3.12+**: Pythonがインストールされ、PATHに通っていることを確認。
- [ ] **Inno Setup 6**: Inno Setupがインストールされていることを確認 (通常: `C:\Program Files (x86)\Inno Setup 6`)。
- [ ] **ソースファイル**: `main.py`, `settings.json`, `personas.json`, `accounts.csv` が揃っているか確認。
- [ ] **クリーンアップ**: 以前の `dist`, `build`, `venv` フォルダがある場合は削除してクリーンな状態にする。

## 2. 依存関係のセットアップ (バッチで自動化済)
- [ ] **仮想環境 (venv)**: 依存関係を隔離するための `venv` を作成。
- [ ] **Pipインストール**: `requirements.txt` (playwright, customtkinter, google-generativeai 等) をインストール。
- [ ] **PyInstaller**: `pyinstaller` をインストール。

## 3. ブラウザ管理 (インストーラー作成に必須)
- [ ] **ダウンロード先**: ブラウザが `dist/browsers` にダウンロードされていること。
- [ ] **コマンド**: `playwright install chromium firefox` (環境変数 `PLAYWRIGHT_BROWSERS_PATH` を指定して実行)。
- [ ] **確認**: `dist/browsers` フォルダ内に `chromium-xxx` や `firefox-xxx` フォルダがあるか確認。

## 4. アプリ本体のビルド (PyInstaller)
- [ ] **コマンド**: `pyinstaller --noconfirm --onefile --windowed ...`
- [ ] **出力**: `dist/X_Auto_Poster.exe` が生成されていること。
- [ ] **アセット**: `settings.json` などが含まれているか確認 (インストーラー側でもコピー処理を行いますが、念のため)。

## 5. インストーラーのコンパイル (Inno Setup)
- [ ] **スクリプト**: `setup.iss` が存在すること。
- [ ] **パス設定**: `.iss` ファイル内の `Source` パスが `..\dist\X_Auto_Poster.exe` と `..\dist\browsers\*` を正しく指しているか。
- [ ] **コンパイル実行**: `ISCC.exe setup.iss` を実行。
- [ ] **出力**: `Output/X_Auto_Poster_Setup_v1.7.0.exe` が生成される。

## 6. 最終確認
- [ ] **インストールテスト**: 生成された `setup.exe` をクリーンな環境 (サンドボックス等) で実行してインストールできるか。
- [ ] **起動テスト**: インストールされたアプリが起動するか。
- [ ] **ブラウザテスト**: アプリからブラウザ (Chromium/Firefox) がエラーなく起動するか。
