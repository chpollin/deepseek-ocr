# DeepSeek-OCR Evaluation Framework

> AI-powered OCR pipeline for printed documents with METS metadata support and interactive visualization

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://chpollin.github.io/deepseek-ocr/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/pytorch-2.6.0-red)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-research-orange)](LICENSE)

---

## 🎯 Overview

Complete OCR evaluation pipeline for processing **printed documents** (METS archives, PDFs) using DeepSeek-OCR:

- 📄 **METS Support** - Process digital archive documents with XML metadata
- 📑 **PDF Processing** - Direct PDF-to-OCR conversion (tested with 595 pages)
- 🔍 **Artifact Filtering** - Automatic removal of color cards, measurements, reference marks
- 📊 **Interactive Viewer** - Side-by-side image/text comparison with zoom
- 🌐 **GitHub Pages** - Lightweight sample deployment (5-10 pages per document)
- 📈 **Detailed Reports** - Statistics, CER metrics, full transcriptions

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/chpollin/deepseek-ocr.git
cd deepseek-ocr

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: ./venv/Scripts/activate (Windows)

# Install dependencies
pip install -r requirements.txt
```

### Process Documents

```bash
# METS document
python scripts/test_ocr_mets.py data/o_szd.151/

# PDF
python scripts/test_ocr_pdf.py data/document.pdf

# Create samples for GitHub Pages
python scripts/create_samples.py

# Generate interactive viewer
python scripts/generate_viewer_simple.py

