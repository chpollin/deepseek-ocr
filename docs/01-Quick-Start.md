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
- `python-Levenshtein>=0.25.0` (metrics)

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

### Process METS Documents

```bash
python test_ocr_mets.py data/o_szd.151/
```

**Output:** `results/mets_o_szd.151_TIMESTAMP/`
- `*_ocr.json` - Raw OCR results
- `*_ocr_cleaned.json` - Filtered results (artifacts removed)

### Process PDF

```bash
python test_ocr_pdf.py data/document.pdf
```

**Output:** `results/pdf_document_TIMESTAMP/`
- `images/` - Converted pages (PNG, 300 DPI)
- `results.json` - OCR results
- `results_cleaned.json` - Filtered results

### Create Samples for GitHub Pages

```bash
python create_samples.py
```

**Output:** `samples/`
- Selects 5-10 representative pages
- Copies sample images
- Creates full transcriptions
- Generates statistical reports

### Generate Interactive Viewer

```bash
python generate_viewer_simple.py
```

**Output:** `index.html`
- Auto-loads from `samples/` if available
- Fallback to full `results/` data
- Side-by-side image/text comparison
- Zoom, navigation, export functions

---

## Quick Examples

### Example 1: Process Single METS Document

```bash
# Download METS data (if not already in data/)
# Process it
python test_ocr_mets.py data/o_szd.151/

# Create samples
python create_samples.py

# Generate viewer
python generate_viewer_simple.py

# Open in browser
# http://localhost:8000/
python -m http.server 8000
```

### Example 2: Process PDF

```bash
# Process PDF (converts to images + OCR)
python test_ocr_pdf.py data/document.pdf

# Filter artifacts
python clean_ocr_results.py results/pdf_document_*/results.json

# Create samples
python create_samples.py

# View results
python generate_viewer_simple.py
python -m http.server 8000
```

---

## Performance Expectations

### RTX 4080 (16 GB VRAM)

| Operation | Speed | Notes |
|-----------|-------|-------|
| **Model Loading** | ~30s | First time only, then cached |
| **OCR per Page** | ~15-20s | Depends on content density |
| **Throughput** | ~120-360 pages/hour | Batch processing |
| **PDF Conversion** | ~1s/page | PyMuPDF, 300 DPI |
| **Artifact Filtering** | <1s/page | Pattern-based |

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
# Reduce batch size or image resolution
# Edit test_ocr_*.py:
# - Lower DPI (300 → 200)
# - Process fewer pages at once
```

### Windows Unicode Errors
```python
# Already fixed in all scripts with:
import io, sys
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## Next Steps

- [[02-Architecture]] - Understand the pipeline
- [[03-Results]] - See example results
- [[04-Learnings]] - Best practices & tips

---

**See also:** [[00-Index]] | [GitHub Repo](https://github.com/chpollin/deepseek-ocr)
