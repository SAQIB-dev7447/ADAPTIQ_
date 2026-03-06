/**
 * summary.js — Renders SummaryOutput schema:
 * { title: string, bullets: string[], key_terms: string[] }
 */
function renderSummary(data) {
    const panel = document.getElementById('panel-summary');
    if (!panel) return;

    const bullets = (data.bullets || []).map(b => `
        <li class="list-group-item border-0 px-0 py-3 d-flex align-items-start">
            <i class="fas fa-check-circle text-success mt-1 me-3 flex-shrink-0"></i>
            <span>${b}</span>
        </li>`).join('');

    const terms = (data.key_terms || []).map(t => `
        <span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 rounded-pill px-3 py-2 me-2 mb-2">${t}</span>
    `).join('');

    panel.innerHTML = `
        <div class="card shadow-sm border-0 rounded-4 p-4">
            <h4 class="fw-bold mb-3">${data.title || 'Summary'}</h4>
            <ul class="list-group list-group-flush border-0 mb-4">${bullets}</ul>
            ${terms ? `<div>
                <p class="text-muted small fw-bold mb-2 text-uppercase tracking-wide">Key Terms</p>
                <div class="d-flex flex-wrap">${terms}</div>
            </div>` : ''}
        </div>`;
}

window.renderSummary = renderSummary;
