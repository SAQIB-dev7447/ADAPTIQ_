function startAdaptation() {
    const content = document.getElementById('raw-content').value;
    if (!content) {
        alert("Please enter some content first!");
        return;
    }

    // Unlock the first tab (Summary) and trigger it
    unlockTab('summary');
    switchTab('summary');
    generateModule('summary', content);
}

function unlockTab(tabId) {
    const tab = document.getElementById(`tab-${tabId}`);
    tab.disabled = false;
    tab.classList.remove('tab-locked');
    tab.querySelector('.tab-status-icon').innerHTML = '<i class="fas fa-check-circle text-success me-2"></i>';
}

function switchTab(tabId) {
    const tabTrigger = new bootstrap.Tab(document.getElementById(`tab-${tabId}`));
    tabTrigger.show();
}

async function generateModule(tabId, content) {
    const tab = document.getElementById(`tab-${tabId}`);
    const statusIcon = tab.querySelector('.tab-status-icon');

    // Set loading state
    statusIcon.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>';

    try {
        // Call the specific loader function from the module's JS
        if (tabId === 'summary') {
            await window.loadSummary(content);
        } else if (tabId === 'read_easy') {
            await window.loadReadEasy(content);
        } else if (tabId === 'focus_mode') {
            await window.loadFocusMode(content);
        } else if (tabId === 'step_mode') {
            await window.loadStepMode(content);
        } else if (tabId === 'mind_map') {
            await window.loadMindMap(content);
        } else if (tabId === 'quiz') {
            await window.loadQuiz(content);
        }

        // Mark as complete and unlock NEXT logical tab if any
        statusIcon.innerHTML = '<i class="fas fa-check-circle text-success me-2"></i>';
        autoUnlockNext(tabId);

    } catch (error) {
        statusIcon.innerHTML = '<i class="fas fa-exclamation-circle text-danger me-2"></i>';
        console.error(`Error in ${tabId}:`, error);
    }
}

function autoUnlockNext(currentTabId) {
    const order = ['summary', 'read_easy', 'focus_mode', 'step_mode', 'mind_map', 'quiz'];
    const currentIndex = order.indexOf(currentTabId);
    if (currentIndex > -1 && currentIndex < order.length - 1) {
        const nextTabId = order[currentIndex + 1];
        unlockTab(nextTabId);
    }
}

// Add event listeners to tabs to trigger generation if unlocked but not yet run
document.addEventListener('DOMContentLoaded', () => {
    const contentArea = document.getElementById('raw-content');

    const tabs = ['summary', 'read_easy', 'focus_mode', 'step_mode', 'mind_map', 'quiz'];
    tabs.forEach(tabId => {
        const el = document.getElementById(`tab-${tabId}`);
        el.addEventListener('shown.bs.tab', () => {
            const content = contentArea.value;
            // Only generate if it hasn't been generated for this specific content yet
            // This is a simple flag, a hash-check would be better in production
            if (!el.dataset.generated && content) {
                generateModule(tabId, content);
                el.dataset.generated = 'true';
            }
        });
    });
});
