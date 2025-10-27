# Learnings & Best Practices

## Key Insights

### 1. Hardware is Critical

**RTX 4060 (8 GB) ❌ → RTX 4080 (16 GB) ✅**

```python
# Always check VRAM first!
import torch
vram = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"VRAM: {vram:.1f} GB")

if vram < 12:
    print("⚠️ DeepSeek-OCR needs 10+ GB VRAM")
    exit(1)
```

**Lesson:** Model requirements are non-negotiable. Check hardware before setup.

---

### 2. Flash-Attention is Optional

**Problem:** Windows installation requires CUDA Toolkit + Visual Studio Build Tools

**Solution:** Simply skip it!

```python
# Works fine without flash_attention_2
model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    # _attn_implementation='flash_attention_2',  # ❌ Skip this
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
)
```

**Performance Impact:** Minimal (~5-10% slower, acceptable trade-off)

---

### 3. Windows Unicode Pain

**Problem:** Default Windows encoding (cp1252) can't handle Unicode

**Solution:** Force UTF-8 everywhere

```python
import io, sys
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

**Why:** German (ü, ö, ä, ß), French (é, è, à, ç), formulas (→, ∫, ∑)

---

### 4. PDF Libraries Matter

**Tried:** `pdf2image` + poppler
- ❌ External dependency (poppler binary)
- ❌ Complex Windows setup
- ❌ PATH configuration issues

**Winner:** `PyMuPDF` (fitz)
- ✅ Pure Python (no external deps)
- ✅ Fast conversion
- ✅ Works cross-platform
- ✅ Simple API

```python
import fitz  # PyMuPDF
pdf = fitz.open("document.pdf")
for page in pdf:
    pix = page.get_pixmap(dpi=300)
    pix.save("page.png")
```

---

### 5. Artifact Filtering is Essential

**Without Filtering:**
```
Blue
Cyan
Green
Yellow
Red
Magenta
White
Black
0 1 2 3 4 5 6 7 8 9
inches
centimetres

[Actual document text...]
```

**With Filtering:**
```
[Actual document text only]
```

**Impact:**
- o:szd.151 Page 2: **99.7%** reduction (empty page)
- o:szd.151 Page 3: **47.9%** reduction (color card)

**Implementation:** Pattern-based keyword matching (< 1s per page)

---

### 6. Sampling Strategy for GitHub Pages

**Problem:** 595 pages × 2 MB/image = **1.2 GB** (too large for GitHub Pages)

**Solution:** Select 5-10 representative samples

```python
def select_samples(pages, max=10):
    # Evenly distributed samples
    step = len(pages) / max
    indices = [int(i * step) for i in range(max)]

    # Always include first and last
    if 0 not in indices: indices[0] = 0
    if len(pages)-1 not in indices: indices[-1] = len(pages)-1

    return [pages[i] for i in indices]
```

**Benefits:**
- ✅ Lightweight deployment (< 10 MB)
- ✅ Representative coverage
- ✅ Full data still available as downloads

---

## What Worked Well

### 1. PyTorch Installation via pip
```bash
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu118
```
- ✅ 2.7 GB download
- ✅ ~60 min on slow connection
- ✅ No manual CUDA setup needed

### 2. Transformers Library
```bash
pip install transformers==4.46.3 tokenizers==0.20.3
```
- ✅ Just works™
- ✅ Automatic model download
- ✅ Caching built-in

### 3. METS XML Parsing
```python
import xml.etree.ElementTree as ET
tree = ET.parse("mets.xml")
root = tree.getroot()

# Namespace handling
ns = {'mets': 'http://www.loc.gov/METS/'}
for file in root.findall('.//mets:file', ns):
    href = file.get('{http://www.w3.org/1999/xlink}href')
```
- ✅ Standard library (no dependencies)
- ✅ XPath support
- ✅ Namespace-aware

### 4. Interactive Viewer (Vanilla JS)
```javascript
// No frameworks needed!
- No build step
- No npm dependencies
- No webpack/rollup/vite
- Just HTML + CSS + JS
```
- ✅ Instant preview
- ✅ GitHub Pages compatible
- ✅ Offline-capable
- ✅ Easy to debug

---

## What Didn't Work

### 1. HuggingFace Spaces API
**Attempted:** Use `akhaliq/DeepSeek-OCR` Space via Gradio Client

**Problem:**
```python
client = Client("akhaliq/DeepSeek-OCR")
result = client.predict(image, api_name="/ocr_process")
# → Generic errors, no stack traces
# → Unreliable (works 50% of the time)
```

**Lesson:** HF Spaces great for demos, not production APIs

### 2. Official DeepSeek API
**Expected:** OCR endpoint like `/v1/ocr`

**Reality:** Only chat/reasoning endpoints available

**Lesson:** Open-source model ≠ Hosted API

### 3. Handwriting Recognition
**Test:** Stefan Zweig handwritten letters (1914)

**Result:** Garbage output ("summum summum summum...")

**Lesson:** DeepSeek-OCR is for **printed text only**
- ✅ Printed documents
- ✅ Typed letters
- ✅ PDFs, screenshots
- ❌ Handwriting
- ❌ Historical scripts (Kurrent, Fraktur)

---

## Best Practices

### 1. Check Hardware First
```bash
# Before anything else
nvidia-smi

