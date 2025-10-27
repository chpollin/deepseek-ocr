# Scripts Documentation

This folder contains all Python scripts for the DeepSeek-OCR evaluation framework.

## Core OCR Processing

### `test_ocr_mets.py`
**Purpose**: Process METS documents with OCR
**Usage**: `python scripts/test_ocr_mets.py data/o_szd.151/`

**What it does**:
- Reads METS XML metadata (title, author, language, URN)
- Extracts logical structure from METS
- Converts each page to image using PyMuPDF
- Runs DeepSeek-OCR inference on each image
- Applies artifact filtering
- Outputs results to `results/{doc_id}_results.json`

**Why we have it**: METS is the standard format for digital archives. This script handles the complete workflow from METS input to OCR output with metadata preservation.

**Key features**:
- METS XML parsing
- Automatic image extraction from document files
- Metadata preservation (URN, signature, author, etc.)
- Integration with artifact filter
- JSON output with full provenance

---

### `test_ocr_pdf.py`
**Purpose**: Process standard PDF documents with OCR
**Usage**: `python scripts/test_ocr_pdf.py data/DTS_Flechte.pdf`

**What it does**:
- Converts PDF pages to images (300 DPI)
- Runs DeepSeek-OCR on each page
- Applies artifact filtering
- Saves images to `data/{filename}/images/`
- Outputs results to `results/{filename}_results.json`

**Why we have it**: For processing standard PDFs that don't have METS metadata. Handles large documents (595+ pages) with progress tracking.

**Key features**:
- PyMuPDF-based PDF→image conversion
- Automatic directory structure creation
- Progress reporting (page X/Y)
- Image caching for re-processing
- Memory-efficient processing

---

## Post-Processing & Filtering

### `filter_artifacts.py`
**Purpose**: Remove OCR artifacts and noise from text
**Usage**: `from filter_artifacts import filter_ocr_text`

**What it does**:
- Detects and removes color reference cards (e.g., "ROTE NEUTRAL 8 BRAUN FARBKARTE")
- Filters measurement scales and reference marks
- Removes repetitive artifact patterns
- Preserves actual document text

**Why we have it**: Historical documents often contain color reference cards, measurement scales, and other scanning artifacts that pollute OCR output. This filter dramatically improves text quality (47-99% artifact reduction).

**Patterns detected**:
```python
- Color cards: "ROT", "GELB", "BLAU", "GRÜN", "NEUTRAL", "FARBKARTE"
- Measurements: "mm", "cm", numbers with decimal points
- Reference marks: "BRAUN FARBKARTE"
- Repetitive short lines (<30 chars with >3 repetitions)
```

**Statistics tracked**:
- Original character count
- Cleaned character count
- Number of filtered characters

---

### `clean_ocr_results.py`
**Purpose**: Apply artifact filter to existing OCR results
**Usage**: `python scripts/clean_ocr_results.py results/o_szd_151_results.json`

**What it does**:
- Loads existing OCR results
- Applies artifact filtering to all pages
- Adds `filtered_text` field to each page
- Preserves original text in `text` field
- Overwrites result file with cleaned version

**Why we have it**: Allows re-filtering of results without re-running OCR (which takes 15-20 seconds per page). Useful for testing and improving filter patterns.

**Output example**:
```json
{
  "page": 1,
  "text": "[original OCR output]",
  "filtered_text": "[cleaned text]",
  "original_characters": 8019,
  "cleaned_characters": 23,
  "filtered": 7996
}
```

---

## Viewer Generation

### `generate_viewer_simple.py`
**Purpose**: Generate interactive HTML viewer for OCR results
**Usage**: `python scripts/generate_viewer_simple.py`

**What it does**:
- Loads OCR results from `samples/samples.json` (GitHub Pages mode) or `results/` (full mode)
- Generates `docs/index.html` with embedded document data
- Creates clean, light-themed scientific UI
- Supports side-by-side image/text comparison

**Why we have it**: Provides visual inspection of OCR results. Essential for quality assessment and comparing images with transcriptions.

**Features generated**:
- Document selector with metadata
- Combined info bar (metadata + navigation)
- Horizontal thumbnail strip
- Image viewer with zoom/pan
- OCR text panel with copy/download
- Keyboard shortcuts (←→ for navigation, ±0 for zoom)

