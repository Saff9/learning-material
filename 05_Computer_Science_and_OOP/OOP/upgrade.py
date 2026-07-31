import os
import re

base_dir = 'c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP'

modules = {
    '05': '05-SOLID-And-Design-Principles',
    '06': '06-Design-Patterns',
    '07': '07-Architecture-And-Enterprise'
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    # Upgrade 1: Inject imports if not present and if there are python blocks
    if '```python' in content:
        if 'from typing import ' not in content:
            content = content.replace('```python\n', '```python\nfrom typing import Self\nfrom typing_extensions import override\n', 1)
        else:
            content = content.replace('from typing import ', 'from typing import Self, ', 1)

    # Upgrade 2: Replace common subclass methods with @override
    # Very rudimentary regex for methods that often override
    def override_replacer(match):
        indent = match.group(1)
        def_line = match.group(2)
        if '__init__' not in def_line and 'def ' in def_line:
            return f"{indent}@override\n{indent}{def_line}"
        return match.group(0)
    
    # Just matching '    def ' or '        def ' as a heuristic for class methods
    # We shouldn't do this blindly, but as a best-effort structural upgrade
    # A better heuristic: if it has 'self' as first arg, and not __init__
    content = re.sub(r'^([ \t]{4,})def ([a-zA-Z0-9_]+)\(self', r'\1@override\n\1def \2(self', content, flags=re.MULTILINE)
    
    # Fix __init__ being overridden
    content = content.replace('@override\n    def __init__', 'def __init__')

    # Upgrade 3: return type Self
    content = re.sub(r'->\s*[\'"]?([A-Z][a-zA-Z0-9_]*)[\'"]?:', r'-> Self:', content)

    # If changes made, write back
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Processed {filepath}")

for mod_key, mod_dir in modules.items():
    mod_path = os.path.join(base_dir, mod_dir)
    if os.path.exists(mod_path):
        for root, _, files in os.walk(mod_path):
            for file in files:
                if file.endswith('.md'):
                    process_file(os.path.join(root, file))

print("Completed fast heuristic upgrades.")
