import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'
backup_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3_backup.html'

# 我们直接从备份文件中抓取完整的 <script> 块，然后在其基础上应用 UI 改进
with open(backup_path, 'r', encoding='utf-8') as f:
    backup_full = f.read()
    script_match = re.search(r'<script>(.*?)</script>', backup_full, flags=re.DOTALL)
    original_js = script_match.group(1)

# 在原始稳健的 JS 基础上应用我们的 UI 改进
# 1. 移除 reset-view 引用 (非常小心地操作)
original_js = original_js.replace("document.getElementById('reset-view').classList.remove('visible');", "")
original_js = original_js.replace("document.getElementById('reset-view').classList.add('visible');", "")
original_js = re.sub(r"document\.getElementById\('reset-view'\)\.onclick =.*?;", "", original_js)

# 2. 应用侧边栏位移隐藏逻辑 (由于我们在 CSS 里改了，JS 逻辑其实没变，但要确保一致)
# 原始 JS 已经有切换 collapsed 类的逻辑了，保持不变

# 3. 增强全局拖放 (把之前的全局 Drop 逻辑补回原始 JS)
global_drop_js = """
        // --- 强化版全局拖放导入系统 ---
        window.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-active');
        });
        window.addEventListener('dragleave', (e) => {
            if (e.relatedTarget === null) dropzone.classList.remove('drag-active');
        });
        window.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                handleFiles(e.dataTransfer.files);
            }
        });
"""
# 替换掉原始 JS 中的旧拖放段落
original_js = re.sub(r'// Drag & Drop.*?handleFiles\(e\.dataTransfer\.files\);\s+\}\);', global_drop_js, original_js, flags=re.DOTALL)

with open(v3_path, 'r', encoding='utf-8') as f:
    current_content = f.read()

# 物理替换整个 Script 块
new_content = re.sub(r'<script>.*?</script>', f"<script>{original_js}</script>", current_content, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.10 Core Restore Complete: Multi-layer logic restored from backup, UI polish preserved.")
