import re, os

filepath = os.path.join(os.path.dirname(__file__), 'AI_Knowledge_Roadmap.md')
with open(filepath, 'r') as f:
    content = f.read()

# Find the two occurrences of "### 11.12 企业级选型决策矩阵"
# Everything between the FIRST occurrence of "### 11.8.1 成本控制策略" (the orphaned one,
# which is now not preceded by a ### header) and "### 11.12" should be removed.

# Strategy: find the second (orphaned) block by locating content after the end of 11.11 新
# The new 11.11 ends with "---\n\n" followed by orphaned content.
# We identify the orphaned block as everything between the end of "### 11.11" content 
# and "### 11.12".

# Split on "### 11.12 企业级选型决策矩阵"
parts = content.split("### 11.12 企业级选型决策矩阵")
print(f"Number of '### 11.12' occurrences: {len(parts) - 1}")

if len(parts) == 2:
    before_1112 = parts[0]
    after_1112 = parts[1]
    
    # The orphaned block sits at the end of before_1112.
    # It starts right after the last "---\n\n" that follows our new 11.11 section.
    # Find the last occurrence of "### 11.11 架构心法与风险管理"
    idx_1111 = before_1112.rfind("### 11.11 架构心法与风险管理")
    print(f"Last 11.11 position: {idx_1111}")
    
    if idx_1111 >= 0:
        # Find the end of the 11.11 section: it ends with "---\n\n"
        end_of_1111 = before_1112.find("\n---\n", idx_1111)
        print(f"End of 11.11 at: {end_of_1111}")
        
        if end_of_1111 >= 0:
            # Keep everything up to and including the "---\n"
            clean_before = before_1112[:end_of_1111 + 5]  # +5 for "\n---\n"
            new_content = clean_before + "\n### 11.12 企业级选型决策矩阵" + after_1112
            
            with open(filepath, 'w') as f:
                f.write(new_content)
            print("✅ Cleanup complete!")
            
            # Verify chapter headers
            for m in re.finditer(r'^### 11\.\d+.*', new_content, re.MULTILINE):
                print(f"  {m.group()}")
        else:
            print("Could not find end of 11.11")
    else:
        print("Could not find 11.11 header")
else:
    print(f"Unexpected split: {len(parts)} parts")
