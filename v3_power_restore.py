import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 按钮“极窄”化微调 (从 40px 压缩至 32px)
old_toggle = "#sidebar-toggle { position: absolute; top: 32px; right: -20px; z-index: 100; width: 40px; height: 20px; border-radius: 0 6px 6px 0; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 5px 0 15px rgba(59,130,246,0.15); transition: all 0.4s var(--easing); }"
new_toggle = "#sidebar-toggle { position: absolute; top: 32px; right: -16px; z-index: 100; width: 32px; height: 20px; border-radius: 0 6px 6px 0; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 5px 0 15px rgba(59,130,246,0.15); transition: all 0.4s var(--easing); }"

content = content.replace(old_toggle, new_toggle)
content = content.replace("#sidebar-toggle:hover { width: 48px; padding-left: 2px; }", "#sidebar-toggle:hover { width: 36px; padding-left: 1px; }")
content = content.replace("#main-sidebar.collapsed #sidebar-toggle { right: -40px; }", "#main-sidebar.collapsed #sidebar-toggle { right: -32px; }")

# 2. 1:1 复刻备份文件中的“能动”流光逻辑
shimmer_power_restore = """
        .shimmer-text {
            /* 1:1 复刻备份中的梯度，但增加 15% 灰度保护底色 */
            background: linear-gradient(90deg, 
                rgba(255,255,255,0.15) 0%, 
                rgba(255,255,255,0.8) 50%, 
                rgba(255,255,255,0.15) 100%
            ) !important;
            background-size: 200% 100% !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: scan 4s linear infinite !important; /* 仅调整为 4s */
            display: inline-block !important;
            font-weight: 950;
            letter-spacing: -0.01em;
            padding: 0 0.15em; /* 解决 O 不完整 */
            filter: drop-shadow(0 0 15px rgba(59,130,246,0.25));
            text-transform: uppercase;
        }

        @keyframes scan {
            0% { background-position: 100% 0; }
            100% { background-position: -100% 0; }
        }
"""

# 清除之前所有版本的 .shimmer-text 和相关 keyframes
content = re.sub(r'\.shimmer-text \{.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'@keyframes tech-scan \{.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'@keyframes scan \{.*?\}', '', content, flags=re.DOTALL)

# 将复刻后的代码重新注入到 <style> 块末尾
content = content.replace("    </style>", shimmer_power_restore + "\n    </style>")

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.5 Power Restore Complete: Shimmer logic synced with backup, Button narrowized.")
