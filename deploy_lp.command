#!/bin/bash

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

echo "========================================"
echo "  LP更新デプロイツール"
echo "========================================"

# 未コミットの変更があるか確認
if [ -n "$(git status --porcelain)" ]; then
    echo "【エラー】未コミットの変更があります。"
    echo "先に git commit してから実行してください。"
    exit 1
fi

echo "1. デプロイ用の一時ブランチを作成中..."
# 現在のmainから一時ブランチを作成（orphan: 履歴を引き継がない）
git checkout --orphan temp-deploy-branch
git reset --hard

echo "2. ファイルを配置中..."
# distribution_siteの中身をルートに展開
cp -r distribution_site/* .
rm -rf distribution_site

# 不要なファイルを削除（念のため）
rm -rf venv .gitattributes .gitignore build_mac.sh main.py requirements.txt Windows_Build_Package Release_Staging

echo "3. コミット中..."
git add .
git commit -m "Update Landing Page"

echo "4. GitHubへ送信中..."
# gh-pagesブランチへ強制プッシュ
git push origin temp-deploy-branch:gh-pages --force

echo "5. お掃除中..."
# mainに戻る
git checkout main
git branch -D temp-deploy-branch

echo "========================================"
echo "  完了しました！"
echo "  数分後に以下で更新されます:"
echo "  https://un907.github.io/X_Auto_Poster/"
echo "========================================"
