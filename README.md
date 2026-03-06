# 🧠 AdaptIQ - Learn the Way Your Brain Prefers

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/)
[![Groq Llama](https://img.shields.io/badge/AI-Groq%20Llama-green.svg)](https://groq.com/)

**AdaptIQ** is a state-of-the-art educational platform that uses advanced AI to transform complex information into the learning formats that work best for *you*. Whether you're a visual learner, a logic-driven student, or someone who needs concise summaries, AdaptIQ tailors content to your unique cognitive style.

---

## ✨ Key Learning Modes

AdaptIQ breaks down content into 6 distinct, high-impact formats:

| Mode | Description | Powered By |
| :--- | :--- | :--- |
| **🚀 Summaries** | High-impact bullet points capturing the core essence of any text. | Gemini 2.5 |
| **📖 Easy Read** | Complex language simplified for high comprehension with key term definitions. | Gemini 2.5 |
| **🎯 Focus Mode** | Progressive content reveal with section-by-section recaps to combat overwhelm. | Gemini 2.5 |
| **🪜 Step-by-Step** | Logical logic breakdowns with plain-English formulas. | Gemini 2.5 |
| **🗺️ Mind Map** | Dynamic, interactive visual structures using Mermaid.js. | Gemini 2.5 |
| **📝 Smart Quiz** | Instant multiple-choice tests to verify your understanding. | Groq Llama |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask
- **Frontend**: Bootstrap 5, Vanilla JS, Mermaid.js
- **AI Engines**: Google Gemini 2.5 Flash, Groq (Llama 3 70B)
- **Database/Cache**: Supabase (PostgreSQL)
- **Environment**: Secured with `.env` management

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Gemini & Groq API Keys

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SAQIB-dev7447/ADAPTIQ_.git
   cd ADAPTIQ_
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   SUPABASE_URL=your_supabase_url (optional)
   SUPABASE_KEY=your_supabase_key (optional)
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://127.0.0.1:5000`

---

## 📂 Project Structure

```text
AdaptIQ/
├── app.py              # Main Flask router
├── config.py           # Configuration management
├── services/           # AI Core logic
├── static/             # CSS, JS, and Images
├── templates/          # Standalone feature pages
└── supabase_client.py  # Database helper
```

---

## 🤝 Contributing

This project is built for **Parallel Development**. Each feature is independent, allowing team members to work on dedicated templates and scripts simultaneously.

1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
2. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the Branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

---

*Transforming information into intelligence. Built with ❤️ for the future of learning.*
