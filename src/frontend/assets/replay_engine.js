/**
 * replay_engine.js  — F1 Replay clientside animation engine
 *
 * Strategy: Python builds the Plotly skeleton ONCE (track outline + N driver
 * traces with fixed trace indices). Every animation tick the browser calls
 * Plotly.restyle with just the new x/y arrays — zero WebSocket roundtrips.
 *
 * Trace layout in replay-graph (must match _build_replay_skeleton in callbacks.py):
 *   0  — track glow wide
 *   1  — track glow mid
 *   2  — track line
 *   3  — halo markers  (one per driver, batched)
 *   4  — driver dots + labels  (one trace, all drivers)
 *   5 … 4+N*TRAIL — trail segments  (N drivers × TRAIL_SEGS segments each)
 *
 * The store `store-replay-data` holds:
 *   { frames, total, drivers, colors, total_laps, track_x, track_y }
 * where frames[i].d[driver] = { x, y, speed }
 */

window._f1Replay = (function () {
    "use strict";

    const GRAPH_ID   = "replay-graph";
    const TRAIL_SEGS = 5;   // trail length in frames
    const TRACE_TRACK_START = 0;  // 3 track traces
    const TRACE_HALO  = 3;
    const TRACE_DOTS  = 4;
    const TRACE_TRAIL_START = 5;

    let _data      = null;   // full replay dataset from store
    let _frameIdx  = 0;
    let _playing   = false;
    let _rafHandle = null;
    let _lastTs    = null;
    let _msPerFrame = 120;   // advance one logical frame every N ms

    /* ── public API called by Dash clientside callbacks ── */

    function loadData(storeData) {
        if (!storeData || !storeData.frames || storeData.frames.length === 0) {
            _data = null;
            return;
        }
        _data    = storeData;
        _frameIdx = 0;
        _lastTs  = null;
    }

    function setPlaying(isPlaying) {
        _playing = !!isPlaying;
        if (_playing) {
            _lastTs = null;
            if (!_rafHandle) _rafHandle = requestAnimationFrame(_tick);
        } else {
            if (_rafHandle) { cancelAnimationFrame(_rafHandle); _rafHandle = null; }
        }
    }

    function seekTo(idx) {
        _frameIdx = Math.max(0, Math.min(idx, (_data ? _data.frames.length - 1 : 0)));
        _renderFrame(_frameIdx);
    }

    function reset() {
        _frameIdx = 0;
        _playing  = false;
        if (_rafHandle) { cancelAnimationFrame(_rafHandle); _rafHandle = null; }
        _renderFrame(0);
    }

    /* ── internal ── */

    function _tick(ts) {
        if (!_playing || !_data) { _rafHandle = null; return; }
        _rafHandle = requestAnimationFrame(_tick);

        if (_lastTs === null) { _lastTs = ts; return; }
        const elapsed = ts - _lastTs;
        if (elapsed < _msPerFrame) return;
        _lastTs = ts;

        _frameIdx = (_frameIdx + 1) % _data.frames.length;
        _renderFrame(_frameIdx);

        // Push slider value without triggering Python callback
        const slider = document.getElementById("replay-frame-slider");
        if (slider) {
            const nativeInput = slider.querySelector("input[type=range]");
            if (nativeInput) {
                nativeInput.value = _frameIdx;
                // Update Dash slider display without firing the callback chain
                nativeInput.dispatchEvent(new Event("input", { bubbles: false }));
            }
        }

        // Update HUD labels directly in DOM — zero React overhead
        _updateHUD(_frameIdx);
    }

    function _renderFrame(idx) {
        if (!_data) return;
        const graph = document.getElementById(GRAPH_ID);
        if (!graph || !graph._fullData) return;  // Plotly not ready yet

        const frames  = _data.frames;
        const drivers = _data.drivers;
        const frame   = frames[Math.min(idx, frames.length - 1)];
        const n       = drivers.length;

        // ── Dot positions ──────────────────────────────────────────────
        const dx = [], dy = [];
        for (const d of drivers) {
            const pt = frame.d[d] || { x: 0.5, y: 0.5 };
            dx.push(pt.x);
            dy.push(pt.y);
        }

        // ── Halo positions (same x/y, one trace batching all drivers) ──
        const styleUpdates = {
            [TRACE_HALO]: { x: [dx], y: [dy] },
            [TRACE_DOTS]: { x: [dx], y: [dy] },
        };

        // ── Trail segments ─────────────────────────────────────────────
        for (let di = 0; di < n; di++) {
            const drv = drivers[di];
            for (let seg = 0; seg < TRAIL_SEGS; seg++) {
                const fi0 = Math.max(0, idx - TRAIL_SEGS + seg);
                const fi1 = Math.max(0, idx - TRAIL_SEGS + seg + 1);
                const p0  = frames[fi0].d[drv] || { x: dx[di], y: dy[di] };
                const p1  = frames[fi1].d[drv] || { x: dx[di], y: dy[di] };
                const traceIdx = TRACE_TRAIL_START + di * TRAIL_SEGS + seg;
                styleUpdates[traceIdx] = { x: [[p0.x, p1.x]], y: [[p0.y, p1.y]] };
            }
        }

        // Single Plotly.restyle call — much faster than react/newPlot
        const traceIndices = Object.keys(styleUpdates).map(Number);
        const update = { x: [], y: [] };
        for (const i of traceIndices) {
            update.x.push(styleUpdates[i].x[0]);
            update.y.push(styleUpdates[i].y[0]);
        }
        try {
            Plotly.restyle(GRAPH_ID, update, traceIndices);
        } catch (e) { /* graph not ready */ }

        // Update leaderboard in DOM
        _updateLeaderboard(frame, drivers);
    }

    function _updateHUD(idx) {
        if (!_data) return;
        const frames = _data.frames;
        const total  = _data.total || 1;
        const laps   = _data.total_laps || 1;
        const frame  = frames[Math.min(idx, frames.length - 1)];

        const tSec  = frame.t || 0;
        const m     = Math.floor(tSec / 60);
        const s     = Math.floor(tSec % 60);
        const cs    = Math.floor((tSec % 1) * 100);
        const tFmt  = String(m).padStart(2, "0") + ":" +
                      String(s).padStart(2, "0") + "." +
                      String(cs).padStart(2, "0");

        const lapNow = Math.max(1, Math.min(laps, Math.floor(idx / total * laps) + 1));

        const elLap  = document.getElementById("replay-lap-num");
        const elTime = document.getElementById("replay-time-val");
        if (elLap)  elLap.textContent  = String(lapNow);
        if (elTime) elTime.textContent = tFmt;
    }

    function _updateLeaderboard(frame, drivers) {
        const container = document.getElementById("replay-leaderboard-body");
        if (!container || !_data) return;

        const rows = drivers.map(d => ({
            drv:   d,
            speed: (frame.d[d] || {}).speed || 0,
            color: _data.colors[d] || "#888",
        })).sort((a, b) => b.speed - a.speed);

        // Reuse existing DOM rows if count matches — avoids layout thrash
        const existing = container.querySelectorAll(".replay-lb-row");
        if (existing.length === rows.length) {
            rows.forEach((r, i) => {
                const row = existing[i];
                row.querySelector(".replay-lb-pos").textContent = String(i + 1);
                row.querySelector(".replay-lb-drv").textContent = r.drv;
                row.querySelector(".replay-lb-speed").textContent =
                    r.speed ? r.speed + " km/h" : "—";
                const dot = row.querySelector(".replay-lb-dot");
                if (dot) {
                    dot.style.background  = r.color;
                    dot.style.boxShadow   = "0 0 8px " + r.color;
                }
            });
        } else {
            // Full rebuild (first render or driver count changed)
            container.innerHTML = "";
            rows.forEach((r, i) => {
                const row   = document.createElement("div");
                row.className = "replay-lb-row";
                row.innerHTML =
                    `<div class="replay-lb-pos">${i + 1}</div>` +
                    `<div class="replay-lb-dot" style="background:${r.color};box-shadow:0 0 8px ${r.color}"></div>` +
                    `<div class="replay-lb-drv">${r.drv}</div>` +
                    `<div class="replay-lb-speed">${r.speed ? r.speed + " km/h" : "—"}</div>`;
                container.appendChild(row);
            });
        }
    }

    return { loadData, setPlaying, seekTo, reset };
}());