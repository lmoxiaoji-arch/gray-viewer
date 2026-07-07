@echo off
chcp 65001 >nul
title 16-bit TIFF 打包工具 (Antigravity-IDE)

echo =======================================================
echo         16-bit TIFF 至 8-bit RG-PNG 打包小工具
echo =======================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "INPUT_PATH=%~1"

if "%INPUT_PATH%"=="" (
    echo [提示] 未拖拽文件，将扫描当前目录下的所有 TIFF 文件。
    set "INPUT_PATH=."
) else (
    echo [提示] 正在处理输入路径: "%INPUT_PATH%"
)

echo.
echo [1/2] 正在检测 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未在系统 PATH 中找到 python 命令行。
    echo 请确保安装了 Python 3 并且在安装时勾选了 "Add Python to PATH"。
    pause
    exit /b
)

echo.
echo [2/2] 运行打包脚本...
python "%SCRIPT_DIR%pack_16bit.py" -i "%INPUT_PATH%" -o "%SCRIPT_DIR%output_pngs"

echo.
echo =======================================================
echo 处理完成！输出文件已保存在: %SCRIPT_DIR%output_pngs
echo =======================================================
echo.
pause
