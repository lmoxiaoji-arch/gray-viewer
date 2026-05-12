import os

backup_path = r'E:\Abel\web\gray-light-tool\index_backup.html'
target_path = r'E:\Abel\web\gray-light-tool\index.html'

with open(backup_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 终极动态挂载逻辑
fusion_logic = r"""
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;600;900&display=swap" rel="stylesheet">
<script>
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #graylight-fusion-system {
            all: initial; font-family: 'Outfit', sans-serif;
            position: fixed; inset: 0; z-index: 999999; pointer-events: none;
            --accent: #3b82f6;
        }
        #graylight-fusion-system * { all: revert; box-sizing: border-box; color: #fff; }
        #graylight-fusion-system aside, #graylight-fusion-system button, #graylight-fusion-system input { pointer-events: auto; }
        
        /* 强制隐藏内核旧 UI */
        header.z-50, aside.w-72, [class*='aside'], [class*='header'], .bottom-12, button.top-10 { 
            display: none !important; opacity: 0 !important; visibility: hidden !important; 
        }

        .text-mask-shimmer {
            background: linear-gradient(90deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.15) 43%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0.15) 57%, rgba(255,255,255,0.15) 100%) !important;
            background-size: 200% 100% !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: tech-scan 4s linear infinite !important;
            display: inline-block !important;
            font-weight: 950; letter-spacing: 1.2em; filter: drop-shadow(0 0 12px rgba(59,130,246,0.3));
            text-transform: uppercase;
        }
        @keyframes tech-scan { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }

        .glass-panel { background: rgba(10,10,10,0.6); backdrop-filter: blur(40px); border: 1px solid rgba(255,255,255,0.08); border-radius: 28px; }
        .bento-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 28px; transition: all 0.4s ease; }
        .bento-card:hover { background: rgba(255,255,255,0.05); border-color: rgba(59,130,246,0.2); }
        .aurora-bg { position: fixed; inset: 0; z-index: -1; background: radial-gradient(circle at 10% 10%, rgba(59,130,246,0.1), transparent 40%), radial-gradient(circle at 90% 90%, rgba(59,130,246,0.05), transparent 40%); filter: blur(80px); }
        input[type='range'] { appearance: none; width: 100%; height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; }
        input[type='range']::-webkit-slider-thumb { appearance: none; width: 14px; height: 14px; background: #3b82f6; border-radius: 50%; cursor: pointer; }
    `;
    document.head.appendChild(style);

    function initFusion() {
        if (document.getElementById('graylight-fusion-system')) return;
        
        const container = document.createElement('div');
        container.id = 'graylight-fusion-system';
        container.innerHTML = `
            <div class='aurora-bg'></div>
            <aside class='w-[380px] h-screen p-6 flex flex-col gap-6' style='background: rgba(8,8,8,0.7); backdrop-filter: blur(30px); border-right: 1px solid rgba(255,255,255,0.05);'>
                <header class='px-2'><h1 class='text-2xl font-black tracking-tighter flex items-center gap-3'><span class='w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-sm font-bold'>G</span><span style='color:white;'>GRAYLIGHT <span class='text-blue-500 font-light italic uppercase'>Studio</span></span></h1></header>
                <div id='f-add' class='bento-card p-8 flex flex-col items-center justify-center gap-4 cursor-pointer border-dashed border-2 h-[180px] border-white/10 group'>
                    <div class='w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center border border-blue-500/20 group-hover:scale-110 transition-transform'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='3' class='text-blue-500'><line x1='12' y1='5' x2='12' y2='19'></line><line x1='5' y1='12' x2='19' y2='12'></line></svg></div>
                    <div class='text-center'><p class='text-sm font-black tracking-widest uppercase text-white'>拖动添加</p><p class='text-[8px] text-white/20 mt-1'>IES / LUT / ASSETS</p></div>
                </div>
                <div class='glass-panel flex-1 overflow-hidden flex flex-col'>
                    <div class='p-5 border-b border-white/5 flex items-center gap-3'><span class='text-[10px] font-black tracking-[0.4em] uppercase text-white/40'>图层管理</span></div>
                    <div id='f-layers' class='flex-1 overflow-y-auto p-4 space-y-3'></div>
                </div>
                <div class='glass-panel p-6 space-y-4'>
                    <div class='flex justify-between text-[9px] font-black uppercase text-white/20 tracking-widest'><span>速率调节</span><span id='f-rate-txt' class='text-blue-500'>1.0x</span></div>
                    <input type='range' id='f-rate' min='0' max='2' step='0.1' value='1.0'>
                </div>
            </aside>
            <main class='flex-1 h-screen relative flex items-center justify-center p-12 overflow-hidden'>
                <div id='f-portal' class='w-full h-full flex items-center justify-center relative z-10'>
                    <div id='f-loading' class='text-center'>
                        <div class='text-6xl font-black tracking-tighter text-mask-shimmer'>TECHSUN STUDIO</div>
                        <div class='text-[10px] tracking-[1.4em] text-white/10 uppercase font-light mt-8'>Waiting for Preview / 等待预览载入</div>
                    </div>
                </div>
            </main>
        `;
        document.body.appendChild(container);

        // 桥接逻辑
        document.getElementById('f-add').onclick = () => {
            const input = document.getElementById('main-input') || document.querySelector('input[type=\"file\"]');
            if (input) input.click();
        };
        
        const rateSlider = document.getElementById('f-rate');
        rateSlider.oninput = (e) => {
            document.getElementById('f-rate-txt').textContent = e.target.value + 'x';
            const s = [...document.querySelectorAll('#root input[type=\"range\"]')].find(i => i.closest('div').querySelector('label')?.textContent.includes('速率'));
            if (s) {
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(s, e.target.value);
                s.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };

        const syncedNames = new Set();
        setInterval(() => {
            const root = document.getElementById('root');
            const portal = document.getElementById('f-portal');
            const canvas = root?.querySelector('canvas');
            if (canvas && portal.firstChild !== canvas) {
                portal.innerHTML = '';
                canvas.style.cssText = 'width: auto; height: 85vh; max-width: 95%; border-radius: 40px; box-shadow: 0 100px 200px -50px rgba(0,0,0,0.8);';
                portal.appendChild(canvas);
            }

            const layers = [...(root?.querySelectorAll('div') || [])].filter(el => (el.innerHTML.includes('text-red-500') || el.innerHTML.includes('M3 6h18')) && el.textContent.length > 0).slice(0, 15);
            const list = document.getElementById('f-layers');
            if (layers.length > 0) {
                layers.forEach((orig, i) => {
                    const name = orig.querySelector('.text-[12px]')?.textContent || 'Layer ' + (i+1);
                    if (!syncedNames.has(name + i)) {
                        const card = document.createElement('div');
                        card.className = 'bento-card p-4 rounded-xl flex items-center justify-between';
                        card.innerHTML = `<div class='flex items-center gap-3'><div class='w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center border border-white/5'><svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='3' class='text-blue-500'><rect x='3' y='3' width='18' height='18' rx='2'/></svg></div><div class='text-[10px] font-black uppercase text-white/50'>${name}</div></div><button class='del-btn p-2 hover:bg-red-500/10 rounded-lg group'><svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='3' class='text-white/10 group-hover:text-red-500'><path d='M3 6h18'/><path d='M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6'/></svg></button>`;
                        card.querySelector('.del-btn').onclick = () => {
                            const btn = [...orig.querySelectorAll('button')].find(b => b.querySelector('.text-red-500') || b.innerHTML.includes('M3 6h18'));
                            if (btn) btn.click();
                        };
                        list.appendChild(card);
                        syncedNames.add(name + i);
                    }
                });
            } else if (syncedNames.size > 0 && layers.length === 0) {
                syncedNames.clear();
                list.innerHTML = '';
            }
        }, 600);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFusion);
    } else {
        initFusion();
    }
})();
</script>
"""

new_content = content.replace('<head>', '<head>' + fusion_logic)
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fusion 2.1 Final Surgery Success")
