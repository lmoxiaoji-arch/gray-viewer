import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在 updateUI 内部注入拖拽排序逻辑
# 我们寻找 layerList.appendChild(div); 之前的位置
sorting_logic = """
                // --- 图层拖拽排序逻辑 ---
                div.ondragstart = (e) => {
                    e.dataTransfer.setData('text/plain', realIdx);
                    div.classList.add('dragging');
                };
                div.ondragend = () => div.classList.remove('dragging');
                div.ondragover = (e) => e.preventDefault();
                div.ondrop = (e) => {
                    e.preventDefault();
                    const fromIdx = parseInt(e.dataTransfer.getData('text/plain'));
                    const toIdx = realIdx;
                    if (fromIdx === toIdx) return;
                    
                    // 数组重排
                    const movedItem = layers.splice(fromIdx, 1)[0];
                    layers.splice(toIdx, 0, movedItem);
                    
                    updateUI();
                    renderCanvas();
                };
"""

# 注入到 updateUI 循环的末尾
content = content.replace("layerList.appendChild(div);", sorting_logic + "\n                layerList.appendChild(div);")

# 2. 增加拖拽时的视觉样式
if ".layer-item.dragging { opacity: 0.5; border: 2px dashed var(--accent); }" not in content:
    content = content.replace("</style>", "        .layer-item.dragging { opacity: 0.5; border: 2px dashed var(--accent); }\n    </style>")

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.22 Layer Sorting logic injected.")
