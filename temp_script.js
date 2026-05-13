
        const VS_SOURCE = `attribute vec2 a_position; attribute vec2 a_uv; varying vec2 v_uv; void main() { gl_Position = vec4(a_position, 0, 1); v_uv = a_uv; }`;
        const FS_SOURCE = `
            precision highp float;
            varying vec2 v_uv;
            uniform sampler2D u_tex_base, u_tex_light, u_tex_mask;
            uniform float u_time, u_bright, u_tolerance;
            uniform int u_mode, u_is_base;
            uniform vec3 u_mask_color;
            uniform vec2 u_res_ratio, u_parallax;

            vec3 hsv2rgb(vec3 c) { vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0); vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www); return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y); }
            
            void main() {
                vec2 uv = (v_uv - 0.5) * u_res_ratio + 0.5;
                if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) discard;
                vec4 base = texture2D(u_tex_base, uv);
                if (distance(base.rgb, u_mask_color) < u_tolerance) discard;

                float finalMask = step(0.5, texture2D(u_tex_mask, uv).r);
                vec2 delta = uv - 0.5;
                float dist = length(delta);
                vec2 refractUV = uv;
                if (finalMask > 0.5) {
                    float rf = dist * 2.0 + pow(dist * 2.0, 3.0) * 0.45;
                    refractUV = 0.5 + normalize(delta) * rf * 0.5;
                }

                // 馃毃 缁濆涓€鑷达細鍏ㄥ憳绂佺敤 UV 鎵洸锛岀‘淇濆厜鏁?1:1 杩樺師鐏板害鍥撅紝涓嶄骇鐢熸姌灏勬柇灞?                vec2 finalUV = uv;
                float h0 = texture2D(u_tex_light, finalUV).r, h = 0.0;
 
                for(int i=-1; i<=1; i++) for(int j=-1; j<=1; j++) h += texture2D(u_tex_light, finalUV+vec2(float(i)*0.0006, float(j)*0.0006)).r;
                h /= 9.0;

                vec3 effect = vec3(0.0);
                // 馃毃 褰诲簳鏀惧紑锛氫笉鍐嶉檺鍒?h 鐨勮寖鍥达紝纭繚璧板厜鍍忕礌 100% 淇濈暀
                float phase = fract(h - u_time), d = abs(phase - 0.5);
                if (u_mode == 0) effect = vec3(pow(smoothstep(0.15, 0.0, d), 1.8) * 0.5 + smoothstep(0.3, 0.0, d) * 0.15) * u_bright * 1.5;
                else effect = hsv2rgb(vec3(fract(h * 1.5 + u_time * 2.0), 0.7, 1.0)) * pow(smoothstep(0.2, 0.0, d), 1.5) * u_bright * 1.5;

                
                vec3 finalEffect = 1.0 - exp(-effect * base.a * 1.5);
                gl_FragColor = vec4((u_is_base == 1) ? (base.rgb + finalEffect) : finalEffect, (u_is_base == 1) ? base.a : 1.0);
            }
        `;

        const layers = [];
        const layerMap = new WeakMap(); // 馃毃 宸ヤ笟绾ф槧灏勶細DOM 鑺傜偣 1:1 鏄犲皠鍒?Layer 瀵硅薄
        const canvas = document.getElementById('main-canvas');
        const gl = canvas.getContext('webgl', { premultipliedAlpha: true, antialias: true });

        function resize() {
            // 鐗╃悊鍒嗚鲸鐜囩敱 renderCanvas 鏍规嵁绱犳潗鍔ㄦ€侀攣瀹氾紝姝ゅ浠呭悓姝?Viewport
            gl.viewport(0, 0, canvas.width, canvas.height);
        }
        window.addEventListener('resize', () => { resize(); updateABUI(); });
        resize();
        function createShader(gl, type, source) { const s = gl.createShader(type); gl.shaderSource(s, source); gl.compileShader(s); return s; }
        const program = gl.createProgram();
        gl.attachShader(program, createShader(gl, gl.VERTEX_SHADER, VS_SOURCE));
        gl.attachShader(program, createShader(gl, gl.FRAGMENT_SHADER, FS_SOURCE));
        gl.linkProgram(program); gl.useProgram(program);

        const buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, 1, 0, 0, 1, 1, 1, 0, -1, -1, 0, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
        const a_pos = gl.getAttribLocation(program, 'a_position'), a_uv = gl.getAttribLocation(program, 'a_uv');
        gl.enableVertexAttribArray(a_pos); gl.vertexAttribPointer(a_pos, 2, gl.FLOAT, false, 16, 0);
        gl.enableVertexAttribArray(a_uv); gl.vertexAttribPointer(a_uv, 2, gl.FLOAT, false, 16, 8);

        const uniforms = {
            tex_base: gl.getUniformLocation(program, 'u_tex_base'), tex_light: gl.getUniformLocation(program, 'u_tex_light'),
            tex_mask: gl.getUniformLocation(program, 'u_tex_mask'), time: gl.getUniformLocation(program, 'u_time'),
            bright: gl.getUniformLocation(program, 'u_bright'), mode: gl.getUniformLocation(program, 'u_mode'),
            mask_color: gl.getUniformLocation(program, 'u_mask_color'), tolerance: gl.getUniformLocation(program, 'u_tolerance'),
            res_ratio: gl.getUniformLocation(program, 'u_res_ratio'), is_base: gl.getUniformLocation(program, 'u_is_base'),
            parallax: gl.getUniformLocation(program, 'u_parallax')
        };

        let isPlaying = true, rate = 0.7, manualPhase = 0, loopStart = 0, loopEnd = 1;
        let lastTime = Date.now(), accumTime = 0, targetViewScale = 1, viewScale = 1, targetViewPos = { x: 0, y: 0 }, viewPos = { x: 0, y: 0 };
        let parallax = { x: 0, y: 0, targetX: 0, targetY: 0 };

        const layerList = document.getElementById('layer-list'), viewport = document.getElementById('viewport');
        const rateSlider = document.getElementById('rate-slider'), rateNum = document.getElementById('rate-num'), timelineSlider = document.getElementById('timeline-slider'), timelineNum = document.getElementById('timeline-num');
        const abTrack = document.getElementById('ab-track-el'), abSelection = document.getElementById('ab-selection'), abHandleStart = document.getElementById('ab-handle-start'), abHandleEnd = document.getElementById('ab-handle-end');
        const playPauseBtn = document.getElementById('play-pause-btn'), playIcon = document.getElementById('play-icon'), pauseIcon = document.getElementById('pause-icon');
        function updatePlayBtn() { if (isPlaying) { playIcon.classList.add('hidden'); pauseIcon.classList.remove('hidden'); } else { playIcon.classList.remove('hidden'); pauseIcon.classList.add('hidden'); } }

        function updateUI() {
            const scrollPos = layerList.scrollTop;
            if (layers.length === 0) { layerList.innerHTML = '<div class="text-center py-20 opacity-20 italic text-xs">绛夊緟绱犳潗瀵煎叆...</div>'; document.getElementById('placeholder').style.display = 'flex'; canvas.style.display = 'none'; return; }
            document.getElementById('placeholder').style.display = 'none'; canvas.style.display = 'block';
            layerList.innerHTML = '';
            [...layers].reverse().forEach((layer, index) => {
                const i = layers.length - 1 - index;
                const div = document.createElement('div');
                layerMap.set(div, layer); // 鐗╃悊缁戝畾
                div.className = `layer-item glass-panel p-4 group ${layer.open ? 'open' : ''} ${layer.keyingOpen ? 'keying-open' : ''}`;
                div.innerHTML = `
                        <div class="flex items-center justify-between gap-3 collapsible-header cursor-pointer">
                        <div class="flex items-center gap-3 min-w-0 flex-1">
                            <div class="drag-handle opacity-20 hover:opacity-100 cursor-grab p-1 touch-none" data-index="${i}"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="3" y1="8" x2="21" y2="8"/><line x1="3" y1="16" x2="21" y2="16"/></svg></div>
                            <span class="text-[12px] font-black uppercase tracking-widest truncate pointer-events-none">${layer.name}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <div class="eye-btn btn-control-circle active-bounce-circle"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="${layer.visible ? 'text-blue-500' : 'opacity-20'}"><path d="M20 12s-3 7-10 7-10-7-10-7 3-7 10-7 10 7 10 7Z"/><circle cx="12" cy="12" r="3"/></svg></div>
                            <div class="w-6 h-6 flex items-center justify-center transition-transform ${layer.open ? 'rotate-180' : ''}"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="m6 9 6 6 6-6"/></svg></div>
                        </div>
                    </div>
                    <div class="layer-panel ${layer.open ? '' : 'hidden'} mt-3 space-y-3">
                        <div class="flex items-center justify-between p-3 rounded-2xl key-toggle cursor-pointer hover:bg-blue-500/5 transition-colors active-bounce-rect" style="background: var(--glass-bg); border: 1px solid var(--glass-border);">
                            <div class="flex items-center gap-3 text-[11px] font-black uppercase"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="text-blue-500"><path d="m2 22 1-1h3l9-9"/><path d="M12.1 7c0-1.5 1.5-3 3-3s3 1.5 3 3"/><path d="m19 11-4-4"/></svg>鍚歌壊鎶犲浘</div>
                        </div>
                        <div class="keying-panel ${layer.keyingOpen ? '' : 'hidden'} space-y-3">
                            <div class="relative aspect-video bg-checkerboard rounded-xl overflow-hidden cursor-crosshair group">
                                <canvas id="prev-${i}" class="block w-full h-full"></canvas>
                                <div id="mag-${i}" class="magnifier"><canvas width="120" height="120"></canvas><div class="magnifier-crosshair"></div></div>
                            </div>
                            <div class="flex items-center gap-2">
                                <div class="flex items-center gap-2 px-2 py-1.5 rounded-lg border flex-grow transition-all duration-500" style="background: var(--glass-bg); border-color: var(--glass-border)">
                                    <div class="relative w-4 h-4 rounded-sm cursor-pointer active-bounce-circle" style="background:${layer.maskColor}">
                                        <input type="color" class="absolute inset-0 opacity-0 cursor-pointer color-picker-trigger" value="${layer.maskColor}">
                                    </div>
                                    <input type="text" class="bg-transparent outline-none text-[11px] font-mono w-16 text-blue-500 hex-input font-black uppercase" value="${layer.maskColor}" onfocus="this.select()" onclick="event.stopPropagation()">
                                </div>
                                <button class="clear-keying-btn btn-control-circle active-bounce-circle text-red-500"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
                            </div>
                            <div class="flex items-center gap-3 px-1">
                                <span class="text-[10px] font-black opacity-40 uppercase">瀹瑰樊</span>
                                <input type="range" class="tolerance-slider grow" min="0" max="100" value="${layer.tolerance}">
                                <span class="text-[11px] font-mono text-blue-500 w-6 text-right font-black">${layer.tolerance}</span>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button class="mode-btn active-bounce-rect flex-1 py-2 rounded-xl text-[10px] font-black uppercase transition-all ${layer.mode === 'white' ? 'btn-mode-active' : 'opacity-40 border-transparent'}" data-mode="white" style="background: var(--glass-bg); color: var(--on-surface); transition: all 0.5s var(--easing);">鐧藉厜妯″紡</button>
                            <button class="mode-btn active-bounce-rect flex-1 py-2 rounded-xl text-[10px] font-black uppercase transition-all ${layer.mode === 'rainbow' ? 'btn-mode-active' : 'opacity-40 border-transparent'}" data-mode="rainbow" style="background: var(--glass-bg); color: var(--on-surface); transition: all 0.5s var(--easing);">鍏ㄦ伅妯″紡</button>
                            <button class="delete-layer-btn btn-control-circle active-bounce-circle text-red-500 ml-auto"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg></button>
                        </div>
                    </div>
                `;
                // 馃毃 缁熶竴浜や簰濮旀墭锛氬彇浠ｆ墍鏈夊垎鏁ｇ殑 onclick锛岀‘淇濆搷搴斾竾鏃犱竴澶?                div.addEventListener('click', (e) => {
                    const t = e.target;
                    
                    // 1. 鍒犻櫎鍥惧眰 (鍨冨溇妗?
                    if (t.closest('.delete-layer-btn')) {
                        e.stopPropagation();
                        if (confirm(`纭畾瑕佸垹闄ゅ浘灞?"${layer.name}" 鍚楋紵`)) {
                            layers.splice(layers.indexOf(layer), 1);
                            updateUI();
                            renderCanvas();
                        }
                    }
                    // 2. 鏄鹃殣鍒囨崲 (鐪肩潧)
                    else if (t.closest('.eye-btn')) {
                        e.stopPropagation();
                        layer.visible = !layer.visible;
                        renderCanvas();
                        updateUI();
                    }
                    // 3. 娓呴櫎鎶犲浘 (绾㈠弶)
                    else if (t.closest('.clear-keying-btn')) {
                        e.stopPropagation();
                        layer.maskColor = '#000000'; layer.maskRGB = [0, 0, 0]; layer.tolerance = 10;
                        renderCanvas();
                        updateUI();
                    }
                    // 4. 妯″紡鍒囨崲 (鐧藉厜/鍏ㄦ伅)
                    else if (t.closest('.mode-btn')) {
                        const m = t.closest('.mode-btn').dataset.mode;
                        layer.mode = m;
                        renderCanvas();
                        updateUI();
                    }
                    // 5. 鎶樺彔闈㈡澘 (鏍囬鏍?
                    else if (t.closest('.collapsible-header')) {
                        if (t.closest('.drag-handle') || t.closest('.eye-btn') || t.closest('.delete-layer-btn')) return;
                        layer.open = !layer.open;
                        updateUI();
                    }
                    // 6. 鍚歌壊闈㈡澘鍒囨崲
                    else if (t.closest('.key-toggle')) {
                        e.stopPropagation();
                        layer.keyingOpen = !layer.keyingOpen;
                        updateUI();
                        if (layer.keyingOpen) {
                            // 鏅鸿兘婊氬姩锛氬榻愮缉鐣ュ浘
                            setTimeout(() => { div.querySelector('.aspect-video').parentElement.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 100);
                        }
                    }
                });

                // 馃毃 鍘熺敓鍙栬壊鍣ㄨ仈鍔?                const colorInp = div.querySelector('.color-picker-trigger');
                if (colorInp) {
                    colorInp.oninput = (e) => {
                        const val = e.target.value.toUpperCase();
                        layer.maskColor = val;
                        const r = parseInt(val.slice(1, 3), 16), g = parseInt(val.slice(3, 5), 16), b = parseInt(val.slice(5, 7), 16);
                        layer.maskRGB = [r, g, b];
                        renderCanvas();
                        updateUI();
                    };
                }


                const handle = div.querySelector('.drag-handle');
                handle.style.touchAction = 'none'; // 寮哄埗绂佹娴忚鍣ㄩ粯璁ゆ墜鍔匡紝纭繚鎷栨嫿绮惧噯
                handle.onpointerdown = (e) => {
                    e.stopPropagation(); e.preventDefault();
                    handle.setPointerCapture(e.pointerId);
                    div.classList.add('sorting-active');
                    div.style.opacity = '0.5';
                    handle.isDragging = true;
                    handle.startY = e.clientY;
                };
                handle.onpointermove = (e) => {
                    if (!handle.isDragging) return; const deltaY = e.clientY - handle.startY; const parent = div.parentNode;
                    // 鐏垫晱搴﹁皟浼橈細25px 瑙﹀彂鎺掑簭
                    if (deltaY > 25 && div.nextElementSibling) {
                        parent.insertBefore(div.nextElementSibling, div);
                        handle.startY = e.clientY;
                        // 瀹炴椂鍚屾鍐呭瓨鏁扮粍
                        const idx = parseInt(handle.dataset.index);
                        const targetIdx = layers.indexOf(layers[idx]);
                        const nextIdx = layers.indexOf(layers[parseInt(div.nextElementSibling.querySelector('.drag-handle').dataset.index)]);
                        syncLayers();
                    }
                    else if (deltaY < -25 && div.previousElementSibling) {
                        parent.insertBefore(div, div.previousElementSibling);
                        handle.startY = e.clientY;
                        syncLayers();
                    }
                };
                handle.onpointerup = (e) => {
                    handle.releasePointerCapture(e.pointerId);
                    handle.isDragging = false;
                    div.style.opacity = '1';
                    div.classList.remove('sorting-active');
                    syncLayers();
                    renderCanvas();
                };

                // 宸茬粡杩佺Щ鍒颁笂闈㈢殑缁熶竴缁戝畾鍖猴紝姝ゅ鍒犻櫎鍐椾綑

                // --- 缁堟瀬缂濆悎锛氶潤榛樺垵濮嬪寲 Canvas 閫昏緫 (鍊熼壌 tool2 鐨勭ǔ鍋ユ€? ---
                const pCanvas = div.querySelector('canvas'), pCtx = pCanvas.getContext('2d'), mag = div.querySelector('.magnifier');
                const ratio = layer.img.width / layer.img.height;
                // 閿佸畾 Canvas 鐗╃悊鍒嗚鲸鐜囦负 16:9
                pCanvas.width = 400; pCanvas.height = 225;
                if (!layer.pScale) { layer.pScale = 1; layer.pOffset = { x: 0, y: 0 }; }

                const draw = () => {
                    pCtx.clearRect(0, 0, pCanvas.width, pCanvas.height);
                    pCtx.imageSmoothingEnabled = false;
                    // 璁＄畻鍩虹 Contain 澶у皬
                    const baseW = (ratio > pCanvas.width / pCanvas.height) ? pCanvas.width : (pCanvas.height * ratio);
                    const baseH = (ratio > pCanvas.width / pCanvas.height) ? (pCanvas.width / ratio) : pCanvas.height;
                    const drawW = baseW * layer.pScale, drawH = baseH * layer.pScale;

                    if (!pDrag) {
                        const leftEdge = (pCanvas.width - drawW) / 2 + layer.pOffset.x;
                        const rightEdge = leftEdge + drawW;
                        const topEdge = (pCanvas.height - drawH) / 2 + layer.pOffset.y;
                        const bottomEdge = topEdge + drawH;

                        const outLeft = leftEdge > 0;
                        const outRight = rightEdge < pCanvas.width;
                        const outTop = topEdge > 0;
                        const outBottom = bottomEdge < pCanvas.height;

                        if (outLeft || outRight || outTop || outBottom) {
                            const damp = 0.35;
                            if (outLeft) layer.pOffset.x += (-(pCanvas.width - drawW) / 2 - layer.pOffset.x) * damp;
                            if (outRight) layer.pOffset.x += ((pCanvas.width - drawW) / 2 - layer.pOffset.x) * damp;
                            if (outTop) layer.pOffset.y += (-(pCanvas.height - drawH) / 2 - layer.pOffset.y) * damp;
                            if (outBottom) layer.pOffset.y += ((pCanvas.height - drawH) / 2 - layer.pOffset.y) * damp;
                        }
                    }

                    const drawX = Math.floor((pCanvas.width - drawW) / 2 + layer.pOffset.x);
                    const drawY = Math.floor((pCanvas.height - drawH) / 2 + layer.pOffset.y);
                    pCtx.drawImage(layer.img, drawX, drawY, Math.floor(drawW), Math.floor(drawH));

                    // --- 鏀惧ぇ闀滃抚绾у悓姝ユ覆鏌?(璺熼殢榧犳爣瀹炴椂閲囨牱) ---
                    if (mag.style.display === 'block' && mag.dataset.mx) {
                        const mCtx = mag.querySelector('canvas').getContext('2d');
                        mCtx.imageSmoothingEnabled = false;
                        mCtx.clearRect(0, 0, 120, 120);
                        const mx = parseFloat(mag.dataset.mx), my = parseFloat(mag.dataset.my);
                        // 閲囨牱鍧愭爣鍔ㄦ€佽窡闅忛紶鏍?                        mCtx.drawImage(pCanvas, mx - 7.5, my - 7.5, 15, 15, 0, 0, 120, 120);
                    }
                };

                let pDrag = false, pLast = { x: 0, y: 0 };

                // 鍚姩鍥惧眰绉佹湁鍔ㄧ敾寰幆 (澧炲姞 _isAnimating 閿侊紝骞剁‘淇濇棫寰幆鑳借閲婃斁)
                if (layer._isAnimating) { layer._isAnimating = false; } // 寮哄埗鏍囪涓哄彲鍒锋柊
                if (!layer._isAnimating) {
                    layer._isAnimating = true;

                    let mountRetries = 0;
                    const pAnim = () => {
                        if (pCanvas.closest('body') === null) {
                            if (mountRetries++ < 10) { setTimeout(pAnim, 100); }
                            else { layer._isAnimating = false; }
                            return;
                        }
                        draw();
                        if (layer.open) requestAnimationFrame(pAnim);
                        else { layer._isAnimating = false; }
                    };
                    pAnim();
                }
                pCanvas.onpointerdown = (e) => {
                    if (e.button !== 0) return; e.preventDefault(); e.stopPropagation();
                    pCanvas.setPointerCapture(e.pointerId); pDrag = true; pLast = { x: e.clientX, y: e.clientY };
                    const r = pCanvas.getBoundingClientRect(), mx = (e.clientX - r.left) * (pCanvas.width / r.width), my = (e.clientY - r.top) * (pCanvas.height / r.height);
                    const baseW = (ratio > pCanvas.width / pCanvas.height) ? pCanvas.width : (pCanvas.height * ratio);
                    const baseH = (ratio > pCanvas.width / pCanvas.height) ? (pCanvas.width / ratio) : pCanvas.height;
                    const drawX = (pCanvas.width - baseW * layer.pScale) / 2 + layer.pOffset.x;
                    const drawY = (pCanvas.height - baseH * layer.pScale) / 2 + layer.pOffset.y;
                    const imgX = Math.floor(((mx - drawX) / (baseW * layer.pScale)) * layer.img.width);
                    const imgY = Math.floor(((my - drawY) / (baseH * layer.pScale)) * layer.img.height);

                    if (imgX >= 0 && imgX < layer.img.width && imgY >= 0 && imgY < layer.img.height) {
                        const tmpC = document.createElement('canvas'); tmpC.width = 1; tmpC.height = 1;
                        const tCtx = tmpC.getContext('2d'); tCtx.drawImage(layer.img, imgX, imgY, 1, 1, 0, 0, 1, 1);
                        const p = tCtx.getImageData(0, 0, 1, 1).data;
                        layer.maskColor = "#" + ((1 << 24) + (p[0] << 16) + (p[1] << 8) + p[2]).toString(16).slice(1).toUpperCase();
                        layer.maskRGB = [p[0], p[1], p[2]]; if (layer.tolerance === 0) layer.tolerance = 10;
                        div.querySelector('.hex-input').value = layer.maskColor;
                        div.querySelector('.hex-input').previousElementSibling.style.background = layer.maskColor;
                        renderCanvas();
                    }
                };
                pCanvas.onwheel = (e) => {
                    e.preventDefault(); e.stopPropagation();
                    layer.pScale = Math.max(0.5, Math.min(50, layer.pScale * (e.deltaY < 0 ? 1.1 : 0.9)));
                };
                pCanvas.onpointermove = (e) => {
                    const r = pCanvas.getBoundingClientRect();
                    const mx = (e.clientX - r.left) * (pCanvas.width / r.width);
                    const my = (e.clientY - r.top) * (pCanvas.height / r.height);

                    // 鏀惧ぇ闀滀綅缃窡闅忛紶鏍囷紝骞惰褰曢噰鏍峰潗鏍?                    mag.style.display = 'block';
                    mag.style.left = `${e.clientX - r.left - 60}px`;
                    mag.style.top = `${e.clientY - r.top - 60}px`;
                    mag.dataset.mx = mx; mag.dataset.my = my; // 浼犻€掔粰 draw() 寰幆

                    if (pDrag) {
                        let dx = (e.clientX - pLast.x) * (pCanvas.width / r.width);
                        let dy = (e.clientY - pLast.y) * (pCanvas.height / r.height);

                        const baseW = (ratio > pCanvas.width / pCanvas.height) ? pCanvas.width : (pCanvas.height * ratio);
                        const baseH = (ratio > pCanvas.width / pCanvas.height) ? (pCanvas.width / ratio) : pCanvas.height;

                        // 姗＄毊绛嬮樆灏奸€昏緫锛氬鏋滆竟缂樺凡缁忓嚭鐣岋紝鎷栨嫿浣嶇Щ鎵?3 鎶?                        const leftEdge = (pCanvas.width - (baseW * layer.pScale)) / 2 + layer.pOffset.x;
                        const rightEdge = leftEdge + (baseW * layer.pScale);
                        const topEdge = (pCanvas.height - (baseH * layer.pScale)) / 2 + layer.pOffset.y;
                        const bottomEdge = topEdge + (baseH * layer.pScale);

                        if ((dx > 0 && leftEdge > pCanvas.width * 0.5) || (dx < 0 && rightEdge < pCanvas.width * 0.5)) dx *= 0.3;
                        if ((dy > 0 && topEdge > pCanvas.height * 0.5) || (dy < 0 && bottomEdge < pCanvas.height * 0.5)) dy *= 0.3;

                        layer.pOffset.x += dx;
                        layer.pOffset.y += dy;
                        pLast = { x: e.clientX, y: e.clientY };
                    }

                    // 瀹炴椂榧犳爣浣嶇疆鍚歌壊棰勮
                    const baseW = (ratio > pCanvas.width / pCanvas.height) ? pCanvas.width : (pCanvas.height * ratio);
                    const baseH = (ratio > pCanvas.width / pCanvas.height) ? (pCanvas.width / ratio) : pCanvas.height;
                    const drawX = (pCanvas.width - baseW * layer.pScale) / 2 + layer.pOffset.x;
                    const drawY = (pCanvas.height - baseH * layer.pScale) / 2 + layer.pOffset.y;
                    const imgX = Math.floor(((mx - drawX) / (baseW * layer.pScale)) * layer.img.width);
                    const imgY = Math.floor(((my - drawY) / (baseH * layer.pScale)) * layer.img.height);

                    if (imgX >= 0 && imgX < layer.img.width && imgY >= 0 && imgY < layer.img.height) {
                        const tmpC = document.createElement('canvas'); tmpC.width = 1; tmpC.height = 1;
                        const tCtx = tmpC.getContext('2d'); tCtx.drawImage(layer.img, imgX, imgY, 1, 1, 0, 0, 1, 1);
                        const p = tCtx.getImageData(0, 0, 1, 1).data;
                        const curColor = "#" + ((1 << 24) + (p[0] << 16) + (p[1] << 8) + p[2]).toString(16).slice(1).toUpperCase();
                        div.querySelector('.hex-input').value = curColor;
                        div.querySelector('.hex-input').previousElementSibling.style.background = curColor;
                    }
                };
                pCanvas.onpointerup = (e) => { pDrag = false; pCanvas.releasePointerCapture(e.pointerId); };
                pCanvas.onmouseleave = () => { mag.style.display = 'none'; div.querySelector('.hex-input').value = layer.maskColor; div.querySelector('.hex-input').previousElementSibling.style.background = layer.maskColor; };
                div.querySelector('.tolerance-slider').oninput = (e) => { layer.tolerance = parseInt(e.target.value); e.target.nextElementSibling.textContent = layer.tolerance; renderCanvas(); };
                const hexInp = div.querySelector('.hex-input');
                hexInp.onchange = () => {
                    let val = hexInp.value.trim().toUpperCase(); if (!val.startsWith('#')) val = '#' + val;
                    if (/^#[0-9A-F]{6}$/.test(val)) {
                        layer.maskColor = val; const r = parseInt(val.slice(1, 3), 16), g = parseInt(val.slice(3, 5), 16), b = parseInt(val.slice(5, 7), 16);
                        layer.maskRGB = [r, g, b]; if (layer.tolerance === 0) layer.tolerance = 10; renderCanvas();
                        hexInp.previousElementSibling.style.background = val;
                    } else hexInp.value = layer.maskColor;
                };
                hexInp.onkeydown = (e) => { if (e.key === 'Enter') hexInp.blur(); };
                if (layer._needsScroll) { setTimeout(() => { div.scrollIntoView({ behavior: 'smooth', block: 'end' }); layer._needsScroll = false; }, 100); }
                layerList.appendChild(div);
            });
            layerList.scrollTop = scrollPos;
        }

        // 馃毃 鏁戝嚭鐨?syncLayers锛氭斁鍒伴《绾т綔鐢ㄥ煙锛屽鍔犻槻寰?        function syncLayers() {
            const items = Array.from(layerList.querySelectorAll('.layer-item'));
            if (items.length === 0) return;
            
            const oldBaseObj = layers[0];
            const newL = [...items].reverse().map(item => layerMap.get(item)).filter(Boolean);

            layers.forEach(l => l._oldBase = l.isBase);
            layers.splice(0, layers.length, ...newL);

            layers.forEach((l, idx) => {
                l.isBase = (idx === 0);
                if (l.isBase && !l._oldBase) l.visible = true;
            });

            // 澧炲姞瀹夊叏妫€鏌ワ細layers[0] 鍙兘宸茶娓呯┖
            if (layers[0]) {
                let baseDimChanged = !oldBaseObj || (layers[0].img.width !== oldBaseObj.img.width || layers[0].img.height !== oldBaseObj.img.height);
                if (baseDimChanged) {
                    const base = layers[0];
                    const pad = 40;
                    const availW = viewport.clientWidth - pad * 2;
                    const availH = viewport.clientHeight - pad * 2;
                    targetViewScale = Math.min(availW / base.img.width, availH / base.img.height) * 0.85;
                    viewScale = targetViewScale;
                    viewPos = { x: 0, y: 0 };
                }
            }

            items.forEach((item, index) => {
                const l = layers[layers.length - 1 - index];
                if (!l) return;
                const eyeSvg = item.querySelector('.eye-btn svg');
                if (eyeSvg) {
                    eyeSvg.classList.toggle('text-blue-500', l.visible);
                    eyeSvg.classList.toggle('opacity-20', !l.visible);
                }
            });
        }

        function renderCanvas() {
            if (layers.length === 0) {
                gl.clearColor(0, 0, 0, 0);
                gl.clear(gl.COLOR_BUFFER_BIT);
                return;
            }
            const base = layers[0]; // 馃毃 鐗╃悊閿佸畾绱㈠紩 0 涓哄簳鍥惧湴鍩?            if (canvas.width !== base.img.width) {
                canvas.width = base.img.width;
                canvas.height = base.img.height;
                gl.viewport(0, 0, canvas.width, canvas.height);
            }
            const now = Date.now();
            if (isPlaying) {
                accumTime += (now - lastTime) / 1000 * rate;
                manualPhase = loopStart + (accumTime % Math.max(0.01, loopEnd - loopStart));
                timelineSlider.value = manualPhase;
                timelineNum.value = (manualPhase * 100).toFixed(1) + '%';
            }
            lastTime = now;
            parallax.x += (parallax.targetX - parallax.x) * 0.08; parallax.y += (parallax.targetY - parallax.y) * 0.08;
            gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
            layers.forEach(l => {
                if (!l.visible) return;
                gl.uniform1f(uniforms.time, manualPhase);
                // 鏍稿績娓叉煋鍗忚 (绗﹀悎璐︽湰 2-24 & 104 鏉?:
                // 1. 鍗曞浘妯″紡锛氫寒搴?0.8 (搴曞浘涓庡厜鏁堝叡瀛?
                // 2. 澶氬浘妯″紡锛氬簳鍥?u_bright=0 (浠呮樉绀哄師鍥捐儗鏅?锛涘彔鍔犲眰 u_bright=0.8 (浠呮樉绀哄姩鎬佸厜鏁?
                let bVal = 0.8;
                if (layers.length > 1) {
                    bVal = l.isBase ? 0.0 : 0.8;
                }
                gl.uniform1f(uniforms.bright, bVal);
                gl.uniform1i(uniforms.mode, l.mode === 'rainbow' ? 1 : 0); gl.uniform1i(uniforms.is_base, l.isBase ? 1 : 0);
                gl.uniform2f(uniforms.parallax, parallax.x, parallax.y);
                const iA = l.img.width / l.img.height, cA = canvas.width / canvas.height;
                let rx = 1, ry = 1; if (iA > cA) ry = cA / iA; else rx = iA / cA; gl.uniform2f(uniforms.res_ratio, 1 / rx, 1 / ry);
                gl.uniform3f(uniforms.mask_color, l.maskRGB[0] / 255, l.maskRGB[1] / 255, l.maskRGB[2] / 255);
                gl.uniform1f(uniforms.tolerance, l.tolerance / 100);
                gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, l.tex); gl.uniform1i(uniforms.tex_base, 0);
                gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, l.tex); gl.uniform1i(uniforms.tex_light, 1);
                gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, l.tex); gl.uniform1i(uniforms.tex_mask, 2);
                gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, l.isBase ? gl.ZERO : gl.ONE);
                gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            });
            canvas.style.transform = `translate(-50%, -50%) translate(${viewPos.x}px, ${viewPos.y}px) scale(${viewScale})`;
        }

        function animate() {
            viewPos.x += (targetViewPos.x - viewPos.x) * 0.15;
            viewPos.y += (targetViewPos.y - viewPos.y) * 0.15;
            viewScale += (targetViewScale - viewScale) * 0.15;

            // 鐗╃悊寮规€у洖寮归€昏緫 (Elastic Snap-back)
            const margin = 150; // 杈圭紭瀹夊叏缂撳啿鍖?            const limitX = (canvas.width * viewScale) / 2 + viewport.clientWidth / 2 - margin;
            const limitY = (canvas.height * viewScale) / 2 + viewport.clientHeight / 2 - margin;
            if (Math.abs(targetViewPos.x) > limitX) targetViewPos.x *= 0.8;
            if (Math.abs(targetViewPos.y) > limitY) targetViewPos.y *= 0.8;

            renderCanvas();
            requestAnimationFrame(animate);
        }
        animate();

        const updateABUI = () => { abSelection.style.left = (loopStart * 100) + '%'; abSelection.style.width = ((loopEnd - loopStart) * 100) + '%'; abHandleStart.style.left = (loopStart * 100) + '%'; abHandleEnd.style.left = (loopEnd * 100) + '%'; document.getElementById('loop-start-num').value = (loopStart * 100).toFixed(1) + '%'; document.getElementById('loop-end-num').value = (loopEnd * 100).toFixed(1) + '%'; };

        const sync = (num, slider, scale, isTimeline) => {
            const focus = () => {
                setTimeout(() => num.select(), 0);
                if (isTimeline && isPlaying) { isPlaying = false; updatePlayBtn(); }
            };
            num.onfocus = focus; num.onclick = focus;
            num.onkeydown = (e) => { if (e.key === 'Enter') num.blur(); };
            num.onchange = () => {
                let v = parseFloat(num.value.replace(/[^\d.]/g, '')) || 0;
                // 鏁板€奸挸鍒朵笌鍗曚綅琛ラ綈
                if (isTimeline) v = Math.max(0, Math.min(100, v));
                else v = Math.max(0.1, Math.min(2.0, v));

                num.value = v.toFixed(1) + (isTimeline ? '%' : 'X');
                const normV = v / scale;
                slider.value = normV;

                if (isTimeline) { isPlaying = false; manualPhase = normV; accumTime = normV / rate; }
                else rate = normV;
                updatePlayBtn(); renderCanvas();
            };
            num.onwheel = (e) => { e.preventDefault(); let v = parseFloat(num.value.replace(/[^\d.]/g, '')) + (e.deltaY < 0 ? 0.1 : -0.1); num.value = v.toFixed(1) + (isTimeline ? '%' : 'X'); num.onchange(); };
            slider.oninput = () => { let v = parseFloat(slider.value); num.value = (v * scale).toFixed(1) + (isTimeline ? '%' : 'X'); if (isTimeline) { isPlaying = false; manualPhase = v; accumTime = v / rate; } else rate = v; updatePlayBtn(); renderCanvas(); };
        };
        sync(rateNum, rateSlider, 1, false); sync(timelineNum, timelineSlider, 100, true);
        const setupAB = (num, isStart) => {
            const focus = () => setTimeout(() => num.select(), 0); num.onfocus = focus; num.onclick = focus;
            num.onkeydown = (e) => { if (e.key === 'Enter') num.blur(); };
            num.onchange = () => {
                let v = parseFloat(num.value.replace(/[^\d.]/g, '')) || 0;
                // 馃毃 杈圭晫纭攣瀹氬崗璁?(Boundary Locking)
                v = Math.max(0, Math.min(100, v)) / 100;
                if (isStart) loopStart = Math.min(v, loopEnd - 0.01);
                else loopEnd = Math.max(v, loopStart + 0.01);
                updateABUI();
            };
            num.onwheel = (e) => { e.preventDefault(); let v = parseFloat(num.value.replace(/[^\d.]/g, '')) + (e.deltaY < 0 ? 0.1 : -0.1); num.value = v.toFixed(1) + '%'; num.onchange(); };
        };
        setupAB(document.getElementById('loop-start-num'), true); setupAB(document.getElementById('loop-end-num'), false);

        function handleFiles(files) {
            // 馃殌 椤烘粦鏀惰捣锛氱洿鎺ユ搷浣?DOM 閬垮厤鍏ㄩ噺閲嶇粯瀵艰嚧鐨勫崱椤?            document.querySelectorAll('.layer-item').forEach(el => {
                el.classList.remove('open', 'keying-open');
                const panel = el.querySelector('.layer-panel');
                if (panel) panel.classList.add('hidden');
                const kPanel = el.querySelector('.keying-panel');
                if (kPanel) kPanel.classList.add('hidden');
                const arrow = el.querySelectorAll('svg')[2];
                if (arrow) arrow.classList.remove('rotate-180');
            });
            layers.forEach(l => { l.open = false; l.keyingOpen = false; });

            Array.from(files).forEach(file => {
                const img = new Image(); img.onload = () => {
                    const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex);
                    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
                    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
                    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
                    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
                    layers.push({ img, tex, name: file.name, visible: true, open: false, isBase: layers.length === 0, mode: 'white', maskColor: '#000000', maskRGB: [0, 0, 0], tolerance: 10 });
                    // --- 鏍稿績鍗忚锛氬崟鍥?澶氬浘鑷姩璁╂浮 ---
                    if (layers.length === 1) {
                        layers[0].u_bright = 1.0; // 鍗曞浘淇濈暀鍏夋晥
                    } else {
                        layers[0].u_bright = 0.0; // 澶氬浘鏃跺簳鍥捐嚜鍔ㄩ€€浣?                    }
                    if (layers.length === 1) {
                        resize(); // 鐗╃悊鍒嗚鲸鐜囧榻?                        targetViewScale = Math.min(viewport.clientWidth / img.width, viewport.clientHeight / img.height) * 0.85;
                        viewScale = targetViewScale; targetViewPos = { x: 0, y: 0 }; viewPos = { x: 0, y: 0 };
                    }
                    updateUI();
                };
                img.src = URL.createObjectURL(file);
            });
        }
        const dropzone = document.getElementById('dropzone');
        dropzone.onclick = () => document.getElementById('file-input').click();
        dropzone.ondragover = (e) => { e.preventDefault(); dropzone.classList.add('drag-active'); };
        dropzone.ondragleave = () => dropzone.classList.remove('drag-active');
        dropzone.ondrop = (e) => { e.preventDefault(); dropzone.classList.remove('drag-active'); handleFiles(e.dataTransfer.files); };
        document.getElementById('file-input').onchange = (e) => { handleFiles(e.target.files); e.target.value = ''; };
        const getPos = (e) => { const r = abTrack.getBoundingClientRect(); return Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)); };
        let dragMode = null, dragOffset = 0;
        abHandleStart.onmousedown = (e) => { e.stopPropagation(); dragMode = 'start'; };
        abHandleEnd.onmousedown = (e) => { e.stopPropagation(); dragMode = 'end'; };
        abSelection.onmousedown = (e) => { e.stopPropagation(); dragMode = 'selection'; dragOffset = getPos(e) - loopStart; };
        window.onmousemove = (e) => {
            if (!dragMode) return;
            const p = getPos(e);
            if (dragMode === 'start') loopStart = Math.min(p, loopEnd - 0.01);
            else if (dragMode === 'end') loopEnd = Math.max(p, loopStart + 0.01);
            else if (dragMode === 'selection') {
                const dur = loopEnd - loopStart;
                loopStart = Math.max(0, Math.min(1 - dur, p - dragOffset));
                loopEnd = loopStart + dur;
            }
            updateABUI();
        };
        window.onmouseup = () => dragMode = null;

        playPauseBtn.onclick = () => { isPlaying = !isPlaying; updatePlayBtn(); };
        document.getElementById('reset-loop-btn').onclick = () => { loopStart = 0; loopEnd = 1; updateABUI(); };
        document.getElementById('clear-all-layers').onclick = () => {
            if (layers.length === 0) return;
            if (confirm('纭瑕佹竻绌烘墍鏈夊浘灞傚悧锛熸鎿嶄綔涓嶅彲鎾ら攢銆?)) {
                layers.length = 0;
                gl.clearColor(0, 0, 0, 0);
                gl.clear(gl.COLOR_BUFFER_BIT);
                updateUI();
                renderCanvas();
            }
        };
        document.getElementById('sidebar-toggle').onclick = () => {
            document.getElementById('main-sidebar').classList.toggle('collapsed');
            setTimeout(resize, 600); // 寰呭姩鐢荤粨鏉熷悗鏍″噯涓€娆?            resize(); // 绔嬪嵆鏍″噯涓€娆?        };
        document.getElementById('theme-toggle').onclick = () => {
            const d = document.body.classList.toggle('theme-dark');
            document.body.classList.toggle('theme-light', !d);
            document.querySelector('.sun-icon').classList.toggle('hidden', d);
            document.querySelector('.moon-icon').classList.toggle('hidden', !d);
        };
        document.getElementById('reset-view').onclick = () => {
            const base = layers.find(l => l.isBase) || layers[0];
            if (!base) return;
            targetViewScale = Math.min(viewport.clientWidth / base.img.width, viewport.clientHeight / base.img.height) * 0.85;
            targetViewPos = { x: 0, y: 0 };
        };
        viewport.onwheel = (e) => { e.preventDefault(); targetViewScale *= e.deltaY < 0 ? 1.1 : 0.9; };

        let viewDrag = false, vLast = { x: 0, y: 0 };
        viewport.onmousedown = (e) => { if (e.button === 0) { e.preventDefault(); viewDrag = true; vLast = { x: e.clientX, y: e.clientY }; } };
        window.addEventListener('mousemove', (e) => { if (!viewDrag) return; targetViewPos.x += e.clientX - vLast.x; targetViewPos.y += e.clientY - vLast.y; vLast = { x: e.clientX, y: e.clientY }; });
        window.addEventListener('mouseup', () => viewDrag = false);

        setTimeout(updateABUI, 100);
    