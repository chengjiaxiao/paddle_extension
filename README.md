# PaddleOCR Vision-Language Module

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-VL-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

English | [简体中文](README_zh.md)

A powerful OCR (Optical Character Recognition) module based on PaddleOCR Vision-Language models, providing table extraction, document processing, and markdown/Excel conversion capabilities.

## Features

- **Vision-Language OCR**: Advanced table and document recognition using PaddleOCR VL models
- **API Service**: FastAPI-based OCR service for batch processing
- **Format Conversion**: Convert OCR results from Markdown to Excel with preserved formatting
- **Batch Processing**: Process multiple images or PDF pages in parallel
- **Table Preservation**: Maintain table structures including merged cells (rowspan/colspan)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
  - [Environment Setup](#1-environment-setup)
  - [Start OCR Service](#2-start-ocr-service)
  - [Basic Usage](#3-basic-usage)
- [Advanced Workflows](#advanced-workflows)
  - [PDF to Excel Pipeline](#pdf-to-excel-pipeline)
  - [Markdown to Excel Conversion](#markdown-to-excel-conversion)
  - [Batch Processing](#batch-processing)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

### 1. Environment Setup

Create a dedicated conda environment for PaddleOCR:

```bash
# Windows
conda create -n paddle_env python=3.10
conda activate paddle_env
pip install paddlepaddle paddleocr fastapi uvicorn pillow requests pydantic
```

### 2. Start OCR Service

**Windows (Quick Start):**
```bash
启动OCR服务_paddle_env.bat
```

**Manual Start:**
```bash
conda activate paddle_env
python ocr_api_service.py  # From parent directory
```

Service will be available at `http://localhost:8000`
- 📚 API docs: http://localhost:8000/docs
- 📖 ReDoc: http://localhost:8000/redoc

### 3. Basic Usage

#### Direct PaddleOCR Usage

```python
from paddleocr import PaddleOCRVL

# Initialize pipeline
pipeline = PaddleOCRVL()

# Process image
output = pipeline.predict("image_path.png")

# Save results
for res in output:
    res.print()  # Print to console
    res.save_to_json(save_path="output")
    res.save_to_markdown(save_path="output")
```

#### API-based Usage

```python
from LLMkit.modules.vision.ocr_client import OCRClient

# Initialize client
client = OCRClient("http://localhost:8000")

# Check service health
if client.health_check():
    # Process single image
    result = client.recognize_image(
        image_path="path/to/image.png",
        save_markdown=True,
        save_json=True,
        output_dir="output"
    )

    print(result.get("markdown_path"))
    print(result.get("json_path"))
```

## Advanced Workflows

### PDF to Excel Pipeline

Complete workflow for extracting tables from PDF documents:

<details>
<summary>Click to expand full workflow code</summary>

```python
from LLMkit.modules.vision.document_processor import DocumentProcessor
from LLMkit.modules.vision.ocr_client import OCRClient
from convert_table import convert_md_to_excel
from pathlib import Path

# Step 1: Convert PDF to images
doc_processor = DocumentProcessor(dpi=200)
png_results = doc_processor.process_document("document.pdf")

# Step 2: Get image paths
dir_path = png_results[0]["output_dir"]
image_files = list(Path(dir_path).glob("*.png"))

# Step 3: OCR each image
client = OCRClient("http://localhost:8000")
md_files = []

for img_path in image_files:
    result = client.recognize_image(
        image_path=str(img_path),
        save_markdown=True,
        output_dir="output"
    )
    md_files.append(result.get("markdown_path"))

# Step 4: Convert to Excel
excel_path = convert_md_to_excel(md_files, output_path="merged_output.xlsx")
print(f"Excel file created: {excel_path}")
```

</details>

### Markdown to Excel Conversion

Convert OCR markdown results to formatted Excel files:

```python
from convert_table import convert_md_to_excel

# Single file
convert_md_to_excel("output.md", output_path="output.xlsx")

# Multiple files (creates multi-sheet workbook)
convert_md_to_excel(
    ["page_001.md", "page_002.md", "page_003.md"],
    output_path="merged.xlsx"
)
```

**Features:**
- Preserves HTML table structures from markdown
- Maintains cell merging (rowspan/colspan)
- Applies formatting (borders, header highlighting)
- Auto-adjusts column widths and row heights
- Includes content before and after tables

### Batch Processing

Process multiple images in parallel:

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
    print(f"Processed: {img_path.name}")
```

## Architecture

### Three-Tier System

1. **Client Layer** (this directory)
   - Jupyter notebooks for experimentation
   - Utility scripts for format conversion
   - Direct PaddleOCRVL usage

2. **API Layer** (parent directory)
   - `ocr_api_service.py` - FastAPI service
   - `ocr_client.py` - HTTP client wrapper

3. **Engine Layer** (paddle_env)
   - PaddleOCRVL core recognition engine
   - Runs in separate conda environment

### Integration Points

- **DocumentProcessor**: PDF to image conversion (from parent module)
- **OCRClient**: HTTP client for API communication (from parent module)
- **convert_table.py**: Markdown to Excel conversion utility

## File Naming Conventions

Output files follow consistent patterns:

- Images: `page_001.png`, `page_002.png`, ...
- Markdown: `page_001.md`, `page_002.md`, ...
- JSON: `page_001.json`, `page_002.json`, ...
- Temporary PDFs: `pdf_images_XXXXX_XXXX/` directories

## Project Structure

```
paddle_ocr_vl/
├── ocr_vl.ipynb              # Main demo notebook
├── ocr_base.ipynb            # Basic OCR experiments
├── convert_table.py          # Markdown to Excel converter
├── 启动OCR服务_paddle_env.bat # Windows service launcher
├── output/                   # OCR output directory
│   ├── *.md                  # Markdown results
│   ├── *.json                # JSON results
│   └── *.png                 # OCR visualization images
└── example/                  # Example files
    └── merged_output.md
```

## Dependencies

**Core:**
- `paddleocr` - OCR engine (in paddle_env)
- `paddlepaddle` - Deep learning framework

**API & Integration:**
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `pydantic` - Data validation

**Utilities:**
- `openpyxl` - Excel file creation
- `pillow` - Image processing
- `pathlib` - Path handling

**Parent Module:**
- `LLMkit.modules.vision.ocr_client` - HTTP client
- `LLMkit.modules.vision.document_processor` - PDF conversion

## Notebooks

### ocr_vl.ipynb

Main demonstration notebook covering:
- Direct PaddleOCRVL usage
- API-based processing
- Batch processing workflows
- PDF to Excel pipelines

### ocr_base.ipynb

Basic OCR setup and experimentation.

## Utilities

### convert_table.py

Converts markdown files with HTML tables to Excel format.

**Key Features:**
- Parses HTML `<table>` blocks from markdown
- Preserves `rowspan` and `colspan` attributes
- Applies gray background to header rows
- Adds borders to all cells
- Auto-adjusts dimensions

**Usage:**
```python
from convert_table import convert_md_to_excel

# Single file
convert_md_to_excel("input.md")

# Multiple files
convert_md_to_excel(["file1.md", "file2.md", "file3.md"])
```

## Troubleshooting

### Service won't start
- Ensure `paddle_env` conda environment is activated
- Check if port 8000 is available
- Verify PaddleOCR installation: `pip list | grep paddle`

### OCR quality issues
- Increase DPI for PDF conversion (default: 200)
- Ensure input images are clear and high-resolution
- Check image orientation

### Excel conversion errors
- Verify markdown contains HTML `<table>` tags
- Check file encoding (should be UTF-8)
- Ensure openpyxl is installed

## Contributing

Contributions are welcome! This module is part of the LLMkit framework.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Reporting Issues

If you encounter any issues or have suggestions, please:
- Check existing issues first
- Provide detailed description and steps to reproduce
- Include environment information (OS, Python version, etc.)

## License

This project is part of the LLMkit framework.

## Acknowledgments

- [PaddlePaddle](https://github.com/PaddlePaddle) - For the PaddleOCR engine
- [FastAPI](https://fastapi.tiangolo.com/) - For the API framework
- All contributors who have helped improve this project

## Related Resources

- 📖 [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- 🔧 [LLMkit Vision Module](../README.md)
- ⚡ [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 📊 [OpenPyXL Documentation](https://openpyxl.readthedocs.io/)

---

<div align="center">

**Made with PaddleOCR and FastAPI**

If you find this project helpful, please consider giving it a ⭐

</div>
