#!/usr/bin/env python3
"""
Create Sample from Single-Image OCR Result
===========================================
Erstellt Sample-Daten für GitHub Pages aus Single-Image OCR-Ergebnissen

Usage:
    python create_sample_from_image.py results/image_image.1_20251028_155204 o_hsa_letter_2261 --title "HSA Letter 2261" --language fr
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

def create_sample(result_dir, doc_id, title, language, author=None, signature=None):
    """
    Erstellt Sample aus Single-Image OCR Result

    Args:
        result_dir: Path zu results/image_XXX_TIMESTAMP
        doc_id: Eindeutige ID für Dokument (z.B. o_hsa_letter_2261)
        title: Dokumenttitel
        language: Sprachcode (de, fr, en, etc.)
        author: Optional - Autor
        signature: Optional - Signatur
    """
    result_path = Path(result_dir)

    # Lade OCR Result
    result_json = result_path / "result.json"
    if not result_json.exists():
        print(f"ERROR: result.json not found in {result_dir}")
        sys.exit(1)

    with open(result_json, 'r', encoding='utf-8') as f:
        result = json.load(f)

    # Sample-Verzeichnisse
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)

    images_dir = samples_dir / "images" / doc_id
    images_dir.mkdir(parents=True, exist_ok=True)

    # Kopiere Bild
    source_image = Path(result['image_path'])
    if not source_image.exists():
        print(f"ERROR: Source image not found: {source_image}")
        sys.exit(1)

    # Bild nach samples/ kopieren
    dest_image = images_dir / source_image.name
    shutil.copy2(source_image, dest_image)
    print(f"[OK] Image copied: {dest_image}")

    # Erstelle Sample-Struktur (kompatibel mit viewer.js)
    sample_data = {
        doc_id: {
            "mets_metadata": {
                "title": title,
                "signature": signature or doc_id,
                "author": author or "Unknown",
                "language": language,
                "owner": "OCR Result",
                "urn": f"ocr:{doc_id}"
            },
            "pages": [
                {
                    "page": 1,
                    "file_id": "page_1",
                    "image_file": source_image.name,
                    "text": result['filtered_text'],
                    "characters": result['filtered_characters'],
                    "time_seconds": result['processing_time_seconds'],
                    "original_characters": result['original_characters'],
                    "cleaned_characters": result['filtered_characters'],
                    "filtered": result['original_characters'] - result['filtered_characters']
                }
            ],
            "total_pages": 1,
            "successful": 1,
            "failed": 0,
            "is_sample": True,
            "sample_indices": [0]
        }
    }

    # Füge Evaluation-Metriken hinzu falls vorhanden
    if result.get('evaluation_metrics'):
        sample_data[doc_id]['evaluation_metrics'] = result['evaluation_metrics']
        sample_data[doc_id]['ground_truth_path'] = result.get('ground_truth_path')

    # Speichere Sample JSON (für Viewer)
    sample_json_path = samples_dir / f"{doc_id}_sample.json"
    with open(sample_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Sample JSON created: {sample_json_path}")

    # Speichere Full JSON (identisch bei Single-Image)
    full_json_path = samples_dir / f"{doc_id}_full.json"
    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Full JSON created: {full_json_path}")

    # Speichere Transcription
    transcription_path = samples_dir / f"{doc_id}_transcription.txt"
    with open(transcription_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Language:** {language}\n")
        f.write(f"**Pages:** 1\n\n")
        f.write("---\n\n")
        f.write(f"## Page 1\n\n")
        f.write(result['filtered_text'])
        f.write("\n")
    print(f"[OK] Transcription created: {transcription_path}")

    # Erstelle Report
    report_path = samples_dir / f"{doc_id}_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Document ID:** `{doc_id}`\n")
        f.write(f"**Language:** {language}\n")
        f.write(f"**Pages:** 1\n")
        f.write(f"**Processing Time:** {result['processing_time_seconds']:.2f}s\n\n")

        f.write(f"## Statistics\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Original Characters | {result['original_characters']:,} |\n")
        f.write(f"| Filtered Characters | {result['filtered_characters']:,} |\n")
        f.write(f"| Removed (Artifacts) | {result['original_characters'] - result['filtered_characters']:,} ({(result['original_characters'] - result['filtered_characters']) / result['original_characters'] * 100:.1f}%) |\n")
        f.write(f"| Processing Time | {result['processing_time_seconds']:.2f}s |\n")

        # Evaluation Metrics (falls vorhanden)
        if result.get('evaluation_metrics'):
            metrics = result['evaluation_metrics']
            f.write(f"\n## Evaluation (vs. Ground-Truth)\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Character Error Rate (CER) | **{metrics['cer_percent']:.2f}%** |\n")
            f.write(f"| Word Error Rate (WER) | **{metrics['wer_percent']:.2f}%** |\n")
            f.write(f"| Ground-Truth Characters | {metrics['ground_truth_chars']:,} |\n")
            f.write(f"| OCR Characters | {metrics['ocr_chars']:,} |\n")
            f.write(f"| Character Difference | {metrics['char_difference']:+,} |\n")
            f.write(f"| Ground-Truth Words | {metrics['ground_truth_words']:,} |\n")
            f.write(f"| OCR Words | {metrics['ocr_words']:,} |\n")
            f.write(f"| Word Difference | {metrics['word_difference']:+,} |\n")

        f.write(f"\n## Files\n\n")
        f.write(f"- **Sample:** `{doc_id}_sample.json` (for viewer)\n")
        f.write(f"- **Full Data:** `{doc_id}_full.json` (download)\n")
        f.write(f"- **Transcription:** `{doc_id}_transcription.txt`\n")
        f.write(f"- **Image:** `images/{doc_id}/{source_image.name}`\n")

    print(f"[OK] Report created: {report_path}")

    print(f"\n[OK] Sample created successfully for {doc_id}!")
    print(f"\nNext steps:")
    print(f"1. Add to samples.json")
    print(f"2. Test viewer at docs/index.html")
    print(f"3. Commit and push to GitHub Pages")

def main():
    parser = argparse.ArgumentParser(description='Create sample from single-image OCR result')
    parser.add_argument('result_dir', help='Path to results/image_XXX_TIMESTAMP directory')
    parser.add_argument('doc_id', help='Unique document ID (e.g., o_hsa_letter_2261)')
    parser.add_argument('--title', required=True, help='Document title')
    parser.add_argument('--language', required=True, help='Language code (de, fr, en, etc.)')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--signature', help='Document signature')

    args = parser.parse_args()

    create_sample(
        args.result_dir,
        args.doc_id,
        args.title,
        args.language,
        args.author,
        args.signature
    )

if __name__ == "__main__":
    main()
