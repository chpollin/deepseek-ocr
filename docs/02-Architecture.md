# System Architecture

## Overview

```
┌─────────────┐
│   Input     │
│ METS / PDF  │
└──────┬──────┘
       │
       v
┌─────────────┐
│  Metadata   │
│  Extraction │
└──────┬──────┘
       │
       v
┌─────────────┐
│ OCR Engine  │
│ DeepSeek-3B │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Filter    │
│  Artifacts  │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Output    │
│ JSON/TXT/MD │
└─────────────┘
```

---

## Components

### 1. Input Processing

#### METS Handler (`test_ocr_mets.py`)
```python
def parse_mets(mets_file):
    """
    Extract metadata from METS XML:
    - Title, author, language
    - URN, signature
    - Page ordering
    - Logical structure
    """
    return {
        'metadata': {...},
        'pages': [...]
    }
```

**Features:**
- XML parsing with `xml.etree`
- URN → Object ID mapping
- Logical to physical structure mapping
- Language detection

#### PDF Handler (`test_ocr_pdf.py`)
```python
def pdf_to_images(pdf_path, dpi=300):
    """
    Convert PDF pages to images:
    - Uses PyMuPDF (fitz)
    - Configurable DPI
    - PNG output
    """
    return image_paths
```

**Features:**
- PyMuPDF for conversion
- No external dependencies (poppler not needed)
- Batch processing
- Progress tracking

---

### 2. OCR Engine

#### Model: DeepSeek-OCR
```python
from transformers import AutoModel

model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
).cuda()

# Inference
result = model.infer(image_path)
```

**Specifications:**
- **Parameters:** 3 Billion
- **Size:** 6.7 GB (BF16)
- **Precision:** Brain Float 16
- **VRAM:** ~10 GB during inference
- **Speed:** ~15-20s per page (RTX 4080)

**Features:**
- Multi-language support (DE, EN, FR, ...)
- Layout preservation
- Formula recognition
- Table structure

---

### 3. Artifact Filter

#### Pattern-Based Filtering (`filter_artifacts.py`)
```python
ARTIFACT_KEYWORDS = {
    'farbkarte', 'grauskala', 'b.i.g.',
    'blue', 'cyan', 'green', 'yellow', 'red',
    'magenta', 'white', 'black',
    'inches', 'centimetres'
}

ARTIFACT_PATTERNS = [
    r'^[A-Z],\s*$',           # Single capitals
    r'^\d{1,2},\s*$',         # Single numbers
    r'^#\d+,\s*$',            # Reference numbers
    r'^\d+\s*inches?',        # Measurements
]
```

**Logic:**
```python
def is_artifact(text):
    # 1. Check keywords
    if any(kw in text.lower() for kw in KEYWORDS):
        return True

    # 2. Check patterns
    if any(re.match(p, text) for p in PATTERNS):
        return True

    return False
```

**Performance:**
- o:szd.151 Page 3: **47.9%** filtered
- o:szd.151 Page 2: **99.7%** filtered (empty)
- o:szd.196: **10-20%** filtered

---

### 4. Sample Generator

#### Sampling Strategy (`create_samples.py`)
```python
def select_sample_pages(pages, max_samples=10):
    """
    Select evenly distributed representative pages:
    - Always include first and last page
    - Evenly distribute remaining samples
    - Total ≤ max_samples
    """
    step = total / max_samples
    indices = [int(i * step) for i in range(max_samples)]
    return sample_pages, indices
```

**Output per Document:**
```
samples/
├── {doc}_sample.json          # Viewer data
├── {doc}_full.json            # Complete data
├── {doc}_transcription.txt    # Full text
├── {doc}_report.md            # Statistics
└── images/{doc}/              # Sample images
```

**Purpose:** GitHub Pages deployment (reduce repo size)

---

### 5. Interactive Viewer

#### UI Components (`generate_viewer_simple.py`)

**Layout:**
```
┌─────────────────────────────────────┐
│  Header (Title, Theme Toggle)       │
├─────────────────────────────────────┤
│  Document Selector (Cards)          │
├─────────────────────────────────────┤
│  Info Bar (Metadata + Page Nav)     │
├─────────────────────────────────────┤
│  Thumbnail Strip (Horizontal)        │
├─────────────────────────────────────┤
│  ┌──────────┬──────────┐            │
│  │  Image   │  OCR     │            │
│  │  Viewer  │  Text    │            │
│  │  (Zoom)  │  (Copy)  │            │
│  └──────────┴──────────┘            │
└─────────────────────────────────────┘
```

**Features:**
- **Image Viewer:** Pan/Zoom (mousewheel), Drag
- **OCR Panel:** Scrollable, monospace font, copy/download
- **Navigation:** Keyboard shortcuts (←→, +-, 0)
- **Thumbnails:** Quick page selection
- **Responsive:** Mobile-optimized

**Data Loading:**
```javascript
// Auto-detect mode
const samplesFile = 'samples/samples.json';
if (exists(samplesFile)) {
    // GitHub Pages mode
    loadSamples();
} else {
    // Full mode
    loadFullResults();
}
```

---

## Data Flow

### METS Processing
```
data/o_szd.151/
├── mets.xml              # Input
└── images/
    ├── IMG_1.jpg
    └── ...
         │
         v
┌────────────────┐
│ parse_mets()   │  Extract metadata
└────────┬───────┘
         │
         v
┌────────────────┐
│ model.infer()  │  OCR each page
└────────┬───────┘
         │
         v
┌────────────────┐
│ filter()       │  Remove artifacts
└────────┬───────┘
         │
         v
results/mets_*/
├── *_ocr.json            # Raw
└── *_ocr_cleaned.json    # Filtered
```

### PDF Processing
```
data/document.pdf
         │
         v
┌────────────────┐
│ pdf_to_images()│  Convert @ 300 DPI
└────────┬───────┘
         │
         v
results/pdf_*/images/
├── page_001.png
├── page_002.png
└── ...
         │
         v
┌────────────────┐
│ model.infer()  │  OCR each page
└────────┬───────┘
         │
         v
┌────────────────┐
│ filter()       │  Remove artifacts
└────────┬───────┘
         │
         v
results/pdf_*/
├── results.json          # Raw
└── results_cleaned.json  # Filtered
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Model** | DeepSeek-OCR (3B, BF16) |
| **Framework** | PyTorch 2.6.0, Transformers 4.46.3 |
| **CUDA** | 11.8 / 13.0 |
| **PDF** | PyMuPDF (fitz) |
| **XML** | xml.etree.ElementTree |
| **Metrics** | python-Levenshtein, jiwer |
| **Frontend** | Vanilla HTML/CSS/JS (no frameworks) |

---

## Performance Optimization

### 1. Model Caching
```python
# First run: ~5 min download
# Subsequent runs: ~30s load from cache
model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    cache_dir="~/.cache/huggingface"
)
```

### 2. Batch Processing
```python
# Process pages sequentially to avoid VRAM spikes
for page in pages:
    result = model.infer(page)
    # Clear CUDA cache periodically
    if i % 10 == 0:
        torch.cuda.empty_cache()
```

### 3. Visual Token Compression
- DeepSeek-OCR uses **10:1 compression** ratio
- Reduces processing time significantly
- Trade-off: Slight accuracy decrease on complex layouts

---

**See also:** [[01-Quick-Start]] | [[03-Results]] | [[04-Learnings]]
