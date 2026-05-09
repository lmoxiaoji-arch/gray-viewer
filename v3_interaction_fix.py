import os

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'

with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 按钮“窄”化微调 (更窄更薄 40x20)
old_toggle = "#sidebar-toggle { position: absolute; top: 32px; right: -32px; z-index: 100; width: 64px; height: 28px; border-radius: 0 8px 8px 0; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 8px 0 20px rgba(59,130,246,0.2); transition: all 0.3s var(--easing); }"
new_toggle = "#sidebar-toggle { position: absolute; top: 32px; right: -20px; z-index: 100; width: 40px; height: 20px; border-radius: 0 6px 6px 0; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; box-shadow: 5px 0 15px rgba(59,130,246,0.15); transition: all 0.4s var(--easing); }"

content = content.replace(old_toggle, new_toggle)
content = content.replace("#sidebar-toggle:hover { width: 72px; padding-left: 4px; }", "#sidebar-toggle:hover { width: 48px; padding-left: 2px; }")

# 增加箭头旋转 CSS
content = content.replace(
    "#main-sidebar.collapsed #sidebar-toggle { right: -48px; border-radius: 0 14px 14px 0; }",
    "#main-sidebar.collapsed #sidebar-toggle { right: -40px; } #sidebar-toggle svg { transition: transform 0.4s var(--easing); } .collapsed #sidebar-toggle svg { transform: rotate(0deg); } #sidebar-toggle svg { transform: rotate(180deg); }"
)

# 2. 修正 JS 逻辑，确保切换顺滑
old_js = """        document.getElementById('sidebar-toggle').onclick = () => {
            document.getElementById('main-sidebar').classList.toggle('collapsed');
        };"""

new_js = """        document.getElementById('sidebar-toggle').onclick = () => {
            const sidebar = document.getElementById('main-sidebar');
            sidebar.classList.toggle('collapsed');
        };"""

content = content.replace(old_js, new_js)

# 3. 初始箭头方向设为向左 (因为初始是展开状态)
# M9 18l6-6-6-6 是向右的，我们要让它默认旋转180度变成向左
# 已在 CSS 中通过 #sidebar-toggle svg { transform: rotate(180deg); } 实现

with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3.4 Interaction Fix Complete: Thinner toggle, Dynamic arrow direction.")
