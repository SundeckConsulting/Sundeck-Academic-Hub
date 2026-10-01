import json
import time
from deep_translator import GoogleTranslator

with open('extracted_strings.json', 'r', encoding='utf-8') as f:
    texts = json.load(f)

translator = GoogleTranslator(source='en', target='de')

translations = {}
batch = []

print(f"Translating {len(texts)} strings...")

for i, text in enumerate(texts):
    # Skip texts that shouldn't be translated
    if len(text.strip()) < 2 or text.isdigit() or text.startswith('http'):
        continue
    if '{' in text or '}' in text or text.startswith('x-') or text.startswith('@'):
        continue
        
    try:
        # Deep translator handles single string well
        res = translator.translate(text)
        translations[text.replace('\n', ' ').strip()] = res.replace('\n', ' ').strip()
    except Exception as e:
        print(f"Error on {text}: {e}")
        translations[text.replace('\n', ' ').strip()] = text
    
    if (i+1) % 50 == 0:
        print(f"Translated {i+1}/{len(texts)}")
        time.sleep(1) # avoid rate limit

# Also hardcode some specific keys if missed
translations['Student Portal'] = 'Studentenportal'
translations['Teacher Portal'] = 'Lehrerportal'

with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, indent=2, ensure_ascii=False)

print("Done! Created translations.json")
