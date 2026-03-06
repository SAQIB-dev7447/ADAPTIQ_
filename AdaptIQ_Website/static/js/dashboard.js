/**
 * dashboard.js — AdaptIQ Dashboard Orchestrator
 *
 * RULES (from instruction file):
 *  - tabCache is a plain JS object in memory. NEVER use localStorage or sessionStorage.
 *  - Each tab click = at most ONE network request (memory cache is checked first).
 *  - No AI calls during upload.
 *  - All API requests include: Authorization: Bearer <token>
 */

// ── State ─────────────────────────────────────────────────────────────────────
let currentSessionId = null;
const tabCache = {};  // { tabName: responseData } — JS memory only, cleared on page reload

const VALID_TABS = ['summary', 'read_easy', 'focus_mode', 'step_by_step', 'mind_map', 'quiz'];

// Tab render functions defined in individual tab JS files
const TAB_RENDERERS = {
    summary: (data) => renderSummary(data),
    read_easy: (data) => renderReadEasy(data),
    focus_mode: (data) => renderFocusMode(data),
    step_by_step: (data) => renderStepByStep(data),
    mind_map: (data) => renderMindMap(data),
    quiz: (data) => renderQuiz(data),
};

// ── Upload Flow ───────────────────────────────────────────────────────────────

/**
 * Reads the active upload tab, builds a FormData, and POSTs to /api/upload.
 * ZERO AI calls happen here — only text extraction + Supabase session row creation.
 */
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

    if (pastePane.classList.contains('active')) {
        const text = document.getElementById('paste-content').value.trim();
        if (!text) { showUploadError(errorEl, 'Please paste some text first.'); return; }
        formData.append('source_type', 'paste');
        formData.append('content', text);

    } else if (urlPane.classList.contains('active')) {
        const url = document.getElementById('url-content').value.trim();
        if (!url) { showUploadError(errorEl, 'Please enter a URL.'); return; }
        formData.append('source_type', 'url');
        formData.append('url', url);

    } else if (pdfPane.classList.contains('active')) {
        const file = document.getElementById('pdf-file').files[0];
        if (!file) { showUploadError(errorEl, 'Please select a PDF file.'); return; }
        formData.append('source_type', 'pdf');
        formData.append('file', file);

    } else if (docxPane.classList.contains('active')) {
        const file = document.getElementById('docx-file').files[0];
        if (!file) { showUploadError(errorEl, 'Please select a DOCX file.'); return; }
        formData.append('source_type', 'docx');
        formData.append('file', file);

    } else {
        showUploadError(errorEl, 'Please select a content type.'); return;
    }

    const sourceName = document.getElementById('source-name').value.trim() || 'Untitled';
    formData.append('source_name', sourceName);

    // Set loading state
    uploadBtn.disabled = true;
    statusEl.classList.remove('d-none');
    statusTxt.textContent = 'Extracting content...';

    try {
        const res = await fetch('/api/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${ACCESS_TOKEN}` },
            body: formData,
        });
        const json = await res.json();

        if (!res.ok) {
            showUploadError(errorEl, json.error || 'Upload failed. Please try again.');
            return;
        }

        currentSessionId = json.session_id;
        statusTxt.textContent = `✅ "${json.source_name}" ready — click any tab to generate`;
        unlockAllTabs();

    } catch (err) {
        showUploadError(errorEl, `Network error: ${err.message}`);
    } finally {
        uploadBtn.disabled = false;
    }
}

// ── Tab Click Handler ─────────────────────────────────────────────────────────

/**
 * Called on every learning tab button click via onclick="handleTabClick('...')".
 *
 * Flow per instruction Section 11:
 *   1. Is data in tabCache?  → YES: render immediately, no network call.
 *   2. No cache?             → POST /api/generate/<tab_name>, store result, render.
 */
async function handleTabClick(tabName) {
    if (!currentSessionId) return;

    // ── MEMORY CACHE HIT ──
    if (tabCache[tabName] !== undefined) {
        TAB_RENDERERS[tabName](tabCache[tabName]);
        return;
    }

    // ── CACHE MISS: call API exactly once ──
    setTabState(tabName, 'loading');

    try {
        const res = await fetch(`/api/generate/${tabName}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${ACCESS_TOKEN}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: currentSessionId }),
        });
        const json = await res.json();

        if (!res.ok) {
            setTabState(tabName, 'error');
            showPanelError(tabName, json.error || 'Generation failed. Try again.');
            return;
        }

        // Store in JS memory — no more requests for this tab this session
        tabCache[tabName] = json.data;
        TAB_RENDERERS[tabName](json.data);
        setTabState(tabName, 'done');

    } catch (err) {
        setTabState(tabName, 'error');
        showPanelError(tabName, `Network error: ${err.message}`);
    }
}

// ── Tab State Helpers ─────────────────────────────────────────────────────────

function unlockAllTabs() {
    VALID_TABS.forEach(tab => {
        const btn = document.getElementById(`tab-${tab}`);
        if (!btn) return;
        btn.disabled = false;
        btn.classList.remove('tab-locked');
        btn.classList.add('tab-unlocked');
        const icon = btn.querySelector('.tab-icon');
        if (icon) icon.innerHTML = '<i class="fas fa-circle me-1 text-secondary" style="font-size:0.45rem;vertical-align:middle"></i>';
    });
}

function setTabState(tabName, state) {
    const btn = document.getElementById(`tab-${tabName}`);
    if (!btn) return;
    const icon = btn.querySelector('.tab-icon');

    if (state === 'loading') {
        btn.disabled = true;
        if (icon) icon.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span>';
    } else if (state === 'done') {
        btn.disabled = false;
        if (icon) icon.innerHTML = '<i class="fas fa-check-circle me-1 text-success"></i>';
        btn.classList.add('tab-done');
    } else if (state === 'error') {
        btn.disabled = false;
        if (icon) icon.innerHTML = '<i class="fas fa-exclamation-circle me-1 text-danger"></i>';
    }
}

// ── Error Helpers ─────────────────────────────────────────────────────────────

function showUploadError(el, message) {
    el.textContent = message;
    el.classList.remove('d-none');
    const statusEl = document.getElementById('upload-status');
    if (statusEl) statusEl.classList.add('d-none');
}

function showPanelError(tabName, message) {
    const panel = document.getElementById(`panel-${tabName}`);
    if (panel) {
        panel.innerHTML = `<div class="alert alert-danger m-4">${message}</div>`;
    }
}
