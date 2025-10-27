#!/usr/bin/env python3
"""
DeepSeek-OCR METS-aware Processing
===================================
Verarbeitet Dokumente mit METS-Metadaten und strukturiert Output entsprechend

Features:
- Liest METS.xml für Metadaten
- Verarbeitet alle Bilder in der richtigen Reihenfolge
- Speichert Ergebnisse mit METS-Kontext
- Erstellt strukturiertes Output-Format

Usage:
    python test_ocr_mets.py data/o_szd.151/
"""

import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time
import xml.etree.ElementTree as ET

def setup_utf8():
    """UTF-8 Fix für Windows"""
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_mets(mets_file):
    """Parse METS XML und extrahiere Metadaten"""
    tree = ET.parse(mets_file)
    root = tree.getroot()

    # Namespaces
    ns = {
        'mets': 'http://www.loc.gov/METS/',
        'mods': 'http://www.loc.gov/mods/v3',
        'xlink': 'http://www.w3.org/1999/xlink',
        'dv': 'http://dfg-viewer.de/',
        'exif': 'http://ns.adobe.com/exif/1.0/'
    }

    # Extrahiere Basis-Metadaten
    metadata = {}

    # Titel
    title_elem = root.find('.//mods:title', ns)
    if title_elem is not None:
        metadata['title'] = title_elem.text

    # Signatur
    sig_elem = root.find('.//mods:note[@type="signature"]', ns)
    if sig_elem is not None:
        metadata['signature'] = sig_elem.text

    # Autor
    author_elem = root.find('.//mods:displayForm', ns)
    if author_elem is not None:
        metadata['author'] = author_elem.text

    # Sprache
    lang_elem = root.find('.//mods:languageTerm[@type="code"]', ns)
    if lang_elem is not None:
        metadata['language'] = lang_elem.text

    # Rechte
    owner_elem = root.find('.//dv:owner', ns)
    if owner_elem is not None:
        metadata['owner'] = owner_elem.text

    # URN
    urn_elem = root.find('.//mods:identifier[@type="urn"]', ns)
    if urn_elem is not None:
        metadata['urn'] = urn_elem.text

    # Extrahiere Seiten-Struktur
    pages = []
    struct_divs = root.findall('.//mets:structMap[@TYPE="PHYSICAL"]//mets:div[@TYPE="page"]', ns)

    for div in struct_divs:
        page_id = div.get('ID')
        order = div.get('ORDER')
        content_id = div.get('CONTENTIDS')

        # Finde zugehörige File-ID
        fptr = div.find('.//mets:fptr', ns)
        if fptr is not None:
            file_id = fptr.get('FILEID')

            pages.append({
                'id': page_id,
                'order': int(order),
                'file_id': file_id,
                'content_id': content_id
            })

    # Extrahiere logische Struktur
    logical_divs = root.findall('.//mets:structMap[@TYPE="LOGICAL"]//mets:div', ns)
    logical_structure = []

    for div in logical_divs:
        div_id = div.get('ID')
        div_type = div.get('TYPE')

        if div_type and div_id and div_id.startswith('U.'):
            logical_structure.append({
                'id': div_id,
                'type': div_type
            })

    # Mapping: Logical → Physical
    smlinks = root.findall('.//mets:smLink', ns)
    logical_to_physical = {}

    for link in smlinks:
        from_id = link.get('{http://www.w3.org/1999/xlink}from')
        to_id = link.get('{http://www.w3.org/1999/xlink}to')

        if from_id not in logical_to_physical:
            logical_to_physical[from_id] = []
        logical_to_physical[from_id].append(to_id)

    return {
        'metadata': metadata,
        'pages': sorted(pages, key=lambda x: x['order']),
        'logical_structure': logical_structure,
        'logical_to_physical': logical_to_physical
    }

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

