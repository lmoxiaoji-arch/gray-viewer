import shutil
import os

v3_path = r'E:\Abel\web\gray-light-tool\index_fusion_v3.html'
v3_backup = r'E:\Abel\web\gray-light-tool\index_fusion_v3_backup.html'

# 1. 物理备份
try:
    shutil.copy2(v3_path, v3_backup)
    print(f"Backup created: {v3_backup}")
except Exception as e:
    print(f"Backup failed: {e}")
    exit(1)

# 2. 读取并修改
with open(v3_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 精准替换 CSS 动画逻辑
# 我们寻找包含 3s scan 的那一行
old_css = ".shimmer-text { background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0.1) 100%); background-size: 200% 100%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: scan 3s linear infinite; }"
new_css = ".shimmer-text { background: linear-gradient(90deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.15) 43%, rgba(255,255,255,0.9) 50%, rgba(255,255,255,0.15) 57%, rgba(255,255,255,0.15) 100%) !important; background-size: 200% 100% !important; -webkit-background-clip: text !important; background-clip: text !important; -webkit-text-fill-color: transparent !important; animation: scan 4s linear infinite !important; display: inline-block !important; font-weight: 950; letter-spacing: 0.1em; filter: drop-shadow(0 0 15px rgba(59,130,246,0.3)); }"

content = content.replace(old_css, new_css)

# 精准替换文本
old_text = 'text-7xl font-black tracking-tighter shimmer-text mb-4">TECHSUN</div>'
new_text = 'text-7xl font-black tracking-tighter shimmer-text mb-4">TECHSUN STUDIO</div>'

content = content.replace(old_text, new_text)

# 写入
with open(v3_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("V3 Iteration Success: 4s Balanced Shimmer applied to index_fusion_v3.html")