# Verify VRAM
python -c "import torch; print(f'{torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB')"
```

### 2. Start Small
```bash
# Test with 1 page first
python test_ocr_mets.py data/o_szd.151/ --limit 1

# Then scale up
python test_ocr_mets.py data/o_szd.151/
```

### 3. Monitor Resources
```bash
# Watch VRAM usage
watch -n 1 nvidia-smi

# Watch system memory
htop  # Linux
# or Task Manager → Performance (Windows)
```

### 4. Use Caching
```python
# Model caches automatically in ~/.cache/huggingface
# Reuse across runs (saves ~5 min per run)

# Clear cache if needed:
# rm -rf ~/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-OCR
```

### 5. Batch Processing Strategy
```python
# DON'T load all images into RAM
# DO process sequentially

for image_path in image_paths:
    result = model.infer(image_path)
    save_result(result)

    # Clear GPU cache every 10 pages
    if i % 10 == 0:
        torch.cuda.empty_cache()
```

---

## Common Pitfalls

### ❌ Forgetting to Filter Artifacts
**Impact:** Noise in results (color cards, measurements, reference marks)

**Fix:** Always run `filter_artifacts.py` or `clean_ocr_results.py`

### ❌ Ignoring Image Resolution
**Too Low (< 200 DPI):** Poor OCR quality
**Too High (> 400 DPI):** Slow processing, OOM errors
**Sweet Spot:** **300 DPI**

### ❌ Processing All Pages for GitHub Pages
**Problem:** Large repo size (> 1 GB with images)

**Fix:** Use sampling (`create_samples.py`)

### ❌ Not Handling Unicode on Windows
**Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode...`

**Fix:**
```python
import io, sys
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## Performance Tips

### 1. Reduce Image Resolution for Testing
```python
# Quick test: 150 DPI
pix = page.get_pixmap(dpi=150)

# Production: 300 DPI
pix = page.get_pixmap(dpi=300)
```

### 2. Process Pages in Parallel (Advanced)
```python
from multiprocessing import Pool

# WARNING: Each process needs ~10 GB VRAM
# Only works with multiple GPUs

with Pool(processes=2) as pool:
    results = pool.map(ocr_page, image_paths)
```

### 3. Use BF16 (Already Default)
```python
# Brain Float 16 = faster + less VRAM
model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    torch_dtype=torch.bfloat16  # ✅
)
```

---

## Future Improvements

### 1. Batch Inference
```python
# Current: 1 image/inference
result = model.infer(image)

# Future: Multiple images/inference (if model supports)
results = model.infer_batch([img1, img2, img3])
```

### 2. Post-Processing Rules
```python
# Fix systematic errors automatically
FIXES = {
    r'\bGroBen\b': 'Größen',
    r'\bMaBnahmen\b': 'Maßnahmen',
    r'\bStraBe\b': 'Straße',
}

for pattern, replacement in FIXES.items():
    text = re.sub(pattern, replacement, text)
```

### 3. Layout Detection
```python
# Detect columns, headers, footers
# Preserve reading order
# Handle complex layouts
```

### 4. Formula Extraction
```python
# Extract LaTeX formulas separately
# Better rendering in viewer
# Export to MathML
```

---

## Recommended Workflow

```bash
# 1. Check hardware
nvidia-smi

# 2. Test with 1 page
python test_ocr_mets.py data/doc/ --limit 1

# 3. Process full document
python test_ocr_mets.py data/doc/

# 4. Filter artifacts
python clean_ocr_results.py results/mets_*/doc_ocr.json

# 5. Create samples
python create_samples.py

# 6. Generate viewer
python generate_viewer_simple.py

# 7. Test locally
python -m http.server 8000

# 8. Commit & deploy
git add samples/ index.html docs/
git commit -m "Add OCR results"
git push
```

---

## Resources

### Documentation
- [[00-Index]] - Project overview
- [[01-Quick-Start]] - Setup guide
- [[02-Architecture]] - System design
- [[03-Results]] - Evaluation results

### External Links
- [DeepSeek-OCR Model](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- [PyMuPDF Docs](https://pymupdf.readthedocs.io/)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)
- [Live Demo](https://chpollin.github.io/deepseek-ocr/)

---

**Last Updated:** 2025-10-27
**Contributors:** Research Team
