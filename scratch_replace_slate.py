import os

def replace_in_files(directory):
    replacements = {
        'text-slate-100': 'text-text-primary',
        'text-slate-600': 'text-text-secondary',
        'placeholder-slate-600': 'placeholder-[#888]',
        'border-slate-600/50': 'border-border-primary/50',
        'border-slate-900': 'border-border-primary',
        'translate-x-': 'translate-x-' # Just to avoid replacing translate strings
    }
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts', '.css')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old, new in replacements.items():
                    content = content.replace(old, new)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filepath}")

replace_in_files(r"c:\sabari\Lyra\frontend\src")
