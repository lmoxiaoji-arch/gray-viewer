import os

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 彻底修复流光不动的问题 & 优化扫射区间
# 我们将 background-position 从 200% 到 -200% 进行大跨度扫射，确保 4s 匀速平衡
new_css_logic = """
        .shimmer-text {
            background: linear-gradient(90deg, 
                rgba(255,255,255,0.1) 0%, 
                rgba(255,255,255,0.1) 40%, 
                rgba(255,255,255,0.9) 50%, 
                rgba(255,255,255,0.1) 60%, 
                rgba(255,255,255,0.1) 100%
            ) !important;
            background-size: 300% 100% !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: tech-scan 4s linear infinite !important;
            display: inline-block !important;
            font-weight: 950;
            letter-spacing: -0.02em; /* 紧凑字间距，符合截图质感 */
            filter: drop-shadow(0 0 15px rgba(59,130,246,0.3));
            text-transform: uppercase;
        }

        /* 亮色模式下的流光优化：保持高对比度质感 */
        .theme-light .shimmer-text {
            background: linear-gradient(90deg, 
                rgba(15, 23, 42, 0.1) 0%, 
                rgba(15, 23, 42, 0.1) 40%, 
                rgba(59, 130, 246, 0.8) 50%, 
                rgba(15, 23, 42, 0.1) 60%, 
                rgba(15, 23, 42, 0.1) 100%
            ) !important;
            filter: drop-shadow(0 0 10px rgba(59,130,246,0.2));
        }

        @keyframes tech-scan {
            0% { background-position: 150% 0; }
            100% { background-position: -150% 0; }
        }
"""

# 替换旧的 .shimmer-text 定义和 scan 动画
import re
content = re.sub(r'\.shimmer-text \{.*?\}', new_css_logic, content, flags=re.DOTALL)
content = re.sub(r'@keyframes scan \{.*?\}', '', content, flags=re.DOTALL) # 移除旧动画名

# 2. 更新 Placeholder 文本和样式 (1:1 还原截图)
old_placeholder = """            <div id="placeholder" class="text-center">
                <div class="text-7xl font-black tracking-tighter shimmer-text mb-4">TECHSUN STUDIO</div>
                <div class="text-[10px] tracking-[1.50em] opacity-20 uppercase">Ready For Creation</div>
            </div>"""

new_placeholder = """            <div id="placeholder" class="text-center">
                <div class="text-7xl font-black tracking-tighter shimmer-text mb-2">TECHSUN STUDIO</div>
                <div class="text-[10px] tracking-[1.2em] opacity-30 uppercase font-bold text-white/40">WAITING FOR PREVIEW / 等待预览</div>
            </div>"""

content = content.replace(old_placeholder, new_placeholder)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.2 Precision Fix applied: Shimmer fixed, Light mode synced, Text updated.")
