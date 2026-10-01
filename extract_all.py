from bs4 import BeautifulSoup, NavigableString
import json
import re

files = ['student-portal.html', 'academic-admin.html', 'teacher-portal.html']
texts = set()

def extract_strings(val):
    matches = re.findall(r"'([^']*)'", val)
    return [m for m in matches if len(m.strip()) > 1 and not m.startswith('/')]

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    for el in soup.find_all(string=True):
        parent = el.parent
        if parent.name not in ['script', 'style', 'title', 'template']:
            text = el.strip()
            if text and len(text) > 1 and not text.startswith('{') and not text.startswith('alpine'):
                texts.add(text)
                
    for tag in soup.find_all(True):
        for attr, val in tag.attrs.items():
            if isinstance(val, list): val = ' '.join(val)
            if attr in ['placeholder', 'title', 'aria-label'] and val.strip():
                texts.add(val.strip())
            elif attr.startswith('x-') or attr.startswith('@') or attr.startswith(':'):
                for s in extract_strings(val):
                    texts.add(s)

# Also extract from embedded script tags
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    script_matches = re.findall(r"<script.*?>([\s\S]*?)</script>", content)
    for s in script_matches:
        for m in extract_strings(s):
            texts.add(m)

texts = list(texts)
texts.sort()

with open('extracted_strings.json', 'w', encoding='utf-8') as f:
    json.dump(texts, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(texts)} unique strings to extracted_strings.json")
