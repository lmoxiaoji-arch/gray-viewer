import os

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    full_content = f.read()

# 终极干净样式块
clean_style = """
    <style>
        :root { --accent: #3b82f6; --easing: cubic-bezier(0.4, 0, 0.2, 1); --sidebar-w: 380px; --spring: cubic-bezier(0.68, -0.6, 0.32, 1.6); }
        .theme-dark { --surface: #0a0a0a; --on-surface: #fff; --glass-bg: rgba(255,255,255,0.03); --glass-border: rgba(255,255,255,0.08); }
        .theme-light { --surface: #f8fafc; --on-surface: #0f172a; --glass-bg: rgba(255,255,255,0.7); --glass-border: rgba(0,0,0,0.05); }

        body { background-color: var(--surface); color: var(--on-surface); font-family: 'Outfit', sans-serif; overflow: hidden; height: 100vh; }
        .aurora-bg { position: fixed; inset: 0; z-index: -1; opacity: 0.5; background: radial-gradient(circle at 10% 10%, rgba(59,130,246,0.1) 0%, transparent 40%), radial-gradient(circle at 90% 90%, rgba(59,130,246,0.06) 0%, transparent 40%); filter: blur(80px); }
        .glass-panel { background: var(--glass-bg); backdrop-filter: blur(40px); border: 1px solid var(--glass-border); border-radius: 28px; }
        .bento-card { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 20px; transition: all 0.4s var(--easing); }
        .bento-card:hover { border-color: var(--accent); transform: translateY(-2px); }
        
        * { -webkit-user-drag: none; user-select: none; }
        
        #main-sidebar { width: var(--sidebar-w); transition: transform 0.6s var(--easing); flex-shrink: 0; position: relative; height: 100vh; z-index: 50; }
        #main-sidebar.collapsed { transform: translateX(-100%); margin-right: calc(var(--sidebar-w) * -1); }

        /* 极窄扁平按钮 (32x20) */
        #sidebar-toggle { 
            position: absolute; top: 32px; right: -16px; z-index: 100; 
            width: 32px; height: 20px; border-radius: 0 6px 6px 0; 
            background: var(--accent); display: flex; align-items: center; justify-content: center; 
            color: white; cursor: pointer; box-shadow: 5px 0 15px rgba(59,130,246,0.15); 
            transition: all 0.4s var(--easing); 
        }
        #sidebar-toggle:hover { width: 36px; padding-left: 1px; }
        #main-sidebar.collapsed #sidebar-toggle { right: -32px; }
        
        /* 箭头动态旋转 */
        #sidebar-toggle svg { transition: transform 0.4s var(--easing); transform: rotate(180deg); }
        .collapsed #sidebar-toggle svg { transform: rotate(0deg); }

        canvas { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 24px; box-shadow: 0 50px 100px -20px rgba(0,0,0,0.5); cursor: move; }
        input[type="range"] { appearance: none; width: 100%; height: 4px; background: rgba(59,130,246,0.1); border-radius: 2px; }
        input[type="range"]::-webkit-slider-thumb { appearance: none; width: 14px; height: 14px; background: var(--accent); border-radius: 50%; cursor: pointer; }
        
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.2); border-radius: 10px; }

        /* 4s 匀速平衡流光 - 动力源复刻版 */
        .shimmer-text { 
            background: linear-gradient(90deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0.15) 100%); 
            background-size: 200% 100%; 
            -webkit-background-clip: text; 
            background-clip: text; 
            -webkit-text-fill-color: transparent; 
            animation: scan 4s linear infinite; 
            font-weight: 950;
            display: inline-block;
            padding: 0 0.15em; /* 确保 O 完整 */
            filter: drop-shadow(0 0 15px rgba(59,130,246,0.25));
        }

        @keyframes scan { 
            0% { background-position: 100% 0; } 
            100% { background-position: -100% 0; } 
        }

        /* 亮色模式流光适配 */
        .theme-light .shimmer-text {
            background: linear-gradient(90deg, rgba(15,23,42,0.1) 0%, rgba(59,130,246,0.8) 50%, rgba(15,23,42,0.1) 100%);
        }
    </style>
"""

import re
# 暴力替换整个 <style> 块
new_content = re.sub(r'<style>.*?</style>', clean_style, full_content, flags=re.DOTALL)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("V3.6 Cleanup Complete: Corrupted CSS purged, 1:1 clean logic restored.")
