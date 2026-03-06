async function loadReadEasy(content) {
    const container = document.getElementById('read-easy-content');
    const keywordsContainer = document.getElementById('read-easy-keywords');

    // Show loading state if needed

    try {
        const response = await fetch('/api/generate/read_easy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();

        // Render Title
        document.getElementById('read-easy-title').innerText = data.title || "Adapted Reading";

        // Render Paragraphs
        container.innerHTML = data.paragraphs.map(p => `<p class="mb-4">${p}</p>`).join('');

        // Render Keywords
        keywordsContainer.innerHTML = data.key_terms.map(t =>
            `<span class="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-25 px-3 py-2 rounded-pill">${t}</span>`
        ).join('');

    } catch (error) {
        console.error("Read Easy Error:", error);
        container.innerHTML = `<div class="alert alert-danger">Failed to load reading mode.</div>`;
    }
}

// Export for use in dashboard.js
window.loadReadEasy = loadReadEasy;
