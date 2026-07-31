import os
import re

def modernize_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all python code blocks
    pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    
    def replace_typing(match):
        code = match.group(1)
        
        # Replace typing module imports (basic)
        code = re.sub(r'from typing import .*?List.*?\n', '', code)
        code = re.sub(r'from typing import .*?Dict.*?\n', '', code)
        
        # Replace old typing with new Python 3.12+ typing
        code = code.replace('List[', 'list[')
        code = code.replace('Dict[', 'dict[')
        code = code.replace('Tuple[', 'tuple[')
        code = code.replace('Set[', 'set[')
        
        # Replace Union[X, Y] with X | Y (heuristic)
        code = re.sub(r'Union\[(.*?), (.*?)\]', r'\1 | \2', code)
        
        # Replace Optional[X] with X | None
        code = re.sub(r'Optional\[(.*?)\]', r'\1 | None', code)
        
        # If there are no docstrings for defs, we could try to inject them (very heuristic)
        # But for safety, we mostly do typing modernization.
        
        return f'```python{code}```'

    new_content = pattern.sub(replace_typing, content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Modernized: {filepath}")

def main(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                modernize_markdown_file(filepath)

if __name__ == "__main__":
    main(".")
