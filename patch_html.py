import re

files = ['student-portal.html', 'academic-admin.html', 'teacher-portal.html']

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add i18n.js script tag in <head>
    if '<script src="/i18n.js"></script>' not in content:
        content = content.replace('</head>', '    <script src="/i18n.js"></script>\n</head>')
    
    # 2. Add lang-toggle-container
    if 'id="lang-toggle-container"' not in content:
        content = re.sub(
            r'(</a>\s*)(<div[^>]*class="[^"]*flex items-center gap-4[^"]*"[^>]*>)',
            r'\1<div class="flex items-center gap-2">\n                    <div id="lang-toggle-container"></div>\n                \2',
            content
        )
        # Close the new div we just opened wrapper
        content = re.sub(
            r'(</button>\s*</div>\s*</div>\s*</div>\s*</nav>)',
            r'\1', # Wait, regex is too brittle.
            content
        )

