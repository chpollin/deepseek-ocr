# Quick Start Guide

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/chpollin/deepseek-ocr.git
cd deepseek-ocr
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
./venv/Scripts/activate   # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages:**
- `torch==2.6.0` (with CUDA 11.8/13.0)
- `transformers==4.46.3`
- `PyMuPDF>=1.26.0` (PDF support)
- `python-Levenshtein>=0.25.0` (CER/WER metrics)
- `jiwer>=3.1.0` (Word Error Rate)

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **GPU** | RTX 3060 (12GB) | RTX 4080 (16GB) |
| **VRAM** | 10 GB | 16 GB |
| **RAM** | 16 GB | 32 GB |
| **Storage** | 20 GB | 50 GB |
| **CUDA** | 11.8+ | 13.0 |

**Check your GPU:**
```bash
nvidia-smi
```

---

## Usage

### 1. Process METS Documents

**Best for:** Digital archives with XML metadata

```bash
python scripts/test_ocr_mets.py data/o_szd.151/
```

**Input:**
- METS XML file (`mets.xml`)
- Image files referenced in XML

**Output:** `results/mets_o_szd.151_TIMESTAMP/`
- `*_ocr.json` - Raw OCR results
- `*_ocr_cleaned.json` - Filtered results (artifacts removed)

**Example:**
```bash
# Process German letter archive
python scripts/test_ocr_mets.py data/o_szd.151/

# Process French speech archive
python scripts/test_ocr_mets.py data/o_szd.196/
```

---

### 2. Process Single Images (NEW)

**Best for:** Individual documents, quality testing, ground-truth evaluation

```bash
python scripts/test_ocr_image.py <image_path> [options]
```

**Options:**
- `--ground-truth <file>` - Compare with reference transcription (CER/WER)
- `--base-size <int>` - Vision encoder resolution (default: 640)
- `--image-size <int>` - Local crop resolution (default: 640)
- `--no-crop` - Disable multi-tile processing
- `--prompt <text>` - Custom OCR prompt

**Output:** `results/image_<name>_TIMESTAMP/`
- `result.json` - OCR result + metadata
- `ocr_text.txt` - Extracted text
- `evaluation_metrics` (if ground-truth provided)

**Examples:**

**Basic OCR:**
```bash
python scripts/test_ocr_image.py data/o_hsa_letter_2261/image.1.jpg
```

**With Ground-Truth Evaluation:**
```bash
python scripts/test_ocr_image.py \
  data/o_hsa_letter_2261/image.1.jpg \
  --ground-truth data/o_hsa_letter_2261/ground-truth-transcription.txt
```

**Output includes:**
- Character Error Rate (CER): 21.87%
- Word Error Rate (WER): 30.75%
- Character/Word differences

**With Parameter Tuning:**
```bash
# Higher resolution for better quality
python scripts/test_ocr_image.py data/image.jpg --base-size 1024 --image-size 640
```

---

### 3. Process PDFs

**Best for:** Small PDFs (<20 pages), scientific documents

```bash
python scripts/test_ocr_pdf.py data/document.pdf
```

**Input:** PDF file

**Output:** `results/pdf_document_TIMESTAMP/`
- `images/` - Converted pages (PNG, 300 DPI)
- `results.json` - OCR results per page
- `results_cleaned.json` - Filtered results

**Example:**
```bash
# Process botanical text
python scripts/test_ocr_pdf.py data/DTS_Flechte_20pages.pdf
```

**Note:** Large PDFs may cause memory issues. Consider extracting pages first.

---

### 4. Create Sample from Single Image (NEW)

**Best for:** Adding single documents to viewer

```bash
python scripts/create_sample_from_image.py \
  <result_dir> \
  <doc_id> \
  --title "Document Title" \
  --language <lang>
```

