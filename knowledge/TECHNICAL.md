# Technical Reference

**Modell:** DeepSeek-OCR | **Version:** Oktober 2025

---

## Modell-Specs

| Eigenschaft | Wert |
|-------------|------|
| Parameter | 3 Milliarden (3B) |
| Größe | 6.7 GB (BF16) |
| VRAM | 16+ GB (empfohlen) |
| Architektur | DeepEncoder (380M) + DeepSeek-3B-MoE (570M aktiv) |
| Kontext | Visual Token Compression (10x) |
| Genauigkeit | 97% bei 10x Kompression |

**Besonderheit:** Komprimiert 1000 Zeichen → 100 visuelle Tokens

---

## Hardware-Anforderungen

### Minimum
- **GPU:** 16 GB VRAM (RTX 3090, RTX 4080, A100)
- **CUDA:** 11.8+
- **RAM:** 16 GB
- **Storage:** 10 GB

### Optimal (Production)
- **GPU:** A100 (40 GB)
- **Throughput:** 2,500 tokens/sec
- **Kapazität:** 200k+ Seiten/Tag

### Nicht ausreichend
- **RTX 4060 (8 GB)** ❌
- **RTX 3060 (12 GB)** ⚠️ (knapp)

---

## Installation

### Core Dependencies
```bash
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118
pip install transformers==4.46.3 tokenizers==0.20.3
pip install einops addict easydict pillow
```

### Optional (Performance)
```bash
# Flash-Attention (benötigt CUDA Toolkit + nvcc)
pip install flash-attn==2.7.3 --no-build-isolation
```

### API-Zugang
```bash
pip install gradio_client  # Für HF Spaces
```

---

## Code-Beispiele

### Lokal (16+ GB VRAM)
```python
from transformers import AutoModel, AutoTokenizer
from PIL import Image

# Model laden
tokenizer = AutoTokenizer.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    trust_remote_code=True
)
model = AutoModel.from_pretrained(
    "deepseek-ai/DeepSeek-OCR",
    trust_remote_code=True,
    use_safetensors=True
).eval().cuda().to(torch.bfloat16)

# OCR
image = Image.open("document.jpg")
prompt = "<image>\n<|grounding|>Convert the document to markdown."

result = model.chat(
    tokenizer=tokenizer,
    image=image,
    prompt=prompt,
    base_size=640
)
```

### API via HuggingFace Space
```python
from gradio_client import Client
import io, sys

# Unicode-Fix für Windows
old_stdout = sys.stdout
sys.stdout = io.StringIO()
client = Client("akhaliq/DeepSeek-OCR")
sys.stdout = old_stdout

# OCR durchführen
result = client.predict(
    "path/to/image.jpg",  # Bildpfad
    "Extract",             # Task: Extract/Convert/Locate/Describe
    640,                   # base_size
    api_name="/ocr_process"
)
print(result)
```

### vLLM (Production)
```python
from vllm import LLM, SamplingParams

llm = LLM(model="deepseek-ai/DeepSeek-OCR")
sampling_params = SamplingParams(temperature=0.0, max_tokens=2048)

outputs = llm.generate(
    prompts=["<image>\nExtract text."],
    images=[image],
    sampling_params=sampling_params
)
```

---

## API-Zugang Optionen

### 1. HuggingFace Spaces (Kostenlos)
**Spaces:**
- `akhaliq/DeepSeek-OCR` ⭐
- `merterbak/DeepSeek-OCR-Demo`
- `khang119966/DeepSeek-OCR-DEMO`

**Status:** Verfügbar aber instabil

### 2. Google Colab (Kostenlos)
```python
# T4 GPU (15 GB VRAM) - Kostenlos ✅
!pip install torch transformers
# A100 (40 GB) - Colab Pro
```

**Status:** Zuverlässig, empfohlen für Testing

### 3. Cloud Provider (Kostenpflichtig)
- **AWS SageMaker:** ~$1-2/h (GPU)
- **HuggingFace Endpoints:** ~$0.60/h
- **RunPod:** ~$0.20/h (RTX 3090)

### 4. Offizielle DeepSeek API
**Status:** ❌ Nicht verfügbar (nur Chat/Reasoner)

---

## Unterstützte Tasks

| Task | Beschreibung | Beispiel-Prompt |
|------|--------------|-----------------|
| Extract | Reiner Text-Extrakt | `Extract all text` |
| Convert | Markdown-Konvertierung | `Convert to markdown` |
| Locate | Inhalte finden | `Find invoice number` |
| Describe | Dokument-Beschreibung | `Describe this document` |

---

## Prompts

### OCR (Basis)
```
<image>
Extract all text from this document.
```

### Markdown-Konvertierung
```
<image>
<|grounding|>Convert the document to markdown.
```

### Strukturierte Extraktion
```
<image>
Extract the following information:
- Name
- Date
- Total Amount
```

### Handschrift (experimentell)
```
<image>
This is a handwritten document in German.
Extract the text carefully, preserving the original structure.
```

---

## Bekannte Limitierungen

### Hardware
- **Keine kleinere Variante** (kein Tiny/Small)
- **Keine Quantization** (4-bit/8-bit nicht offiziell)
- **16 GB VRAM Minimum** (nicht verhandelbar)

### API
- **Keine offizielle API** für OCR-Modell
- **HF Inference API:** Nicht deployed
- **HF Spaces:** Community, instabil

### Funktionalität
- **Handschrift:** Begrenzt (primär für Druckschrift)
- **Komplexe Layouts:** Gut aber nicht perfekt
- **Nicht-lateinische Schriften:** Limitiert

---

## Performance

### Geschwindigkeit (A100)
- **vLLM:** 2,500 tokens/sec
- **Standard:** ~500 tokens/sec

### Speicher
- **VRAM:** ~8-10 GB während Inferenz
- **RAM:** ~4-6 GB
- **Disk Cache:** ~/.cache/huggingface/ (~7 GB)

### Batch Processing
```python
# Mehrere Bilder parallel
results = model.batch_predict(images, prompts, batch_size=4)
```

---

## Troubleshooting

### OOM Error
```python
# Lösung 1: Kleinere base_size
result = model.chat(..., base_size=480)  # Statt 640

# Lösung 2: bfloat16
model = model.to(torch.bfloat16)

# Lösung 3: API-Zugang
# Wenn nichts hilft → HF Space oder Colab
```

### Flash-Attention Error
```python
# Einfach weglassen:
model = AutoModel.from_pretrained(
    MODEL_NAME,
    # _attn_implementation='flash_attention_2',  # ❌ Raus
    trust_remote_code=True
)
```

### Windows UTF-8 Error
```python
import io, sys
old_stdout = sys.stdout
sys.stdout = io.StringIO()
# ... gradio_client Code ...
sys.stdout = old_stdout
```

---

## Alternativen

| Modell | VRAM | Stärken | Use Case |
|--------|------|---------|----------|
| TrOCR | 2 GB | Schnell, leicht | Einfache Dokumente |
| Donut | 8 GB | End-to-end | Formulare, Receipts |
| PaddleOCR | < 1 GB | CPU-freundlich | Chinesisch, Batch |
| Tesseract | 0 GB | Klassisch, CPU | Legacy, einfach |

---

## Links

- **Model:** https://huggingface.co/deepseek-ai/DeepSeek-OCR
- **GitHub:** https://github.com/deepseek-ai/DeepSeek-OCR
- **API Docs:** https://api-docs.deepseek.com/ (nur Chat)
- **vLLM:** https://docs.vllm.ai/
