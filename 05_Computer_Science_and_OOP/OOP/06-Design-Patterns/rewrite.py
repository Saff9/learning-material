import re

file_path = r'c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP/06-Design-Patterns/Creational-Patterns.md'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add override
text = re.sub(
    r'(from abc import ABC, abstractmethod\n\n)',
    r'\1from typing import override\n\n',
    text,
    count=1
)

text = re.sub(
    r'(class Truck\(Transport\):\n\s+)(def deliver\(self\) -> str:)',
    r'\1@override\n    \2',
    text
)
text = re.sub(
    r'(class Ship\(Transport\):\n\s+)(def deliver\(self\) -> str:)',
    r'\1@override\n    \2',
    text
)
text = re.sub(
    r'(class RoadLogistics\(Logistics\):\n\s+)(def create_transport\(self\) -> Transport:)',
    r'\1@override\n    \2',
    text
)
text = re.sub(
    r'(class SeaLogistics\(Logistics\):\n\s+)(def create_transport\(self\) -> Transport:)',
    r'\1@override\n    \2',
    text
)

text = re.sub(
    r'(from abc import ABC, abstractmethod\n\n\n# ---- Abstract products ----)',
    r'from abc import ABC, abstractmethod\nfrom typing import override\n\n\n# ---- Abstract products ----',
    text
)

for cls_name in ['LightButton', 'LightInput', 'DarkButton', 'DarkInput']:
    text = re.sub(
        f'(class {cls_name}\\([^)]+\\):\\n\\s+)(def render\\(self\\) -> str:)',
        r'\1@override\n    \2',
        text
    )

for cls_name in ['LightUIFactory', 'DarkUIFactory']:
    text = re.sub(
        f'(class {cls_name}\\(UIFactory\\):\\n\\s+)(def create_button\\(self\\) -> Button:)',
        r'\1@override\n    \2',
        text
    )
    text = re.sub(
        f'(class {cls_name}\\(UIFactory\\):\\n\\s+@override\\n\\s+def create_button\\(self\\) -> Button:\\n\\s+return [^\\n]+\\n\\n\\s+)(def create_input\\(self\\) -> Input:)',
        r'\1@override\n    \2',
        text
    )

# 2. Add Self
text = re.sub(
    r'(import json\n\n)',
    r'import json\nfrom typing import Self\n\n',
    text
)
text = re.sub(r'-> "Point":', r'-> Self:', text)

text = re.sub(
    r'(from dataclasses import dataclass, field\n\n)',
    r'from dataclasses import dataclass, field\nfrom typing import Self\n\n',
    text,
    count=1
)
text = re.sub(r'-> "PizzaBuilder":', r'-> Self:', text)

text = re.sub(
    r'(class QueryBuilder:\n)',
    r'from typing import Self\n\n\1',
    text
)
text = re.sub(r'-> "QueryBuilder":', r'-> Self:', text)

text = re.sub(
    r'(class HTMLBuilder:\n)',
    r'from typing import Self\n\n\1',
    text
)
text = re.sub(r'-> "HTMLBuilder":', r'-> Self:', text)

text = re.sub(
    r'(from dataclasses import dataclass, replace\n\n)',
    r'from dataclasses import dataclass, replace\nfrom typing import Self\n\n',
    text
)

text = re.sub(
    r'(import copy\n\n)',
    r'import copy\nfrom typing import Self\n\n',
    text
)

text = re.sub(r'(def __copy__\(self\))(:)', r'\1 -> Self\2', text)
text = re.sub(r'(def __deepcopy__\(self, memo\))(:)', r'\1 -> Self\2', text)

# 3. match/case
old_db_driver = """def get_connection_factory(driver: str):
    if driver == "sqlite":
        import sqlite3
        return sqlite3.connect
    elif driver == "postgres":
        import psycopg2
        return psycopg2.connect
    else:
        raise ValueError(driver)"""

new_db_driver = """def get_connection_factory(driver: str):
    match driver:
        case "sqlite":
            import sqlite3
            return sqlite3.connect
        case "postgres":
            import psycopg2
            return psycopg2.connect
        case _:
            raise ValueError(driver)"""

text = text.replace(old_db_driver, new_db_driver)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
