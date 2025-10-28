#!/usr/bin/env python3
"""
Create DTS Sample from partial results
"""
import json
import sys
import io
from pathlib import Path
import shutil

# UTF-8 Fix für Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Lade DTS Result
with open('results/pdf_DTS_Flechte_20pages_20251027_192318/DTS_Flechte_20pages_ocr.json', 'r', encoding='utf-8') as f:
    dts_data = json.load(f)

# Nur erfolgreiche Seiten
successful_pages = [p for p in dts_data['pages'] if 'text' in p]

print(f'Erfolgreiche Seiten: {len(successful_pages)} von {dts_data["total_pages"]}')

# Erstelle Sample-Struktur
sample = {
    'DTS_Flechte_20pages': {
        'mets_metadata': {
            'title': 'Die Flechten Tirols (Sample: 2 pages)',
            'signature': 'DTS-Flechte',
            'author': 'Dalla Torre, K. W. von; Sarnthein, L. von',
            'language': 'de',
            'owner': 'Botanisches Institut Innsbruck',
            'urn': 'info:fedora/o:DTS_Flechte_20pages'
        },
        'pages': [
            {
                'page': p['page'],
                'file_id': f'page_{p["page"]:03d}',
                'image_file': p['image_file'],
                'text': p['text'],
                'characters': p['characters'],
                'time_seconds': p['time_seconds'],
                'original_characters': p['characters'],
                'cleaned_characters': p['characters'],
                'filtered': 0
            }
            for p in successful_pages
        ],
        'total_pages': len(successful_pages),
        'successful': len(successful_pages),
        'failed': 0,
        'is_sample': True,
        'sample_indices': [0, 1],
        'note': f'Sample: Only {len(successful_pages)} of {dts_data["total_pages"]} pages processed successfully'
    }
}

# Speichere Sample
samples_dir = Path('samples')
with open(samples_dir / 'DTS_Flechte_20pages_sample.json', 'w', encoding='utf-8') as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)

with open(samples_dir / 'DTS_Flechte_20pages_full.json', 'w', encoding='utf-8') as f:
    json.dump(sample, f, ensure_ascii=False, indent=2)

print('[OK] Sample JSON created')

# Kopiere Bilder
images_src = Path('results/pdf_DTS_Flechte_20pages_20251027_192318/images')
images_dest = samples_dir / 'images' / 'o_DTS_Flechte_20pages'
images_dest.mkdir(parents=True, exist_ok=True)

for page in successful_pages:
    src = images_src / page['image_file']
    dst = images_dest / page['image_file']
    if src.exists():
        shutil.copy2(src, dst)
        print(f'[OK] Copied {page["image_file"]}')

print(f'[OK] Images copied to {images_dest}')

# Transcription
trans_path = samples_dir / 'DTS_Flechte_20pages_transcription.txt'
with open(trans_path, 'w', encoding='utf-8') as f:
    f.write('# Die Flechten Tirols (Sample: 2 pages)\n\n')
    f.write('**Language:** de\n')
    f.write(f'**Pages:** {len(successful_pages)} (of {dts_data["total_pages"]} total)\n\n')
    f.write('---\n\n')
    for i, page in enumerate(successful_pages, 1):
        f.write(f'## Page {page["page"]}\n\n')
        f.write(page['text'])
        f.write('\n\n')

print(f'[OK] Transcription created')

# Report
report_path = samples_dir / 'DTS_Flechte_20pages_report.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('# Die Flechten Tirols (Sample)\n\n')
    f.write('**Document ID:** DTS_Flechte_20pages\n')
    f.write('**Language:** German\n')
    f.write(f'**Sample Pages:** {len(successful_pages)} (of {dts_data["total_pages"]} total)\n')
    f.write('**Note:** Only first 2 pages processed successfully\n\n')
    f.write('## Statistics\n\n')
    f.write('| Metric | Value |\n')
    f.write('|--------|-------|\n')

    total_chars = sum(p['characters'] for p in successful_pages)
    total_time = sum(p['time_seconds'] for p in successful_pages)

    f.write(f'| Total Characters | {total_chars:,} |\n')
    f.write(f'| Total Processing Time | {total_time:.2f}s |\n')
    f.write(f'| Average Time per Page | {total_time/len(successful_pages):.2f}s |\n')
    f.write(f'| Pages Processed | {len(successful_pages)}/{dts_data["total_pages"]} |\n')

print(f'[OK] Report created')
print('\n[OK] DTS Sample complete!')
