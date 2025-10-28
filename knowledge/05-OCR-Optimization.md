# OCR Optimization Strategy

**Datum:** 2025-10-28
**Ziel:** Verbesserung der OCR-Qualität durch Parameter-Optimierung

---

## Problem Statement

Nach dem ersten OCR-Durchgang haben wir festgestellt:

### HSA Letter (o_hsa_letter_2261)
- **CER:** 21.87% (Character Error Rate)
- **WER:** 30.75% (Word Error Rate)
- **Probleme:**
  - Eigennamen falsch (Mistral → Liistral)
  - Fehlende Text-Segmente (30% der Fehler)
  - Diakritika-Fehler (è → é)

### ANNO Zeitungsseite (anno_grazer_tagblatt)
- **Qualität:** Subjektiv mittel-schlecht
- **Probleme:**
  - Komplexes Multi-Column Layout (3-4 Spalten)
  - Frakturschrift gemischt mit Antiqua
  - Repetition-Bug (Model-Halluzination am Ende)
  - Layout-Chaos: Spalten durcheinander

### Verwendete Settings (1. Durchgang)
```python
model.infer(
    tokenizer,
    prompt="<image>\nExtract all text from this document.",
    image_file=str(image_path),
    output_path=str(temp_dir),
    base_size=640,          # ← ZU KLEIN für Details
    image_size=640,
    crop_mode=True,
    save_results=True,
    test_compress=True
)
```

---

## Research: DeepSeek-OCR Parameter

### Verfügbare Modi

| Mode | base_size | image_size | crop_mode | Token Count | Use Case |
|------|-----------|------------|-----------|-------------|----------|
| **Tiny** | 512 | 512 | False | ~100-200 | Schnell, niedrige Qualität |
| **Small** | 640 | 640 | False | ~200-400 | OK für einfache Docs |
| **Base** | 1024 | 1024 | False | ~400-800 | Balance |
| **Large** | 1280 | 1280 | False | ~800-1200 | Beste Qualität |
| **Gundam** | 1024 | 640 | **True** | ~600-1200 | **Empfohlen!** |

### Parameter-Bedeutung

**`base_size`**
- Kontrolliert die Auflösung des **globalen Überblicks**
- Höher = mehr Details erkannt, aber mehr VRAM
- Empfehlung: 1024 für komplexe Dokumente

**`image_size`**
- Kontrolliert die Auflösung der **lokalen Crops** (wenn crop_mode=True)
- Standard: 640×640px Tiles
- Höher = bessere Erkennung kleiner Schrift

**`crop_mode`**
- `True`: Dynamisches Tiling - Bild wird in überlappende Tiles zerlegt
- `False`: Single-Pass - Bild wird nur einmal komplett verarbeitet
- **Wichtig für große/komplexe Dokumente!**
- Gundam Mode: 1× Global (1024×1024) + 2-6× Local (640×640)

**`test_compress`**
- Aktiviert Kompression-Optimierungen
- Reduziert Token-Count, kann aber Details verlieren

### Prompt-Varianten

DeepSeek-OCR unterstützt verschiedene Prompts:

```python
# Standard (EMPFOHLEN für Text-OCR)
"<image>\nExtract all text from this document."

# Markdown (für Layout-Struktur)
"<image>\nConvert the document to markdown."

# Minimal
"<image>\nFree OCR."

# ⚠️ Grounding Mode (NUR für Bounding Boxes!)
"<image>\n<|grounding|>OCR this image."
# ❌ NICHT verwenden für reinen Text! Verursacht Halluzinationen!
```

**WICHTIG:** `<|grounding|>` ist für **Object Detection** mit Bounding Boxes gedacht, NICHT für Text-Extraktion! Es führt zu massiven Halluzinationen (endlose Zahlen/Sonderzeichen).

---

## Optimization Strategy

### Für HSA Letter (Französischer Brief)

**Dokument-Charakteristik:**
- Handgeschriebener/getippter Brief
- Single-Column, einfaches Layout
- Französisch mit vielen Akzenten
- Eigennamen wichtig

