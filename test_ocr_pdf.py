#!/usr/bin/env python3
"""
DeepSeek-OCR PDF Processing
============================
Konvertiert PDF zu Bildern und führt OCR durch

Usage:
    python test_ocr_pdf.py data/DTS_Flechte.pdf
"""

import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import fitz  # PyMuPDF
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time

def setup_utf8():
    """UTF-8 Fix für Windows"""
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_model():
    """Lade DeepSeek-OCR Modell"""
    print("="*60)
    print("LOADING MODEL")
    print("="*60)

    model_name = "deepseek-ai/DeepSeek-OCR"

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    print("[OK] Tokenizer loaded")

    model = AutoModel.from_pretrained(
        model_name,
        trust_remote_code=True,
        use_safetensors=True
    )
    model = model.eval().cuda().to(torch.bfloat16)
    print("[OK] Model loaded to GPU\n")

    return tokenizer, model

def pdf_to_images(pdf_path, output_dir, dpi=300):
    """
    Konvertiert PDF zu Bildern mit PyMuPDF

    Args:
        pdf_path: Pfad zum PDF
        output_dir: Output-Verzeichnis für Bilder
        dpi: Auflösung (300 DPI empfohlen)

    Returns:
        Liste von Bild-Pfaden
    """
    print("="*60)
    print("CONVERTING PDF TO IMAGES")
    print("="*60)
    print(f"PDF: {pdf_path}")
    print(f"DPI: {dpi}\n")

    os.makedirs(output_dir, exist_ok=True)

    try:
        # Öffne PDF
        pdf_document = fitz.open(pdf_path)
        page_count = len(pdf_document)

        print(f"[OK] {page_count} pages found\n")

        # Zoom-Faktor für DPI (72 DPI ist Standard)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        # Konvertiere jede Seite
        image_paths = []

        for page_num in range(page_count):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=mat)

            image_path = os.path.join(output_dir, f"page_{page_num + 1:03d}.png")
            pix.save(image_path)

            image_paths.append(image_path)
            print(f"  Page {page_num + 1}: {pix.width}x{pix.height}px → {Path(image_path).name}")

        pdf_document.close()

        return image_paths

    except Exception as e:
        print(f"[ERROR] PDF conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def process_image(image_path, page_num, tokenizer, model, output_dir, base_size=640):
    """Verarbeite ein Bild"""
    print("="*60)
    print(f"PAGE {page_num}")
    print("="*60)
    print(f"Image: {Path(image_path).name}")

    try:
        image = Image.open(image_path)
        print(f"Size: {image.size[0]}x{image.size[1]}px")

        start_time = time.time()

        prompt = "<image>\nExtract all text from this document."

        # Temp output
        temp_output = os.path.join(output_dir, f"page_{page_num:03d}")
        os.makedirs(temp_output, exist_ok=True)

        model.infer(
            tokenizer,
            prompt=prompt,
            image_file=str(image_path),
            output_path=temp_output,
            base_size=base_size,
            image_size=640,
            crop_mode=True,
            save_results=True,
            test_compress=True
        )

        elapsed = time.time() - start_time

        # Lese Ergebnis
        result_file = os.path.join(temp_output, "result.mmd")
        text = ""

        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                text = f.read()

        char_count = len(text.strip())
        print(f"[OK] {char_count} characters in {elapsed:.1f}s\n")

        return {
            'page': page_num,
            'image_file': Path(image_path).name,
            'text': text,
            'characters': char_count,
            'time_seconds': round(elapsed, 2)
        }

    except Exception as e:
        print(f"[ERROR] {e}\n")
        return {
            'page': page_num,
            'image_file': Path(image_path).name,
            'error': str(e)
        }

def main():
    """Hauptprogramm"""
    setup_utf8()

    if len(sys.argv) < 2:
        print("Usage: python test_ocr_pdf.py <pdf_file>")
        print("Example: python test_ocr_pdf.py data/DTS_Flechte.pdf")
        sys.exit(1)

    pdf_file = sys.argv[1]

    if not os.path.exists(pdf_file):
        print(f"[ERROR] File not found: {pdf_file}")
        sys.exit(1)

    print("\n" + "="*60)
    print("DEEPSEEK-OCR PDF PROCESSING")
    print("="*60)
    print(f"Input: {pdf_file}\n")

    # Output setup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_name = Path(pdf_file).stem
    output_dir = f"results/pdf_{pdf_name}_{timestamp}"
    images_dir = os.path.join(output_dir, "images")

    os.makedirs(output_dir, exist_ok=True)

    # 1. PDF → Images
    image_paths = pdf_to_images(pdf_file, images_dir, dpi=300)

    if not image_paths:
        print("[ERROR] No images created")
        sys.exit(1)

    # 2. Load Model
    tokenizer, model = load_model()

    # 3. Process alle Seiten
    results = []

    for i, image_path in enumerate(image_paths, 1):
        result = process_image(image_path, i, tokenizer, model, os.path.join(output_dir, "temp"))
        results.append(result)

    # 4. Speichere Ergebnisse
    output_data = {
        'source_pdf': str(Path(pdf_file).name),
        'total_pages': len(image_paths),
        'successful': sum(1 for r in results if 'text' in r),
        'failed': sum(1 for r in results if 'error' in r),
        'pages': results,
        'timestamp': timestamp
    }

    output_file = os.path.join(output_dir, f"{pdf_name}_ocr.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Fulltext
    text_file = os.path.join(output_dir, f"{pdf_name}_fulltext.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        for page_result in results:
            if 'text' in page_result:
                f.write(f"--- PAGE {page_result['page']} ---\n\n")
                f.write(page_result['text'])
                f.write("\n\n")

    # Summary
    print("="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"PDF: {Path(pdf_file).name}")
    print(f"Pages: {output_data['total_pages']}")
    print(f"Success: {output_data['successful']}")
    print(f"Failed: {output_data['failed']}")
    print(f"\nResults:")
    print(f"  JSON: {output_file}")
    print(f"  Text: {text_file}")
    print(f"  Images: {images_dir}/")
    print("="*60)

if __name__ == "__main__":
    main()
