from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from config import Config
import supabase_client
from routes.api import api as api_blueprint

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Register the API blueprint (upload, generate-tab, session-status routes)
app.register_blueprint(api_blueprint)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            supabase = supabase_client.get_supabase_client()
            response = supabase.auth.sign_up({"email": email, "password": password})
            flash('Registration successful! Please sign in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            import supabase_client as sc
            raw = sc.sign_in(email, password)   # returns raw dict from Supabase
            access_token = raw.get('access_token', '')
            user_obj = raw.get('user') or {}
            user_id = user_obj.get('id', '')
            user_email = user_obj.get('email', email)

            print(f"[LOGIN] user_id={user_id} token_len={len(access_token)}")  # debug

            if not user_id or not access_token:
                flash('Login failed: no token returned.', 'danger')
                return redirect(url_for('login'))

            session['user_id'] = user_id
            session['email'] = user_email
            session['access_token'] = access_token
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    try:
        supabase = supabase_client.get_supabase_client()
        supabase.auth.sign_out()
    except Exception:
        pass
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html', access_token=session.get('access_token', ''))


if __name__ == '__main__':
    app.run(debug=True)
