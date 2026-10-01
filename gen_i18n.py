import json
import time

while True:
    try:
        with open('translations.json', 'r', encoding='utf-8') as f:
            trans = f.read()
            if "Studentenportal" in trans:
                break
    except:
        pass
    print("Waiting for translations...")
    time.sleep(5)

print("Translations loaded, generating i18n.js...")

js_content = f"""
(function() {{
    window.i18n = {{
        lang: localStorage.getItem('app_lang') || 'de',
        dict: {{
            de: {trans}
        }},
        t(str) {{
            if (!str) return str;
            if (this.lang === 'en') return str;
            const normalized = str.trim().replace(/\s+/g, ' ');
            return this.dict.de[normalized] || str;
        }},
        setLang(l) {{
            this.lang = l;
            localStorage.setItem('app_lang', l);
            window.location.reload();
        }}
    }};

    window.t = (str) => window.i18n.t(str);

    document.addEventListener('DOMContentLoaded', () => {{
        setupLanguageToggle();
        
        if (window.i18n.lang === 'en') return;

        function translateNode(node) {{
            if (node.nodeType === Node.TEXT_NODE) {{
                const text = node.textContent;
                if (text.trim().length > 1) {{
                    const translated = window.i18n.t(text);
                    if (translated !== text.trim().replace(/\s+/g, ' ')) {{
                        const newText = text.replace(text.trim(), translated);
                        if (newText !== text) {{
                            node.textContent = newText;
                        }}
                    }}
                }}
            }} else if (node.nodeType === Node.ELEMENT_NODE) {{
                if (['SCRIPT', 'STYLE'].includes(node.tagName)) return;
                
                ['placeholder', 'title', 'aria-label'].forEach(attr => {{
                    if (node.hasAttribute(attr)) {{
                        const val = node.getAttribute(attr);
                        if (val && val.trim().length > 1) {{
                            const translated = window.i18n.t(val);
                            if (translated !== val.trim().replace(/\s+/g, ' ')) {{
                                node.setAttribute(attr, translated);
                            }}
                        }}
                    }}
                }});
                
                for (let child of node.childNodes) {{
                    translateNode(child);
                }}
            }}
        }}

        translateNode(document.body);

        const observer = new MutationObserver((mutations) => {{
            let shouldDisconnect = false;
            for (let mutation of mutations) {{
                if (mutation.type === 'childList') {{
                    for (let node of mutation.addedNodes) {{
                        shouldDisconnect = true;
                        translateNode(node);
                    }}
                }} else if (mutation.type === 'characterData') {{
                    const text = mutation.target.textContent;
                    if (text.trim().length > 1) {{
                        const translated = window.i18n.t(text);
                        if (translated !== text.trim().replace(/\s+/g, ' ')) {{
                            shouldDisconnect = true;
                            mutation.target.textContent = text.replace(text.trim(), translated);
                        }}
                    }}
                }} else if (mutation.type === 'attributes') {{
                    const attr = mutation.attributeName;
                    const val = mutation.target.getAttribute(attr);
                    if (val && val.trim().length > 1) {{
                        const translated = window.i18n.t(val);
                        if (translated !== val.trim().replace(/\s+/g, ' ')) {{
                            shouldDisconnect = true;
                            mutation.target.setAttribute(attr, translated);
                        }}
                    }}
                }}
            }}
            
            if (shouldDisconnect) {{
                observer.disconnect();
                setTimeout(() => {{
                    observer.observe(document.body, {{ childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['placeholder', 'aria-label', 'title'] }});
                }}, 0);
            }}
        }});
        
        observer.observe(document.body, {{ childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['placeholder', 'aria-label', 'title'] }});
    }});

    function setupLanguageToggle() {{
        // We'll look for an element with id="lang-toggle-container"
        const toggleContainer = document.getElementById('lang-toggle-container');
        if (!toggleContainer) return;

        toggleContainer.innerHTML = \
            <div class="flex items-center gap-1 bg-slate-100 rounded-lg p-1 border border-slate-200 shadow-sm ml-4 h-8">
                <button onclick="window.i18n.setLang('de')" class="px-2.5 py-0.5 text-xs font-medium rounded-md transition-all \">DE</button>
                <button onclick="window.i18n.setLang('en')" class="px-2.5 py-0.5 text-xs font-medium rounded-md transition-all \">EN</button>
            </div>
        \;
    }}
}})();
"""

with open('i18n.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
    
print("Generated i18n.js")
