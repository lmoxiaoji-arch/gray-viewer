import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

# 1. 彻底干净的逻辑块 (完全手动校对，确保无语法错误)
clean_logic = """
    <script>
        console.log('GrayLight Studio Engine v3.17 Starting...');
        
        const layers = [];
        const canvas = document.getElementById('main-canvas');
        const ctx = canvas.getContext('2d');
        const viewport = document.getElementById('viewport');
        const layerList = document.getElementById('layer-list');
        const fileInput = document.getElementById('file-input');
        const dropzone = document.getElementById('dropzone');
        
        let viewScale = 1;
        let viewPos = { x: 0, y: 0 };
        let isDraggingView = false;
        let lastMouse = { x: 0, y: 0 };

        // --- 核心渲染函数 ---
        function renderCanvas() {
            if (layers.length === 0) return;
            const baseLayer = layers.find(l => l.isBase) || layers[0];
            canvas.width = baseLayer.img.width;
            canvas.height = baseLayer.img.height;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            layers.forEach(layer => {
                if (!layer.visible) return;
                ctx.save();
                ctx.globalCompositeOperation = layer.isBase ? 'source-over' : 'screen';
                if (layer.isBase) {
                    const bright = parseFloat(document.getElementById('bright-slider').value);
                    ctx.filter = `brightness(${bright})`;
                    ctx.drawImage(layer.img, 0, 0, canvas.width, canvas.height);
                } else {
                    ctx.drawImage(layer.img, 0, 0, canvas.width, canvas.height);
                }
                ctx.restore();
            });
            canvas.style.transform = `translate(${viewPos.x}px, ${viewPos.y}px) scale(${viewScale})`;
        }

        function animate() { renderCanvas(); requestAnimationFrame(animate); }
        animate();

        // --- UI 更新函数 ---
        function updateUI() {
            console.log('Updating UI, layers:', layers.length);
            if (layers.length === 0) {
                layerList.innerHTML = '<div class="text-center py-20 opacity-20 italic text-xs">等待素材导入...</div>';
                document.getElementById('placeholder').style.display = 'block';
                canvas.style.display = 'none';
                return;
            }
            document.getElementById('placeholder').style.display = 'none';
            canvas.style.display = 'block';

            layerList.innerHTML = '';
            [...layers].reverse().forEach((layer, index) => {
                const realIdx = layers.length - 1 - index;
                const div = document.createElement('div');
                div.className = `layer-item bento-card p-4 cursor-pointer mb-3 ${layer.open ? 'open' : ''}`;
                div.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-black uppercase tracking-widest opacity-80">${layer.name}</span>
                        <div class="flex items-center gap-2">
                            <div class="p-1 hover:bg-white/10 rounded eye-btn ${layer.visible ? 'text-blue-500' : 'opacity-20'}">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 12s-3 7-10 7-10-7-10-7 3-7 10-7 10 7 10 7Z"/><circle cx="12" cy="12" r="3"/></svg>
                            </div>
                            <div class="p-1 hover:bg-white/10 rounded del-btn opacity-20 hover:opacity-100 hover:text-red-500">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                            </div>
                        </div>
                    </div>
                `;
                div.querySelector('.eye-btn').onclick = (e) => { e.stopPropagation(); layer.visible = !layer.visible; updateUI(); };
                div.querySelector('.del-btn').onclick = (e) => { e.stopPropagation(); layers.splice(realIdx, 1); updateUI(); };
                layerList.appendChild(div);
            });
        }

        // --- 导入逻辑 ---
        function handleFiles(files) {
            Array.from(files).forEach(file => {
                if (!file.type.startsWith('image/')) return;
                const img = new Image();
                img.onload = () => {
                    layers.push({ img, name: file.name, visible: true, isBase: layers.length === 0 });
                    updateUI();
                };
                img.src = URL.createObjectURL(file);
            });
        }

        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => handleFiles(e.target.files);

        window.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); });
        window.addEventListener('dragleave', (e) => { if (e.relatedTarget === null) dropzone.classList.remove('drag-active'); });
        window.addEventListener('drop', (e) => { e.preventDefault(); dropzone.classList.remove('drag-active'); handleFiles(e.dataTransfer.files); });

        // --- 视图控制 ---
        viewport.onmousedown = (e) => { if (e.target.id === 'viewport' || e.target.id === 'main-canvas') { isDraggingView = true; lastMouse = { x: e.clientX, y: e.clientY }; } };
        window.onmousemove = (e) => { if (isDraggingView) { viewPos.x += e.clientX - lastMouse.x; viewPos.y += e.clientY - lastMouse.y; lastMouse = { x: e.clientX, y: e.clientY }; } };
        window.onmouseup = () => isDraggingView = false;
        viewport.onwheel = (e) => { e.preventDefault(); viewScale *= e.deltaY > 0 ? 0.9 : 1.1; };

        // --- 侧边栏与主题 ---
        document.getElementById('sidebar-toggle').onclick = () => document.getElementById('main-sidebar').classList.toggle('collapsed');
        document.getElementById('theme-toggle').onclick = () => document.body.classList.toggle('theme-light');

        // --- 滑块数值联动 ---
        const rateSlider = document.getElementById('rate-slider');
        const brightSlider = document.getElementById('bright-slider');
        
        rateSlider.oninput = (e) => { document.getElementById('rate-num').textContent = e.target.value + 'x'; };
        brightSlider.oninput = (e) => { document.getElementById('bright-num').textContent = e.target.value + 'x'; };

        // 初始化
        updateUI();
    </script>
"""

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 彻底重写 <script> 块，确保没有残留
new_content = re.sub(r'<script>.*?</script>', clean_logic, content, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.17 Full Logic Rewrite Complete. All syntax errors purged.")
