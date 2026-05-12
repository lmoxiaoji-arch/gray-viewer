import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'
backup_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3_backup.html'

with open(backup_path, 'r', encoding='utf-8') as f:
    backup_js = re.search(r'<script>(.*?)</script>', f.read(), flags=re.DOTALL).group(1)

# 1. 物理删除导致崩溃的“死代码”
backup_js = re.sub(r"document\.getElementById\('reset-view'\)\.onclick =.*?;", "", backup_js, flags=re.DOTALL)
backup_js = backup_js.replace("document.getElementById('reset-view').classList.remove('visible');", "")
backup_js = backup_js.replace("document.getElementById('reset-view').classList.add('visible');", "")
backup_js = re.sub(r"const sun =.*?;", "", backup_js)
backup_js = re.sub(r"const moon =.*?;", "", backup_js)
backup_js = backup_js.replace("sun.classList.remove('hidden');", "").replace("moon.classList.add('hidden');", "")
backup_js = backup_js.replace("sun.classList.add('hidden');", "").replace("moon.classList.remove('hidden');", "")

# 2. 修复“重复载入”问题
backup_js = backup_js.replace("handleFiles(e.target.files);", "handleFiles(e.target.files); e.target.value = '';")

# 3. 补齐滑块数字更新逻辑 (原始备份可能没有这个)
slider_update = """
        document.getElementById('rate-slider').oninput = (e) => { document.getElementById('rate-num').textContent = e.target.value + 'x'; };
        document.getElementById('bright-slider').oninput = (e) => { document.getElementById('bright-num').textContent = e.target.value + 'x'; };
"""
backup_js = backup_js.replace("updateUI();", "updateUI();" + slider_update, 1) # 只在初始化时加一次

# 4. 补齐全局拖拽逻辑
global_drop = """
        window.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); });
        window.addEventListener('dragleave', (e) => { if (e.relatedTarget === null) dropzone.classList.remove('drag-active'); });
        window.addEventListener('drop', (e) => { e.preventDefault(); dropzone.classList.remove('drag-active'); handleFiles(e.dataTransfer.files); });
"""
backup_js = backup_js.replace("handleFiles(e.dataTransfer.files);", "handleFiles(e.dataTransfer.files);" + global_drop)

with open(v3_path, 'r', encoding='utf-8') as f:
    current = f.read()

new_content = re.sub(r'<script>.*?</script>', f"<script>{backup_js}</script>", current, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.18 Functional Restore Complete: Backup logic synchronized, Duplicate loading fixed.")
