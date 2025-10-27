#!/usr/bin/env python3
"""
Simplified OCR Viewer - Focus on Image vs Text comparison
"""

import io, sys
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import os
from pathlib import Path

def load_ocr_results(results_file):
    with open(results_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_simple_viewer(documents, output_file='index.html'):
    docs_json = json.dumps(documents, ensure_ascii=False, indent=2)

    html_content = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR Analysis Viewer</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-600: #4b5563;
            --gray-800: #1f2937;
            --white: #ffffff;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --radius: 0.5rem;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: var(--gray-50);
            color: var(--gray-800);
            line-height: 1.6;
        }}

        header {{
            background: var(--white);
            border-bottom: 3px solid var(--primary);
            padding: 1.5rem 2rem;
            box-shadow: var(--shadow-md);
        }}

        h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: 0.25rem;
        }}

        .subtitle {{
            color: var(--gray-600);
            font-size: 0.95rem;
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Document Selector - Compact */
        .doc-selector {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--gray-200);
        }}

        .doc-selector-title {{
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }}

        .doc-buttons {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .doc-btn {{
            padding: 0.625rem 1rem;
            border: 2px solid var(--gray-300);
            background: var(--white);
            border-radius: var(--radius);
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
            font-weight: 500;
        }}

        .doc-btn:hover {{
            border-color: var(--primary);
            transform: translateY(-1px);
        }}

        .doc-btn.active {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        .doc-btn-meta {{
            font-size: 0.75rem;
            opacity: 0.8;
            margin-top: 0.25rem;
        }}

        /* Combined Info Bar - Metadata + Page Nav */
        .info-bar {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .info-meta {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}

        .info-item {{
            display: flex;
            flex-direction: column;
        }}

        .info-label {{
            font-size: 0.75rem;
            color: var(--gray-600);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}

        .info-value {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--gray-800);
            margin-top: 0.125rem;
        }}

        .page-nav {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}

        .page-nav-btn {{
            padding: 0.5rem 1rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: var(--radius);
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 600;
            transition: all 0.2s;
        }}

        .page-nav-btn:hover:not(:disabled) {{
            background: var(--primary-dark);
        }}

        .page-nav-btn:disabled {{
            background: var(--gray-300);
            cursor: not-allowed;
            opacity: 0.6;
        }}

        .page-info {{
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
            background: var(--gray-100);
            border-radius: var(--radius);
        }}

        /* Thumbnail Strip - Horizontal only */
        .thumbnail-strip {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 1rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--gray-200);
            overflow-x: auto;
        }}

        .thumbnails {{
            display: flex;
            gap: 0.75rem;
        }}

        .thumbnail {{
            flex-shrink: 0;
            width: 80px;
            height: 110px;
            border: 2px solid var(--gray-300);
            border-radius: 0.375rem;
            cursor: pointer;
            overflow: hidden;
            transition: all 0.2s;
            position: relative;
        }}

        .thumbnail:hover {{
            border-color: var(--primary);
            transform: scale(1.05);
        }}

        .thumbnail.active {{
            border-color: var(--primary);
            border-width: 3px;
            box-shadow: var(--shadow-md);
        }}

        .thumbnail img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .thumbnail-label {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(37, 99, 235, 0.9);
            color: white;
            padding: 0.25rem;
            text-align: center;
            font-size: 0.7rem;
            font-weight: 600;
        }}

        /* Main Comparison - Side by Side */
        .comparison {{
            display: grid;
            grid-template-columns: 1.3fr 0.7fr;
            gap: 1.5rem;
        }}

        @media (max-width: 1200px) {{
            .comparison {{
                grid-template-columns: 1fr;
            }}
        }}

        .panel {{
            background: var(--white);
            border-radius: var(--radius);
            box-shadow: var(--shadow-md);
            overflow: hidden;
            border: 1px solid var(--gray-200);
            height: 700px;
            display: flex;
            flex-direction: column;
        }}

        .panel-header {{
            padding: 1rem 1.25rem;
            background: var(--gray-100);
            border-bottom: 2px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}

        .panel-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--gray-800);
        }}

        .panel-actions {{
            display: flex;
            gap: 0.375rem;
        }}

        .icon-btn {{
            background: var(--white);
            border: 1px solid var(--gray-300);
            color: var(--gray-600);
            cursor: pointer;
            padding: 0.375rem 0.625rem;
            border-radius: 0.375rem;
            transition: all 0.2s;
            font-size: 1rem;
        }}

        .icon-btn:hover {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        .panel-content {{
            flex: 1;
            overflow: hidden;
            position: relative;
        }}

        /* Image Viewer */
        .image-viewer {{
            width: 100%;
            height: 100%;
            background: var(--gray-50);
            overflow: hidden;
            cursor: grab;
            position: relative;
        }}

        .image-viewer:active {{
            cursor: grabbing;
        }}

        .image-viewer img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.2s;
            user-select: none;
        }}

        .zoom-controls {{
            position: absolute;
            bottom: 1rem;
            right: 1rem;
            display: flex;
            gap: 0.375rem;
            background: rgba(255, 255, 255, 0.95);
            border-radius: var(--radius);
            padding: 0.5rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--gray-200);
        }}

        .zoom-btn {{
            background: var(--gray-100);
            border: 1px solid var(--gray-300);
            color: var(--gray-800);
            cursor: pointer;
            padding: 0.375rem 0.75rem;
            border-radius: 0.375rem;
            font-weight: 600;
            transition: all 0.2s;
            min-width: 2.5rem;
        }}

        .zoom-btn:hover {{
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }}

        /* OCR Text */
        .ocr-text {{
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            white-space: pre-wrap;
            line-height: 1.8;
            padding: 1.5rem;
            background: var(--gray-50);
            height: 100%;
            overflow-y: auto;
            font-size: 0.9rem;
        }}

        .empty-page {{
            text-align: center;
            padding: 3rem 1.5rem;
            color: var(--gray-600);
            font-style: italic;
        }}

        /* Toast */
        .toast {{
            position: fixed;
            top: 5.5rem;
            right: 2rem;
            background: #059669;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s;
            font-weight: 600;
        }}

        .toast.show {{
            transform: translateX(0);
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .info-bar {{ flex-direction: column; align-items: flex-start; }}
            .panel {{ height: 500px; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>OCR Analysis Viewer</h1>
        <p class="subtitle">Document Analysis & Text Recognition</p>
    </header>

    <div class="container">
        <!-- Document Selector -->
        <div class="doc-selector">
            <div class="doc-selector-title">Select Document</div>
            <div class="doc-buttons" id="docButtons"></div>
        </div>

        <!-- Combined Info Bar -->
        <div class="info-bar" id="infoBar" style="display: none;">
            <div class="info-meta" id="infoMeta"></div>
            <div class="page-nav">
                <button class="page-nav-btn" onclick="previousPage()" id="prevBtn">←</button>
                <div class="page-info" id="pageInfo"></div>
                <button class="page-nav-btn" onclick="nextPage()" id="nextBtn">→</button>
            </div>
        </div>

        <!-- Thumbnail Strip -->
        <div class="thumbnail-strip" id="thumbnailStrip" style="display: none;">
            <div class="thumbnails" id="thumbnails"></div>
        </div>

        <!-- Main Comparison -->
        <div class="comparison" id="comparison" style="display: none;">
            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">Original Image</h3>
                    <div class="panel-actions">
                        <button class="icon-btn" onclick="resetZoom()" title="Reset">↺</button>
                        <button class="icon-btn" onclick="downloadImage()" title="Download">↓</button>
                    </div>
                </div>
                <div class="panel-content">
                    <div class="image-viewer" id="imageViewer">
                        <img id="pageImage" alt="Page" draggable="false">
                        <div class="zoom-controls">
                            <button class="zoom-btn" onclick="zoomOut()">−</button>
                            <button class="zoom-btn" onclick="zoomReset()"><span id="zoomLevel">100%</span></button>
                            <button class="zoom-btn" onclick="zoomIn()">+</button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <h3 class="panel-title">OCR Result</h3>
                    <div class="panel-actions">
                        <button class="icon-btn" onclick="copyText()" title="Copy">⎘</button>
                        <button class="icon-btn" onclick="downloadText()" title="Download">↓</button>
                    </div>
                </div>
                <div class="panel-content">
                    <div class="ocr-text" id="ocrText">
                        <div class="empty-page">Select a document to view results</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        const DOCUMENTS = {docs_json};
        let currentDoc = null;
        let currentPageIndex = 0;
        let zoomLevel = 1;
        let isDragging = false;
        let startX, startY, translateX = 0, translateY = 0;

        window.addEventListener('DOMContentLoaded', () => {{
            initializeDocumentButtons();
            initializeKeyboardShortcuts();
            initializeImageViewer();
        }});

        function initializeDocumentButtons() {{
            const container = document.getElementById('docButtons');
            Object.entries(DOCUMENTS).forEach(([docId, doc]) => {{
                const btn = document.createElement('button');
                btn.className = 'doc-btn';
                btn.onclick = () => selectDocument(docId);

                const meta = doc.metadata || doc.mets_metadata || {{}};
                const pageCount = doc.pages ? doc.pages.length : 0;

                const totalPages = doc.total_pages || pageCount;
                const sampleText = doc.is_sample ? ` (${{pageCount}} samples)` : '';

                btn.innerHTML = `
                    <div>${{meta.title || docId}}</div>
                    <div class="doc-btn-meta">${{meta.author || ''}} • ${{meta.language ? meta.language.toUpperCase() : ''}} • ${{totalPages}} pages${{sampleText}}</div>
                `;
                container.appendChild(btn);
            }});
        }}

        function selectDocument(docId) {{
            currentDoc = DOCUMENTS[docId];
            currentPageIndex = 0;

            document.querySelectorAll('.doc-btn').forEach((btn, idx) => {{
                btn.classList.toggle('active', Object.keys(DOCUMENTS)[idx] === docId);
            }});

            displayInfoBar();
            createThumbnails();
            displayPage();

            document.getElementById('infoBar').style.display = 'flex';
            document.getElementById('thumbnailStrip').style.display = 'block';
            document.getElementById('comparison').style.display = 'grid';
        }}

        function displayInfoBar() {{
            const container = document.getElementById('infoMeta');
            const meta = currentDoc.metadata || currentDoc.mets_metadata || {{}};

            let html = '';
            if (meta.title) html += `<div class="info-item"><span class="info-label">Title</span><span class="info-value">${{meta.title}}</span></div>`;
            if (meta.author) html += `<div class="info-item"><span class="info-label">Author</span><span class="info-value">${{meta.author}}</span></div>`;
            if (meta.language) html += `<div class="info-item"><span class="info-label">Language</span><span class="info-value">${{meta.language.toUpperCase()}}</span></div>`;
            html += `<div class="info-item"><span class="info-label">Pages</span><span class="info-value">${{currentDoc.pages ? currentDoc.pages.length : 0}}</span></div>`;

            container.innerHTML = html;
        }}

        function createThumbnails() {{
            const container = document.getElementById('thumbnails');
            container.innerHTML = '';

            if (!currentDoc.pages) return;

            currentDoc.pages.forEach((page, idx) => {{
                const thumb = document.createElement('div');
                thumb.className = 'thumbnail';
                thumb.onclick = () => {{
                    currentPageIndex = idx;
                    displayPage();
                }};

                const img = document.createElement('img');
                img.src = getImagePath(page);
                img.alt = `Page ${{idx + 1}}`;

                const label = document.createElement('div');
                label.className = 'thumbnail-label';
                label.textContent = idx + 1;

                thumb.appendChild(img);
                thumb.appendChild(label);
                container.appendChild(thumb);
            }});

            updateThumbnailActive();
        }}

        function getImagePath(page) {{
            // For samples: use samples/images/ path
            if (currentDoc.is_sample && page.image_file) {{
                const urn = currentDoc.mets_metadata?.urn || '';
                if (urn) {{
                    const objectId = urn.split('/').pop().replace(/:/g, '_');
                    return `samples/images/${{objectId}}/${{page.image_file}}`;
                }}
            }}

            // Standard paths
            if (page.image_path) return page.image_path;
            if (page.image) return page.image;
            if (page.image_file && currentDoc.mets_metadata) {{
                const urn = currentDoc.mets_metadata.urn;
                if (urn) {{
                    const objectId = urn.split('/').pop().replace(/:/g, '_');
                    return `data/${{objectId}}/images/${{page.image_file}}`;
                }}
            }}
            if (page.file) return page.file;
            return '';
        }}

        function updateThumbnailActive() {{
            document.querySelectorAll('.thumbnail').forEach((thumb, idx) => {{
                thumb.classList.toggle('active', idx === currentPageIndex);
            }});
        }}

        function displayPage() {{
            if (!currentDoc.pages || !currentDoc.pages[currentPageIndex]) return;

            const page = currentDoc.pages[currentPageIndex];
            document.getElementById('pageImage').src = getImagePath(page);

            const textContainer = document.getElementById('ocrText');
            if (page.filtered_text && page.filtered_text.trim()) {{
                textContainer.textContent = page.filtered_text;
                textContainer.classList.remove('empty-page');
            }} else if (page.text && page.text.trim()) {{
                textContainer.textContent = page.text;
                textContainer.classList.remove('empty-page');
            }} else {{
                textContainer.innerHTML = '<div class="empty-page">[EMPTY PAGE]</div>';
                textContainer.classList.add('empty-page');
            }}

            updateNavigation();
            updateThumbnailActive();
            resetZoom();
        }}

        function updateNavigation() {{
            const pageCount = currentDoc.pages ? currentDoc.pages.length : 0;
            document.getElementById('prevBtn').disabled = currentPageIndex === 0;
            document.getElementById('nextBtn').disabled = currentPageIndex === pageCount - 1;
            document.getElementById('pageInfo').textContent = `${{currentPageIndex + 1}} / ${{pageCount}}`;
        }}

        function previousPage() {{
            if (currentPageIndex > 0) {{
                currentPageIndex--;
                displayPage();
            }}
        }}

        function nextPage() {{
            const pageCount = currentDoc.pages ? currentDoc.pages.length : 0;
            if (currentPageIndex < pageCount - 1) {{
                currentPageIndex++;
                displayPage();
            }}
        }}

        function initializeImageViewer() {{
            const viewer = document.getElementById('imageViewer');
            viewer.addEventListener('mousedown', (e) => {{
                if (zoomLevel > 1) {{
                    isDragging = true;
                    startX = e.clientX - translateX;
                    startY = e.clientY - translateY;
                }}
            }});
            viewer.addEventListener('mousemove', (e) => {{
                if (isDragging) {{
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    updateImageTransform();
                }}
            }});
            viewer.addEventListener('mouseup', () => {{ isDragging = false; }});
            viewer.addEventListener('mouseleave', () => {{ isDragging = false; }});
            viewer.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const delta = e.deltaY > 0 ? -0.1 : 0.1;
                zoomLevel = Math.max(0.5, Math.min(5, zoomLevel + delta));
                updateImageTransform();
                updateZoomDisplay();
            }});
        }}

        function updateImageTransform() {{
            const img = document.getElementById('pageImage');
            img.style.transform = `scale(${{zoomLevel}}) translate(${{translateX / zoomLevel}}px, ${{translateY / zoomLevel}}px)`;
        }}

        function updateZoomDisplay() {{
            document.getElementById('zoomLevel').textContent = Math.round(zoomLevel * 100) + '%';
        }}

        function zoomIn() {{
            zoomLevel = Math.min(5, zoomLevel + 0.25);
            updateImageTransform();
            updateZoomDisplay();
        }}

        function zoomOut() {{
            zoomLevel = Math.max(0.5, zoomLevel - 0.25);
            updateImageTransform();
            updateZoomDisplay();
        }}

        function zoomReset() {{
            zoomLevel = 1;
            updateImageTransform();
            updateZoomDisplay();
        }}

        function resetZoom() {{
            zoomLevel = 1;
            translateX = 0;
            translateY = 0;
            updateImageTransform();
            updateZoomDisplay();
        }}

        function copyText() {{
            const text = document.getElementById('ocrText').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                showToast('✓ Text copied');
            }});
        }}

        function downloadText() {{
            const text = document.getElementById('ocrText').textContent;
            const blob = new Blob([text], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `page_${{currentPageIndex + 1}}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            showToast('✓ Text downloaded');
        }}

        function downloadImage() {{
            const img = document.getElementById('pageImage');
            const a = document.createElement('a');
            a.href = img.src;
            a.download = `page_${{currentPageIndex + 1}}.jpg`;
            a.click();
            showToast('✓ Image downloaded');
        }}

        function initializeKeyboardShortcuts() {{
            document.addEventListener('keydown', (e) => {{
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
                switch(e.key) {{
                    case 'ArrowLeft': e.preventDefault(); previousPage(); break;
                    case 'ArrowRight': e.preventDefault(); nextPage(); break;
                    case '+': case '=': e.preventDefault(); zoomIn(); break;
                    case '-': e.preventDefault(); zoomOut(); break;
                    case '0': e.preventDefault(); zoomReset(); break;
                }}
            }});
        }}

        function showToast(message) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }}
    </script>
</body>
</html>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Simplified viewer generated: {output_file}")
    return output_file

def main():
    # Try to load from samples first (for GitHub Pages)
    samples_file = Path('samples/samples.json')

    if samples_file.exists():
        print("✓ Loading from samples/ (GitHub Pages mode)")
        try:
            documents = load_ocr_results(samples_file)
            print(f"✓ Loaded {len(documents)} documents from samples")
            for doc_id, data in documents.items():
                total = data.get('total_pages', len(data.get('pages', [])))
                print(f"  - {doc_id}: {len(data.get('pages', []))} sample pages (of {total} total)")
        except Exception as e:
            print(f"⚠ Error loading samples: {e}")
            documents = {}
    else:
        # Fallback to full results
        print("✓ Loading from results/ (full mode)")
        results_dir = Path('results')
        documents = {}

        if results_dir.exists():
            for result_file in results_dir.glob('*/*_ocr_cleaned.json'):
                doc_id = result_file.stem.replace('_ocr_cleaned', '')
                try:
                    data = load_ocr_results(result_file)
                    documents[doc_id] = data
                    print(f"✓ Loaded: {doc_id} ({len(data.get('pages', []))} pages)")
                except Exception as e:
                    print(f"⚠ Error: {e}")

    if documents:
        generate_simple_viewer(documents)
        print(f"\n🎉 Viewer ready: index.html")
    else:
        print("❌ No OCR results found")

if __name__ == '__main__':
    main()
