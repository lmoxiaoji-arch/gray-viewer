import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修正右侧文本
content = content.replace(
    '<div class="text-7xl font-black tracking-tighter shimmer-text mb-4">TECHSUN</div>',
    '<div class="text-7xl font-black tracking-tighter shimmer-text mb-4">TECHSUN STUDIO</div>'
)

# 2. 物理铲除“视图复原” HTML
content = re.sub(r'<button id="reset-view".*?</button>', '', content)

# 3. 修复滑块不更新数字的问题 (补全 JS)
slider_fix = """
        document.getElementById('rate-slider').oninput = (e) => {
            document.getElementById('rate-num').textContent = e.target.value + 'x';
        };
        document.getElementById('bright-slider').oninput = (e) => {
            document.getElementById('bright-num').textContent = e.target.value + 'x';
        };
"""
# 寻找脚本末尾位置注入
content = content.replace("updateUI();", slider_fix + "\n        updateUI();")

# 4. 再次确保 JS 里没有 reset-view 报错
content = re.sub(r"document\.getElementById\('reset-view'\)\.onclick =.*?;", "", content, flags=re.DOTALL)
content = content.replace("document.getElementById('reset-view').classList.remove('visible');", "")
content = content.replace("document.getElementById('reset-view').classList.add('visible');", "")

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.16 Final Alignment Complete: Text corrected, Reset removed, Sliders linked.")
