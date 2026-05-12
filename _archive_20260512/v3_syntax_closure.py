import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修正错误的箭头函数语法，增加花括号包裹
# 找到之前错误的逻辑并替换
content = content.replace(
    "handleFiles(e.target.files); document.getElementById('file-input').value = '';",
    "{ handleFiles(e.target.files); e.target.value = ''; }"
)

# 2. 为了保险，在 handleFiles 函数定义的末尾也强行插入一行重置 (针对某些浏览器的兼容)
# 寻找 handleFiles 函数的闭合处
content = content.replace(
    "img.src = URL.createObjectURL(file);\r\n            });\r\n        }",
    "img.src = URL.createObjectURL(file);\r\n            });\r\n            document.getElementById('file-input').value = '';\r\n        }"
)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.21 Syntax Closure Complete: Duplicate loading logic is now active.")
