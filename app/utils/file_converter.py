import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
import fitz  # PyMuPDF
from PIL import Image as PILImage
import io
import json
from paddleocr import PaddleOCR

# Initialize PaddleOCR for both English and Chinese
paddle_ocr_en = PaddleOCR(use_angle_cls=True, lang='en')
paddle_ocr_zh = PaddleOCR(use_angle_cls=True, lang='ch')

FONT_PATH = os.path.join(os.path.dirname(__file__), 'NotoSansSC-VariableFont_wght.ttf')

async def convert_excel_to_pdf(excel_path: str):
    """
    Convert Excel file to PDF and extract cell info (row, col, value, ocr_text if image)
    Returns: (pdf_path, cell_info_path)
    """
    try:
        wb = load_workbook(excel_path)
        sheet = wb.active

        # Create a new PDF document
        pdf_document = fitz.open()
        page = pdf_document.new_page()

        # Convert Excel to DataFrame for easier text handling
        df = pd.read_excel(excel_path)
        print('Excel DataFrame preview:')
        print(df.head(10))

        y_position = 50
        cell_info = []
        for row_idx, row in df.iterrows():
            text = " | ".join(str(cell) if pd.notna(cell) else '' for cell in row)
            page.insert_textbox(
                fitz.Rect(50, y_position, 550, y_position + 20),
                text,
                fontname="NotoSansSC",
                fontfile=FONT_PATH
            )
            y_position += 20
            for col_idx, cell in enumerate(row):
                cell_dict = {
                    "row": row_idx + 2,  # +2 for header and 0-index
                    "col": col_idx + 1,
                    "value": str(cell) if pd.notna(cell) else ''
                }
                # Add each cell as a separate text block for search
                page.insert_textbox(
                    fitz.Rect(50 + col_idx * 100, y_position, 150 + col_idx * 100, y_position + 20),
                    str(cell) if pd.notna(cell) else '',
                    fontname="NotoSansSC",
                    fontfile=FONT_PATH
                )
                # Check for image in cell (openpyxl stores images separately)
                for img in getattr(sheet, '_images', []):
                    anchor = getattr(img.anchor, '_from', None)
                    if anchor and anchor.row == row_idx + 1 and anchor.col == col_idx:
                        try:
                            # Extract image bytes
                            img_bytes = io.BytesIO()
                            img.image.save(img_bytes, format=img.image.format)
                            img_bytes.seek(0)
                            pil_img = PILImage.open(img_bytes)
                            # Run OCR on the image (both EN and ZH)
                            try:
                                ocr_results_en = paddle_ocr_en.ocr(pil_img)
                            except Exception as ocr_e:
                                print(f"[ERROR] PaddleOCR EN failed for Excel cell ({row_idx+2},{col_idx+1}): {ocr_e}")
                                ocr_results_en = None
                            try:
                                ocr_results_zh = paddle_ocr_zh.ocr(pil_img)
                            except Exception as ocr_e:
                                print(f"[ERROR] PaddleOCR ZH failed for Excel cell ({row_idx+2},{col_idx+1}): {ocr_e}")
                                ocr_results_zh = None
                            ocr_texts = set()
                            for result in (ocr_results_en[0] if ocr_results_en and len(ocr_results_en) > 0 else []):
                                ocr_texts.add(result[1][0])
                            for result in (ocr_results_zh[0] if ocr_results_zh and len(ocr_results_zh) > 0 else []):
                                ocr_texts.add(result[1][0])
                            cell_dict["ocr_text"] = list(ocr_texts)
                        except Exception as img_e:
                            print(f"[ERROR] Image extraction/OCR failed for Excel cell ({row_idx+2},{col_idx+1}): {img_e}")
                            cell_dict["ocr_error"] = str(img_e)
                cell_info.append(cell_dict)
            y_position += 20  # Add extra space after each row

        # Save PDF
        pdf_path = excel_path.rsplit('.', 1)[0] + '.pdf'
        pdf_document.save(pdf_path)
        pdf_document.close()

        # Save cell info as JSON
        cell_info_path = excel_path.rsplit('.', 1)[0] + '_cellinfo.json'
        with open(cell_info_path, 'w', encoding='utf-8') as f:
            json.dump(cell_info, f, ensure_ascii=False, indent=2)

        return pdf_path, cell_info_path

    except Exception as e:
        print(f"[ERROR] Excel to PDF conversion failed: {e}")
        raise Exception(f"Error converting Excel to PDF: {str(e)}") 