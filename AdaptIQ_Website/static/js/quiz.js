/**
 * quiz.js — Renders QuizOutput schema:
 * { questions: [{ question, options: [{ text, is_correct }], explanation }] }
 */
let _quizData = [];
let _quizAnswers = {};
let _quizSubmitted = false;

function renderQuiz(data) {
    const panel = document.getElementById('panel-quiz');
    if (!panel) return;

    _quizData = data.questions || [];
    _quizAnswers = {};
    _quizSubmitted = false;

    _renderQuizQuestions(panel);
}

function _renderQuizQuestions(panel) {
    if (!_quizData.length) {
        panel.innerHTML = `<div class="alert alert-warning m-4">No questions generated.</div>`;
        return;
    }

    const questionsHTML = _quizData.map((q, i) => `
        <div class="card shadow-sm border-0 rounded-4 p-4 mb-4" id="quiz-q-${i}">
            <h6 class="fw-bold mb-3">${i + 1}. ${q.question}</h6>
            <div class="options-list">
                ${q.options.map((opt, j) => `
                    <div class="form-check p-3 border rounded-3 mb-2"
                         style="cursor:pointer"
                         id="quiz-opt-${i}-${j}"
                         onclick="quizSelectOption(${i}, ${j})">
                        <input class="form-check-input" type="radio" name="q${i}" id="q${i}o${j}"
                               ${_quizAnswers[i] === j ? 'checked' : ''}>
                        <label class="form-check-label ms-2" for="q${i}o${j}">${opt.text}</label>
                    </div>`).join('')}
            </div>
            <div class="quiz-explanation d-none mt-3 alert alert-info border-0" id="quiz-exp-${i}">
                <small><i class="fas fa-info-circle me-1"></i><strong>Explanation:</strong> ${q.explanation}</small>
            </div>
        </div>`).join('');

    panel.innerHTML = `
        <div class="p-3">
            <h4 class="fw-bold mb-4"><i class="fas fa-question-circle text-primary me-2"></i>Quiz</h4>
            <div id="quiz-questions">${questionsHTML}</div>
            <div class="text-center mt-2 mb-4">
                <button onclick="quizSubmit()" class="btn btn-primary px-5 py-2 rounded-pill fw-bold shadow" id="quiz-submit-btn">
                    Submit Answers
                </button>
            </div>
            <div id="quiz-result" class="d-none text-center mb-4">
                <div class="display-4 fw-bold mb-2" id="quiz-score-display"></div>
                <p class="text-muted" id="quiz-score-text"></p>
            </div>
        </div>`;
}

function quizSelectOption(qIdx, optIdx) {
    if (_quizSubmitted) return;
    _quizAnswers[qIdx] = optIdx;

    // Update radio visual
    const q = document.getElementById(`quiz-q-${qIdx}`);
    if (!q) return;
    q.querySelectorAll('.form-check').forEach((el, j) => {
        el.classList.toggle('border-primary', j === optIdx);
        el.classList.toggle('bg-primary', j === optIdx);
        el.classList.toggle('bg-opacity-10', j === optIdx);
    });
    const radio = document.getElementById(`q${qIdx}o${optIdx}`);
    if (radio) radio.checked = true;
}

function quizSubmit() {
    if (_quizSubmitted) return;
    _quizSubmitted = true;

    const submitBtn = document.getElementById('quiz-submit-btn');
    if (submitBtn) submitBtn.disabled = true;

    let score = 0;

    _quizData.forEach((q, i) => {
        const selected = _quizAnswers[i];
        const correctIdx = q.options.findIndex(o => o.is_correct === true);

        // Colour-code options
        q.options.forEach((opt, j) => {
            const el = document.getElementById(`quiz-opt-${i}-${j}`);
            if (!el) return;
            if (j === correctIdx) {
                el.classList.add('border-success', 'bg-success', 'bg-opacity-10');
            } else if (j === selected && j !== correctIdx) {
                el.classList.add('border-danger', 'bg-danger', 'bg-opacity-10');
            }
        });

        if (selected === correctIdx) score++;

        // Show explanation
        const exp = document.getElementById(`quiz-exp-${i}`);
        if (exp) exp.classList.remove('d-none');
    });

    // Show result
    const total = _quizData.length;
    const pct = Math.round((score / total) * 100);
    const resultEl = document.getElementById('quiz-result');
    const scoreDisplay = document.getElementById('quiz-score-display');
    const scoreText = document.getElementById('quiz-score-text');

    if (resultEl) resultEl.classList.remove('d-none');
    if (scoreDisplay) {
        scoreDisplay.textContent = `${score}/${total}`;
        scoreDisplay.className = `display-4 fw-bold mb-2 ${pct >= 70 ? 'text-success' : 'text-danger'}`;
    }
    if (scoreText) scoreText.textContent = `${pct}% — ${pct >= 70 ? 'Great job!' : 'Keep practising!'}`;
}

window.renderQuiz = renderQuiz;
window.quizSelectOption = quizSelectOption;
window.quizSubmit = quizSubmit;
