async function loadMindMap(content) {
    const root = document.getElementById('mermaid-root');

    try {
        const response = await fetch('/api/generate/mind_map', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();
        const code = data || "mindmap\n  root((No diagram generated))";

        // Mermaid rendering
        root.removeAttribute('data-processed');
        root.innerHTML = code;
        if (window.mermaid) {
            mermaid.run({
                nodes: [root]
            });
        }

    } catch (error) {
        console.error("Mind Map Error:", error);
        root.innerHTML = `<div class="alert alert-danger">Failed to render mind map.</div>`;
    }
}

window.loadMindMap = loadMindMap;
