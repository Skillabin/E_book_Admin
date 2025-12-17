import streamlit as st
import google.generativeai as genai
from streamlit_quill import st_quill
from datetime import datetime
import os

# --- AUTHENTICATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Please set your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HR E-Book Generator",
    page_icon="📘",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .reportview-container { background: #f5f5f5; }
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2c3e50; font-weight: 700; }
    .stButton>button { background-color: #2c3e50; color: white; border-radius: 5px; height: 3em; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #34495e; border: 1px solid white; }
    /* Increase height of the editor */
    iframe[title="streamlit_quill.st_quill"] { min-height: 600px; } 
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Settings")
    st.markdown("**System Status:** ✅ API Connected")
    st.markdown("---")
    st.markdown("**Mode:** Visual Editor (WYSIWYG)")

# --- PROMPT LOGIC (EXACTLY AS REQUESTED) ---
def build_prompt(community):
    return f"""
    You are an Expert Industry Analyst and Career Strategist with an IQ of 220. 
    Your task is to write a comprehensive, publication-ready E-Book for a IT and Non-IT Recruiting Agency targeting the specific community: '{community}'.

    **OBJECTIVE:**
    Generate a 10-15 page equivalent professional guide. The tone must be authoritative, motivational, 
    and strictly industry-focused but make it human refined for GenZ or Youth.
    
    **CONSTRAINTS:**
    1. NO storytelling, NO metaphors, NO fictional scenarios.
    2. NO conversational filler (e.g., "Let's dive in") or No Conversational Heading(e.g., "Defining...)
    3. Output MUST be valid, standalone HTML5 code with embedded CSS.
    4. The CSS must ensure the document looks like a professional whitepaper (Serif fonts for body, distinct headers, good line-height & padding, clear margins).
    5. Make it human refined for GenZ or Youth and make it humanized with a professional documnetation format.
    6. Avoid adding any of the instructions in the E Book content.
    7. Make sure that all the sections are formatted properly in bold, headers and sub headers)
    
    **INTERNAL MINDSET (Do not explicitly state this, but embody it):**
    - What is the Industry? -> Insights, trends.
    - What is there for Me? -> Roles, specific skills.
    - How do I enter? -> Actionable roadmaps.

    **REQUIRED E-BOOK STRUCTURE (Strictly follow this order and have a golden format same for every resume):**
    1. PREFACE (Brief executive summary)
    2. TABLE OF CONTENTS (Hyperlinked internally and Indexed Numbering tabular format)
    3. INTRODUCTION (Definition and scope of {community})
    4. INDUSTRY EVOLUTION (History and Future of that respective field)
    5. ROLES (Detailed job titles and hierarchies)
    6. SKILLS (Hard and Soft skills matrix)
    7. 10-YEAR GROWTH OUTLOOK (Future trends, AI impact)
    8. HOW TO PREPARE (Prerequisites and mindset)
    9. INTERPERSONAL & BEHAVIORAL SKILLS (Communication, leadership)
    10. LEARNING CURVE & ROADMAP (0-6 months, 6-12 months, 1-3 years)
    11. EXAMPLE PROJECTS (3 specific, real-world portfolio projects with descriptions)
    12. CERTIFICATIONS / COURSES / TOOLS (Specific names of tools and credentials)
    13. COMPANY EXAMPLES (Top tier, mid-tier, and startups hiring {community})
    14. SALARY RANGES & PERKS (Entry, Mid, Senior levels)
    15. CONCLUSION (Final actionable advice)
    16. APPENDIX & TEMPLATES (Checklists, resume keywords)

    **HTML STYLING REQUIREMENTS:**
    - Use a clean font-family (e.g., 'Merriweather', serif for text; 'Arial', sans-serif for headers).
    - Use <h2>, <h3> for sections.
    - Use <ul> and <li> for lists to make it scannable.
    - Use <div style="background-color: #f0f2f6; padding: 15px; border-left: 5px solid #2c3e50; margin: 10px 0;"> for key takeaway, Have text in proper black color text.
    - Do NOT include markdown blocks (```html). Just return the raw HTML code.
    - Make it  an editable E-Book through HTML.
    """

# --- MAIN APP ---
st.markdown("<h1 class='main-header'>📘 Professional HR E-Book Generator</h1>", unsafe_allow_html=True)
st.markdown("Generate, **visually edit**, and publish guides.")

col1, col2 = st.columns([2, 1])
with col1:
    target_community = st.text_input("Target Community / Job Role", placeholder="e.g., Data Scientists")
with col2:
    st.write("")
    st.write("")
    generate_btn = st.button("Generate E-Book")

# --- SESSION STATE ---
if 'ebook_content' not in st.session_state:
    st.session_state['ebook_content'] = ""

# --- GENERATION ---
if generate_btn:
    if not target_community:
        st.warning("Target community required.")
    else:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # Using 1.5 Pro for best adherence to your detailed prompt structure
            model = genai.GenerativeModel('gemini-2.5-flash') 
            
            with st.spinner(f"Drafting content for {target_community}..."):
                response = model.generate_content(build_prompt(target_community))
                
                # Clean up response for the Editor
                # We strip the outer HTML tags so the Editor can just focus on the body text
                clean_text = response.text.replace("```html", "").replace("```", "")
                clean_text = clean_text.replace("<!DOCTYPE html>", "")
                clean_text = clean_text.replace("<html>", "").replace("</html>", "")
                clean_text = clean_text.replace("<body>", "").replace("</body>", "")
                
                # Note: We try to keep the style block if possible, but some visual editors 
                # might strip it. The final download re-injects the professional styles.
                
                st.session_state['ebook_content'] = clean_text
            st.rerun() # Refresh to show editor

        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- VISUAL EDITOR ---
if st.session_state['ebook_content']:
    st.divider()
    st.subheader("✍️ Visual Editor")
    st.caption("Edit the content below directly (like a Word doc). Changes are saved for the download button.")
    
    # The Visual Editor Component
    edited_content = st_quill(
        value=st.session_state['ebook_content'],
        html=True,
        key="quill_editor",
        preserve_whitespace=True
    )

    st.divider()
    
    # WRAPPER FOR DOWNLOAD
    # We wrap the edited body content back into a full HTML file for the final download
    # This ensures that even if the editor stripped the CSS, the download looks professional.
    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="[https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&display=swap](https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&display=swap)" rel="stylesheet">
        <style>
            body {{ font-family: 'Merriweather', serif; line-height: 1.6; padding: 40px; max-width: 900px; margin: auto; color: #333; }}
            h1, h2, h3 {{ font-family: 'Helvetica Neue', sans-serif; color: #2c3e50; margin-top: 30px; }}
            ul {{ margin-bottom: 20px; }}
            li {{ margin-bottom: 10px; }}
            .highlight {{ background-color: #f0f2f6; padding: 15px; border-left: 5px solid #2c3e50; margin: 20px 0; }}
        </style>
    </head>
    <body>
        {edited_content}
    </body>
    </html>
    """
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        st.download_button(
            label="📥 Download Final E-Book",
            data=final_html,
            file_name=f"{target_community.replace(' ', '_')}_Guide.html" if target_community else "guide.html",
            mime="text/html"
        )