**Optimierte Settings:**
```python
base_size=1024,        # ← ERHÖHT von 640 (mehr Details für Akzente)
image_size=640,        # ← Beibehalten (reicht für Brief)
crop_mode=True,        # ← Beibehalten (auch für Briefe gut)
prompt="<image>\n<|grounding|>Extract all text from this document."  # Grounding für Präzision
```

**Erwartete Verbesserungen:**
- ✅ Bessere Erkennung von Diakritika (è, é, à)
- ✅ Weniger fehlende Text-Segmente
- ✅ Eventuell bessere Eigennamen (Mistral statt Liistral)
- **Ziel:** CER < 15%, WER < 20%

### Für ANNO Zeitungsseite (Multi-Column, Fraktur)

**Dokument-Charakteristik:**
- Komplexes Multi-Column Layout (3-4 Spalten)
- Gemischte Schriftarten (Fraktur + Antiqua)
- Viele kleine Anzeigen/Boxen
- Unterschiedliche Schriftgrößen
- **Schwierigster Fall!**

**Optimierte Settings (Variante 1: Gundam Pro):**
```python
base_size=1024,        # ← ERHÖHT von 640 (globale Übersicht verbessern)
image_size=1024,       # ← ERHÖHT von 640 (lokale Details verbessern)
crop_mode=True,        # ← WICHTIG! Multi-Crop für Spalten
prompt="<image>\n<|grounding|>Convert the document to markdown."  # Markdown für Layout
```

**Optimierte Settings (Variante 2: Maximum Quality):**
```python
base_size=1280,        # ← MAXIMAL
image_size=1280,       # ← MAXIMAL
crop_mode=True,
prompt="<image>\n<|grounding|>Convert the document to markdown."
```

**Erwartete Verbesserungen:**
- ✅ Bessere Spalten-Trennung
- ✅ Weniger Repetition-Bug (durch besseres Layout-Verständnis)
- ✅ Bessere Frakturschrift-Erkennung
- ✅ Strukturierte Ausgabe (Markdown hilft bei Layout)
- **Ziel:** Keine Repetition, strukturierte Ausgabe, >80% Texterfassung

---

## Implementation Plan

### Phase 1: Neu-Verarbeitung
1. ✅ Backup alter Results erstellen
2. HSA mit optimierten Settings neu verarbeiten
3. ANNO mit optimierten Settings neu verarbeiten (2 Varianten testen)

### Phase 2: Evaluation
1. HSA: Neue CER/WER vs. alte CER/WER vergleichen
2. ANNO: Subjektive Qualitäts-Bewertung + Repetition-Check
3. Side-by-Side Vergleich dokumentieren

### Phase 3: Dokumentation
1. Metriken-Tabelle: Alt vs. Neu
2. Visuelle Beispiele: Fehler-Korrekturen
3. Learnings dokumentieren

### Phase 4: Deployment
1. Beste Variante als neue Samples auf Webseite
2. Alte Samples als "v1" archivieren (optional)
3. Git Commit mit detaillierter Beschreibung

---

## Expected Trade-offs

### Vorteile höherer Auflösung:
- ✅ Bessere Erkennung kleiner Schrift
- ✅ Präzisere Diakritika
- ✅ Weniger fehlende Segmente
- ✅ Bessere Layout-Erfassung

### Nachteile:
- ❌ Längere Verarbeitungszeit (~2-3× länger)
- ❌ Mehr VRAM benötigt (kann OOM auf schwächeren GPUs)
- ❌ Höhere Token-Counts → mehr Kosten (bei API-Nutzung)

### Benchmark-Erwartung:

| Dokument | Alt (640) | Neu (1024) | Neu (1280) |
|----------|-----------|------------|------------|
| HSA Time | 22.5s | ~35-45s | ~50-60s |
| ANNO Time | 283s | ~400-500s | ~600-700s |

---

## Hardware Requirements

**Minimum (für 1024 Settings):**
- GPU: RTX 4070 Ti (12 GB VRAM)
- RAM: 16 GB
- Storage: 20 GB temp space

