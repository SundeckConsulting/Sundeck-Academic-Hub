from bs4 import BeautifulSoup
import re

with open('student-portal.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

texts = set()

# text nodes
for el in soup.find_all(string=True):
    parent = el.parent
    if parent.name not in ['script', 'style', 'title']:
        text = el.strip()
        if text and len(text) > 1 and not text.startswith('{'):
            texts.add(text)

# attributes
for tag in soup.find_all(True):
    for attr, val in tag.attrs.items():
        if isinstance(val, list): val = ' '.join(val)
        if attr in ['placeholder', 'title', 'aria-label'] and val.strip():
            texts.add(val.strip())
        elif attr == 'x-text':
            # look for strings in single quotes
            matches = re.findall(r"'([^']*)'", val)
            for m in matches:
                if len(m) > 1 and not m.startswith('/'):
                    texts.add(m)

print(f"Found {len(texts)} unique text strings.")
print("Sample:", list(texts)[:20])
