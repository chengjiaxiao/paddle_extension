# PaddleOCR 视觉-语言模块

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-VL-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README.md) | 简体中文

基于 PaddleOCR 视觉-语言模型的强大 OCR（光学字符识别）模块，提供表格提取、文档处理和 Markdown/Excel 转换功能。

## 功能特性

- **视觉-语言 OCR**：使用 PaddleOCR VL 模型进行高级表格和文档识别
- **API 服务**：基于 FastAPI 的 OCR 服务，支持批量处理
- **格式转换**：将 OCR 结果从 Markdown 转换为 Excel，保留格式
- **批量处理**：并行处理多个图片或 PDF 页面
- **表格保持**：保持表格结构，包括合并单元格（rowspan/colspan）

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
  - [环境设置](#1-环境设置)
  - [启动 OCR 服务](#2-启动-ocr-服务)
  - [基本用法](#3-基本用法)
- [高级工作流](#高级工作流)
  - [PDF 转 Excel 流程](#pdf-转-excel-流程)
  - [Markdown 转 Excel 转换](#markdown-转-excel-转换)
  - [批量处理](#批量处理)
- [架构设计](#架构设计)
- [项目结构](#项目结构)
- [依赖项](#依赖项)
- [故障排除](#故障排除)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 快速开始

### 1. 环境设置

为 PaddleOCR 创建专用的 conda 环境：

```bash
# Windows
conda create -n paddle_env python=3.10
conda activate paddle_env
pip install paddlepaddle paddleocr fastapi uvicorn pillow requests pydantic
```

### 2. 启动 OCR 服务

**Windows（快速启动）：**
```bash
启动OCR服务_paddle_env.bat
```

**手动启动：**
```bash
conda activate paddle_env
python ocr_api_service.py  # 从父目录运行
```

服务将在 `http://localhost:8000` 上运行
- 📚 API 文档: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

### 3. 基本用法

#### 直接使用 PaddleOCR

```python
from paddleocr import PaddleOCRVL

# 初始化管道
pipeline = PaddleOCRVL()

# 处理图片
output = pipeline.predict("image_path.png")

# 保存结果
for res in output:
    res.print()  # 打印到控制台
    res.save_to_json(save_path="output")
    res.save_to_markdown(save_path="output")
```

#### 基于 API 的用法

```python
from LLMkit.modules.vision.ocr_client import OCRClient

# 初始化客户端
client = OCRClient("http://localhost:8000")

# 检查服务健康状态
if client.health_check():
    # 处理单张图片
    result = client.recognize_image(
        image_path="path/to/image.png",
        save_markdown=True,
        save_json=True,
        output_dir="output"
    )

    print(result.get("markdown_path"))
    print(result.get("json_path"))
```

## 高级工作流

### PDF 转 Excel 流程

从 PDF 文档中提取表格的完整工作流：

<details>
<summary>点击展开完整工作流代码</summary>

```python
from LLMkit.modules.vision.document_processor import DocumentProcessor
from LLMkit.modules.vision.ocr_client import OCRClient
from convert_table import convert_md_to_excel
from pathlib import Path

# 步骤 1：将 PDF 转换为图片
doc_processor = DocumentProcessor(dpi=200)
png_results = doc_processor.process_document("document.pdf")

# 步骤 2：获取图片路径
dir_path = png_results[0]["output_dir"]
image_files = list(Path(dir_path).glob("*.png"))

# 步骤 3：对每张图片进行 OCR
client = OCRClient("http://localhost:8000")
md_files = []

for img_path in image_files:
    result = client.recognize_image(
        image_path=str(img_path),
        save_markdown=True,
        output_dir="output"
    )
    md_files.append(result.get("markdown_path"))

# 步骤 4：转换为 Excel
excel_path = convert_md_to_excel(md_files, output_path="merged_output.xlsx")
print(f"Excel 文件已创建: {excel_path}")
```

</details>

### Markdown 转 Excel 转换

将 OCR Markdown 结果转换为格式化的 Excel 文件：

```python
from convert_table import convert_md_to_excel

# 单个文件
convert_md_to_excel("output.md", output_path="output.xlsx")

# 多个文件（创建多工作表工作簿）
convert_md_to_excel(
    ["page_001.md", "page_002.md", "page_003.md"],
    output_path="merged.xlsx"
)
```

**功能特性：**
- 保留 Markdown 中的 HTML 表格结构
- 保持单元格合并（rowspan/colspan）
- 应用格式（边框、表头高亮）
- 自动调整列宽和行高
- 包含表格前后的内容

### 批量处理

并行处理多张图片：

```python
from pathlib import Path
from LLMkit.modules.vision.ocr_client import OCRClient

client = OCRClient("http://localhost:8000")
image_dir = Path("images")

for img_path in image_dir.glob("*.png"):
    result = client.recognize_image(
        image_path=str(img_path),
        save_markdown=True,
        output_dir="output"
    )
    print(f"已处理: {img_path.name}")
```

## 架构设计

### 三层系统架构

1. **客户端层**（本目录）
   - Jupyter notebooks 用于实验
   - 格式转换工具脚本
   - 直接使用 PaddleOCRVL

2. **API 层**（父目录）
   - `ocr_api_service.py` - FastAPI 服务
   - `ocr_client.py` - HTTP 客户端封装

3. **引擎层**（paddle_env）
   - PaddleOCRVL 核心识别引擎
   - 在独立的 conda 环境中运行

### 集成点

- **DocumentProcessor**：PDF 转图片转换（来自父模块）
- **OCRClient**：API 通信的 HTTP 客户端（来自父模块）
- **convert_table.py**：Markdown 转 Excel 转换工具

## 文件命名约定

输出文件遵循一致的命名模式：

- 图片：`page_001.png`, `page_002.png`, ...
- Markdown：`page_001.md`, `page_002.md`, ...
- JSON：`page_001.json`, `page_002.json`, ...
- 临时 PDF：`pdf_images_XXXXX_XXXX/` 目录

## 项目结构

```
paddle_ocr_vl/
├── ocr_vl.ipynb              # 主演示笔记本
├── ocr_base.ipynb            # 基础 OCR 实验
├── convert_table.py          # Markdown 转 Excel 转换器
├── 启动OCR服务_paddle_env.bat # Windows 服务启动器
├── output/                   # OCR 输出目录
│   ├── *.md                  # Markdown 结果
│   ├── *.json                # JSON 结果
│   └── *.png                 # OCR 可视化图片
└── example/                  # 示例文件
    └── merged_output.md
```

## 依赖项

**核心依赖：**
- `paddleocr` - OCR 引擎（在 paddle_env 中）
- `paddlepaddle` - 深度学习框架

**API 与集成：**
- `fastapi` - API 框架
- `uvicorn` - ASGI 服务器
- `requests` - HTTP 客户端
- `pydantic` - 数据验证

**工具库：**
- `openpyxl` - Excel 文件创建
- `pillow` - 图像处理
- `pathlib` - 路径处理

**父模块：**
- `LLMkit.modules.vision.ocr_client` - HTTP 客户端
- `LLMkit.modules.vision.document_processor` - PDF 转换

## Notebooks 说明

### ocr_vl.ipynb

主演示笔记本，涵盖：
- 直接使用 PaddleOCRVL
- 基于 API 的处理
- 批量处理工作流
- PDF 转 Excel 流程

### ocr_base.ipynb

基础 OCR 设置和实验。

## 工具说明

### convert_table.py

将包含 HTML 表格的 Markdown 文件转换为 Excel 格式。

**核心功能：**
- 从 Markdown 解析 HTML `<table>` 块
- 保留 `rowspan` 和 `colspan` 属性
- 为表头行应用灰色背景
- 为所有单元格添加边框
- 自动调整尺寸

**使用方法：**
```python
from convert_table import convert_md_to_excel

# 单个文件
convert_md_to_excel("input.md")

# 多个文件
convert_md_to_excel(["file1.md", "file2.md", "file3.md"])
```

## 故障排除

### 服务无法启动
- 确保 `paddle_env` conda 环境已激活
- 检查端口 8000 是否可用
- 验证 PaddleOCR 安装：`pip list | grep paddle`

### OCR 质量问题
- 提高 PDF 转换的 DPI（默认：200）
- 确保输入图片清晰且高分辨率
- 检查图片方向

### Excel 转换错误
- 验证 Markdown 包含 HTML `<table>` 标签
- 检查文件编码（应为 UTF-8）
- 确保已安装 openpyxl

## 贡献指南

欢迎贡献！本模块是 LLMkit 框架的一部分。

### 如何贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 报告问题

如果您遇到任何问题或有建议，请：
- 首先检查现有 issues
- 提供详细的描述和重现步骤
- 包含环境信息（操作系统、Python 版本等）

## 许可证

本项目是 LLMkit 框架的一部分。

## 致谢

- [PaddlePaddle](https://github.com/PaddlePaddle) - 提供 PaddleOCR 引擎
- [FastAPI](https://fastapi.tiangolo.com/) - 提供 API 框架
- 所有帮助改进本项目的贡献者

## 相关资源

- 📖 [PaddleOCR 文档](https://github.com/PaddlePaddle/PaddleOCR)
- 🔧 [LLMkit 视觉模块](../README.md)
- ⚡ [FastAPI 文档](https://fastapi.tiangolo.com/)
- 📊 [OpenPyXL 文档](https://openpyxl.readthedocs.io/)

---

<div align="center">

**使用 PaddleOCR 和 FastAPI 构建**

如果您觉得这个项目有帮助，请考虑给它一个 ⭐

</div>
