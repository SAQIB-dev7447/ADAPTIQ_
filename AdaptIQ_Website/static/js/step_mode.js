async function loadStepMode(content) {
    const list = document.getElementById('step-list');

    try {
        const response = await fetch('/api/generate/step_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();
        const steps = data.steps || [];

        list.innerHTML = steps.map((s, i) => `
            <div class="card shadow-sm border-0 mb-4 p-4 rounded-4 transition-all hover-lift">
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center fw-bold me-3" style="width: 32px; height: 32px;">${i + 1}</div>
                    <h5 class="fw-bold mb-0">${s.title}</h5>
                </div>
                <div class="text-secondary ms-5">
                    <p class="mb-3">${s.explanation}</p>
                    ${s.plain_english_formula ? `
                        <div class="bg-light p-3 rounded-3 small">
                            <span class="fw-bold text-muted">Plain English:</span> ${s.plain_english_formula}
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error("Step Mode Error:", error);
        list.innerHTML = `<div class="alert alert-danger">Failed to load step-by-step mode.</div>`;
    }
}

window.loadStepMode = loadStepMode;