**Example:**
```bash
python scripts/create_sample_from_image.py \
  results/image_image.1_20251028_155204 \
  o_hsa_letter_2261 \
  --title "HSA Letter 2261 - Nobel Prize Candidature" \
  --language fr
```

**Output:** `samples/`
- `<doc_id>_sample.json` - Viewer data
- `<doc_id>_full.json` - Complete data
- `<doc_id>_transcription.txt` - Full text
- `<doc_id>_report.md` - Statistics
- `images/<doc_id>/` - Image copy

---

### 5. Create Multi-Image Sample (NEW)

**Best for:** Document collections (karteikarten, photo albums)

```bash
python scripts/create_multi_image_sample.py \
  <doc_id> \
  "<title>" \
  --language <lang> \
  <result_dir1> <result_dir2> <result_dir3> ...
```

**Example:**
```bash
python scripts/create_multi_image_sample.py \
  karteikarten \
  "Historical Archive Cards Collection" \
  --language multi \
  results/image_signal-2025-10-29-073743_20251029_074156 \
  results/image_signal-2025-10-29-073743_002_20251029_074221 \
  results/image_signal-2025-10-29-073743_003_20251029_074256 \
  results/image_signal-2025-10-29-073743_004_20251029_074314 \
  results/image_signal-2025-10-29-073743_005_20251029_074343 \
  results/image_signal-2025-10-29-073743_006_20251029_074412
```

**Output:** Combined sample with all 6 cards
- Total characters: 4,349
- Total time: 55.5s
- Per-card statistics

---

### 6. Create METS Samples

**Best for:** METS archives for viewer

```bash
python scripts/create_samples.py
```

**Output:** `samples/`
- Selects 5-10 representative pages per document
- Copies sample images to `samples/images/`
- Creates full transcriptions
- Generates statistical reports

---

### 7. Generate Interactive Viewer

```bash
python scripts/generate_viewer_simple.py
```

**Input:** `samples/samples.json` (master list)

**Output:** `docs/index.html`
- Auto-loads all samples from `samples/`
- Side-by-side image/text comparison
- Document selector
- Statistics display
- Responsive design

**Test locally:**
```bash
python -m http.server 8000 --directory docs
# Open: http://localhost:8000/
```

---

## Complete Workflows

### Workflow 1: METS Archive → Viewer

```bash
# 1. Process METS
python scripts/test_ocr_mets.py data/o_szd.151/

# 2. Create samples
python scripts/create_samples.py

# 3. Add to samples.json manually or use existing

# 4. Generate viewer
python scripts/generate_viewer_simple.py

# 5. Test locally
python -m http.server 8000 --directory docs
```

---

### Workflow 2: Single Image + Ground-Truth → Viewer

```bash
# 1. Run OCR with evaluation
python scripts/test_ocr_image.py \
  data/o_hsa_letter_2261/image.1.jpg \
  --ground-truth data/o_hsa_letter_2261/ground-truth-transcription.txt

# 2. Create sample
python scripts/create_sample_from_image.py \
  results/image_image.1_20251028_155204 \
  o_hsa_letter_2261 \
  --title "HSA Letter 2261" \
  --language fr

# 3. Add to samples.json (manual)

# 4. Copy images to docs/
mkdir -p docs/samples/images/o_hsa_letter_2261
cp samples/images/o_hsa_letter_2261/*.jpg docs/samples/images/o_hsa_letter_2261/

# 5. Generate viewer
python scripts/generate_viewer_simple.py

# 6. Commit & push to GitHub Pages
git add docs/ samples/
git commit -m "Add HSA sample"
git push
```

---

### Workflow 3: Multi-Image Collection → Viewer

