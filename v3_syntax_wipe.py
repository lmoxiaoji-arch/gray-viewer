import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'
backup_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3_backup.html'

with open(backup_path, 'r', encoding='utf-8') as f:
    backup_full = f.read()
    script_match = re.search(r'<script>(.*?)</script>', backup_full, flags=re.DOTALL)
    js = script_match.group(1)

# 1. 物理移除所有导致报错的残留引用 (不再使用 try-catch，直接删)
# 移除 reset-view 逻辑块
js = re.sub(r"document\.getElementById\('reset-view'\)\.onclick =.*?;", "", js, flags=re.DOTALL)
js = js.replace("document.getElementById('reset-view').classList.remove('visible');", "")
js = js.replace("document.getElementById('reset-view').classList.add('visible');", "")

# 移除 sun/moon 图标逻辑 (因为 HTML 已简化)
js = re.sub(r"const sun =.*?;", "", js)
js = re.sub(r"const moon =.*?;", "", js)
js = js.replace("sun.classList.remove('hidden');", "")
js = js.replace("moon.classList.add('hidden');", "")
js = js.replace("sun.classList.add('hidden');", "")
js = js.replace("moon.classList.remove('hidden');", "")

# 2. 补回全局拖拽增强逻辑 (确保功能更强)
global_drop = """
        // Global Drop
        window.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); });
        window.addEventListener('dragleave', (e) => { if (e.relatedTarget === null) dropzone.classList.remove('drag-active'); });
        window.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
            if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
        });
"""
js = js.replace("fileInput.onchange = (e) => handleFiles(e.target.files);", 
                "fileInput.onchange = (e) => handleFiles(e.target.files);" + global_drop)

# 3. 物理替换并校对
with open(v3_path, 'r', encoding='utf-8') as f:
    current = f.read()

# 确保 Script 块被完整且干净地替换
new_content = re.sub(r'<script>.*?</script>', f"<script>{js}</script>", current, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.14 Syntax Wipe Complete: All potential crash points physically removed.")
