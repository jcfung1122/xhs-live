#!/usr/bin/env bash
# xhs-live 依赖安装 (macOS / Linux)
cd "$(dirname "$0")" || exit 1
python3 install_deps.py "$@"
if [ $? -ne 0 ]; then
  echo ""
  echo "安装失败, 可尝试: python3 install_deps.py --online"
  exit 1
fi
