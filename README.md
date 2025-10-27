# DeepSeek-OCR Evaluation Project

**Ziel:** DeepSeek-OCR auf **gedruckten deutschen Dokumenten** testen und evaluieren

## Project Scope

**IN SCOPE:**
- ✅ OCR für gedruckte Texte (PDFs, Scans, Screenshots)
- ✅ Formeln, Tabellen, strukturierte Layouts
- ✅ Mehrsprachige Dokumente (Deutsch, Englisch, etc.)
- ✅ Quantitative Evaluation (CER, WER, Performance)

**OUT OF SCOPE:**
- ❌ Handschrifterkennung (HTR)
- ❌ Historische Dokumente (Kurrentschrift)
- ❌ Handgeschriebene Notizen

## Hardware Requirements

**Verfügbar:**
- GPU: RTX 4080 (16 GB VRAM) ✅
- CUDA: 13.0 ✅
- RAM: 16+ GB (empfohlen) ✅

**Ergebnis:** Perfekt für lokale DeepSeek-OCR Inferenz!

## Quick Start

### 1. Setup Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Test OCR on Sample Document
```bash
python test_ocr_simple.py
```

### 3. Process Multiple Documents
```bash
python test_ocr_batch.py data/printed_docs/
```

### 4. Evaluate Results
```bash
python compare_results.py
```

## Project Structure

```
deepseek-ocr/
├── data/
│   ├── printed_docs/          # Gedruckte Test-Dokumente
│   │   ├── sample_01.pdf
│   │   ├── sample_02.png
│   │   └── ground_truth/      # Manuell transkribierte Referenzen
│   └── _archive/               # Alte Handschrift-Daten (ignoriert)
│       ├── szd-letter-htr/
│       └── km-karteikarten/
├── knowledge/
│   ├── README.md              # Projekt-Überblick
│   ├── TECHNICAL.md           # Technische Details
│   ├── LEARNINGS.md           # Lessons Learned
│   └── TEST_RESULTS.md        # Test-Ergebnisse
├── results/                   # OCR Outputs
├── venv/                      # Python Environment
├── requirements.txt           # Dependencies
├── test_ocr_simple.py        # Einzelner Test
├── test_ocr_batch.py         # Batch-Processing
└── compare_results.py        # Evaluation
```

## Current Status

| Task | Status | Details |
|------|--------|---------|
| Environment Setup | ✅ | Python 3.11.9, PyTorch 2.6.0+cu118 |
| Model Download | ✅ | DeepSeek-OCR (6.7 GB) cached |
| Hardware Verification | ✅ | RTX 4080, 16 GB VRAM |
| Single Document Test | ✅ | Script funktioniert |
| Test Data Collection | ⏳ | Gedruckte Dokumente benötigt |
| Batch Processing | ⏹️ | Noch nicht implementiert |
| Evaluation Framework | ⏹️ | CER/WER noch nicht implementiert |

## Next Steps

1. **Test-Dokumente sammeln:**
   - PDFs (wissenschaftliche Papers, Artikel)
   - Screenshots (Webseiten, Präsentationen)
   - Gescannte Bücher/Zeitschriften
   - Formeln und Tabellen

2. **Ground Truth erstellen:**
   - Manuell korrekte Transkriptionen
   - Oder: OCR auf sehr klaren Dokumenten

3. **Batch-Processing implementieren:**
   - Mehrere Dokumente automatisch verarbeiten
   - Ergebnisse strukturiert speichern

4. **Evaluation:**
   - CER/WER berechnen
   - Geschwindigkeit messen
   - Qualitative Analyse (Fehlertypen)

## Use Cases für DeepSeek-OCR

### Ideal:
- 📄 PDFs digitalisieren
- 🧮 Formeln extrahieren
- 📊 Tabellen in Markdown konvertieren
- 🌐 Mehrsprachige Dokumente
- 📚 Gescannte Bücher

### Nicht geeignet:
- ✍️ Handschrifterkennung
- 🏛️ Historische Dokumente
- 📝 Notizen, Skizzen

## Performance (RTX 4080)

```
Model Loading:     ~5 min (first time, dann cached)
Inference:         ~10-30 sec per image
Throughput:        ~120-360 pages/hour
VRAM Usage:        ~10 GB
```

## Links

- **Model:** https://huggingface.co/deepseek-ai/DeepSeek-OCR
- **GitHub:** https://github.com/deepseek-ai/DeepSeek-OCR
- **Paper:** Coming soon

---

**Last Updated:** 2025-10-27
**Hardware:** RTX 4080 (16 GB VRAM)
**Python:** 3.11.9
**Status:** Ready for printed document OCR testing
