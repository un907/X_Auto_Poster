#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PATH="$DIR/X_Auto_Poster.app"

if [ -d "$APP_PATH" ]; then
    echo "Fixing 'App is damaged' error for X_Auto_Poster.app..."
    xattr -cr "$APP_PATH"
    echo "Success! You can now open the app."
else
    echo "Error: X_Auto_Poster.app not found in this folder."
    echo "Please make sure this script is in the same folder as the app."
fi
read -p "Press Enter to exit..."
