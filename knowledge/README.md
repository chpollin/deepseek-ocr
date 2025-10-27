# DeepSeek-OCR Projekt - Überblick

**Ziel:** DeepSeek-OCR auf **gedruckten deutschen Dokumenten** evaluieren

## Quick Facts

- **Anwendung:** OCR für gedruckte Texte (PDFs, Scans, Screenshots)
- **Modell:** DeepSeek-OCR (3B Parameter, 6.7 GB)
- **Hardware:** RTX 4080 (16 GB VRAM) ✅ Perfekt!
- **Setup:** Lokal, Python 3.11.9, CUDA 13.0
- **Status:** Ready for testing

## Projekt-Scope

### ✅ IN SCOPE (Was wir testen)
- Gedruckte Dokumente (PDF, PNG, JPG)
- Formeln und Tabellen
- Mehrsprachige Texte (Deutsch, Englisch)
- Wissenschaftliche Papers
- Screenshots von Webseiten

### ❌ OUT OF SCOPE (Was wir NICHT testen)
- Handschrifterkennung (HTR)
- Historische Dokumente (Kurrentschrift)
- Handgeschriebene Notizen

**Grund:** DeepSeek-OCR ist für gedruckte Texte optimiert, nicht für Handschrift.

## Projektstruktur

```
deepseek-ocr/
├── data/
│   ├── printed_docs/          # Test-Dokumente (gedruckt)
│   │   ├── README.md          # Anleitung für Test-Daten
│   │   ├── sample_01.png      # Beispiel-Dokument
│   │   └── ground_truth/      # Manuelle Transkriptionen
│   │       └── sample_01.txt
│   └── _archive/              # Alte Handschrift-Daten (ignoriert)
├── knowledge/                 # Dokumentation
│   ├── README.md             # Dieser Überblick
│   ├── TECHNICAL.md          # Technische Details
│   ├── LEARNINGS.md          # Lessons Learned
│   └── TEST_RESULTS.md       # Test-Ergebnisse
├── results/                  # OCR Outputs
│   └── batch_TIMESTAMP/      # Batch-Ergebnisse
├── venv/                     # Python Environment
├── requirements.txt          # Dependencies
├── test_ocr_simple.py       # Single-Image Test
├── test_ocr_batch.py        # Batch Processing
└── compare_results.py       # Evaluation (CER/WER)
```

## Workflow

### 1. Test-Dokumente vorbereiten
```bash
# Kopiere gedruckte Dokumente nach:
data/printed_docs/sample_01.png
data/printed_docs/sample_02.pdf
...

# Erstelle Ground Truth (manuelle Transkription):
data/printed_docs/ground_truth/sample_01.txt
data/printed_docs/ground_truth/sample_02.txt
...
```

### 2. Batch-Processing durchführen
```bash
python test_ocr_batch.py data/printed_docs/
```

**Output:**
```
results/batch_20251027_120000/
├── sample_01.txt          # OCR Ergebnis
├── sample_02.txt
├── summary.json           # Statistiken
└── temp/                  # Intermediate files
```

### 3. Evaluation
```bash
python compare_results.py results/batch_20251027_120000/
```

**Metriken:**
- **CER (Character Error Rate):** Zeichenfehler-Rate
- **WER (Word Error Rate):** Wortfehler-Rate
- **Precision/Recall/F1:** Genauigkeit

**Output:** `results/batch_TIMESTAMP/evaluation.json`

## Aktueller Status

| Task | Status | Details |
|------|--------|---------|
| Environment Setup | ✅ | Python 3.11.9, PyTorch 2.6.0+cu118 |
| Model Download | ✅ | DeepSeek-OCR cached (~7 GB) |
| Hardware Verification | ✅ | RTX 4080, 16 GB VRAM, CUDA 13.0 |
| Single Image Test | ✅ | test_ocr_simple.py funktioniert |
| Batch Processing | ✅ | test_ocr_batch.py erstellt |
| Evaluation Framework | ✅ | compare_results.py mit CER/WER |
| **Test Data** | ⏳ | **Benötigt gedruckte Dokumente!** |
| OCR Durchführung | ⏹️ | Wartet auf Test-Daten |
| Quantitative Analyse | ⏹️ | Wartet auf OCR-Ergebnisse |

## Nächste Schritte

### 1. Test-Dokumente sammeln (TODO)

**Einfacher Start:** Wikipedia-Screenshots
```python
# Beispiel: Screenshot erstellen
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://de.wikipedia.org/wiki/Künstliche_Intelligenz")
driver.save_screenshot("data/printed_docs/wikipedia_ki.png")
```

**Empfohlene Quellen:**
- Wikipedia-Artikel (Deutsch)
- arXiv Papers (PDF → PNG)
- Gescannte Bücher (Google Books, Archive.org)
- Screenshots von Nachrichtenseiten

**Benötigt:** 5-10 Dokumente für erste Evaluation

### 2. Ground Truth erstellen
Für jedes Dokument: Manuell abtippen → `.txt` File

### 3. Batch-Processing
```bash
python test_ocr_batch.py data/printed_docs/
```

### 4. Evaluation
```bash
python compare_results.py results/batch_TIMESTAMP/
```

## Performance (RTX 4080)

```
Model Loading:     ~5 min (first time, cached danach)
Inference:         ~10-30 sec/image (abhängig von Größe)
Throughput:        ~120-360 pages/hour
VRAM Usage:        ~10 GB während Inferenz
Memory:            ~6 GB RAM
```

## Use Cases

### ✅ Ideal für DeepSeek-OCR:
- 📄 PDFs digitalisieren
- 🧮 LaTeX-Formeln extrahieren
- 📊 Tabellen → Markdown konvertieren
- 📚 Gescannte Bücher transkribieren
- 🌐 Mehrsprachige Dokumente

### ❌ Nicht geeignet:
- ✍️ Handschrifterkennung
- 🏛️ Historische Dokumente (Fraktur, Kurrentschrift)
- 📝 Handgeschriebene Notizen

## Links

- **Model:** https://huggingface.co/deepseek-ai/DeepSeek-OCR
- **GitHub:** https://github.com/deepseek-ai/DeepSeek-OCR
- **Hardware-Check:** `nvidia-smi`

---

**Last Updated:** 2025-10-27
**Status:** Ready - benötigt nur Test-Dokumente
**Hardware:** RTX 4080 (16 GB VRAM) ✅
