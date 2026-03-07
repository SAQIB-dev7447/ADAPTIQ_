/**
 * dashboard.js — AdaptIQ Dashboard (Multi-Page Architecture)
 *
 * After upload:
 *   - Stores session_id in memory + URL query param
 *   - Updates all feature card onclick handlers to pass session_id
 *   - Does NOT call AI — only text extraction + Supabase session creation
 */

// ── State ─────────────────────────────────────────────────────────────────────
let currentSessionId = new URLSearchParams(window.location.search).get("session_id") || null;

const FEATURE_ROUTES = {
    summary: "feature/summary",
    read_easy: "feature/read-easy",
    focus_mode: "feature/focus-mode",
    step_by_step: "feature/step-by-step",
    mind_map: "feature/mind-map",
    quiz: "feature/quiz",
};

// ── On Page Load: restore session_id from URL ─────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    if (currentSessionId) {
        updateFeatureCards(currentSessionId);
        showSessionReady(null); // show unlocked state without banner text
    }
});

// ── Upload Flow ───────────────────────────────────────────────────────────────

async function startAdaptation() {
    const uploadBtn = document.getElementById('upload-btn');
    const statusEl = document.getElementById('upload-status');
    const errorEl = document.getElementById('upload-error');
    const statusTxt = document.getElementById('upload-status-text');

    errorEl.classList.add('d-none');

    const formData = new FormData();

    // Detect which upload pane is active
    const pastePane = document.getElementById('upload-paste');
    const urlPane = document.getElementById('upload-url');
    const pdfPane = document.getElementById('upload-pdf');
    const docxPane = document.getElementById('upload-docx');

    if (pastePane.classList.contains('active') || pastePane.classList.contains('show')) {
        const text = document.getElementById('paste-content').value.trim();
        if (!text) { showUploadError(errorEl, 'Please paste some text first.'); return; }
        formData.append('source_type', 'paste');
        formData.append('content', text);

    } else if (urlPane.classList.contains('active') || urlPane.classList.contains('show')) {
        const url = document.getElementById('url-content').value.trim();
        if (!url) { showUploadError(errorEl, 'Please enter a URL.'); return; }
        formData.append('source_type', 'url');
        formData.append('url', url);

    } else if (pdfPane.classList.contains('active') || pdfPane.classList.contains('show')) {
        const file = document.getElementById('pdf-file').files[0];
        if (!file) { showUploadError(errorEl, 'Please select a PDF file.'); return; }
        formData.append('source_type', 'pdf');
        formData.append('file', file);

    } else if (docxPane.classList.contains('active') || docxPane.classList.contains('show')) {
        const file = document.getElementById('docx-file').files[0];
        if (!file) { showUploadError(errorEl, 'Please select a DOCX file.'); return; }
        formData.append('source_type', 'docx');
        formData.append('file', file);

    } else {
        showUploadError(errorEl, 'Please select a content type.'); return;
    }

    const sourceName = document.getElementById('source-name').value.trim() || 'Untitled';
    formData.append('source_name', sourceName);

    // Loading state
    uploadBtn.disabled = true;
    statusEl.classList.remove('d-none');
    statusTxt.textContent = 'Extracting content...';

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` },
            body: formData,
        });

        let json;
        try { json = await res.json(); }
        catch (e) { throw new Error('Server error — please try again.'); }

        if (!res.ok) {
            showUploadError(errorEl, json.error || 'Upload failed. Please try again.');
            return;
        }

        currentSessionId = json.session_id;

        // Update URL so reload/back keeps session
        const newUrl = `${window.location.pathname}?session_id=${currentSessionId}`;
        window.history.replaceState({}, '', newUrl);

        // Update all feature cards to carry the session_id
        updateFeatureCards(currentSessionId);

        // Show success banner
        showSessionReady(json.source_name);

        statusEl.classList.add('d-none');

    } catch (err) {
        showUploadError(errorEl, `Network error: ${err.message}`);
    } finally {
        uploadBtn.disabled = false;
    }
}

// ── Feature Card Updater ──────────────────────────────────────────────────────

/**
 * Updates every feature card's onclick to navigate with session_id.
 * This replaces the old unlockAllTabs() which only worked in the single-page layout.
 */
function updateFeatureCards(sessionId) {
    Object.entries(FEATURE_ROUTES).forEach(([key, path]) => {
        // Find the card by its onclick attribute pattern
        const cards = document.querySelectorAll(`[data-feature="${key}"]`);
        cards.forEach(card => {
            card.onclick = () => {
                window.location.href = `/${path}?session_id=${sessionId}`;
            };
            card.classList.add('feature-ready');
            card.style.opacity = '1';
        });
    });
}

// ── Success Banner ────────────────────────────────────────────────────────────

function showSessionReady(sourceName) {
    // Remove any existing banner
    const existing = document.getElementById('session-ready-banner');
    if (existing) existing.remove();

    // Only show banner when a new upload just happened
    if (!sourceName) return;

    const banner = document.createElement('div');
    banner.id = 'session-ready-banner';
    banner.className = 'alert alert-success mt-3 d-flex align-items-center gap-2';
    banner.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span><strong>"${sourceName}"</strong> is ready! Click any learning mode on the right →</span>`;

    const uploadBtn = document.getElementById('upload-btn');
    uploadBtn.insertAdjacentElement('afterend', banner);

    // Auto-dismiss after 6s
    setTimeout(() => banner.remove(), 6000);
}

// ── Error Helper ──────────────────────────────────────────────────────────────

function showUploadError(el, message) {
    el.textContent = message;
    el.classList.remove('d-none');
    const statusEl = document.getElementById('upload-status');
    if (statusEl) statusEl.classList.add('d-none');
}


