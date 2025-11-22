from PIL import Image
import sys
import os

def convert_to_ico(png_path, ico_path):
    try:
        img = Image.open(png_path)
        img.save(ico_path, format='ICO', sizes=[(256, 256)])
        print(f"Successfully converted {png_path} to {ico_path}")
    except Exception as e:
        print(f"Error converting icon: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Mac側で生成された画像パスを指定（ユーザー環境に合わせて調整が必要だが、
    # ここでは配布用フォルダ内で完結させるため、ユーザーにPNGを配置してもらう前提か、
    # あるいはMacで変換してから配布フォルダに入れる）
    
    # 今回はMacで変換して、icoファイルを配布フォルダに入れるフローにする。
    # よってこのスクリプトはMacで実行する。
    
    if len(sys.argv) < 3:
        print("Usage: python convert_icon.py <input_png> <output_ico>")
        sys.exit(1)
        
    convert_to_ico(sys.argv[1], sys.argv[2])
