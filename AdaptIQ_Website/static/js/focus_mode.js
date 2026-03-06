/**
 * focus_mode.js — Renders FocusModeOutput schema:
 * { sections: [{ title, content, recap }] }
 * Progressive reveal: section content hidden until user clicks "Show".
 */
let focusCurrentSection = 0;

function renderFocusMode(data) {
    const panel = document.getElementById('panel-focus_mode');
    if (!panel) return;

    const sections = data.sections || [];
    focusCurrentSection = 0;

    const sectionHTML = sections.map((s, i) => `
        <div class="focus-section card border-0 shadow-sm rounded-4 mb-3 overflow-hidden"
             id="focus-section-${i}" style="opacity:${i === 0 ? '1' : '0.4'}; transition: opacity 0.3s;">
            <div class="card-body p-4">
                <div class="d-flex align-items-center justify-content-between mb-3">
                    <h5 class="fw-bold mb-0">
                        <span class="badge bg-primary rounded-pill me-2">${i + 1}</span>${s.title}
                    </h5>
                    ${i > 0 ? `<span class="badge bg-light text-muted border">Locked</span>` :
            `<span class="badge bg-success">Active</span>`}
                </div>
                <div class="focus-content" id="focus-content-${i}" ${i > 0 ? 'style="display:none"' : ''}>
                    <p class="mb-3 lh-lg">${s.content}</p>
                    <div class="alert alert-light border-start border-primary border-3 mb-3">
                        <small><strong>Recap:</strong> ${s.recap}</small>
                    </div>
                    ${i < sections.length - 1 ? `
                    <button class="btn btn-primary btn-sm rounded-pill" onclick="focusNext(${i + 1}, ${sections.length})">
                        Next Section <i class="fas fa-arrow-right ms-1"></i>
                    </button>` : `
                    <div class="alert alert-success border-0">
                        <i class="fas fa-trophy me-2"></i><strong>Complete!</strong> You've finished all sections.
                    </div>`}
                </div>
            </div>
        </div>`).join('');

    panel.innerHTML = `
        <div class="p-3">
            <h4 class="fw-bold mb-4"><i class="fas fa-crosshairs text-primary me-2"></i>Focus Mode
                <small class="text-muted fs-6 ms-2">Section 1 of ${sections.length}</small>
            </h4>
            ${sectionHTML}
        </div>`;
}

function focusNext(nextIdx, total) {
    const prev = document.getElementById(`focus-section-${nextIdx - 1}`);
    const next = document.getElementById(`focus-section-${nextIdx}`);
    const nextContent = document.getElementById(`focus-content-${nextIdx}`);
    const nextBadge = next ? next.querySelector('.badge.bg-light') : null;

    if (prev) prev.style.opacity = '0.7';
    if (next) next.style.opacity = '1';
    if (nextContent) nextContent.style.display = '';
    if (nextBadge) { nextBadge.textContent = 'Active'; nextBadge.className = 'badge bg-success'; }

    // Scroll to next section
    if (next) next.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

window.renderFocusMode = renderFocusMode;
window.focusNext = focusNext;