def process_document(input_dir, tokenizer, model, output_dir, base_size=640):
    """Verarbeite METS-Dokument"""

    input_path = Path(input_dir)

    # Lade METS
    mets_file = input_path / "mets.xml"
    if not mets_file.exists():
        print(f"[ERROR] METS file not found: {mets_file}")
        return None

    print("="*60)
    print("PARSING METS")
    print("="*60)

    mets_data = parse_mets(mets_file)

    print(f"Title:    {mets_data['metadata'].get('title', 'N/A')}")
    print(f"Author:   {mets_data['metadata'].get('author', 'N/A')}")
    print(f"Signature: {mets_data['metadata'].get('signature', 'N/A')}")
    print(f"Language: {mets_data['metadata'].get('language', 'N/A')}")
    print(f"Pages:    {len(mets_data['pages'])}")
    print()

    # Finde Bilder
    images_dir = input_path / "images"
    if not images_dir.exists():
        print(f"[ERROR] Images directory not found: {images_dir}")
        return None

    # Verarbeite alle Seiten
    results = []

    for page in mets_data['pages']:
        file_id = page['file_id']
        order = page['order']

        # Finde passendes Bild
        image_file = None
        for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            candidate = images_dir / f"{file_id}{ext}"
            if candidate.exists():
                image_file = candidate
                break

            # Versuche auch ohne Punkt
            candidate = images_dir / f"{file_id.replace('.', '_')}{ext}"
            if candidate.exists():
                image_file = candidate
                break

        if not image_file:
            print(f"[WARNING] Image not found for {file_id}")
            continue

        print("="*60)
        print(f"PAGE {order}: {file_id}")
        print("="*60)

        try:
            image = Image.open(image_file)
            print(f"Size: {image.size[0]}x{image.size[1]}px")

            start_time = time.time()

            prompt = "<image>\nExtract all text from this document."

            # Temporäres Output
            temp_output = os.path.join(output_dir, "temp", file_id)
            os.makedirs(temp_output, exist_ok=True)

            model.infer(
                tokenizer,
                prompt=prompt,
                image_file=str(image_file),
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

            results.append({
                'page': order,
                'file_id': file_id,
                'image_file': str(image_file.name),
                'text': text,
                'characters': char_count,
                'time_seconds': round(elapsed, 2)
            })

        except Exception as e:
            print(f"[ERROR] {e}\n")
            results.append({
                'page': order,
                'file_id': file_id,
                'error': str(e)
            })

    return {
        'mets_metadata': mets_data['metadata'],
        'logical_structure': mets_data['logical_structure'],
        'pages': results,
        'total_pages': len(results),
        'successful': sum(1 for r in results if 'text' in r),
        'failed': sum(1 for r in results if 'error' in r)
    }

def main():
    """Hauptprogramm"""
    setup_utf8()

    if len(sys.argv) < 2:
        print("Usage: python test_ocr_mets.py <mets_directory>")
        print("Example: python test_ocr_mets.py data/o_szd.151/")
        sys.exit(1)

    input_dir = sys.argv[1]

    if not os.path.exists(input_dir):
        print(f"[ERROR] Directory not found: {input_dir}")
        sys.exit(1)

    print("\n" + "="*60)
    print("DEEPSEEK-OCR METS PROCESSING")
    print("="*60)
    print(f"Input: {input_dir}\n")

    # Output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_id = Path(input_dir).name
    output_dir = f"results/mets_{object_id}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Output: {output_dir}\n")

    # Model laden
    tokenizer, model = load_model()

    # Verarbeiten
    result = process_document(input_dir, tokenizer, model, output_dir)

    if not result:
        print("[ERROR] Processing failed")
        sys.exit(1)

    # Speichere strukturiertes Ergebnis
    output_file = os.path.join(output_dir, f"{object_id}_ocr.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # Speichere auch als Plain Text (alle Seiten)
    text_file = os.path.join(output_dir, f"{object_id}_fulltext.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        for page_result in result['pages']:
            if 'text' in page_result:
                f.write(f"--- PAGE {page_result['page']} ---\n\n")
                f.write(page_result['text'])
                f.write("\n\n")

    # Summary
    print("="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Document: {result['mets_metadata'].get('title', 'N/A')}")
    print(f"Pages:    {result['total_pages']}")
    print(f"Success:  {result['successful']}")
    print(f"Failed:   {result['failed']}")
    print(f"\nResults:")
    print(f"  JSON:     {output_file}")
    print(f"  Fulltext: {text_file}")
    print("="*60)

if __name__ == "__main__":
    main()
