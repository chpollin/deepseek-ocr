#!/usr/bin/env python3
"""
DeepSeek-OCR Single Image Processing & Evaluation
==================================================
Führt OCR auf einzelnen Bildern durch und vergleicht mit Ground-Truth

Usage:
    # OCR ohne Ground-Truth
    python test_ocr_image.py data/anno/annoshow.jpg

    # OCR mit Ground-Truth Evaluation
    python test_ocr_image.py data/o_hsa_letter_2261/image.1.jpg --ground-truth data/o_hsa_letter_2261/ground-trurth-transcription.txt
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
import argparse

# Evaluation libraries
try:
    import Levenshtein
    from jiwer import wer
    EVAL_AVAILABLE = True
except ImportError:
    EVAL_AVAILABLE = False
    print("Warning: Levenshtein/jiwer not installed - evaluation disabled")

# Import artifact filter
sys.path.append(str(Path(__file__).parent))
from filter_artifacts import clean_ocr_text

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

def perform_ocr(image_path, tokenizer, model):
    """
    Führt OCR auf einem Bild durch

    Args:
        image_path: Pfad zum Bild
        tokenizer: DeepSeek Tokenizer
        model: DeepSeek Model

    Returns:
        tuple: (ocr_text, time_seconds)
    """
    print(f"Processing: {Path(image_path).name}")

    # Lade Bild
    image = Image.open(image_path).convert('RGB')
    print(f"  Size: {image.size[0]}x{image.size[1]}px")

    # OCR
    start_time = time.time()

    # Temporäres Output-Verzeichnis
    temp_dir = Path("results") / "temp" / Path(image_path).stem
    temp_dir.mkdir(parents=True, exist_ok=True)

    prompt = "<image>\nExtract all text from this document."

    model.infer(
        tokenizer,
        prompt=prompt,
        image_file=str(image_path),
        output_path=str(temp_dir),
        base_size=640,
        image_size=640,
        crop_mode=True,
        save_results=True,
        test_compress=True
    )

    elapsed = time.time() - start_time

    # Lese Ergebnis
    result_file = temp_dir / "result.mmd"
    ocr_result = ""

    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            ocr_result = f.read()

    print(f"  Time: {elapsed:.2f}s")
    print(f"  Characters: {len(ocr_result)}")

    return ocr_result, elapsed

def normalize_text(text):
    """
    Normalisiert Text für Evaluation
    - Entfernt führende/trailing Whitespace
    - Normalisiert Zeilenumbrüche
    - Entfernt markdown code blocks (```)
    """
    # Entferne markdown code blocks
    text = text.replace('```', '')

    # Entferne "page X:" Zeilen
    lines = text.split('\n')
    filtered_lines = [line for line in lines if not line.strip().startswith('page ')]

    # Normalisiere
    normalized = '\n'.join(filtered_lines)
    normalized = normalized.strip()

    return normalized

def calculate_cer(reference, hypothesis):
    """
    Berechnet Character Error Rate (CER)

    CER = (Substitutions + Deletions + Insertions) / Total Characters
    """
    if not EVAL_AVAILABLE:
        return None

    distance = Levenshtein.distance(reference, hypothesis)
    cer = distance / len(reference) if len(reference) > 0 else 0

    return cer * 100  # Als Prozent

def calculate_wer(reference, hypothesis):
    """
    Berechnet Word Error Rate (WER)
    """
    if not EVAL_AVAILABLE:
        return None

    try:
        error_rate = wer(reference, hypothesis)
        return error_rate * 100  # Als Prozent
    except:
        return None

def evaluate_ocr(ocr_text, ground_truth_text):
    """
    Evaluiert OCR-Ergebnis gegen Ground-Truth

    Returns:
        dict mit Metriken
    """
    if not EVAL_AVAILABLE:
        return {"error": "Evaluation libraries not installed"}

    print("\n" + "="*60)
    print("EVALUATION")
    print("="*60)

    # Normalisiere beide Texte
    ocr_normalized = normalize_text(ocr_text)
    gt_normalized = normalize_text(ground_truth_text)

    # Berechne Metriken
    cer = calculate_cer(gt_normalized, ocr_normalized)
    word_error_rate = calculate_wer(gt_normalized, ocr_normalized)

    # Zeichenstatistiken
    gt_chars = len(gt_normalized)
    ocr_chars = len(ocr_normalized)

    # Wortstatistiken
    gt_words = len(gt_normalized.split())
    ocr_words = len(ocr_normalized.split())

    metrics = {
        "cer_percent": round(cer, 2) if cer is not None else None,
        "wer_percent": round(word_error_rate, 2) if word_error_rate is not None else None,
        "ground_truth_chars": gt_chars,
        "ocr_chars": ocr_chars,
        "char_difference": ocr_chars - gt_chars,
        "ground_truth_words": gt_words,
        "ocr_words": ocr_words,
        "word_difference": ocr_words - gt_words
    }

    # Output
    print(f"Character Error Rate (CER): {metrics['cer_percent']:.2f}%")
    print(f"Word Error Rate (WER): {metrics['wer_percent']:.2f}%")
    print(f"\nGround-Truth: {gt_chars} chars, {gt_words} words")
    print(f"OCR Result:   {ocr_chars} chars, {ocr_words} words")
    print(f"Difference:   {metrics['char_difference']:+d} chars, {metrics['word_difference']:+d} words")

    return metrics

def main():
    setup_utf8()

    # Argument Parsing
    parser = argparse.ArgumentParser(description='DeepSeek-OCR Single Image Processing')
    parser.add_argument('image_path', help='Path to image file')
    parser.add_argument('--ground-truth', help='Path to ground-truth transcription file')
    parser.add_argument('--no-filter', action='store_true', help='Disable artifact filtering')

    args = parser.parse_args()

    # Validiere Input
    if not os.path.exists(args.image_path):
        print(f"ERROR: Image not found: {args.image_path}")
        sys.exit(1)

    ground_truth = None
    if args.ground_truth:
        if not os.path.exists(args.ground_truth):
            print(f"ERROR: Ground-truth file not found: {args.ground_truth}")
            sys.exit(1)

        with open(args.ground_truth, 'r', encoding='utf-8') as f:
            ground_truth = f.read()

        print(f"Ground-Truth loaded: {len(ground_truth)} characters\n")

    # Lade Model
    tokenizer, model = load_model()

    # OCR
    print("="*60)
    print("OCR PROCESSING")
    print("="*60)

    ocr_text, elapsed = perform_ocr(args.image_path, tokenizer, model)

    # Artifact Filtering
    filtered_text = ocr_text
    if not args.no_filter:
        print("\n" + "="*60)
        print("ARTIFACT FILTERING")
        print("="*60)

        original_chars = len(ocr_text)
        filtered_text = clean_ocr_text(ocr_text, preserve_structure=True)
        filtered_chars = len(filtered_text)
        removed = original_chars - filtered_chars
        filter_percentage = (removed / original_chars * 100) if original_chars > 0 else 0

        print(f"Original: {original_chars} chars")
        print(f"Filtered: {filtered_chars} chars")
        print(f"Removed:  {removed} chars ({filter_percentage:.1f}%)")

    # Evaluation (falls Ground-Truth vorhanden)
    metrics = None
    if ground_truth:
        metrics = evaluate_ocr(filtered_text, ground_truth)

    # Speichere Ergebnisse
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = Path(args.image_path).stem

    output_dir = Path("results") / f"image_{image_name}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON Output
    result = {
        "image_path": str(args.image_path),
        "timestamp": timestamp,
        "ocr_text": ocr_text,
        "filtered_text": filtered_text,
        "processing_time_seconds": round(elapsed, 2),
        "original_characters": len(ocr_text),
        "filtered_characters": len(filtered_text),
        "ground_truth_path": args.ground_truth if args.ground_truth else None,
        "evaluation_metrics": metrics
    }

    json_path = output_dir / "result.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Text Output
    txt_path = output_dir / "ocr_text.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(filtered_text)

    # Evaluation Report (falls vorhanden)
    if metrics:
        report_path = output_dir / "evaluation_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR Evaluation Report\n\n")
            f.write(f"**Image:** `{args.image_path}`\n")
            f.write(f"**Ground-Truth:** `{args.ground_truth}`\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Metrics\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Character Error Rate (CER) | {metrics['cer_percent']:.2f}% |\n")
            f.write(f"| Word Error Rate (WER) | {metrics['wer_percent']:.2f}% |\n")
            f.write(f"| Ground-Truth Characters | {metrics['ground_truth_chars']} |\n")
            f.write(f"| OCR Characters | {metrics['ocr_chars']} |\n")
            f.write(f"| Character Difference | {metrics['char_difference']:+d} |\n")
            f.write(f"| Ground-Truth Words | {metrics['ground_truth_words']} |\n")
            f.write(f"| OCR Words | {metrics['ocr_words']} |\n")
            f.write(f"| Word Difference | {metrics['word_difference']:+d} |\n")
            f.write(f"| Processing Time | {elapsed:.2f}s |\n\n")
            f.write(f"## OCR Output\n\n")
            f.write(f"```\n{filtered_text}\n```\n\n")
            f.write(f"## Ground-Truth\n\n")
            f.write(f"```\n{ground_truth}\n```\n")

    print("\n" + "="*60)
    print("RESULTS SAVED")
    print("="*60)
    print(f"Directory: {output_dir}")
    print(f"  - result.json")
    print(f"  - ocr_text.txt")
    if metrics:
        print(f"  - evaluation_report.md")

    print("\n" + "="*60)
    print("DONE")
    print("="*60)

if __name__ == "__main__":
    main()
