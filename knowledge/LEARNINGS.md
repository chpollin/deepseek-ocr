# Lessons Learned

**Datum:** 2025-10-25 | **Kontext:** Im Zug, instabile Verbindung, RTX 4060 (8GB)

---

## ❌ Was NICHT funktioniert hat

### 1. Lokale Inferenz auf RTX 4060
**Problem:** 8 GB VRAM < 16 GB benötigt
**Lesson:** VRAM-Check VOR Modell-Download
```python
# Das sollte man ZUERST machen:
import torch
vram = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"VRAM: {vram:.1f} GB")
# RTX 4060: 8 GB → DeepSeek-OCR: 16 GB → ❌
```

### 2. Flash-Attention Installation (Windows)
**Problem:** Braucht CUDA Toolkit + nvcc + Visual Studio Build Tools
**Lesson:** Flash-Attention ist optional, nicht kritisch
```python
# Einfach weglassen:
model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    # _attn_implementation='flash_attention_2',  # ❌ Raus
    trust_remote_code=True
)
```

### 3. Offizielle DeepSeek API für OCR
**Problem:** Nur Chat/Reasoner verfügbar, kein OCR-Endpoint
**Lesson:** Open-Source ≠ API verfügbar

### 4. HuggingFace Spaces API
**Problem:** Instabil, generische Fehler, keine Doku
```python
# Fehler:
"The upstream Gradio app has raised an exception..."
```
**Lesson:** HF Spaces gut für UI, nicht für Production API

---

## ✅ Was funktioniert hat

### 1. PyTorch Installation über pip
```bash
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu118
# ✅ 2.7 GB, ~60 Min, Background-Download half
```

### 2. Transformers ohne Probleme
```bash
pip install transformers==4.46.3 tokenizers==0.20.3
# ✅ 15 MB, ~3 Min
```

### 3. Windows Unicode-Fix
```python
# Problem: cp1252 kann Unicode nicht
# Lösung: Output unterdrücken
import io, sys
old_stdout = sys.stdout
sys.stdout = io.StringIO()
client = Client(HF_SPACE)
sys.stdout = old_stdout
```

### 4. Gradio Client Endpoint-Discovery
```python
client = Client("akhaliq/DeepSeek-OCR")
print(client.endpoints)  # API-Namen finden
# {1: Endpoint api_name: /ocr_process, ...}
```

---

## 🎯 Top 5 Erkenntnisse

### 1. Hardware-Check ist das Erste
VRAM-Anforderungen VOR Installation prüfen. Hätte uns Stunden gespart.

### 2. API als Fallback planen
Bei hohen VRAM-Anforderungen direkt API-Lösung vorbereiten:
- HuggingFace Spaces (kostenlos, instabil)
- Google Colab (kostenlos, zuverlässig)
- Cloud Provider (kostenpflichtig, Production)

### 3. Optionale Dependencies sind optional
Flash-Attention, spezielle Quantization, etc. → Erst mal ohne testen

### 4. Windows + ML = Extra Aufwand
- UTF-8 Encoding Probleme
- Build Tools für Kompilierung
- CUDA Toolkit Installation komplex
→ Linux/Colab ist einfacher

### 5. Open-Source Modelle ≠ API-Zugang
Nur weil Modell auf HuggingFace liegt, heißt das nicht:
- ✅ Inference API verfügbar
- ✅ Offizielle API vorhanden
- ✅ Community Spaces funktionieren

---

## 🔧 Best Practices

### Pre-Installation Checklist
```python
# 1. VRAM Check
import torch
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# 2. Modell-Größe recherchieren
# HuggingFace Model Card → Files → model.safetensors Größe

# 3. VRAM-Anforderung = Modell-Größe × 2.5
# Beispiel: 6.7 GB Modell → 16-17 GB VRAM

# 4. Falls VRAM < Anforderung → API-Lösung planen
```

### Installation Strategy
1. **Core Dependencies zuerst** (PyTorch, Transformers)
2. **Optional Dependencies später** (Flash-Attention)
3. **Test ohne Optionals**
4. **Nur bei Bedarf nachrüsten**

### API-Zugang Prioritäten
1. **Offizielle API** (falls vorhanden)
2. **HuggingFace Inference API** (falls deployed)
3. **Google Colab** (kostenlos, zuverlässig) ⭐
4. **HuggingFace Spaces** (kostenlos, instabil)
5. **Cloud Provider** (kostenpflichtig)

---

## 💡 Nächstes Mal anders

### 1. VRAM-Check als Erstes
```bash
nvidia-smi
# Vor irgendwas anderem!
```

### 2. Google Colab von Anfang an
Bei 8 GB VRAM direkt Colab-Notebook statt lokale Installation

### 3. Dokumentation während der Arbeit
Nicht am Ende alles rekonstruieren

### 4. Git von Anfang an
```bash
git init
git commit -m "Initial setup"
# Bei jedem Schritt committen
```

---

## 📊 Zeit-Bilanz

| Aktivität | Zeit | Vermeidbar? |
|-----------|------|-------------|
| PyTorch Download | 60 Min | ❌ (Modell-Größe) |
| Flash-Attention Debug | 30 Min | ✅ (Hätte überspringen können) |
| HF Spaces API Trial & Error | 45 Min | ⏸️ (Läuft noch) |
| Windows UTF-8 Fix | 15 Min | ✅ (Linux/Colab) |
| VRAM-Problem erkennen | 20 Min | ✅ (Pre-Check) |
| **Gesamt** | **170 Min** | **~60 Min vermeidbar** |

**Optimiert:** Mit VRAM-Check + Colab direkt → **~60-90 Min Gesamtzeit**

---

## 🚀 Empfehlung für ähnliche Projekte

### Wenn VRAM unsicher
1. **VRAM prüfen:** `nvidia-smi`
2. **Modell-Anforderungen recherchieren**
3. **Colab-Notebook als Plan A** (nicht B)
4. **Lokale Installation nur bei genug VRAM**

### Für Production
- Keine HuggingFace Spaces
- Eigener Inference Server oder Cloud Provider
- Load Testing vor Deployment
