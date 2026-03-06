let quizData = [];
let currentAnswers = {};

async function loadQuiz(content) {
    const list = document.getElementById('quiz-content');

    try {
        const response = await fetch('/api/generate/quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        });

        const data = await response.json();
        quizData = Array.isArray(data) ? data : data.questions || [];

        renderQuiz();

    } catch (error) {
        console.error("Quiz Error:", error);
        list.innerHTML = `<div class="alert alert-danger">Failed to generate quiz.</div>`;
    }
}

function renderQuiz() {
    const list = document.getElementById('quiz-content');

    list.innerHTML = quizData.map((q, i) => `
        <div class="card shadow-sm border-0 p-4 mb-4 rounded-4">
            <h5 class="fw-bold mb-3">${i + 1}. ${q.question}</h5>
            <div class="options-list">
                ${q.options.map((opt, optIdx) => `
                    <div class="form-check p-3 border rounded-3 mb-2 transition-all hover-bg-light" style="cursor: pointer;" onclick="selectOption(${i}, ${optIdx})">
                        <input class="form-check-input ms-0" type="radio" name="q${i}" id="q${i}o${optIdx}" ${currentAnswers[i] === optIdx ? 'checked' : ''}>
                        <label class="form-check-label ms-3" for="q${i}o${optIdx}">${opt}</label>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('') + `
        <div class="text-center mt-4">
            <button onclick="submitModuleQuiz()" class="btn btn-primary px-5 py-3 rounded-pill fw-bold shadow">Submit Answers</button>
        </div>
    `;
}

function selectOption(qIdx, optIdx) {
    currentAnswers[qIdx] = optIdx;
    renderQuiz();
}

function submitModuleQuiz() {
    let score = 0;
    quizData.forEach((q, i) => {
        if (currentAnswers[i] === q.correct_answer_index) score++;
    });

    const percentage = Math.round((score / quizData.length) * 100);
    document.getElementById('quiz-badge').innerText = `${score}/${quizData.length} Score`;
    document.getElementById('final-score').innerText = `${percentage}%`;
    document.getElementById('quiz-results').classList.remove('d-none');
    document.getElementById('quiz-content').classList.add('opacity-50');
    // Disable inputs
    document.querySelectorAll('input').forEach(i => i.disabled = true);
}

window.loadQuiz = loadQuiz;
window.selectOption = selectOption;
window.submitModuleQuiz = submitModuleQuiz;