**Modes**:
1. **GitHub Pages mode**: Loads from `samples/samples.json` (5-10 sample pages)
2. **Full mode**: Loads all results from `results/` directory

---

## Sampling & Deployment

### `create_samples.py`
**Purpose**: Create GitHub Pages-compatible samples from full results
**Usage**: `python scripts/create_samples.py --max-samples 10`

**What it does**:
- Selects N evenly distributed sample pages from each document
- Copies sample images to `samples/images/{doc_id}/`
- Creates `samples/samples.json` (viewer data)
- Generates `{doc}_full.json` (complete data download)
- Creates `{doc}_transcription.txt` (full text export)
- Generates `{doc}_report.md` (statistics and metrics)

**Why we have it**: GitHub Pages has file size limits. Can't host 595 pages × 2 MB = 1.2 GB. Solution: show 5-10 representative samples, provide full data as downloads.

**Sampling strategy**:
- Evenly distributed across document
- Always includes first and last page
- Preserves original page numbers
- Example: 595 pages → 10 samples (pages 1, 60, 119, 178, ..., 595)

**Output structure**:
```
samples/
├── samples.json                    # Master index
├── o_szd_151_sample.json          # Viewer data
├── o_szd_151_full.json            # Complete download
├── o_szd_151_transcription.txt    # Full text
├── o_szd_151_report.md            # Statistics
└── images/
    └── o_szd_151/
        ├── IMG_1.jpg
        ├── IMG_60.jpg
        └── ...
```

**Reports include**:
- Document metadata (title, author, language)
- Processing statistics (time, characters, CER)
- Artifact filtering metrics
- Page-by-page breakdown
- Sample indices and rationale

---

## Workflow

### 1. Process METS Document
```bash
python scripts/test_ocr_mets.py data/o_szd.151/
```
Output: `results/o_szd_151_results.json`

### 2. Process PDF Document
```bash
python scripts/test_ocr_pdf.py data/DTS_Flechte.pdf
```
Output: `results/DTS_Flechte_results.json`

### 3. (Optional) Re-filter Results
```bash
python scripts/clean_ocr_results.py results/o_szd_151_results.json
```

### 4. Create Samples for GitHub Pages
```bash
python scripts/create_samples.py --max-samples 10
```
Output: `samples/` directory

### 5. Generate Viewer
```bash
python scripts/generate_viewer_simple.py
```
Output: `docs/index.html` (with embedded data and external CSS/JS)

### 6. Deploy to GitHub Pages
```bash
git add docs/ samples/
git commit -m "Update viewer and samples"
git push
```
Visit: `https://yourusername.github.io/deepseek-ocr/`

---

## Dependencies

All scripts require:
- Python 3.8+
- PyTorch
- Transformers
- PyMuPDF (fitz)
- Pillow
- lxml (for METS parsing)

Install: `pip install -r requirements.txt`

---

## Performance

| Script | Speed | Notes |
|--------|-------|-------|
| test_ocr_mets.py | ~15-20s/page | GPU-bound |
| test_ocr_pdf.py | ~15-20s/page | GPU-bound |
| filter_artifacts.py | <1ms/page | Regex-based |
| clean_ocr_results.py | <1s total | I/O-bound |
| create_samples.py | <5s | I/O-bound |
| generate_viewer_simple.py | <1s | I/O-bound |

**Bottleneck**: OCR inference (15-20s/page)
**Throughput**: 120-360 pages/hour
**VRAM usage**: ~10 GB (RTX 4080)

---

## File Locations

```
deepseek-ocr/
├── scripts/              # ← All Python scripts here
│   ├── test_ocr_mets.py
│   ├── test_ocr_pdf.py
│   ├── filter_artifacts.py
│   ├── clean_ocr_results.py
│   ├── create_samples.py
│   └── generate_viewer_simple.py
├── data/                 # Input documents (METS, PDFs)
├── results/              # Full OCR results (JSON)
├── samples/              # GitHub Pages samples
├── docs/                 # GitHub Pages website
│   ├── index.html
│   ├── style.css
│   ├── viewer.js
│   └── samples/         # Symlink or copy
└── knowledge/           # Obsidian vault documentation
```
