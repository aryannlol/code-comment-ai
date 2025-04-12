import streamlit as st
import google.generativeai as genai
import ast
import os
from dotenv import load_dotenv

# 🔐 Load API key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# App UI
st.set_page_config(page_title="💡 AI Code Comments Generator", layout="centered")
st.title("🧠 AI Code Comments Generator")

# 🌐 Language selector
language = st.selectbox("Select Programming Language", ["Python", "JavaScript", "Java"])

# 📂 File upload
uploaded_file = st.file_uploader("Upload your code file", type=["py", "js", "java"])
code_input = ""

if uploaded_file:
    code_input = uploaded_file.read().decode("utf-8")
else:
    code_input = st.text_area("Or paste your code here:", height=300)

# ✅ Python syntax check
def is_python_syntax_valid(code):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"# ⚠️ Syntax Error at line {e.lineno}: {e.msg}\n# Possible fix: Check syntax near -> {e.text.strip() if e.text else ''}"

# 🧠 Generate Comments
if st.button("💬 Generate Comments") and code_input:
    syntax_ok = True
    syntax_message = ""
    
    if language == "Python":
        syntax_ok, syntax_message = is_python_syntax_valid(code_input)
    
    with st.container():
        st.subheader("🔍 Syntax Check")
        if syntax_ok:
            st.success("✅ No syntax errors found.")
        else:
            st.warning("⚠️ Syntax issue detected (Python only). Marked in comments.")

    with st.spinner("Generating comments..."):
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")

        code_for_prompt = syntax_message + "\n\n" + code_input if not syntax_ok else code_input

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
            response = model.generate_content(prompt)
            commented_code = response.text.strip().replace(f"```{language.lower()}", "").replace("```", "")
            st.subheader("📝 Commented Code")
            st.code(commented_code, language=language.lower())
            st.download_button("⬇️ Download commented code", commented_code, f"commented_code.{language[:2].lower()}")
        except Exception as e:
            st.error(f"Gemini API Error: {str(e)}")
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")
