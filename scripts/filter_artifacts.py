#!/usr/bin/env python3
"""
Artifact Filter für OCR-Ergebnisse
===================================
Entfernt automatisch Farbreferenzen und andere Scan-Artefakte

Features:
- Pattern-basierte Erkennung von Farbreferenzen
- Keyword-Filtering (Farbkarte, Grauskala, B.I.G., etc.)
- Strukturelle Filterung (isolierte Zahlen/Buchstaben)
- Line-by-line cleaning

Usage:
    from filter_artifacts import clean_ocr_text

    cleaned = clean_ocr_text(raw_ocr_output)
"""

import re
from typing import List, Set

# Bekannte Artefakt-Keywords
ARTIFACT_KEYWORDS = {
    # Farbreferenzen
    'farbkarte', 'grauskala', 'color chart', 'gray scale',
    'b.i.g.', 'b.i.g', 'big',

    # Farbnamen
    'blue', 'cyan', 'green', 'yellow', 'red', 'magenta', 'white', 'black',

    # Maßeinheiten
    'inches', 'centimetres', 'centimeters', 'cm', 'mm',

    # Häufige Referenz-Labels
    'color', '3/color', 'grayscale', 'colour'
}

# Pattern für Farbreferenz-Strukturen
ARTIFACT_PATTERNS = [
    r'^[A-Z]$',                          # Einzelne Großbuchstaben (A, B, M)
    r'^\d{1,2}$',                        # Einzelne Zahlen (1-19)
    r'^#\d+$',                           # Nummern (#13, #14)
    r'^[A-Z]\.\s?[A-Z]\.\s?[A-Z]\.$',   # B.I.G.
    r'^\d+/\w+$',                        # 3/Color
]

def is_artifact_line(line: str) -> bool:
    """
    Prüfe, ob eine Zeile ein Artefakt ist

    Args:
        line: Einzelne Textzeile

    Returns:
        True wenn Artefakt, False wenn echter Inhalt
    """
    line_stripped = line.strip()

    # Leere Zeilen behalten
    if not line_stripped:
        return False

    line_lower = line_stripped.lower()

    # 1. Keyword-Check
    for keyword in ARTIFACT_KEYWORDS:
        if keyword in line_lower:
            return True

    # 2. Pattern-Check
    for pattern in ARTIFACT_PATTERNS:
        if re.match(pattern, line_stripped):
            return True

    # 3. Strukturelle Checks
    # Sehr kurze Zeilen mit nur Zahlen/Buchstaben
    if len(line_stripped) <= 3 and line_stripped.isalnum():
        return True

    return False

def is_empty_page_artifact(text: str) -> bool:
    """
    Prüfe, ob Text nur aus Whitespace/Unicode-Artefakten besteht

    Kriterien:
    - Mehr als 90% Whitespace oder Sonderzeichen
    - Weniger als 50 tatsächliche Buchstaben
    """
    # Entferne Whitespace
    no_whitespace = re.sub(r'\s', '', text)

    # Zähle ASCII-Buchstaben
    letters = re.findall(r'[a-zA-ZäöüÄÖÜß]', no_whitespace)

    if len(letters) < 50:
        return True

    # Ratio prüfen
    ratio = len(letters) / len(text) if len(text) > 0 else 0

    if ratio < 0.05:  # Weniger als 5% echte Buchstaben
        return True

    return False

def clean_ocr_text(text: str, preserve_structure: bool = True) -> str:
    """
    Bereinige OCR-Text von Artefakten

    Args:
        text: Raw OCR output
        preserve_structure: Behalte Leerzeilen zwischen Absätzen

    Returns:
        Gereinigter Text
    """
    # Check: Ist die ganze Seite leer?
    if is_empty_page_artifact(text):
        return "[EMPTY PAGE - FILTERED]"

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Prüfe ob Artefakt
        if is_artifact_line(line):
            continue

        # Prüfe auf Code-Blöcke (```) - das sind meist Artefakte
        if line.strip().startswith('```'):
            continue

        # Behalte die Zeile
        cleaned_lines.append(line)

    # Zusammenfügen
    result = '\n'.join(cleaned_lines)

    # Optional: Mehrfache Leerzeilen reduzieren
    if not preserve_structure:
        result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()

def clean_mets_ocr_result(ocr_result: dict) -> dict:
    """
    Bereinige ein komplettes METS-OCR Ergebnis

    Args:
        ocr_result: Output von test_ocr_mets.py

    Returns:
        Gereinigtes Result-Dict
    """
    cleaned_result = ocr_result.copy()

    for page in cleaned_result.get('pages', []):
        if 'text' in page:
            original_text = page['text']
            cleaned_text = clean_ocr_text(original_text)

            page['text'] = cleaned_text
            page['original_characters'] = page.get('characters', 0)
            page['cleaned_characters'] = len(cleaned_text)
            page['filtered'] = page['original_characters'] - page['cleaned_characters']

    return cleaned_result

def print_filtering_stats(original: str, cleaned: str):
    """Zeige Filterungs-Statistik"""
    orig_lines = original.split('\n')
    clean_lines = cleaned.split('\n')

    print("="*60)
    print("FILTERING STATISTICS")
    print("="*60)
    print(f"Original lines:  {len(orig_lines)}")
    print(f"Cleaned lines:   {len(clean_lines)}")
    print(f"Removed lines:   {len(orig_lines) - len(clean_lines)}")
    print(f"Original chars:  {len(original)}")
    print(f"Cleaned chars:   {len(cleaned)}")
    print(f"Removed chars:   {len(original) - len(cleaned)}")
    print("="*60)

# Beispiel-Usage
if __name__ == "__main__":
    # Test-Text mit Artefakten
    test_text = """Inches

Centimetres

Farbkarte #13

B.I.G.

Blue

Cyan

Green

Ihr freundliches Schreiben erreicht mich leider in einer Zeit,

da mir aus personlichen Gründen eine wirklich eingehende

Beantwortung nicht möglich wird.

Grauskala #13

A

2

3

M

8
"""

    print("ORIGINAL:")
    print(test_text)
    print()

    cleaned = clean_ocr_text(test_text)

    print("CLEANED:")
    print(cleaned)
    print()

    print_filtering_stats(test_text, cleaned)