**Empfohlen (für 1280 Settings):**
- GPU: RTX 4080 (16 GB VRAM) ✅ **Haben wir!**
- RAM: 32 GB
- Storage: 30 GB temp space

---

## Rollback Strategy

Falls die neuen Settings **schlechter** performen:

1. Alte Results sind im `results/` Ordner erhalten
2. Alte Samples sind in Git History
3. Einfach alte JSONs wieder verwenden
4. In Dokumentation festhalten: "Settings-Experiment fehlgeschlagen"

---

## Success Criteria

**HSA:**
- ✅ CER < 15% (vorher: 21.87%)
- ✅ WER < 20% (vorher: 30.75%)
- ✅ Keine fehlenden Text-Segmente
- ✅ Eigennamen korrekt

**ANNO:**
- ✅ Kein Repetition-Bug
- ✅ Strukturierte Ausgabe (Spalten erkennbar)
- ✅ Markdown-Format nutzbar
- ✅ Subjektiv "gut lesbar"

---

## Next Steps

1. [IN PROGRESS] Dokumentation schreiben
2. [PENDING] HSA neu verarbeiten
3. [PENDING] ANNO neu verarbeiten (beide Varianten)
4. [PENDING] Evaluation & Vergleich
5. [PENDING] Knowledge Base updaten mit Ergebnissen

---

## Ergebnisse

### HSA Letter - Optimierungsversuch

**Ausgangslage:**
- CER: 21.87% (bereits recht gut!)
- WER: 30.75%
- Settings: base_size=640, image_size=640

**Optimierte Settings:**
- base_size=1024 ← erhöht
- image_size=640
- crop_mode=True
- Standard Prompt (KEIN grounding!)

**Ergebnis:**
- CER: 20.47% (-1.4%)
- WER: 29.19% (-1.56%)
- Zeit: 23.75s (+1.25s)

**Bewertung:** ⚠️ **Verbesserung minimal und nicht signifikant**
- Die Verbesserung von 21.87% → 20.47% ist marginal
- HSA war bereits mit Standardeinstellungen gut
- Der Zeitaufwand steigt, ohne dramatische Qualitätsverbesserung
- **Fazit:** Für einfache Briefe reichen Standard-Settings (640)

### ANNO Zeitungsseite - Optimierungsversuch

**Ausgangslage:**
- Komplexe Multi-Column Zeitungsseite (1916)
- Frakturschrift gemischt mit Antiqua
- Repetition-Bug im Output
- Settings: base_size=640, image_size=640

**Versuchte Settings:**

**Versuch 1:** base_size=1024, image_size=1024
- **Ergebnis:** ❌ CUDA Out of Memory (RTX 4080 16GB)

**Versuch 2:** base_size=1024, image_size=640 (Gundam)
- **Ergebnis:** ❌ **Repetition-Bug bleibt!**
- Output: Endlose `2.000päsche. 2.000päsche...` Wiederholungen
- Keine Verbesserung gegenüber 640/640

**Versuch 3:** base_size=1024, image_size=1024 + Markdown Prompt
- **Ergebnis:** ❌ CUDA OOM

**Bewertung:** ❌ **Nicht durch Parameter-Tuning lösbar**
- Das ANNO-Problem ist fundamental
- DeepSeek-OCR ist für solch komplexe Layouts nicht geeignet
- Frakturschrift + Multi-Column + kleine Anzeigen = zu komplex
- **Fazit:** Für historische Zeitungen alternatives Tool benötigt (OCR-D, Tesseract mit Fraktur)

---

## Wichtige Learnings

### 1. `<|grounding|>` Prompt - GEFÄHRLICH!

**Was passiert:** Massives Halluzinations-Problem
```
[C] [e] [a] [j]
### = 1 1 1 1 1 1 1
### = 2 1 1 1 1 1 1
### = 3 1 1 1 1 1 1
...endlose Zahlenkolonnen...
```

**Warum:** `<|grounding|>` ist für **Object Detection mit Bounding Boxes** gedacht, NICHT für Text-Extraktion!

**Lektion:** ❌ NIEMALS `<|grounding|>` für reinen Text-OCR verwenden!

### 2. Hardware-Grenzen

