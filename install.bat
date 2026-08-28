@echo off
rem xhs-live 依赖安装 (Windows)
cd /d "%~dp0"
python install_deps.py %*
if errorlevel 1 (
  echo.
  echo 安装失败, 可尝试: python install_deps.py --online
  pause
)
