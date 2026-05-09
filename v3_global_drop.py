import os

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 增强全局拖放 JS 逻辑
old_drop_logic = """        // Drag & Drop
        window.addEventListener('dragover', (e) => e.preventDefault());
        window.addEventListener('drop', (e) => e.preventDefault());

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-active');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('drag-active');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
            handleFiles(e.dataTransfer.files);
        });"""

new_drop_logic = """        // --- 强化版全局拖放导入系统 ---
        window.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-active'); // 全局进入时，卡片产生视觉反馈
        });

        window.addEventListener('dragleave', (e) => {
            // 只有当鼠标离开视口时才取消高亮
            if (e.relatedTarget === null) {
                dropzone.classList.remove('drag-active');
            }
        });

        window.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-active');
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                handleFiles(e.dataTransfer.files);
            }
        });
        
        // 保留局部卡片的高亮逻辑以便更精确的反馈
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-active');
        });"""

content = content.replace(old_drop_logic, new_drop_logic)

# 2. 增强视觉反馈：给 drag-active 增加一个呼吸动效
content = content.replace(
    "#dropzone.drag-active { border-color: var(--accent); background: rgba(59,130,246,0.05); transform: scale(1.02); }",
    "#dropzone.drag-active { border-color: var(--accent); background: rgba(59,130,246,0.1); transform: scale(1.05); box-shadow: 0 0 30px rgba(59,130,246,0.2); border-style: solid; }"
)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.8 Global Drop functionality enabled.")