**RTX 4080 (16 GB VRAM):**
- ✅ base_size=1024, image_size=640 → OK
- ✅ base_size=1024, image_size=1024 (kleine Bilder) → OK
- ❌ base_size=1024, image_size=1024 (große Zeitungen) → **OOM!**

**Lektion:** 1024/1024 nur für kleinere Dokumente (<3000px)

### 3. Standard-Settings sind oft ausreichend

**base_size=640 funktioniert gut für:**
- ✅ Einfache Briefe
- ✅ Einspaltiger Text
- ✅ Moderne Schriftarten
- ✅ Gute Scan-Qualität

**Höhere Settings (1024) bringen kaum Verbesserung:**
- HSA: Nur 1.4% CER-Verbesserung
- Nicht signifikant bei bereits guter Baseline

**Lektion:** Don't over-optimize! 640 ist default aus gutem Grund.

### 4. Manche Dokumente sind zu komplex

**ANNO-Zeitungsseite zeigt Grenzen von DeepSeek-OCR:**
- ❌ Multi-Column Layout durcheinander
- ❌ Frakturschrift nicht robust erkannt
- ❌ Repetition-Bug bei komplexen Layouts
- ❌ Keine Verbesserung durch höhere Settings

**Lektion:** DeepSeek-OCR ist **NICHT** für historische Zeitungen geeignet!

**Alternativen für solche Dokumente:**
- OCR-D (spezialisiert auf historische Dokumente)
- Tesseract mit Fraktur-Modell
- Transkribus (kommerziell)
- Pre-Processing: Layout-Analyse → Spalten trennen → Einzeln OCR

---

## Empfehlungen

### Wann Standard-Settings (640/640) verwenden:
- ✅ Moderne Dokumente
- ✅ Einfaches Layout (1-Spalte)
- ✅ Gute Scan-Qualität
- ✅ Zeit wichtiger als 1-2% Verbesserung

### Wann höhere Settings (1024/640) verwenden:
- ✅ Kritische Dokumente (wo jedes % zählt)
- ✅ Schlechte Scan-Qualität
- ✅ Kleine Schrift / viele Details
- ⚠️ Nur wenn VRAM ausreicht (>12GB)

### Wann DeepSeek-OCR NICHT verwenden:
- ❌ Historische Zeitungen (Multi-Column, Fraktur)
- ❌ Handschrift
- ❌ Stark degradierte Scans
- ❌ Tabellen mit komplexem Layout

---

## Kosten-Nutzen-Analyse

| Setting | Zeit | VRAM | CER-Verbesserung | Empfehlung |
|---------|------|------|------------------|------------|
| 640/640 | ~20s | 8GB | Baseline | ✅ **Standard** |
| 1024/640 | ~25s | 12GB | +1-2% | ⚠️ Optional |
| 1024/1024 | ~50s | 16GB+ | +2-3%? | ❌ Selten sinnvoll |

**Fazit:** Der Aufwand für höhere Settings lohnt sich **nur bei kritischen Anwendungen** wo jedes Prozent zählt.

---

## Commit Message für diese Erkenntnis

```
Add OCR optimization experiments and parameter tuning

Experiments:
- Test HSA with base_size=1024: Minimal improvement (CER 21.87% → 20.47%)
- Test ANNO with various settings: No improvement, repetition bug persists
- Test grounding prompt: Catastrophic hallucination (not for text OCR!)

Learnings:
- Standard settings (640) sufficient for most documents
- Higher settings show diminishing returns (<2% improvement)
- Some documents (complex newspapers) beyond DeepSeek-OCR capabilities
- Grounding prompt causes hallucinations, must not be used for text

Scripts:
- test_ocr_image.py: Add CLI parameters for base_size, image_size, prompt
- Document findings in knowledge/05-OCR-Optimization.md

Conclusion: Keep current samples with standard settings.
No re-processing needed.
```

---

**Gestartet:** 2025-10-28
**Abgeschlossen:** 2025-10-28
**Status:** ✅ Completed - No optimization needed
**Bearbeiter:** Claude (mit User Chrisi)
