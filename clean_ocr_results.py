#!/usr/bin/env python3
"""
Clean OCR Results
=================
Wendet Artifact-Filter auf existierende OCR-Ergebnisse an

Usage:
    python clean_ocr_results.py results/mets_o_szd.151_TIMESTAMP/o_szd.151_ocr.json
"""

import sys
import json
from pathlib import Path
from filter_artifacts import clean_mets_ocr_result, print_filtering_stats

def setup_utf8():
    """UTF-8 Fix für Windows"""
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    setup_utf8()

    if len(sys.argv) < 2:
        print("Usage: python clean_ocr_results.py <ocr_result.json>")
        print("Example: python clean_ocr_results.py results/mets_o_szd.151_*/o_szd.151_ocr.json")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)

    print("="*60)
    print("CLEANING OCR RESULTS")
    print("="*60)
    print(f"Input: {input_file}\n")

    # Lade OCR-Ergebnis
    with open(input_file, 'r', encoding='utf-8') as f:
        ocr_result = json.load(f)

    print(f"Document: {ocr_result['mets_metadata'].get('title', 'N/A')}")
    print(f"Pages: {ocr_result['total_pages']}\n")

    # Bereinige
    cleaned_result = clean_mets_ocr_result(ocr_result)

    # Statistik pro Seite
    print("="*60)
    print("PER-PAGE STATISTICS")
    print("="*60)

    for page in cleaned_result['pages']:
        page_num = page['page']
        orig_chars = page.get('original_characters', 0)
        clean_chars = page.get('cleaned_characters', 0)
        filtered = page.get('filtered', 0)

        if filtered > 0:
            pct = (filtered / orig_chars * 100) if orig_chars > 0 else 0
            print(f"Page {page_num}: {orig_chars} → {clean_chars} chars ({filtered} filtered, {pct:.1f}%)")
        else:
            print(f"Page {page_num}: {clean_chars} chars (no filtering)")

    # Speichere bereinigtes Ergebnis
    output_file = str(input_file).replace('.json', '_cleaned.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_result, f, indent=2, ensure_ascii=False)

    # Speichere auch als Plain Text
    text_file = str(input_file).replace('_ocr.json', '_fulltext_cleaned.txt')
    with open(text_file, 'w', encoding='utf-8') as f:
        for page in cleaned_result['pages']:
            if 'text' in page and page['text'].strip():
                # Skip leere Seiten
                if page['text'] == "[EMPTY PAGE - FILTERED]":
                    f.write(f"--- PAGE {page['page']} ---\n\n[EMPTY PAGE]\n\n")
                else:
                    f.write(f"--- PAGE {page['page']} ---\n\n")
                    f.write(page['text'])
                    f.write("\n\n")

    print(f"\n{'='*60}")
    print("CLEANING COMPLETE")
    print("="*60)
    print(f"Cleaned JSON: {output_file}")
    print(f"Cleaned Text: {text_file}")
    print("="*60)

if __name__ == "__main__":
    main()
