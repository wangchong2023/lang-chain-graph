import re
import os

filepath = os.path.join(os.path.dirname(__file__), 'AI_Knowledge_Roadmap.md')
with open(filepath, 'r') as f:
    lines = f.readlines()

# Extract each section (0-indexed)
sec_old_6 = lines[1592:1612]
sec_old_7 = lines[1613:1700]
sec_old_8 = lines[1700:1737]
sec_old_9 = lines[1737:1835]
sec_old_10 = lines[1835:1848]
sec_old_11 = lines[1848:1943]

def renumber_section(lines_list, old_prefix, new_prefix):
    result = []
    for line in lines_list:
        new_line = re.sub(
            r'(#{2,5}\s+)' + re.escape(old_prefix) + r'(\b)',
            r'\g<1>' + new_prefix + r'\2',
            line
        )
        result.append(new_line)
    return result

# Reorder: OLD 11.11 -> NEW 11.6, OLD 11.6 -> NEW 11.7, etc.
new_6 = renumber_section(sec_old_11, '11.11', '11.6')
new_7 = renumber_section(sec_old_6, '11.6', '11.7')
new_8 = renumber_section(sec_old_9, '11.9', '11.8')
new_9 = renumber_section(sec_old_7, '11.7', '11.9')
new_10 = renumber_section(sec_old_8, '11.8', '11.10')
new_11 = renumber_section(sec_old_10, '11.10', '11.11')

before = lines[:1592]
after = lines[1943:]

new_content = before + new_6 + new_7 + new_8 + new_9 + new_10 + new_11 + after

with open(filepath, 'w') as f:
    f.writelines(new_content)

print('Restructuring complete.')
print(f'Total lines before: {len(lines)}')
print(f'Total lines after: {len(new_content)}')

for i, line in enumerate(new_content):
    if re.match(r'^#{2,4}\s+11\.\d+', line):
        print(f'Line {i+1}: {line.rstrip()}')
