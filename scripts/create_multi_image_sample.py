#!/usr/bin/env python3
"""
Create Sample from Multiple-Image OCR Results
==============================================
Erstellt Sample-Daten für GitHub Pages aus mehreren Single-Image OCR-Ergebnissen

Usage:
    python create_multi_image_sample.py karteikarten "Historical Archive Cards" --language multi \
        results/image_signal-2025-10-29-073743_20251029_074156 \
        results/image_signal-2025-10-29-073743_002_20251029_074221 \
        results/image_signal-2025-10-29-073743_003_20251029_074256 \
        results/image_signal-2025-10-29-073743_004_20251029_074314 \
        results/image_signal-2025-10-29-073743_005_20251029_074343 \
        results/image_signal-2025-10-29-073743_006_20251029_074412
"""

import json
import shutil
import sys
import io
from pathlib import Path
import argparse

# UTF-8 Fix für Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_multi_sample(result_dirs, doc_id, title, language, author=None, signature=None):
    """
    Erstellt Sample aus mehreren Single-Image OCR Results

    Args:
        result_dirs: Liste von Paths zu results/image_XXX_TIMESTAMP
        doc_id: Eindeutige ID für Dokument (z.B. karteikarten)
        title: Dokumenttitel
        language: Sprachcode (de, fr, en, multi, etc.)
        author: Optional - Autor
        signature: Optional - Signatur
    """

    # Sample-Verzeichnisse
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)

    images_dir = samples_dir / "images" / doc_id
    images_dir.mkdir(parents=True, exist_ok=True)

    # Sammle alle OCR-Ergebnisse
    pages = []
    total_time = 0
    total_chars = 0
    successful = 0
    failed = 0

    for i, result_dir in enumerate(result_dirs, 1):
        result_path = Path(result_dir)

        # Lade OCR Result
        result_json = result_path / "result.json"
        if not result_json.exists():
            print(f"[WARN] result.json not found in {result_dir}, skipping")
            failed += 1
            continue

        with open(result_json, 'r', encoding='utf-8') as f:
            result = json.load(f)

        # Kopiere Bild
        source_image = Path(result['image_path'])
        if not source_image.exists():
            print(f"[WARN] Source image not found: {source_image}, skipping")
            failed += 1
            continue

        # Bild nach samples/ kopieren
        dest_image = images_dir / source_image.name
        shutil.copy2(source_image, dest_image)
        print(f"[OK] Image {i} copied: {dest_image}")

        # Erstelle Page-Entry
        page_data = {
            "page": i,
            "file_id": f"page_{i}",
            "image_file": source_image.name,
            "text": result['filtered_text'],
            "characters": result['filtered_characters'],
            "time_seconds": result['processing_time_seconds'],
            "original_characters": result['original_characters'],
            "cleaned_characters": result['filtered_characters'],
            "filtered": result['original_characters'] - result['filtered_characters']
        }

        pages.append(page_data)
        total_time += result['processing_time_seconds']
        total_chars += result['filtered_characters']
        successful += 1

    if not pages:
        print("[ERROR] No valid OCR results found!")
        sys.exit(1)

    # Erstelle Sample-Struktur (kompatibel mit viewer.js)
    sample_data = {
        doc_id: {
            "mets_metadata": {
                "title": title,
                "signature": signature or doc_id,
                "author": author or "Various",
                "language": language,
                "owner": "OCR Result",
                "urn": f"ocr:{doc_id}"
            },
            "pages": pages,
            "total_pages": len(pages),
            "successful": successful,
            "failed": failed,
            "is_sample": True,
            "sample_indices": list(range(len(pages)))
        }
    }

    # Speichere Sample JSON (für Viewer)
    sample_json_path = samples_dir / f"{doc_id}_sample.json"
    with open(sample_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Sample JSON created: {sample_json_path}")

    # Speichere Full JSON (identisch bei diesem Use Case)
    full_json_path = samples_dir / f"{doc_id}_full.json"
    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Full JSON created: {full_json_path}")

    # Speichere Transcription
    transcription_path = samples_dir / f"{doc_id}_transcription.txt"
    with open(transcription_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Language:** {language}\n")
        f.write(f"**Pages:** {len(pages)}\n\n")
        f.write("---\n\n")

        for page in pages:
            f.write(f"## Page {page['page']}\n\n")
            f.write(f"**Image:** {page['image_file']}\n")
            f.write(f"**Characters:** {page['characters']}\n")
            f.write(f"**Time:** {page['time_seconds']:.2f}s\n\n")
            f.write(page['text'])
            f.write("\n\n---\n\n")

    print(f"[OK] Transcription created: {transcription_path}")

    # Erstelle Report
    report_path = samples_dir / f"{doc_id}_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Document ID:** `{doc_id}`\n")
        f.write(f"**Language:** {language}\n")
        f.write(f"**Total Pages:** {len(pages)}\n")
        f.write(f"**Successful:** {successful}\n")
        f.write(f"**Failed:** {failed}\n")
        f.write(f"**Total Processing Time:** {total_time:.2f}s\n")
        f.write(f"**Total Characters:** {total_chars:,}\n\n")

        f.write(f"## Page Statistics\n\n")
        f.write(f"| Page | Image | Characters | Filtered | Time | Artifacts % |\n")
        f.write(f"|------|-------|------------|----------|------|-------------|\n")

        for page in pages:
            artifacts_pct = (page['filtered'] / page['original_characters'] * 100) if page['original_characters'] > 0 else 0
            f.write(f"| {page['page']} | {page['image_file']} | {page['characters']:,} | {page['filtered']:,} | {page['time_seconds']:.2f}s | {artifacts_pct:.1f}% |\n")

        f.write(f"\n## Files\n\n")
        f.write(f"- **Sample:** `{doc_id}_sample.json` (for viewer)\n")
        f.write(f"- **Full Data:** `{doc_id}_full.json` (download)\n")
        f.write(f"- **Transcription:** `{doc_id}_transcription.txt`\n")
        f.write(f"- **Images:** `images/{doc_id}/` ({len(pages)} images)\n")

    print(f"[OK] Report created: {report_path}")

    print(f"\n[OK] Multi-image sample created successfully for {doc_id}!")
    print(f"  Total pages: {len(pages)}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"\nNext steps:")
    print(f"1. Add to samples.json")
    print(f"2. Test viewer at docs/index.html")
    print(f"3. Commit and push to GitHub Pages")

def main():
    parser = argparse.ArgumentParser(description='Create sample from multiple-image OCR results')
    parser.add_argument('doc_id', help='Unique document ID (e.g., karteikarten)')
    parser.add_argument('title', help='Document title')
    parser.add_argument('--language', required=True, help='Language code (de, fr, en, multi, etc.)')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--signature', help='Document signature')
    parser.add_argument('result_dirs', nargs='+', help='Paths to results/image_XXX_TIMESTAMP directories')

    args = parser.parse_args()

    create_multi_sample(
        args.result_dirs,
        args.doc_id,
        args.title,
        args.language,
        args.author,
        args.signature
    )

if __name__ == "__main__":
    main()
