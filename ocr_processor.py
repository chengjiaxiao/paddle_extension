#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Document Processor

Process PDF and image files using PaddleOCR, generating both individual page
markdown files and a merged markdown file.

Usage:
    python ocr_processor.py input.pdf
    python ocr_processor.py input.png --output results
    python ocr_processor.py input.pdf --dpi 300 --merged-name output.md
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_document(
    input_path: Union[str, Path],
    output_dir: Union[str, Path] = "output",
    api_url: str = "http://localhost:8000",
    dpi: int = 200,
    merged_name: str = "merged_output.md",
    save_json: bool = False
) -> Dict[str, any]:
    """
    Process a PDF or image file with OCR, generating markdown outputs.

    Args:
        input_path: Path to input PDF or image file
        output_dir: Directory to save output files
        api_url: OCR API service URL
        dpi: DPI for PDF to image conversion (default: 200)
        merged_name: Name of the merged markdown file
        save_json: Whether to save JSON results

    Returns:
        Dictionary with processing results:
        {
            'status': 'success' | 'error',
            'input_file': str,
            'page_files': List[str],
            'merged_file': str,
            'message': str
        }
    """
    from LLMkit.modules.vision.ocr_client import OCRClient
    from LLMkit.modules.vision.document_processor import DocumentProcessor

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate input file
    if not input_path.exists():
        error_msg = f"输入文件不存在: {input_path}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'input_file': str(input_path),
            'message': error_msg
        }

    # Initialize OCR client
    client = OCRClient(api_url)

    # Check service health
    if not client.health_check():
        error_msg = (
            f"OCR 服务不可用: {api_url}\n"
            f"请先启动服务: 启动OCR服务_paddle_env.bat"
        )
        logger.error(error_msg)
        return {
            'status': 'error',
            'input_file': str(input_path),
            'message': error_msg
        }

    logger.info(f"开始处理文件: {input_path}")

    # Step 1: Get image file list
    image_files = []

    if input_path.suffix.lower() == '.pdf':
        logger.info(f"检测到 PDF 文件，开始转换 (DPI={dpi})...")
        doc_processor = DocumentProcessor(dpi=dpi)

        try:
            png_results = doc_processor.process_document(str(input_path))
            if not png_results:
                raise ValueError("PDF 转换失败")

            # Get image directory
            image_dir = Path(png_results[0]["output_dir"])
            image_files = sorted(image_dir.glob("*.png"))

            logger.info(f"PDF 转换完成，共 {len(image_files)} 页")

        except Exception as e:
            error_msg = f"PDF 转换失败: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'input_file': str(input_path),
                'message': error_msg
            }

    elif input_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
        logger.info("检测到图片文件")
        image_files = [input_path]

    else:
        error_msg = f"不支持的文件格式: {input_path.suffix}"
        logger.error(error_msg)
        return {
            'status': 'error',
            'input_file': str(input_path),
            'message': error_msg
        }

    # Step 2: Process each image with OCR
    logger.info(f"开始 OCR 处理，共 {len(image_files)} 个文件...")

    md_files = []
    page_contents = []
    failed_pages = []

    for idx, img_path in enumerate(image_files, 1):
        try:
            logger.info(f"处理第 {idx}/{len(image_files)} 页: {img_path.name}")

            result = client.recognize_image(
                image_path=str(img_path),
                save_markdown=True,
                save_json=save_json,
                output_dir=str(output_dir)
            )

            if result.get('status') == 'error':
                raise ValueError(result.get('message', 'OCR 处理失败'))

            # Get markdown path
            md_path = result.get("markdown_path")
            if md_path:
                md_path_obj = Path(md_path)
                if not md_path_obj.is_absolute():
                    # Handle relative paths
                    md_path_obj = output_dir / md_path_obj.name

                md_files.append(str(md_path_obj))

                # Read content for merging
                if md_path_obj.exists():
                    md_content = md_path_obj.read_text(encoding="utf-8")
                    page_contents.append(md_content)
                else:
                    logger.warning(f"Markdown 文件不存在: {md_path_obj}")

        except Exception as e:
            logger.error(f"处理第 {idx} 页失败: {str(e)}")
            failed_pages.append(idx)

    # Step 3: Merge markdown files
    if page_contents:
        merged_path = output_dir / merged_name
        logger.info(f"合并 markdown 文件到: {merged_path}")

        try:
            with open(merged_path, "w", encoding="utf-8") as f:
                for idx, content in enumerate(page_contents, 1):
                    # Add page separator
                    if idx > 1:
                        f.write("\n\n---\n\n")
                    f.write(f"<!-- Page {idx} -->\n\n")
                    f.write(content)

            logger.info(f"合并完成！共 {len(page_contents)} 页")

        except Exception as e:
            logger.error(f"合并文件失败: {str(e)}")
            merged_path = None
    else:
        merged_path = None
        logger.warning("没有可合并的内容")

    # Summary
    success_count = len(md_files)
    total_count = len(image_files)

    result_msg = (
        f"处理完成！\n"
        f"  成功: {success_count}/{total_count} 页\n"
        f"  输出目录: {output_dir}\n"
        f"  独立文件: {success_count} 个\n"
        f"  合并文件: {merged_path if merged_path else '无'}"
    )

    if failed_pages:
        result_msg += f"\n  失败页面: {failed_pages}"

    logger.info(result_msg)

    return {
        'status': 'success' if success_count > 0 else 'error',
        'input_file': str(input_path),
        'total_pages': total_count,
        'success_pages': success_count,
        'failed_pages': failed_pages,
        'page_files': md_files,
        'merged_file': str(merged_path) if merged_path else None,
        'output_dir': str(output_dir),
        'message': result_msg
    }


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='OCR 文档处理工具 - 处理 PDF 和图片文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理 PDF 文件
  python ocr_processor.py document.pdf

  # 指定输出目录
  python ocr_processor.py document.pdf --output results

  # 处理图片文件
  python ocr_processor.py image.png

  # 自定义 DPI 和合并文件名
  python ocr_processor.py document.pdf --dpi 300 --merged-name output.md

  # 同时保存 JSON 结果
  python ocr_processor.py document.pdf --save-json
        """
    )

    parser.add_argument(
        'input_path',
        type=str,
        help='输入文件路径 (PDF 或图片)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output',
        help='输出目录 (默认: ./output)'
    )

    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000',
        help='OCR API 服务地址 (默认: http://localhost:8000)'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=200,
        help='PDF 转图片 DPI (默认: 200)'
    )

    parser.add_argument(
        '--merged-name',
        type=str,
        default='merged_output.md',
        help='合并文件名 (默认: merged_output.md)'
    )

    parser.add_argument(
        '--save-json',
        action='store_true',
        help='是否保存 JSON 结果'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志'
    )

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Process document
    result = process_document(
        input_path=args.input_path,
        output_dir=args.output,
        api_url=args.api_url,
        dpi=args.dpi,
        merged_name=args.merged_name,
        save_json=args.save_json
    )

    # Exit with appropriate code
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == "__main__":
    main()
