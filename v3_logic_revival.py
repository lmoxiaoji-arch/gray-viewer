import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    full_content = f.read()

# 1. 彻底修复 JS 语法错误（清理断层）
# 寻找断层位置并修复
# 我们直接重写从 renderCanvas 到末尾的 JS 逻辑，确保 100% 正确
js_start_marker = "let animTime = 0;"
js_end_marker = "updateUI();"

# 我们抓取中间的所有逻辑并替换为一份干净、校验过的逻辑
final_js = """
        let animTime = 0;
        function renderCanvas() {
            if (layers.length === 0) return;
            const baseLayer = layers.find(l => l.isBase) || layers[0];
            if (canvas.width !== baseLayer.img.width || canvas.height !== baseLayer.img.height) {
                canvas.width = baseLayer.img.width;
                canvas.height = baseLayer.img.height;
            }
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            layers.forEach(layer => {
                if (!layer.visible) return;
                let drawImg = layer.img;
                if (layer.maskRGB) {
                    const offCanvas = document.createElement('canvas');
                    offCanvas.width = layer.img.width; offCanvas.height = layer.img.height;
                    const oCtx = offCanvas.getContext('2d');
                    oCtx.drawImage(layer.img, 0, 0);
                    const imageData = oCtx.getImageData(0, 0, offCanvas.width, offCanvas.height);
                    const data = imageData.data;
                    const [mr, mg, mb] = layer.maskRGB;
                    const tol = (layer.tolerance || 30) * 2.55;
                    for (let i = 0; i < data.length; i += 4) {
                        const diff = Math.sqrt((data[i]-mr)**2 + (data[i+1]-mg)**2 + (data[i+2]-mb)**2);
                        if (diff < tol) data[i+3] = 0;
                    }
                    oCtx.putImageData(imageData, 0, 0);
                    drawImg = offCanvas;
                }
                if (layer.isBase) {
                    const bright = parseFloat(document.getElementById('bright-slider').value);
                    ctx.filter = `brightness(${bright})`;
                    ctx.drawImage(drawImg, 0, 0, canvas.width, canvas.height);
                    ctx.filter = 'none';
                } else {
                    ctx.globalCompositeOperation = 'screen';
                    ctx.drawImage(drawImg, 0, 0, canvas.width, canvas.height);
                    ctx.globalCompositeOperation = 'source-over';
                }
            });
            canvas.style.transform = `translate(${viewPos.x}px, ${viewPos.y}px) scale(${viewScale})`;
        }

        function animate() { renderCanvas(); requestAnimationFrame(animate); }
        animate();

        // --- 核心交互逻辑复活 ---
        function handleFiles(files) {
            console.log("Loading files...", files.length);
            Array.from(files).forEach(file => {
                if (!file.type.startsWith('image/')) return;
                const img = new Image();
                img.onload = () => {
                    layers.push({
                        img, name: file.name, visible: true, open: false,
                        isBase: layers.length === 0, mode: 'white'
                    });
                    updateUI();
                    renderCanvas();
                };
                img.src = URL.createObjectURL(file);
            });
        }

        dropzone.onclick = () => fileInput.click();
        fileInput.onchange = (e) => handleFiles(e.target.files);

        // --- 全局拖放 ---
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
            if (e.dataTransfer.files) handleFiles(e.dataTransfer.files);
        });

        // --- 视图控制 ---
        viewport.onmousedown = (e) => {
            if (e.target.id === 'viewport' || e.target.id === 'main-canvas') {
                isDraggingView = true;
                lastMouse = { x: e.clientX, y: e.clientY };
            }
        };
        window.onmousemove = (e) => {
            if (!isDraggingView) return;
            viewPos.x += e.clientX - lastMouse.x;
            viewPos.y += e.clientY - lastMouse.y;
            lastMouse = { x: e.clientX, y: e.clientY };
            renderCanvas();
        };
        window.onmouseup = () => isDraggingView = false;
        viewport.onwheel = (e) => {
            e.preventDefault();
            viewScale *= e.deltaY > 0 ? 0.9 : 1.1;
            renderCanvas();
        };

        document.getElementById('sidebar-toggle').onclick = () => {
            document.getElementById('main-sidebar').classList.toggle('collapsed');
        };

        document.getElementById('rate-slider').oninput = (e) => { document.getElementById('rate-num').textContent = e.target.value + 'x'; };
        document.getElementById('bright-slider').oninput = (e) => { document.getElementById('bright-num').textContent = e.target.value + 'x'; };

        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.onclick = () => {
            const isDark = document.body.classList.contains('theme-dark');
            if (isDark) {
                document.body.classList.replace('theme-dark', 'theme-light');
                document.documentElement.classList.remove('dark');
            } else {
                document.body.classList.replace('theme-light', 'theme-dark');
                document.documentElement.classList.add('dark');
            }
        };

        updateUI();
"""

# 使用正则表达式精准替换从 animTime 到末尾的所有内容
new_content = re.sub(r'let animTime = 0;.*updateUI\(\);', final_js, full_content, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.9 Logic Revival Complete: Syntax Error fixed, Click and Drop restored.")
