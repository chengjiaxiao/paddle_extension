@echo off
chcp 65001 >nul
REM 在 paddle_env 中启动 OCR 服务的批处理脚本

echo.
echo ================================================
echo PaddleOCR API 服务启动脚本
echo ================================================
echo.

REM 检查是否安装了 Conda
where conda >nul 2>nul
if errorlevel 1 (
    echo 错误: 未找到 Conda
    echo 请先安装 Anaconda 或 Miniconda
    pause
    exit /b 1
)

echo 正在激活 paddle_env 环境...
call conda activate paddle_env

if errorlevel 1 (
    echo 错误: 无法激活 paddle_env 环境
    echo 请确保已安装 paddle_env，运行以下命令创建:
    echo   conda create -n paddle_env python=3.10
    echo   conda activate paddle_env
    echo   pip install paddlepaddle paddleocr
    pause
    exit /b 1
)

REM 改变工作目录到项目根目录
cd /d E:\OneDrive\project_code

echo.
echo ================================================
echo 启动 PaddleOCR API 服务...
echo ================================================
echo.
echo API 文档: http://localhost:8000/docs
echo 可视化文档: http://localhost:8000/redoc
echo.
echo 按 Ctrl+C 停止服务
echo ================================================
echo.

python LLMkit\modules\vision\ocr_api_service.py

pause
