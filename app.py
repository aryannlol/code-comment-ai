from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import ast
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Serve the React UI
@app.route('/')
def serve_ui():
    return send_from_directory(app.static_folder, 'index.html')

# Python syntax validation
def is_python_syntax_valid(code):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"# ⚠️ Syntax Error at line {e.lineno}: {e.msg}\n# Possible fix: Check syntax near -> {e.text.strip() if e.text else ''}"

# API endpoint for generating comments
@app.route('/generate_comments', methods=['POST'])
def generate_comments():
    data = request.get_json()
    language = data.get('language', 'Python')
    code = data.get('code', '')

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    # Syntax check for Python
    syntax_ok = True
    syntax_message = ""
    if language == "Python":
        syntax_ok, syntax_message = is_python_syntax_valid(code)

    # Prepare code with syntax message if applicable
    code_for_prompt = syntax_message + "\n\n" + code if not syntax_message else code

    # Gemini API prompt
    prompt = f"""
    Generate professional and helpful comments for the following {language} code.

    Requirements:
    1. Add clear docstrings to functions and classes explaining purpose, parameters, and return values
    2. Add concise inline comments for complex logic
    3. Follow {language}-specific comment conventions
    4. DO NOT modify the actual code, only add comments
    5. Preserve all original code formatting and functionality

    Code to comment:
    ```{language.lower()}
    {code_for_prompt}
    ```

    Return ONLY the commented code.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        commented_code = response.text.strip().replace(f"```{language.lower()}", "").replace("```", "")

        return jsonify({
            'commented_code': commented_code,
            'syntax_ok': syntax_ok,
            'syntax_message': syntax_message if not syntax_ok else "No syntax errors found."
        })
    except Exception as e:
        return jsonify({'error': f"Gemini API Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)