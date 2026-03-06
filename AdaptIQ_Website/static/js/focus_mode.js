let focusSections = [];

async function loadFocusMode(content) {
    const navList = document.getElementById('focus-nav-list');
    const display = document.getElementById('focus-content-display');

    try {
        const response = await fetch('/api/generate/focus_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();
        focusSections = data.sections || [];

        // Render Nav
        navList.innerHTML = focusSections.map((s, i) => `
            <button onclick="renderFocusSection(${i})" class="list-group-item list-group-item-action border-0 py-3 px-4 fw-medium focus-nav-item" id="focus-nav-${i}">
                ${s.heading}
                <div class="small opacity-50 fw-normal">Section ${i + 1}</div>
            </button>
        `).join('');

        // Show first section
        if (focusSections.length > 0) renderFocusSection(0);

    } catch (error) {
        console.error("Focus Error:", error);
        display.innerHTML = `<div class="alert alert-danger">Failed to load focus mode.</div>`;
    }
}

function renderFocusSection(index) {
    const section = focusSections[index];
    const display = document.getElementById('focus-content-display');

    // Update active state in nav
    document.querySelectorAll('.focus-nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`focus-nav-${index}`).classList.add('active');

    display.innerHTML = `
        <div class="card shadow-sm border-0 p-5 rounded-4 animate-fade-in">
            <h2 class="fw-bold mb-4">${section.heading}</h2>
            <div class="lead mb-5">${section.content}</div>
            <div class="recap-block p-4 bg-primary bg-opacity-10 border-start border-primary border-4 rounded-3">
                <h5 class="fw-bold text-primary mb-2">Section Recap</h5>
                <p class="mb-0 italic">${section.recap}</p>
            </div>
        </div>
    `;
}

window.loadFocusMode = loadFocusMode;
window.renderFocusSection = renderFocusSection;
