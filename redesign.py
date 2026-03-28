import re

path = r'c:\julian\proyectos\tradingMico\templates\strategy_analyzer.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Caso general: ind-value con jinja bullish/bearish -> ind-badge ind-ok/ind-nok
# Hay múltiples variantes, la más común es:
# "ind-value {% if COND %}bullish{% else %}bearish{% endif %}"
# -> "ind-badge {% if COND %}ind-ok{% else %}ind-nok{% endif %}"

# Variante 1: bullish/else bearish
html = re.sub(
    r'class="ind-value (\{%[^"]+%\})\s*bullish(\{%[^"]+%\})\s*bearish(\{%[^"]+%\})"',
    r'class="ind-badge \1ind-ok\2ind-nok\3"',
    html
)

# Variante 2: bullish/elif bearish/else neutral (triple)
html = re.sub(
    r'class="ind-value (\{%[^"]+%\})\s*bullish(\{%[^"]+%\})\s*bearish(\{%[^"]+%\})\s*neutral(\{%[^"]+%\})"',
    r'class="ind-badge \1ind-ok\2ind-nok\3ind-neutral\4"',
    html
)

# Variante 3: bearish/else neutral
html = re.sub(
    r'class="ind-value (\{%[^"]+%\})\s*bearish(\{%[^"]+%\})\s*neutral(\{%[^"]+%\})"',
    r'class="ind-badge \1ind-nok\2ind-neutral\3"',
    html
)

# Variante 4: bullish/else neutral  
html = re.sub(
    r'class="ind-value (\{%[^"]+%\})\s*bullish(\{%[^"]+%\})\s*neutral(\{%[^"]+%\})"',
    r'class="ind-badge \1ind-ok\2ind-neutral\3"',
    html
)

# Variante 5: bearish/else bullish
html = re.sub(
    r'class="ind-value (\{%[^"]+%\})\s*bearish(\{%[^"]+%\})\s*bullish(\{%[^"]+%\})"',
    r'class="ind-badge \1ind-nok\2ind-ok\3"',
    html
)

# Caso plain (sin clase): ind-value"
html = re.sub(r'class="ind-value"', 'class="ind-badge ind-neutral"', html)

# Limpiar spans internos de color que ya no son necesarios
html = re.sub(r'<span class="(bullish|bearish|neutral)">(.*?)</span>', r'\2', html)

count_remaining = html.count('ind-value')
count_badges = html.count('ind-badge')
print(f"ind-value restantes: {count_remaining}")
print(f"ind-badge aplicados: {count_badges}")

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Completado.")
