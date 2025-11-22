import subprocess
import sys
import os

def run_command(command):
    print(f"実行中: {' '.join(command)}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

def main():
    print("=== Windows版 デバッグ用ビルドスクリプト ===")
    print("注意: このモードでは黒い画面(コンソール)が表示されます。エラーログを確認するために使用します。")

    # 1. Playwrightのブラウザ(Firefox)をインストール
    print("\n[1/3] Firefoxブラウザを確認しています...")
    run_command([sys.executable, "-m", "playwright", "install", "firefox"])

    # 2. ブラウザのパスを特定
    local_app_data = os.environ.get('LOCALAPPDATA')
    playwright_path = os.path.join(local_app_data, "ms-playwright")
    
    firefox_dir = None
    if os.path.exists(playwright_path):
        for item in os.listdir(playwright_path):
            if item.startswith("firefox-"):
                firefox_dir = os.path.join(playwright_path, item)
                break
    
    if not firefox_dir:
        print("エラー: Firefoxのインストールフォルダが見つかりませんでした。")
        sys.exit(1)
    
    folder_name = os.path.basename(firefox_dir)
    destination_path = os.path.join("playwright", "driver", "package", ".local-browsers", folder_name)
    add_data_arg = f"{firefox_dir};{destination_path}"
    
    # 3. PyInstallerでビルド (コンソールあり)
    print("\n[3/3] デバッグ版アプリをビルドしています...")
    
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        # "--windowed",  <-- これを外してコンソールを表示させる
        "--name", "X_Auto_Poster_Debug", # 名前を変える
        "--clean",
        "--add-data", "accounts.csv;.",
        "--add-data", add_data_arg,
        "--collect-all", "customtkinter",
        "--icon", "icon.ico",
        "main.py"
    ]
    
    run_command(cmd)

    print("\n=== ビルド完了！ ===")
    print("dist フォルダ内の X_Auto_Poster_Debug.exe を実行し、黒い画面に出るログを確認してください。")

if __name__ == "__main__":
    main()
