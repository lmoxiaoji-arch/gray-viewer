import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 移除按钮 HTML
content = re.sub(r'<button id="reset-view".*?</button>', '', content)

# 2. 移除 CSS
content = re.sub(r'#reset-view \{.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'#reset-view\.visible \{.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'#reset-view:hover \{.*?\}', '', content, flags=re.DOTALL)

# 3. 移除 JS 逻辑
# 匹配 document.getElementById('reset-view').onclick = () => { ... };
content = re.sub(r"document\.getElementById\('reset-view'\)\.onclick =.*?;", '', content, flags=re.DOTALL)
# 移除 updateUI 中对 reset-view 的操作
content = content.replace("document.getElementById('reset-view').classList.remove('visible');", "")
content = content.replace("document.getElementById('reset-view').classList.add('visible');", "")

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Reset View functionality removed successfully.")
