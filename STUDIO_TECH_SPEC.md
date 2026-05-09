# GrayLight Studio 交互工具技术规格书 (V3.15)

## 1. 项目定位
本工具是专为 **TechSun 光刻工艺** 设计的独立调参及视觉验证工具。它作为工业母库 (Base) 的独立演化版本，侧重于高精度的交互质感与视觉反馈。

## 2. 核心功能
- **全域画布交互**：支持图片的平移（Drag）与缩放（Zoom），支持无限边界拖拽。
- **三维感光模式**：
  - **Gray (灰度模式)**：严格锁定 1-254 灰阶范围，过滤极端黑白噪点。
  - **Light (感光模式)**：模拟 WebGL 指数级能量光晕。
  - **Color (色彩模式)**：支持实时色值提取与色偏矫正。
- **工业级 UI 架构**：左侧参数面板、右侧实时监控，支持全沉浸式暗色模式。

## 3. 交互规范 (Interaction Standards) - 【核心修复项】
为了确保类原生 App 的流畅触感，必须严格遵守以下规范：

### 3.1 指针事件架构 (Pointer Events)
- **禁用旧版事件**：严禁使用 `mousedown/mousemove/mouseup`，全面迁移至 `pointerdown/pointermove/pointerup`。
- **指针捕获 (Pointer Capture)**：在 `pointerdown` 时必须执行 `element.setPointerCapture(e.pointerId)`。
  - *目的*：确保鼠标移出浏览器窗口或滑入其他 UI 遮罩层时，拖拽状态仍能被正确捕捉并释放。
- **全局防黏连保护**：
  - 必须监听 `window` 的 `blur` 事件，在用户切换窗口或弹出系统对话框时，强制执行 `isDragging = false`。
  - 严禁通过 `window.onmouseup = ...` 直接覆盖全局事件，必须使用 `addEventListener` 以防事件链断裂。

### 3.2 触感保护
- **防划选**：全局应用 `user-select: none`。
- **防原生拖拽**：对所有 `<img>` 和 `canvas` 应用 `-webkit-user-drag: none`，避免触发浏览器的默认图片拖动行为。

## 4. 视觉标准 (Visual Standards)
- **调色板**：采用 TechSun 工业深空蓝 (`#0d0d15`) 为基底。
- **动态特效**：
  - **极光扫光 (Aurora Sweep)**：按钮及容器边框采用 5 段式线性渐变动画。
  - **磨砂玻璃 (Glassmorphism)**：UI 面板必须具备 `backdrop-filter: blur(20px)` 效果。
- **渲染基准**：WebGL 渲染层需锁定 50% 锐度保护，防止过度曝光。

## 5. 版本与同步
- **本地路径**：`e:\Abel\web\gray-light-tool`
- **Git 仓库**：关联至 `lmoxiaoji-arch/gray-viewer`
- **备份建议**：重大修改前需执行 `Copy-Item index.html index_backup_YYYYMMDD.html`。

---
*文档生成日期：2026-05-09*
*维护者：Antigravity AI & Abel*
