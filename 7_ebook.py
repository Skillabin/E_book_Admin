import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os

# --- AUTHENTICATION ---
try:
    # This loads the key from Streamlit Cloud's secret storage
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    # Fallback message
    st.error("Please set your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HR E-Book Generator",
    page_icon="📘",
    layout="wide"
)

# --- CUSTOM CSS FOR APP UI ---
st.markdown("""
<style>
    .reportview-container { background: #f5f5f5; }
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #2c3e50; font-weight: 700; }
    .stButton>button { background-color: #2c3e50; color: white; border-radius: 5px; height: 3em; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #34495e; border: 1px solid white; }
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
    st.markdown("**Output Format:**\n- HTML 5\n- Publication Ready\n- Mobile Responsive")

# --- PROMPT GENERATION LOGIC (Restored from 7_ebook.py) ---
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

# --- MAIN APP LOGIC ---
st.markdown("<h1 class='main-header'>📘 Professional HR E-Book Generator</h1>", unsafe_allow_html=True)
st.markdown("Generate comprehensive, industry-standard guides for any professional community.")

col1, col2 = st.columns([2, 1])

with col1:
    target_community = st.text_input("Target Community / Job Role", placeholder="e.g., Data Scientists, Nursing Staff")

with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    generate_btn = st.button("Generate E-Book")

# --- SESSION STATE INITIALIZATION ---
# This holds the book content in memory so we can edit it
if 'ebook_content' not in st.session_state:
    st.session_state['ebook_content'] = ""

# --- GENERATION PROCESS ---
if generate_btn:
    if not target_community:
        st.warning("Please specify a target community.")
    else:
        try:
            # 1. Configure Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Using 1.5 Pro because it is smarter and better at long formats
            model = genai.GenerativeModel('gemini-1.5-pro') 

            # 2. UI Feedback
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            status_text.markdown("### 🧠 Analyzing Industry Trends...")
            progress_bar.progress(20)

            # 3. Call API
            prompt = build_prompt(target_community)
            status_text.markdown(f"### ✍️ Drafting content for '{target_community}'... (This may take a moment)")
            progress_bar.progress(50)
            
            response = model.generate_content(prompt)
            
            # 4. Process & Save to Session State
            clean_text = response.text.replace("```html", "").replace("```", "")
            st.session_state['ebook_content'] = clean_text
            
            progress_bar.progress(100)
            status_text.success("E-Book Generated Successfully! Scroll down to Edit/Download.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# --- EDITOR & DOWNLOAD SECTION ---
# We only show this if there is content in the session state
if st.session_state['ebook_content']:
    st.divider()
    st.subheader("✍️ Edit Content")
    st.info("You can edit the HTML code below directly. The Preview and Download will update automatically when you click out of the box or press Ctrl+Enter.")

    # TEXT AREA for Editing
    # We use the session state as the initial value
    edited_html = st.text_area(
        "HTML Source Editor", 
        value=st.session_state['ebook_content'], 
        height=400
    )

    # ACTION BUTTONS
    col_d1, col_d2 = st.columns([1, 2])
    
    with col_d1:
        st.download_button(
            label="📥 Download Final HTML",
            data=edited_html,  # We download the EDITED version, not the original
            file_name=f"{target_community.replace(' ', '_')}_Career_Guide.html" if target_community else "Ebook.html",
            mime="text/html"
        )

    # PREVIEW SECTION
    st.divider()
    st.subheader("📖 Live Preview")
    # We preview the EDITED version
    st.components.v1.html(edited_html, height=800, scrolling=True)

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey; font-size: 12px;'>"
    f"Generated by Gemini AI • {datetime.now().year} • HR Professional Suite"
    "</div>", 
    unsafe_allow_html=True
)
