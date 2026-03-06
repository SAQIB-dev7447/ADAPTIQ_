async function loadSummary(content) {
    const list = document.getElementById('summary-list');

    try {
        const response = await fetch('/api/generate/summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();

        // Expecting data to be a string or array of bullets
        const points = Array.isArray(data) ? data : data.split('\n').filter(p => p.trim());

        list.innerHTML = `<ul class="list-group list-group-flush border-0">
            ${points.map(p => `<li class="list-group-item border-0 px-0 py-3 d-flex align-items-start">
                <i class="fas fa-check-circle text-success mt-1 me-3"></i>
                <span>${p.replace(/^[-*•]\s*/, '')}</span>
            </li>`).join('')}
        </ul>`;

    } catch (error) {
        console.error("Summary Error:", error);
        list.innerHTML = `<div class="alert alert-danger">Failed to load summary.</div>`;
    }
}

window.loadSummary = loadSummary;
