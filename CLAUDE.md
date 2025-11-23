# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Module Overview

This is the `paddle_ocr_vl` subdirectory within the LLMkit vision module, containing PaddleOCR Vision-Language model integration and table conversion utilities.

## Environment Setup

### PaddleOCR Service Environment

PaddleOCR requires a separate conda environment:

```bash
# Create paddle_env (Windows)
conda create -n paddle_env python=3.10
conda activate paddle_env
pip install paddlepaddle paddleocr fastapi uvicorn pillow requests pydantic

# For macOS/Linux, check parent module requirements.txt
```

### Starting the OCR Service

**Windows:**
```bash
# Run the batch file from this directory
启动OCR服务_paddle_env.bat
```

The script automatically:
- Activates the `paddle_env` conda environment
- Changes to the project root (`E:\OneDrive\project_code`)
- Starts the FastAPI service on `http://localhost:8000`

**Manual Start:**
```bash
conda activate paddle_env
cd E:\OneDrive\project_code
python LLMkit\modules\vision\ocr_api_service.py
```

Service endpoints:
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Core Components

### Jupyter Notebooks

#### `ocr_vl.ipynb`
Main notebook demonstrating PaddleOCR Vision-Language usage:

**Basic direct usage:**
```python
from paddleocr import PaddleOCRVL

pipeline = PaddleOCRVL()
output = pipeline.predict("image_path.png")
for res in output:
    res.print()  # Print structured output
    res.save_to_json(save_path="output")
    res.save_to_markdown(save_path="output")
```

**API-based usage (requires running service):**
```python
from LLMkit.modules.vision.ocr_client import OCRClient

client = OCRClient("http://localhost:8000")
result = client.recognize_image(
    image_path="image.png",
    save_markdown=True,
    save_json=False,
    output_dir="output"
)
```

**Batch processing workflow:**
1. Convert PDF to images using `DocumentProcessor`
2. Process images in batch with `OCRClient`
3. Merge markdown outputs into single file

#### `ocr_base.ipynb`
Basic OCR setup and experimentation notebook.

### Python Utilities

#### `convert_table.py`
Converts markdown files with HTML tables to Excel format.

**Key Function:**
```python
from convert_table import convert_md_to_excel

# Single file
result = convert_md_to_excel("input.md", output_path="output.xlsx")

# Multiple files (creates multi-sheet workbook)
result = convert_md_to_excel(
    ["file1.md", "file2.md", "file3.md"],
    output_path="merged.xlsx"
)
```

**Features:**
- Parses HTML tables from markdown files
- Preserves cell merging (rowspan/colspan)
- Applies formatting (borders, header highlighting)
- Handles content before and after tables
- Auto-adjusts column widths and row heights

**Table Processing Details:**
- Extracts HTML `<table>` blocks from markdown
- Preserves `rowspan` and `colspan` attributes
- Applies gray background to first two rows (headers)
- Adds thin borders to all cells
- Includes non-table content at top/bottom of sheet

## Common Development Tasks

### Running OCR on a Single Image

```python
from LLMkit.modules.vision.ocr_client import OCRClient

client = OCRClient("http://localhost:8000")

# Ensure service is running (check with health_check)
if client.health_check():
    result = client.recognize_image(
        image_path="path/to/image.png",
        save_markdown=True,
        save_json=True,
        output_dir="output"
    )

    # Access result paths
    print(result.get("markdown_path"))
    print(result.get("json_path"))
```

### Batch Processing PDF to Excel

Complete workflow from PDF to Excel table:

```python
from LLMkit.modules.vision.document_processor import DocumentProcessor
from LLMkit.modules.vision.ocr_client import OCRClient
from convert_table import convert_md_to_excel
from pathlib import Path

# 1. Convert PDF to images
doc_processor = DocumentProcessor(dpi=200)
png_results = doc_processor.process_document("document.pdf")

# 2. Get image paths
dir_path = png_results[0]["output_dir"]
image_files = list(Path(dir_path).glob("*.png"))

# 3. OCR each image
client = OCRClient("http://localhost:8000")
md_files = []

for img_path in image_files:
    result = client.recognize_image(
        image_path=str(img_path),
        save_markdown=True,
        output_dir="output"
    )
    md_files.append(result.get("markdown_path"))

# 4. Convert markdown to Excel
excel_path = convert_md_to_excel(md_files, output_path="merged_output.xlsx")
```

### Merging Multiple Markdown Files

```python
from pathlib import Path

# Collect markdown content
md_files = ["output/page_001.md", "output/page_002.md", "output/page_003.md"]
content = []

for md_file in md_files:
    content.append(Path(md_file).read_text(encoding="utf-8"))

# Write merged file
output_path = "merged_output.md"
with open(output_path, "w", encoding="utf-8") as f:
    for md_text in content:
        f.write(md_text)
        f.write("\n\n")  # Separator between pages
```

## Architecture Notes

### OCR Service Architecture

This subdirectory is part of a three-tier OCR system:

1. **Client Layer** (this directory):
   - Jupyter notebooks for experimentation
   - Utility scripts for format conversion
   - Direct PaddleOCRVL usage

2. **API Layer** (parent directory):
   - `ocr_api_service.py` - FastAPI service
   - `ocr_client.py` - HTTP client wrapper

3. **Engine Layer** (paddle_env):
   - PaddleOCRVL core recognition engine
   - Runs in separate conda environment

### Integration with Parent Module

This subdirectory extends the parent vision module:

- Uses `DocumentProcessor` from parent for PDF conversion
- Uses `OCRClient` from parent for API communication
- Outputs integrate with parent's workflow (markdown → Excel)
- Shares output directory structure with parent module

### File Naming Conventions

Output files follow consistent patterns:

- Images: `page_XXX.png` (e.g., `page_001.png`, `page_098.png`)
- Markdown: `page_XXX.md`
- JSON: `page_XXX.json`
- Temporary PDFs: `pdf_images_XXXXX_XXXX/` directories

## Dependencies

This module depends on:

**Core:**
- `paddleocr` - OCR engine (in paddle_env)
- `paddlepaddle` - Deep learning framework

**Integration:**
- `LLMkit.modules.vision.ocr_client` - HTTP client
- `LLMkit.modules.vision.document_processor` - PDF conversion
- `LLMkit` - Output paths and utilities

**Utilities:**
- `openpyxl` - Excel file creation
- `pathlib` - Path handling
- `re` - Regular expression parsing
