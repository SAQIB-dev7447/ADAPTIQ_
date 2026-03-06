/**
 * step_mode.js — Renders StepByStepOutput schema:
 * { steps: [{ number, title, explanation }], closing: string }
 */
function renderStepByStep(data) {
    const panel = document.getElementById('panel-step_by_step');
    if (!panel) return;

    const steps = (data.steps || []).map(s => `
        <div class="d-flex align-items-start mb-4">
            <div class="step-number bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold flex-shrink-0 me-3"
                 style="width:40px;height:40px;font-size:1rem;">${s.number}</div>
            <div class="flex-grow-1">
                <h6 class="fw-bold mb-1">${s.title}</h6>
                <p class="text-muted mb-0 lh-lg">${s.explanation}</p>
            </div>
        </div>`).join('');

    panel.innerHTML = `
        <div class="card shadow-sm border-0 rounded-4 p-4">
            <h4 class="fw-bold mb-4"><i class="fas fa-list-ol text-primary me-2"></i>Step by Step</h4>
            <div class="steps-list">${steps}</div>
            ${data.closing ? `
            <div class="alert alert-success border-0 mt-3 rounded-3">
                <i class="fas fa-flag-checkered me-2"></i>${data.closing}
            </div>` : ''}
        </div>`;
}

window.renderStepByStep = renderStepByStep;
