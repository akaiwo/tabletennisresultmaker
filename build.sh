#!/usr/bin/env bash

set -o errexit  # エラーが出たら止める
set -o nounset  # 未定義変数で止める
set -o pipefail # パイプの途中でエラーでも止める

echo "▶ Install system dependencies"
apt-get update
apt-get install -y fonts-noto-cjk

echo "▶ Install Python dependencies"
pip install -r requirements.txt