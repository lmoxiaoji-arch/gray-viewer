import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修正索引变量名 (从 realIdx 改回 i)
content = content.replace("e.dataTransfer.setData('text/plain', realIdx);", "e.dataTransfer.setData('text/plain', i);")
content = content.replace("const toIdx = realIdx;", "const toIdx = i;")

# 2. 确保 draggable 属性存在
if "div.draggable = true;" not in content:
    content = content.replace("const div = document.createElement('div');", "const div = document.createElement('div'); div.draggable = true;")

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.23 Variable Alignment Complete: Dragging should be functional now.")
