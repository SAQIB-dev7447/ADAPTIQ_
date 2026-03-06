/**
 * read_easy.js — Renders ReadEasyOutput schema:
 * { intro: string, paragraphs: string[], summary_line: string }
 */
function renderReadEasy(data) {
    const panel = document.getElementById('panel-read_easy');
    if (!panel) return;

    const paras = (data.paragraphs || []).map(p => `
        <p class="mb-3 lh-lg">${p}</p>`).join('');

    panel.innerHTML = `
        <div class="card shadow-sm border-0 rounded-4 p-4">
            <h4 class="fw-bold mb-3"><i class="fas fa-book-open text-primary me-2"></i>Read Easy</h4>
            <p class="lead text-muted fst-italic border-start border-primary border-3 ps-3 mb-4">${data.intro || ''}</p>
            <div class="mb-4">${paras}</div>
            ${data.summary_line ? `
            <div class="alert alert-info border-0 rounded-3">
                <i class="fas fa-lightbulb me-2"></i><strong>Takeaway:</strong> ${data.summary_line}
            </div>` : ''}
        </div>`;
}

window.renderReadEasy = renderReadEasy;
