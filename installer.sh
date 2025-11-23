#!/bin/bash
set -e

REPO="https://github.com/SchnookelWang/hawker.py/archive/refs/heads/main.tar.gz"
I_DIR="$HOME/.hawker"
VIR_ENV_DIR="$I_DIR/.venv"

echo "HOME: $HOME"
echo "I_DIR: $I_DIR"
echo "VIR_ENV_DIR: $VIR_ENV_DIR"


echo "Downloading hawker.py..."
rm -rf "$I_DIR"
mkdir -p "$I_DIR"

curl -L "$REPO" -o /tmp/hawker.py.tar.gz

echo "Extracting..."
tar -xzf /tmp/hawker.py.tar.gz --strip-components=1 -C "$I_DIR"

echo "Creating virtual enviroment..."
python3 -m venv "$VIR_ENV_DIR"
source "$VIR_ENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r "$I_DIR/requirements.txt"

echo "DONE!"

