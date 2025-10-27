#!/usr/bin/env python3
"""
OCR Viewer Generator
====================
Erstellt eine Single Page Application zur Visualisierung von OCR-Ergebnissen

Features:
- Side-by-side Ansicht: Original-Bild + OCR-Text
- Navigation zwischen Seiten/Dokumenten
- Highlighting von Problembereichen
- Statistiken und Metriken
- Responsive Design

Usage:
    python generate_viewer.py results/mets_o_szd.151_*/
"""

import json
import sys
from pathlib import Path
from base64 import b64encode

def generate_html(ocr_results: list, output_file: str = "ocr_viewer.html"):
    """
    Generiere HTML Single Page App

    Args:
        ocr_results: Liste von OCR-Result-Dicts
        output_file: Output HTML file
    """

    # HTML Template
    html = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepSeek-OCR Evaluation Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            opacity: 0.9;
            font-size: 1rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .document-selector {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .document-selector h2 {
            margin-bottom: 1rem;
            color: #667eea;
        }

        .doc-buttons {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .doc-btn {
            padding: 0.75rem 1.5rem;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
        }

        .doc-btn:hover {
            background: #667eea;
            color: white;
        }

        .doc-btn.active {
            background: #667eea;
            color: white;
        }

        .metadata {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .metadata h3 {
            color: #667eea;
            margin-bottom: 1rem;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .metadata-item {
            padding: 0.5rem;
        }

        .metadata-label {
            font-weight: bold;
            color: #666;
            font-size: 0.9rem;
        }

        .metadata-value {
            margin-top: 0.25rem;
            font-size: 1.1rem;
        }

        .page-navigation {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .page-nav-btn {
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
        }

        .page-nav-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .page-info {
            font-size: 1.1rem;
            font-weight: bold;
        }

        .comparison-view {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        @media (max-width: 1024px) {
            .comparison-view {
                grid-template-columns: 1fr;
            }
        }

        .image-panel, .text-panel {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .panel-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #667eea;
        }

        .image-container {
            width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: hidden;
        }

        .image-container img {
            width: 100%;
            height: auto;
            display: block;
        }

        .ocr-text {
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            line-height: 1.6;
            padding: 1rem;
            background: #f9f9f9;
            border-radius: 4px;
            border: 1px solid #ddd;
            max-height: 600px;
            overflow-y: auto;
        }

        .stats {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .stats h3 {
            color: #667eea;
            margin-bottom: 1rem;
        }

        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }

        .stat-card {
            padding: 1rem;
            background: #f9f9f9;
            border-radius: 6px;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            margin-top: 0.5rem;
            color: #666;
            font-size: 0.9rem;
        }

        .error-highlight {
            background-color: #fff3cd;
            padding: 0.2rem;
            border-radius: 2px;
        }

        .success-badge {
            background: #28a745;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.9rem;
        }

        .warning-badge {
            background: #ffc107;
            color: #333;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.9rem;
        }

        .error-badge {
            background: #dc3545;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.9rem;
        }

        footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }

        .hide {
            display: none;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>DeepSeek-OCR Evaluation Viewer</h1>
            <p class="subtitle">Interaktive Visualisierung von OCR-Ergebnissen auf Stefan Zweig Dokumenten</p>
        </div>
    </header>

    <div class="container">
        <!-- Document Selector -->
        <div class="document-selector">
            <h2>Dokument auswählen</h2>
            <div class="doc-buttons" id="docButtons"></div>
        </div>

        <!-- Metadata -->
        <div class="metadata" id="metadata"></div>

        <!-- Page Navigation -->
        <div class="page-navigation" id="pageNav">
            <button class="page-nav-btn" id="prevBtn" onclick="prevPage()">← Vorherige</button>
            <div class="page-info" id="pageInfo">Seite 1</div>
            <button class="page-nav-btn" id="nextBtn" onclick="nextPage()">Nächste →</button>
        </div>

        <!-- Comparison View -->
        <div class="comparison-view">
            <div class="image-panel">
                <div class="panel-title">Original-Scan</div>
                <div class="image-container" id="imageContainer">
                    <p style="padding: 2rem; text-align: center; color: #999;">Bild wird geladen...</p>
                </div>
            </div>
            <div class="text-panel">
                <div class="panel-title">OCR-Ergebnis (gefiltert)</div>
                <div class="ocr-text" id="ocrText">Text wird geladen...</div>
            </div>
        </div>

        <!-- Statistics -->
        <div class="stats" id="stats"></div>
    </div>

    <footer>
        <p>Generated by DeepSeek-OCR Pipeline | Model: DeepSeek-OCR (3B) | Hardware: RTX 4080</p>
    </footer>

    <script>
        // Data will be injected here
        const OCR_DATA = """ + json.dumps(ocr_results, ensure_ascii=False) + """;

        let currentDocIndex = 0;
        let currentPageIndex = 0;

        function init() {
            renderDocumentButtons();
            loadDocument(0);
        }

        function renderDocumentButtons() {
            const container = document.getElementById('docButtons');
            container.innerHTML = '';

            OCR_DATA.forEach((doc, index) => {
                const btn = document.createElement('button');
                btn.className = 'doc-btn' + (index === 0 ? ' active' : '');
                btn.textContent = doc.mets_metadata.title;
                btn.onclick = () => loadDocument(index);
                btn.id = `doc-btn-${index}`;
                container.appendChild(btn);
            });
        }

        function loadDocument(docIndex) {
            currentDocIndex = docIndex;
            currentPageIndex = 0;

            // Update button states
            document.querySelectorAll('.doc-btn').forEach((btn, i) => {
                btn.classList.toggle('active', i === docIndex);
            });

            renderMetadata();
            renderPage();
            renderStats();
        }

        function renderMetadata() {
            const doc = OCR_DATA[currentDocIndex];
            const meta = doc.mets_metadata;

            const html = `
                <h3>Dokument-Metadaten</h3>
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <div class="metadata-label">Titel</div>
                        <div class="metadata-value">${meta.title || 'N/A'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Autor</div>
                        <div class="metadata-value">${meta.author || 'N/A'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Signatur</div>
                        <div class="metadata-value">${meta.signature || 'N/A'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Sprache</div>
                        <div class="metadata-value">${meta.language || 'N/A'}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Seiten</div>
                        <div class="metadata-value">${doc.total_pages}</div>
                    </div>
                    <div class="metadata-item">
                        <div class="metadata-label">Status</div>
                        <div class="metadata-value">
                            ${doc.successful === doc.total_pages ?
                                '<span class="success-badge">✓ Vollständig</span>' :
                                '<span class="warning-badge">⚠ Teilweise</span>'}
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('metadata').innerHTML = html;
        }

        function renderPage() {
            const doc = OCR_DATA[currentDocIndex];
            const page = doc.pages[currentPageIndex];

            // Page info
            document.getElementById('pageInfo').textContent = `Seite ${page.page} von ${doc.total_pages}`;

            // Navigation buttons
            document.getElementById('prevBtn').disabled = currentPageIndex === 0;
            document.getElementById('nextBtn').disabled = currentPageIndex === doc.pages.length - 1;

            // Image
            const imagePath = page.image_file;
            // Extract object ID from URN (info:fedora/o:szd.151 → o_szd.151)
            const urn = doc.mets_metadata.urn || '';
            // Get last part after last '/' and replace ':' with '_'
            const objectId = urn.split('/').pop().replace(/:/g, '_'); // o:szd.151 → o_szd.151
            const imageUrl = `data/${objectId}/images/${imagePath}`;

            document.getElementById('imageContainer').innerHTML =
                `<img src="${imageUrl}" alt="Page ${page.page}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\'%3E%3Ctext x=\\'50%%\\' y=\\'50%%\\' text-anchor=\\'middle\\'%3EBild nicht gefunden%3C/text%3E%3C/svg%3E'">`;

            // OCR Text
            let ocrText = page.text || '[Kein Text erkannt]';

            // Highlight known issues
            if (doc.mets_metadata.language === 'de' || doc.mets_metadata.language === 'Deutsch') {
                // Highlight ß→B errors
                ocrText = ocrText.replace(/([A-Z][a-z]*)B([a-z]+)/g, '<span class="error-highlight">$1B$2</span>');
            }

            document.getElementById('ocrText').innerHTML = ocrText;
        }

        function renderStats() {
            const doc = OCR_DATA[currentDocIndex];
            const page = doc.pages[currentPageIndex];

            const totalChars = doc.pages.reduce((sum, p) => sum + (p.cleaned_characters || p.characters || 0), 0);
            const avgTime = doc.pages.reduce((sum, p) => sum + (p.time_seconds || 0), 0) / doc.pages.length;

            const html = `
                <h3>Statistiken</h3>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-value">${page.cleaned_characters || page.characters || 0}</div>
                        <div class="stat-label">Zeichen (diese Seite)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${totalChars}</div>
                        <div class="stat-label">Zeichen (gesamt)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${(page.time_seconds || 0).toFixed(1)}s</div>
                        <div class="stat-label">OCR-Zeit (diese Seite)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${avgTime.toFixed(1)}s</div>
                        <div class="stat-label">⌀ Zeit pro Seite</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${page.filtered || 0}</div>
                        <div class="stat-label">Gefilterte Zeichen</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${doc.successful}/${doc.total_pages}</div>
                        <div class="stat-label">Erfolgsrate</div>
                    </div>
                </div>
            `;

            document.getElementById('stats').innerHTML = html;
        }

        function prevPage() {
            if (currentPageIndex > 0) {
                currentPageIndex--;
                renderPage();
                renderStats();
            }
        }

        function nextPage() {
            const doc = OCR_DATA[currentDocIndex];
            if (currentPageIndex < doc.pages.length - 1) {
                currentPageIndex++;
                renderPage();
                renderStats();
            }
        }

        // Initialize on load
        init();
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ HTML Viewer created: {output_file}")

def load_ocr_result(result_dir: str) -> dict:
    """Lade OCR-Ergebnis aus Verzeichnis"""
    result_path = Path(result_dir)

    # Suche nach _cleaned.json oder .json
    json_files = list(result_path.glob("*_cleaned.json"))
    if not json_files:
        json_files = list(result_path.glob("*_ocr.json"))

    if not json_files:
        raise FileNotFoundError(f"No OCR JSON found in {result_dir}")

    with open(json_files[0], 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # UTF-8 Fix
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print("Usage: python generate_viewer.py <result_dir1> [result_dir2] ...")
        print("Example: python generate_viewer.py results/mets_o_szd.151_*/")
        sys.exit(1)

    result_dirs = sys.argv[1:]

    print("="*60)
    print("GENERATING OCR VIEWER")
    print("="*60)

    ocr_results = []

    for result_dir in result_dirs:
        print(f"Loading: {result_dir}")
        try:
            ocr_data = load_ocr_result(result_dir)
            ocr_results.append(ocr_data)
            print(f"  ✓ {ocr_data['mets_metadata']['title']}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    if not ocr_results:
        print("\n[ERROR] No OCR results loaded")
        sys.exit(1)

    print(f"\nTotal documents: {len(ocr_results)}")
    print()

    # Generate HTML
    generate_html(ocr_results)

    print("="*60)
    print("DONE")
    print("="*60)
    print("\nOpen: ocr_viewer.html in your browser")

if __name__ == "__main__":
    main()