# View locally
cd docs && python -m http.server 8000
# Open http://localhost:8000/
```

---

## 📊 Results

| Document | Lang | Pages | CER | Status |
|----------|------|-------|-----|--------|
| **o:szd.151** | DE | 3 | ~2-3% | ✅ Complete |
| **o:szd.196** | FR | 9 | N/A | ✅ Complete |
| **DTS_Flechte.pdf** | DE | 595 | TBD | 🔄 Processing |

**Live Demo:** [https://chpollin.github.io/deepseek-ocr/](https://chpollin.github.io/deepseek-ocr/)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Model** | [DeepSeek-OCR](https://huggingface.co/deepseek-ai/DeepSeek-OCR) (3B params, BF16) |
| **Framework** | PyTorch 2.6.0, Transformers 4.46.3 |
| **PDF** | PyMuPDF (fitz) |
| **CUDA** | 11.8 / 13.0 |
| **Frontend** | Vanilla HTML/CSS/JS (no frameworks) |

**Hardware:** RTX 4080 (16 GB VRAM) recommended

---

## 📂 Project Structure

```
deepseek-ocr/
├── docs/                         # 🌐 GitHub Pages Website
│   ├── index.html               # Main viewer page
│   ├── style.css                # Viewer styles
│   ├── viewer.js                # Viewer logic + data
│   └── samples/                 # Sample images
├── scripts/                      # 🔧 Python Scripts
│   ├── README.md                # Scripts documentation
│   ├── test_ocr_mets.py         # METS document processor
│   ├── test_ocr_pdf.py          # PDF processor
│   ├── filter_artifacts.py      # Artifact detection & removal
│   ├── create_samples.py        # Sample generator for GitHub Pages
│   ├── generate_viewer_simple.py # Viewer generator
│   └── clean_ocr_results.py     # Apply filters to results
├── knowledge/                    # 📚 Obsidian Vault Documentation
│   ├── 00-Index.md              # Overview & quick navigation
│   ├── 01-Quick-Start.md        # Installation & usage
│   ├── 02-Architecture.md       # System design & data flow
│   ├── 03-Results.md            # Evaluation & metrics
│   └── 04-Learnings.md          # Best practices & tips
├── samples/                      # 🎨 Deployment Samples
│   ├── images/                  # Sample images (12 total)
│   ├── *_sample.json            # Viewer data
│   ├── *_full.json              # Complete data
│   ├── *_transcription.txt      # Full transcriptions
│   └── *_report.md              # Statistical reports
├── data/                         # 📂 Input Documents
│   ├── o_szd.151/               # METS (German, 3 pages)
│   ├── o_szd.196/               # METS (French, 9 pages)
│   └── DTS_Flechte.pdf          # PDF (595 pages)
├── results/                      # 💾 OCR Outputs
│   ├── mets_*/                  # METS processing results
│   └── pdf_*/                   # PDF processing results
└── requirements.txt             # Python dependencies
```

---

## ✨ Features

### OCR Processing
- **METS XML Parsing** - Extract metadata (title, author, URN, language)
- **PDF Conversion** - High-quality 300 DPI image extraction
- **Batch Processing** - Sequential page-by-page processing
- **Progress Tracking** - Real-time character count and timing

### Artifact Filtering
- **Pattern-Based Detection** - Keywords, regex, structural analysis
- **Effectiveness** - 47-99% noise reduction on test documents
- **Categories** - Color references, measurements, scale markers

### Interactive Viewer
- **Side-by-Side Comparison** - Original image vs OCR text
- **Zoom & Pan** - Mousewheel zoom, drag to navigate
- **Thumbnail Navigation** - Quick page selection
- **Keyboard Shortcuts** - ←→ (pages), +- (zoom), C (copy)
- **Export Functions** - Download text, download image

### GitHub Pages Support
- **Smart Sampling** - 5-10 evenly distributed representative pages
- **Lightweight** - < 10 MB total (vs 1+ GB for full data)
- **Full Access** - Complete transcriptions and data available as downloads

---

## 📖 Documentation

Comprehensive documentation in Obsidian-compatible Markdown:

- **[00-Index.md](knowledge/00-Index.md)** - Project overview & navigation
- **[01-Quick-Start.md](knowledge/01-Quick-Start.md)** - Installation & usage examples
- **[02-Architecture.md](knowledge/02-Architecture.md)** - System design & components
- **[03-Results.md](knowledge/03-Results.md)** - Performance metrics & evaluation
- **[04-Learnings.md](knowledge/04-Learnings.md)** - Best practices & troubleshooting
- **[scripts/README.md](scripts/README.md)** - Scripts documentation & workflow

**View in Obsidian:** Open `knowledge/` folder as vault

---

## 🎯 Use Cases

### ✅ Ideal For
- 📄 Digitalizing printed documents
- 📊 Extracting text from scanned PDFs
- 🏛️ Processing digital archives (METS format)
- 🌐 Multi-language documents (DE, EN, FR, ...)
- 🔢 Documents with formulas and tables

### ❌ Not Suitable For
- ✍️ Handwriting recognition
- 🏛️ Historical scripts (Kurrent, Fraktur)
- 📝 Handwritten notes
- 🎨 Complex artistic layouts

---

## 🔬 Performance

| Metric | Value | Hardware |
|--------|-------|----------|
| **Model Load** | ~30-45s | First run (cached after) |
| **OCR per Page** | ~15-20s | RTX 4080 |
| **Throughput** | 120-360 pages/hour | Varies by content |
| **VRAM Usage** | ~10 GB | During inference |
| **Accuracy (DE)** | ~97-98% | CER on test docs |

---

## 🤝 Contributing

This is a research project. Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📝 License

Research use only. See [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Live Demo:** https://chpollin.github.io/deepseek-ocr/
- **Model:** https://huggingface.co/deepseek-ai/DeepSeek-OCR
- **Documentation:** [docs/](docs/)
- **Issues:** https://github.com/chpollin/deepseek-ocr/issues

---

## 🙏 Acknowledgments

- **DeepSeek AI** - For the excellent OCR model
- **Stefan Zweig Digital** - For METS test data
- **PyMuPDF** - For reliable PDF processing

---

**Last Updated:** 2025-10-27
**Status:** Active Development
**Maintainer:** Research Team
