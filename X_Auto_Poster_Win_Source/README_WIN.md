# X自動投稿アプリ Windows版ビルドガイド

このフォルダには、Windowsでアプリをビルドするために必要なファイルが一式入っています。
以下の手順に従って、Windows上で `.exe` ファイルを作成してください。

## 前提条件
- **Python** がインストールされていること (推奨: Python 3.10 〜 3.12)
  - インストール時に "Add Python to PATH" にチェックを入れていること。

## 手順

### 1. コマンドプロンプト (または PowerShell) を開く
このフォルダ (`X_Auto_Poster_Win_Source`) の中で、何もないところを `Shift` キーを押しながら **右クリック** し、「PowerShell ウィンドウをここに開く」または「コマンドウィンドウをここに開く」を選択します。
(または、アドレスバーに `cmd` と入力して Enter)

### 2. 仮想環境の作成 (Python 3.12 指定)
複数のPythonが入っている場合に備えて、一度環境をリセットし、バージョンを指定して作成します。

1. **既存の環境を削除** (もしあれば):
   ```powershell
   if (Test-Path venv) { Remove-Item -Recurse -Force venv }
   ```

2. **Python 3.12の確認と作成**:
   Windowsには通常 `py` ランチャーが入っています。これを使って 3.12 を指定します。
   ```powershell
   # バージョン確認
   py --list
   
   # 3.12を指定して仮想環境作成
   py -3.12 -m venv venv
   ```
   ※ `py` コマンドが使えない場合は、`python --version` で 3.12 であることを確認してから `python -m venv venv` を実行してください。

3. **有効化**:
   ```powershell
   .\venv\Scripts\activate
   ```
   ※ 左側に `(venv)` と表示されたら成功です。

4. **場所の確認 (重要)**:
   念のため、仮想環境の Python が使われているか確認します。
   ```powershell
   Get-Command python
   ```
   ※ Source が `...X_Auto_Poster_Win_Source\venv\Scripts\python.exe` になっていればOKです。

### 3. ライブラリのインストール
必要な部品をダウンロードします。

```powershell
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

### 4. ビルドの実行 (自動スクリプト)
以下のコマンドを実行すると、ブラウザのダウンロードからビルドまでを自動で行います。

```powershell
python build_win.py
```

### 5. 完成！
処理が終わると、同じフォルダの中に `dist` というフォルダができます。
その中にある `X_Auto_Poster.exe` が完成したアプリです。

## 配布時の注意
配布する際は、以下の2つのファイルを同じフォルダに入れて渡してください。

1. `X_Auto_Poster.exe` (distフォルダから取り出す)
2. `accounts.csv` (このフォルダにあるものをコピー)

※ `manual.html` も同梱すると親切です。
