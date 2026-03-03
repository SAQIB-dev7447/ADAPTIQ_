document.addEventListener('DOMContentLoaded', () => {
    console.log('AdaptIQ initialized');

    // Handle Quiz Option Selection
    const quizOptions = document.querySelectorAll('.quiz-option');
    quizOptions.forEach(option => {
        option.addEventListener('click', () => {
            const parent = option.closest('.options-container');
            const siblingOptions = parent.querySelectorAll('.quiz-option');

            // Remove active class from siblings
            siblingOptions.forEach(opt => {
                opt.classList.remove('border-primary', 'bg-primary', 'bg-opacity-10');
                const letter = opt.querySelector('.option-letter');
                if (letter) {
                    letter.classList.remove('bg-primary', 'text-white');
                    letter.classList.add('bg-light');
                }
                const check = opt.querySelector('.check-icon');
                if (check) check.classList.add('d-none');
                const radio = opt.querySelector('input[type="radio"]');
                if (radio) radio.checked = false;
            });

            // Add active class to clicked
            option.classList.add('border-primary', 'bg-primary', 'bg-opacity-10');
            const letter = option.querySelector('.option-letter');
            if (letter) {
                letter.classList.remove('bg-light');
                letter.classList.add('bg-primary', 'text-white');
            }
            const check = option.querySelector('.check-icon');
            if (check) check.classList.remove('d-none');
            const radio = option.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    // Text-to-Speech (TTS) Functionality
    const ttsButtons = document.querySelectorAll('.tts-btn');
    ttsButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const text = btn.dataset.text;
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                btn.innerHTML = '<i class="fas fa-volume-up me-2"></i> READ ALOUD';
                return;
            }

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.onstart = () => {
                btn.innerHTML = '<i class="fas fa-stop me-2"></i> STOP';
            };
            utterance.onend = () => {
                btn.innerHTML = '<i class="fas fa-volume-up me-2"></i> READ ALOUD';
            };
            window.speechSynthesis.speak(utterance);
        });
    });

    // Dashboard Char Counter
    const textarea = document.querySelector('.input-box');
    if (textarea) {
        textarea.addEventListener('input', function () {
            const count = this.value.length;
            const counter = document.getElementById('char-count');
            if (counter) counter.textContent = `${count.toLocaleString()} / 5,000 CHARACTERS`;
        });

        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                const btn = form.querySelector('button[type="submit"]');
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Adapting Content...';
                btn.disabled = true;
            });
        }
    }
});
