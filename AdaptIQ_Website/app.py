from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
import json
import logging
import re

app = Flask(__name__)
app.secret_key = 'adaptiq_secret_key'

OLLAMA_URL = "http://localhost:11434/api/generate"

# Configure logging
logging.basicConfig(level=logging.INFO)

PROMPT_TEMPLATE = """
As an expert cognitive learning assistant, transform the following educational content into a structured format for three distinct learning modes. 

Return your response ONLY as a valid JSON object with the following structure:
{{
  "read_easy": {{
    "title": "Title for this section",
    "paragraphs": ["Paragraph 1 (max 3 sentences, simplified vocab)", "Paragraph 2..."],
    "key_terms": ["Term 1", "Term 2"]
  }},
  "focus_mode": {{
    "sections": [
      {{
        "heading": "Section Heading",
        "content": "Max 100 words of core content.",
        "recap": "A one-sentence summary."
      }}
    ],
    "mermaid_diagram": "graph TD\\nA --> B"
  }},
  "step_by_step": {{
    "steps": [
      {{
        "title": "Step Title",
        "explanation": "Clear breakdown of the concept/process.",
        "plain_english_formula": "Optional: Formula explained in words"
      }}
    ]
  }},
  "quiz_data": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer_index": 0
    }}
  ]
}}

CONTENT TO ADAPT:
{content}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/adapt', methods=['POST'])
def adapt():
    content = request.form.get('content')
    if not content:
        return redirect(url_for('dashboard'))

    # Prepare Ollama request
    prompt = PROMPT_TEMPLATE.format(content=content)
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        app.logger.info("Attempting adaptation with model: llama3")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        ai_raw_response = response.json().get('response', '')
    except Exception as e:
        app.logger.error(f"Ollama Request Failed: {e}")
        session['adapted_data'] = get_mock_data()
        return redirect(url_for('read_easy'))

    try:
        # Robust Parsing: Find JSON block in case AI adds preamble/postamble
        json_match = re.search(r'\{.*\}', ai_raw_response, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            adapted_data = json.loads(json_str)
        else:
            raise ValueError("No valid JSON block found in AI response")

        # Validate and Merge with Defaults
        final_data = validate_and_merge(adapted_data)
        
        session['adapted_data'] = final_data
        session['quiz_score'] = None  # Reset quiz score
        return redirect(url_for('read_easy'))
    except Exception as e:
        app.logger.error(f"Adaptation Error: {e}")
        app.logger.error(f"Raw response trace: {ai_raw_response if 'ai_raw_response' in locals() else 'No response'}")
        # Fallback to mock data for demo if Ollama is not running or fails
        session['adapted_data'] = get_mock_data()
        return redirect(url_for('read_easy'))

def validate_and_merge(data):
    """Ensures all required keys exist to prevent KeyErrors in templates."""
    defaults = get_mock_data()
    
    # Ensure top level keys
    for key in ['read_easy', 'focus_mode', 'step_by_step', 'quiz_data']:
        if key not in data:
            data[key] = defaults[key]
            
    # Sub-validation for critical structures
    if not isinstance(data['read_easy'], dict) or 'paragraphs' not in data['read_easy']:
        data['read_easy'] = defaults['read_easy']
    
    if not isinstance(data['focus_mode'], dict) or 'sections' not in data['focus_mode']:
        data['focus_mode'] = defaults['focus_mode']
        
    if not isinstance(data['step_by_step'], dict) or 'steps' not in data['step_by_step']:
        data['step_by_step'] = defaults['step_by_step']
        
    if not isinstance(data['quiz_data'], list) or len(data['quiz_data']) == 0:
        data['quiz_data'] = defaults['quiz_data']
        
    return data


@app.route('/read-easy')
def read_easy():
    data = session.get('adapted_data')
    if not data: return redirect(url_for('dashboard'))
    return render_template('read_easy.html', data=data['read_easy'])

@app.route('/focus')
def focus():
    data = session.get('adapted_data')
    if not data: return redirect(url_for('dashboard'))
    return render_template('focus.html', data=data['focus_mode'])

@app.route('/step-by-step')
def step_by_step():
    data = session.get('adapted_data')
    if not data: return redirect(url_for('dashboard'))
    return render_template('step_by_step.html', data=data['step_by_step'])

@app.route('/quiz')
def quiz():
    data = session.get('adapted_data')
    if not data: return redirect(url_for('dashboard'))
    return render_template('quiz.html', quiz=data['quiz_data'])

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    data = session.get('adapted_data')
    if not data: return redirect(url_for('dashboard'))
    
    # Calculate score
    score = 0
    quiz_data = data['quiz_data']
    for i, q in enumerate(quiz_data):
        user_answer = request.form.get(f'q{i}')
        if user_answer and int(user_answer) == q['correct_answer_index']:
            score += 1
    
    session['quiz_score'] = {
        "score": score,
        "total": len(quiz_data),
        "percentage": round((score / len(quiz_data)) * 100)
    }
    return redirect(url_for('results'))

@app.route('/results')
def results():
    results = session.get('quiz_score')
    if not results: return redirect(url_for('quiz'))
    return render_template('results.html', results=results)

def get_mock_data():
    return {
        "read_easy": {
            "title": "Machine Learning Basics",
            "paragraphs": ["Machine learning helps computers learn from data.", "It uses patterns to make predictions."],
            "key_terms": ["Algorithm", "Dataset"]
        },
        "focus_mode": {
            "sections": [{"heading": "Introduction", "content": "ML is a subset of AI.", "recap": "ML learns from patterns."}],
            "mermaid_diagram": "graph LR\\nData-->Model\\nModel-->Prediction"
        },
        "step_by_step": {
            "steps": [{"title": "Collect Data", "explanation": "Gather information.", "plain_english_formula": "Data = Input"}]
        },
        "quiz_data": [
            {"question": "What does ML stand for?", "options": ["Machine Learning", "Model Logic"], "correct_answer_index": 0}
        ]
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