```bash
# 1. Process all images
for img in data/karteikarten/*.jpeg; do
  python scripts/test_ocr_image.py "$img"
done

# 2. Create combined sample
python scripts/create_multi_image_sample.py \
  karteikarten \
  "Historical Archive Cards" \
  --language multi \
  results/image_signal-*

# 3. Add to samples.json (manual)

# 4. Copy images
mkdir -p docs/samples/images/o_karteikarten
cp samples/images/karteikarten/*.jpeg docs/samples/images/o_karteikarten/

# 5. Generate viewer
python scripts/generate_viewer_simple.py

# 6. Deploy
git add docs/ samples/
git commit -m "Add karteikarten collection"
git push
```

---

### Workflow 4: PDF → Partial Sample (on failure)

```bash
# 1. Process PDF (may partially fail)
python scripts/test_ocr_pdf.py data/DTS_Flechte_20pages.pdf

# 2. Check which pages succeeded
ls results/pdf_DTS_Flechte_*/

# 3. Create sample from successful pages only
python scripts/create_dts_sample.py \
  results/pdf_DTS_Flechte_20251028_120000 \
  DTS_Flechte_20pages \
  --title "Die Flechten Tirols (Sample: 2 pages)" \
  --language de

# 4. Generate viewer
python scripts/generate_viewer_simple.py
```

---

## Performance Expectations

### RTX 4080 (16 GB VRAM)

| Content Type | Speed | Example |
|--------------|-------|---------|
| **Simple Forms** | 6-10s/page | English registration cards |
| **Typed Letters** | 15-20s/page | German/French correspondence |
| **Scientific Text** | 20-30s/page | Botanical descriptions |
| **Complex Newspapers** | 280s+/page | Fraktur multi-column (often fails) |
| **Model Loading** | ~30s | First time only, then cached |
| **PDF Conversion** | ~1s/page | PyMuPDF, 300 DPI |
| **Artifact Filtering** | <1s/page | Pattern-based |

**Throughput:**
- Simple documents: 360-600 pages/hour
- Standard documents: 120-200 pages/hour
- Complex documents: 10-60 pages/hour

---

## Troubleshooting

### Model Download Issues
```python
# Manually download model
from transformers import AutoModel
model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    trust_remote_code=True,
    cache_dir="./cache"
)
```

### CUDA Out of Memory
```bash
# Option 1: Reduce resolution
python scripts/test_ocr_image.py image.jpg --base-size 640 --no-crop

# Option 2: Process fewer images at once
# Process one at a time instead of batch
```

### Windows Unicode Errors
```python
# Already fixed in all scripts with:
import io, sys
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### Repetition Bug (Complex Layouts)
```python
# No fix available - avoid:
# - Historical newspapers (Fraktur)
# - Complex multi-column layouts
# - Documents with heavy stamps/overlays

# Use Tesseract for Fraktur instead
```

### PDF Memory Issues
```bash
# Extract pages first
pdftk input.pdf cat 1-10 output part1.pdf
python scripts/test_ocr_pdf.py part1.pdf
```

---

## Configuration Options

### OCR Parameters (test_ocr_image.py)

| Parameter | Default | Recommended | Description |
|-----------|---------|-------------|-------------|
| `base_size` | 640 | 640-1024 | Vision encoder resolution |
| `image_size` | 640 | 640 | Local crop resolution |
| `crop_mode` | True | True | Multi-tile processing |

**Standard Settings (640/640):**
- Sufficient for most documents
- Fast processing (15-20s)
- Good quality (97-98% accuracy)

**High Quality (1024/640):**
- Minimal improvement (~1-2% CER reduction)
- Slower processing (25-30s)
- Not worth it for clean documents

**See:** [[05-OCR-Optimization]] for detailed experiments

---

## Next Steps

- [[02-Architecture]] - Understand the pipeline
- [[03-Results]] - See all 6 documented samples
- [[04-Learnings]] - Best practices & tips
- [[05-OCR-Optimization]] - Parameter tuning experiments

---

**See also:** [[00-Index]] | [GitHub Repo](https://github.com/chpollin/deepseek-ocr) | [Live Viewer](https://chpollin.github.io/deepseek-ocr/)
