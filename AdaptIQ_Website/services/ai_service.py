import google.generativeai as genai
import requests
from config import Config

# Initialize Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

def generate_with_gemini(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def generate_with_groq(prompt):
    # Groq Llama implementation using requests (or groq-sdk if installed)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

def generate_summary(content):
    prompt = f"Summarize the following content in bullet points:\n\n{content}"
    return generate_with_gemini(prompt)

def generate_read_easy(content):
    prompt = f"Rewrite the following content for high comprehension (simple vocabulary, short sentences):\n\n{content}"
    return generate_with_gemini(prompt)

def generate_focus_mode(content):
    prompt = f"Split the following content into sections for progressive reveal. Return a JSON array of objects with 'heading', 'content', and 'recap':\n\n{content}"
    return generate_with_gemini(prompt)

def generate_step_mode(content):
    prompt = f"Break down the following content into logical step-by-step instructions:\n\n{content}"
    return generate_with_gemini(prompt)

def generate_mind_map(content):
    prompt = f"Create a Mermaid.js mindmap code for the following content. Start with 'mindmap':\n\n{content}"
    return generate_with_gemini(prompt)

def generate_quiz(content):
    prompt = f"Generate a 5-question multiple choice quiz based on the following content. Return ONLY as a JSON array:\n\n{content}"
    return generate_with_groq(prompt)
