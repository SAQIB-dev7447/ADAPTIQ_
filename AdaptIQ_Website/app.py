from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import hashlib
from config import Config
from services import ai_service
import supabase_client

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/generate/<tab_type>', methods=['POST'])
def generate_tab(tab_type):
    content = request.json.get('content')
    user_id = session.get('user_id', 'anonymous')  # Placeholder user_id
    
    if not content:
        return jsonify({"error": "No content provided"}), 400

    content_hash = get_content_hash(content)
    
    # 1. Check Supabase cache
    cached = supabase_client.get_cached_content(user_id, content_hash, tab_type)
    if cached:
        return jsonify(cached['result_json'])

    # 2. Call specialized AI service
    try:
        if tab_type == 'summary':
            result = ai_service.generate_summary(content)
        elif tab_type == 'read_easy':
            result = ai_service.generate_read_easy(content)
        elif tab_type == 'focus_mode':
            result = ai_service.generate_focus_mode(content)
        elif tab_type == 'step_mode':
            result = ai_service.generate_step_mode(content)
        elif tab_type == 'mind_map':
            result = ai_service.generate_mind_map(content)
        elif tab_type == 'quiz':
            result = ai_service.generate_quiz(content)
        else:
            return jsonify({"error": "Invalid tab type"}), 400
        
        # 3. Save to cache and return
        supabase_client.save_content_cache(user_id, content_hash, tab_type, result)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error generating {tab_type}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
