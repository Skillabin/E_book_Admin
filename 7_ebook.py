import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
import tempfile
import subprocess

# =====================
# CONFIG & SECRETS
# =====================
# Streamlit Secrets ONLY (no dotenv)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY not found. Please add it to Streamlit Secrets.")
    st.stop()

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(
    page_title="HR E-Book Generator",
    page_icon="📘",
    layout="wide"
)

# =====================
# UI STYLING
# =====================
st.markdown("""
<style>
body {
    background-color: #ffffff;
}
.main-header {
    font-size: 34px;
    font-weight: 700;
    color: #2c3e50;
}
hr {
    margin: 30px 0;
}
</style>
""", unsafe_allow_html=True)

# =====================
# PROMPT
# =====================
def build_prompt(community):
    return f"""
You are an Expert Industry Analyst and Career Strategist.

Generate a professional, publication-ready E-Book for the community: "{community}".

Rules:
- Output ONLY valid standalone HTML5
- Do NOT use Markdown syntax of any kind
- Use ONLY valid HTML tags (<strong>, <em>, <h2>, <h3>, <p>, <ul>, <li>)
- Internal TOC hyperlinks must work
- Clean, professional formatting
- Editable document

INTERNAL MINDSET (do not state explicitly):
- Industry insights & trends
- Roles & skill expectations
- Entry and growth roadmap

REQUIRED STRUCTURE (strict order):
1. PREFACE
2. TABLE OF CONTENTS (hyperlinked, numbered)
3. INTRODUCTION
4. INDUSTRY EVOLUTION
5. ROLES
6. SKILLS
7. 10-YEAR GROWTH OUTLOOK
8. HOW TO PREPARE
9. INTERPERSONAL & BEHAVIORAL SKILLS
10. LEARNING CURVE & ROADMAP
11. EXAMPLE PROJECTS
12. CERTIFICATIONS / COURSES / TOOLS
13. COMPANY EXAMPLES (India)
14. SALARY RANGES & PERKS
15. CONCLUSION
16. APPENDIX & TEMPLATES

CONSTRAINTS:
- NO storytelling
- NO metaphors
- NO conversational filler
- NO markdown (**bold**, *italic*, backticks, underscores)
- Return raw HTML only
"""

# =====================
# HEADER
# =====================
st.markdown("<div class='main-header'>📘 HR E-Book Generator</div>", unsafe_allow_html=True)
st.caption("Generate → Edit directly → Download (PDF)")

# =====================
# INPUT
# =====================
col1, col2 = st.columns([3, 1])

with col1:
    target_community = st.text_input(
        "Target Community / Role",
        placeholder="e.g., AIML Engineer, Data Analyst"
    )

with col2:
    st.write("")
    generate_btn = st.button("Generate E-Book")

# =====================
# SESSION STATE
# =====================
if "ebook_html" not in st.session_state:
    st.session_state.ebook_html = ""

if "edited_html" not in st.session_state:
    st.session_state.edited_html = ""

# =====================
# HTML → PDF (wkhtmltopdf)
# =====================
def html_to_pdf(html_content):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode="w",
        encoding="utf-8"
    ) as html_file:
        html_file.write(html_content)
        html_path = html_file.name

    pdf_path = html_path.replace(".html", ".pdf")

    subprocess.run(
        ["wkhtmltopdf", "--enable-local-file-access", html_path, pdf_path],
        check=True
    )

    return pdf_path

# =====================
# GENERATION
# =====================
if generate_btn and target_community:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    with st.spinner("Generating professional E-Book…"):
        response = model.generate_content(build_prompt(target_community))

    html = (
        response.text
        .replace("```html", "")
        .replace("```", "")
    )

    st.session_state.ebook_html = html
    st.session_state.edited_html = html

# =====================
# EDITABLE PREVIEW
# =====================
if st.session_state.ebook_html:

    st.divider()
    st.subheader("✏️ Editable Preview")

    editable_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Georgia, serif;
                padding: 30px;
                line-height: 1.7;
                background-color: #ffffff !important;
                color: #000000 !important;
            }}
            h2, h3 {{
                font-family: Arial, sans-serif;
            }}
            a {{
                color: #1e3799;
            }}
            .editor {{
                outline: none;
            }}
        </style>
    </head>
    <body>
        <div id="editor" class="editor" contenteditable="true">
            {st.session_state.edited_html}
        </div>
    </body>
    </html>
    """

    st.components.v1.html(editable_html, height=750, scrolling=True)

    # =====================
    # DOWNLOAD SECTION
    # =====================
    st.divider()
    st.subheader("📥 Download Edited E-Book")

    if st.button("📄 Generate PDF"):
        with st.spinner("Generating PDF…"):
            pdf_path = html_to_pdf(st.session_state.edited_html)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF",
                data=f,
                file_name=f"{target_community.replace(' ', '_')}_HR_Ebook.pdf",
                mime="application/pdf"
            )

        os.remove(pdf_path)

# =====================
# FOOTER
# =====================
st.markdown("---")
st.caption(f"HR Publishing System • {datetime.now().year}")
