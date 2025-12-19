import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
import tempfile
import subprocess

# =====================
# SECRETS (Streamlit only)
# =====================
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ GEMINI_API_KEY not found in Streamlit Secrets.")
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
# PROMPT (UNCHANGED)
# =====================
def build_prompt(community):
 return f"""
You are an Expert Industry Analyst and Career Strategist.

Generate a **professional, publication-ready E-Book** for the community: "{community}".

Rules:
- Output ONLY valid standalone HTML5
- No markdown blocks
- Use <h2>, <h3>, <p>, <ul>, <li>
- Internal TOC hyperlinks must work
- Clean, professional formatting
- Editable document

    **INTERNAL MINDSET (Do not explicitly state this, but embody it):**
    - What is the Industry? -> Insights, trends.
    - What is there for Me? -> Roles, specific skills.
    - How do I enter? -> Actionable roadmaps.

 **REQUIRED E-BOOK STRUCTURE (Strictly follow this order and have a golden format same for every resume):**
    1. PREFACE (Brief executive summary)
    2. TABLE OF CONTENTS (Hyperlinked internally and strictly Indexed Numbering tabular format)
    3. INTRODUCTION (Definition and scope of {community})
    4. INDUSTRY EVOLUTION (History and Future of Development of that respective feild)
    4. INDUSTRY EVOLUTION (History and Future of Development of that respective field)
    5. ROLES (Detailed job titles and hierarchies)
    6. SKILLS (Hard and Soft skills matrix)
    7. 10-YEAR GROWTH OUTLOOK (Future trends, AI impact)
    8. HOW TO PREPARE (Prerequisites and mindset)
    9. INTERPERSONAL & BEHAVIORAL SKILLS (Communication, leadership)
    10. LEARNING CURVE & ROADMAP (0-6 months, 6-12 months, 1-3 years)
    11. EXAMPLE PROJECTS (3 specific, real-world portfolio projects with descriptions)
    12. CERTIFICATIONS / COURSES / TOOLS (Specific names of tools and credentials)
    13. COMPANY EXAMPLES (List of Top tier, mid-tier, and startups hiring {community} from perspective of Indian Job Market)
    14. SALARY RANGES & PERKS (Entry, Mid, Senior levels)
    15. CONCLUSION (Final actionable advice)
    16. APPENDIX & TEMPLATES (resume keywords)

**CONSTRAINTS:**
1. NO storytelling, NO metaphors, NO fictional scenarios.
2. NO conversational filler (e.g., "Let's dive in", "In this guide...") or Conversational Headings.
3. Make it human refined for GenZ/Youth but maintain a professional documentation format.
4. Do not output any preamble or post-script instructions;
5.Do NOT use Markdown syntax of any kind.
 This includes **bold**, *italic*, __underline__, backticks, or markdown headings.
 Use ONLY valid HTML tags such as <strong>, <em>, <ul>, <li>, <p>.
"""

# =====================
# HEADER
# =====================
st.markdown("<div class='main-header'>📘 HR E-Book Generator</div>", unsafe_allow_html=True)
st.caption("Generate → Edit directly → Download (HTML → Print to PDF)")

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
# GENERATION
# =====================
if generate_btn and target_community:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    with st.spinner("Generating professional E-Book…"):
        response = model.generate_content(build_prompt(target_community))

    html = response.text.replace("```html", "").replace("```", "")

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
    # DOWNLOAD SECTION (HTML → PRINT PDF)
    # =====================
    st.divider()
    st.subheader("📥 Download E-Book")

    st.info(
        "📄 To get PDF: Download HTML → Open it in your browser → "
        "Press Ctrl+P / Cmd+P → Save as PDF. "
        "All Table of Contents links will remain clickable."
    )

    st.download_button(
        label="⬇️ Download HTML (Printable & Editable)",
        data=st.session_state.edited_html,
        file_name=f"{target_community.replace(' ', '_')}_HR_Ebook.html",
        mime="text/html"
    )

# =====================
# FOOTER
# =====================
st.markdown("---")
st.caption(f"HR Publishing System • {datetime.now().year}")
