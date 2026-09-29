import os, re
js_dir = r'd:\3rd sem created files\AIML PROJECT\ecommerce_app\static\js'

for f in os.listdir(js_dir):
    if not f.endswith('.js'): continue
    path = os.path.join(js_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    print(f"{f}:")
    for i, line in enumerate(content.split('\n')):
        if '$$?' in line or '$$₹' in line or '$$' in line or '₹' in line:
            print(f"  {i+1}: {line.strip()}")
