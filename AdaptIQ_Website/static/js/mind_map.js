/**
 * mind_map.js — Renders MindMapOutput schema:
 * { mermaid: string, fallback_used: bool }
 * Uses Mermaid.js v10 (loaded in dashboard.html).
 */
function renderMindMap(data) {
    const panel = document.getElementById('panel-mind_map');
    if (!panel) return;

    const mermaidCode = (data.mermaid || '').trim() || 'mindmap\n  root((No diagram))';
    const isFallback = data.fallback_used === true;

    panel.innerHTML = `
        <div class="card shadow-sm border-0 rounded-4 p-4">
            <h4 class="fw-bold mb-3">
                <i class="fas fa-project-diagram text-primary me-2"></i>Mind Map
                ${isFallback ? '<small class="badge bg-warning text-dark ms-2">Fallback</small>' : ''}
            </h4>
            ${isFallback ? '<div class="alert alert-warning border-0 mb-3">A fallback diagram was used due to a generation issue.</div>' : ''}
            <div class="mermaid-wrapper border rounded-4 bg-light p-3 overflow-auto">
                <pre class="mermaid" id="mermaid-root" style="background:transparent;border:none;margin:0;">${mermaidCode}</pre>
            </div>
        </div>`;

    // Re-run Mermaid after injecting
    if (window.mermaid) {
        mermaid.initialize({ startOnLoad: false, theme: 'default' });
        const el = document.getElementById('mermaid-root');
        if (el) {
            el.removeAttribute('data-processed');
            mermaid.run({ nodes: [el] }).catch(err => {
                el.innerHTML = `<div class="alert alert-danger">Diagram render error: ${err.message}</div>`;
            });
        }
    }
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

window.renderMindMap = renderMindMap;
