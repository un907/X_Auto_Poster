import subprocess
import sys
import os
import shutil

def run_command(command):
    print(f"実行中: {' '.join(command)}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

def main():
    print("=== Windows版 自動ビルドスクリプト ===")

    # 1. Playwrightのブラウザ(Firefox)をインストール
    print("\n[1/3] Firefoxブラウザをダウンロードしています...")
    run_command([sys.executable, "-m", "playwright", "install", "firefox"])

    # 2. ブラウザのパスを特定
    print("\n[2/3] ブラウザのインストール場所を特定しています...")
    # Windowsのデフォルトパス
    local_app_data = os.environ.get('LOCALAPPDATA')
    if not local_app_data:
        print("エラー: LOCALAPPDATA環境変数が見つかりません。")
        sys.exit(1)
    
    playwright_path = os.path.join(local_app_data, "ms-playwright")
    
    # firefox-xxxx というフォルダを探す
    firefox_dir = None
    if os.path.exists(playwright_path):
        for item in os.listdir(playwright_path):
            if item.startswith("firefox-"):
                firefox_dir = os.path.join(playwright_path, item)
                break
    
    if not firefox_dir:
        print("エラー: Firefoxのインストールフォルダが見つかりませんでした。")
        sys.exit(1)
    
    print(f"ブラウザ発見: {firefox_dir}")

    # 3. PyInstallerでビルド
    print("\n[3/3] アプリをビルドしています...")
    
    # --add-data の形式は Windowsでは "ソース;宛先"
    # ブラウザフォルダごと、playwrightが期待する内部パスに配置する
    # 期待されるパス: ms-playwright/firefox-xxxx/...
    # しかし、PyInstallerのtempディレクトリ構造上、ルートに置くのが無難か、
    # あるいはPlaywrightの仕様に合わせて配置する必要がある。
    # Playwrightは通常、環境変数がない場合、自身のパッケージ内のドライバパスなどを参照するが、
    # 実行ファイル化された場合は sys._MEIPASS を参照する。
    
    # ここでは、シンプルに実行ファイルの横に 'browsers' フォルダとして置く方式を採用したいが、
    # ユーザーは「1つのexe」を希望している。
    # よって、exe内部に埋め込む。
    # 埋め込み先は "playwright/driver/package/.local-browsers/firefox-xxxx" のような深い階層が必要になる場合があるが、
    # 最近のPlaywrightは環境変数 PLAYWRIGHT_BROWSERS_PATH があればそこを見る。
    
    # 最も確実なのは、ブラウザをexeに含めず、初回起動時にインストールさせることだが、
    # 今回は「配布用」なので、exeに含めるトライをする。
    # 宛先パスは、Playwrightが内部で探すパスに合わせる必要がある。
    # しかし、バージョン番号が変わるとパスも変わるため、
    # ここでは「ビルド時に見つけたフォルダ」をそのまま使う。
    
    folder_name = os.path.basename(firefox_dir)
    # 宛先: playwright/driver/package/.local-browsers/firefox-xxxx
    destination_path = os.path.join("playwright", "driver", "package", ".local-browsers", folder_name)
    
    add_data_arg = f"{firefox_dir};{destination_path}"
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "X_Auto_Poster",
        "--clean",
        "--add-data", "accounts.csv;.",
        "--add-data", add_data_arg,
        "--collect-all", "customtkinter",
        "--icon", "icon.ico",
        "main.py"
    ]
    
    run_command(cmd)

    print("\n=== ビルド完了！ ===")
    print("dist フォルダ内の X_Auto_Poster.exe を確認してください。")

if __name__ == "__main__":
    main()
