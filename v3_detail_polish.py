import os
import re

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 侧边栏 Toggle 扁平化 & 侧边栏隐藏逻辑重构
# 修改 #main-sidebar 的过渡方案，改用 transform 位移
content = content.replace(
    "#main-sidebar { width: var(--sidebar-w); transition: transform 0.5s var(--easing), width 0.5s var(--easing); flex-shrink: 0; position: relative; height: 100vh; z-index: 50; }",
    "#main-sidebar { width: var(--sidebar-w); transition: transform 0.6s var(--easing); flex-shrink: 0; position: relative; height: 100vh; z-index: 50; }"
)
content = content.replace(
    "#main-sidebar.collapsed { width: 0; padding: 0; transform: translateX(-100%); }",
    "#main-sidebar.collapsed { transform: translateX(-100%); margin-right: calc(var(--sidebar-w) * -1); }"
)

# 修改切换按钮样式：扁平化 (48x48 -> 64x24)
old_toggle_style = "#sidebar-toggle { position: absolute; top: 24px; right: -24px; z-index: 100; width: 48px; height: 48px; border-radius: 0 14px 14px 0; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 10px 0 20px rgba(59,130,246,0.2); transition: all 0.3s var(--easing); }"
new_toggle_style = "#sidebar-toggle { position: absolute; top: 32px; right: -32px; z-index: 100; width: 64px; height: 28px; border-radius: 0 8px 8px 0; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 8px 0 20px rgba(59,130,246,0.2); transition: all 0.3s var(--easing); }"

content = content.replace(old_toggle_style, new_toggle_style)
content = content.replace("#sidebar-toggle:hover { width: 56px; padding-left: 8px; }", "#sidebar-toggle:hover { width: 72px; padding-left: 4px; }")

# 2. 流光文字修复：彻底解决“不动”和“O 不完整”
# 增加 padding 解决 O 被切掉的问题，调整动画范围
shimmer_fix = """
        .shimmer-text {
            background: linear-gradient(90deg, 
                rgba(255,255,255,0.15) 0%, 
                rgba(255,255,255,0.15) 35%, 
                rgba(255,255,255,0.95) 50%, 
                rgba(255,255,255,0.15) 65%, 
                rgba(255,255,255,0.15) 100%
            ) !important;
            background-size: 200% 100% !important;
            -webkit-background-clip: text !important;
            background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: tech-scan 4s linear infinite !important;
            display: inline-block !important;
            font-weight: 950;
            letter-spacing: -0.01em;
            padding: 0 0.2em; /* 关键：给文字预留左右空间，防止 O 被切断 */
            filter: drop-shadow(0 0 15px rgba(59,130,246,0.3));
            text-transform: uppercase;
        }

        @keyframes tech-scan {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
"""

content = re.sub(r'\.shimmer-text \{.*?\}', shimmer_fix, content, flags=re.DOTALL)
content = re.sub(r'@keyframes tech-scan \{.*?\}', '', content, flags=re.DOTALL) # 移除多余的重复定义

# 3. 更新切换按钮图标，使其更符合扁平设计
content = content.replace(
    '<div id="sidebar-toggle"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/></svg></div>',
    '<div id="sidebar-toggle"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M9 18l6-6-6-6"/></svg></div>'
)

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.3 Detail Polish Complete: Flatter button, Slide-hide logic, Shimmer fixed, 'O' restored.")
