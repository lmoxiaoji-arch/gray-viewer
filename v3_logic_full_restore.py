import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'
backup_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3_backup.html'

# 1. 读取备份文件中的原始 JS 逻辑 (1:1 抓取)
with open(backup_path, 'r', encoding='utf-8') as f:
    backup_full = f.read()
    script_match = re.search(r'<script>(.*?)</script>', backup_full, flags=re.DOTALL)
    original_js = script_match.group(1)

# 2. 对原始 JS 进行最小化“避雷”修改 (防止因为 reset-view 消失导致的报错)
# 我们直接把原始 JS 中涉及 reset-view 的部分包裹在 try-catch 中
original_js = original_js.replace(
    "document.getElementById('reset-view').onclick = () => {",
    "try { document.getElementById('reset-view').onclick = () => {"
)
original_js = original_js.replace(
    "viewScale = 1; viewPos = { x: 0, y: 0 }; renderCanvas();\r\n        };",
    "viewScale = 1; viewPos = { x: 0, y: 0 }; renderCanvas();\r\n        }; } catch(e) {}"
)
# 同时处理 updateUI 内部的 classList 操作
original_js = original_js.replace(
    "document.getElementById('reset-view').classList.remove('visible');",
    "try { document.getElementById('reset-view').classList.remove('visible'); } catch(e) {}"
)
original_js = original_js.replace(
    "document.getElementById('reset-view').classList.add('visible');",
    "try { document.getElementById('reset-view').classList.add('visible'); } catch(e) {}"
)

# 3. 补回全局拖拽增强逻辑 (这是原始 JS 没有但您需要的好功能)
global_drop_logic = """
        // Global Drop Support
        window.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); });
        window.addEventListener('dragleave', (e) => { if (e.relatedTarget === null) dropzone.classList.remove('drag-active'); });
        window.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
            if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
        });
"""
# 将全局拖拽逻辑注入到 handleFiles 之后
original_js = original_js.replace("fileInput.onchange = (e) => handleFiles(e.target.files);", 
                                "fileInput.onchange = (e) => handleFiles(e.target.files);" + global_drop_logic)

# 4. 物理替换当前文件脚本
with open(v3_path, 'r', encoding='utf-8') as f:
    current_content = f.read()

new_content = re.sub(r'<script>.*?</script>', f"<script>{original_js}</script>", current_content, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.13 Logic Fully Restored from Backup. Reset-view safely bypassed.")
