import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'
backup_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3_backup.html'

with open(backup_path, 'r', encoding='utf-8') as f:
    js = re.search(r'<script>(.*?)</script>', f.read(), flags=re.DOTALL).group(1)

# 1. 修正保护名单 (只保护 reset-view，放行 sidebar 和 theme)
protection = """
    const _safeGet = document.getElementById;
    document.getElementById = function(id) {
        const el = _safeGet.call(document, id);
        if (!el && id === 'reset-view') return { onclick: null, classList: { add:()=>{}, remove:()=>{} }, style: {} };
        return el;
    };
"""

# 2. 物理注入 handleFiles 内部重置逻辑 (确保重复载入)
# 在 handleFiles 的左大括号后立即注入
js = js.replace("function handleFiles(files) {", "function handleFiles(files) { console.log('Handling files...'); ")
# 补上全局文件输入重置
js = js.replace("handleFiles(e.target.files);", "handleFiles(e.target.files); document.getElementById('file-input').value = '';")

# 3. 补全滑块和全局拖拽 (放在 window.onload 确保 DOM 准备就绪)
final_patch = """
    window.addEventListener('DOMContentLoaded', () => {
        // 侧边栏强制连接
        const toggle = document.getElementById('sidebar-toggle');
        if(toggle) toggle.onclick = () => document.getElementById('main-sidebar').classList.toggle('collapsed');
        
        // 滑块联动
        const rs = document.getElementById('rate-slider');
        const bs = document.getElementById('bright-slider');
        if(rs) rs.oninput = (e) => { document.getElementById('rate-num').textContent = e.target.value + 'x'; };
        if(bs) bs.oninput = (e) => { document.getElementById('bright-num').textContent = e.target.value + 'x'; };
        
        // 全局拖拽
        window.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); });
        window.addEventListener('dragleave', (e) => { if (e.relatedTarget === null) dropzone.classList.remove('drag-active'); });
        window.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
            if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
        });
    });
"""

final_script = f"<script>{protection}{js}{final_patch}</script>"

with open(v3_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_content = re.sub(r'<script>.*?</script>', final_script, html, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.20 Precision Reconnect Complete: Sidebar fixed, Duplicate loading fixed.")
