import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os

# --- AUTHENTICATION ---
try:
    # This loads the key from Streamlit Cloud's secret storage
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Please set your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="E-Book Generator",
    page_icon="📘",
    layout="wide"
)

# --- CUSTOM CSS FOR APP UI ---
st.markdown("""
<style>
    .reportview-container {
        background: #f5f5f5;
    }
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2c3e50;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 5px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #34495e;
        border: 1px solid white;
    }
    /* Hide the deploy button if running locally to look cleaner */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Cleaned up, no key input) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Settings")
    st.markdown("**System Status:** ✅ API Connected")
    st.markdown("---")
    st.markdown("**Output Format:**\n- HTML 5\n- Publication Ready\n- Mobile Responsive")

# --- PROMPT GENERATION LOGIC ---
def build_prompt(community):
    return f"""
    You are an Expert Industry Analyst and Career Strategist with an IQ of 220. 
    Your task is to write a comprehensive, publication-ready E-Book for a IT and Non-IT Recruiting Agency targeting the specific community: '{community}'.

    **OBJECTIVE:**
    Generate a 10-15 page equivalent professional guide. The tone must be authoritative, motivational, and strictly industry-focused.
    
    **CONSTRAINTS:**
    1. NO storytelling, NO metaphors, NO fictional scenarios.
    2. NO conversational filler (e.g., "Let's dive in").
    3. Output MUST be valid, standalone HTML5 code with embedded CSS.
    4. The CSS must ensure the document looks like a professional whitepaper (Serif fonts for body, distinct headers, good line-height, clear margins).
    
    **INTERNAL MINDSET (Do not explicitly state this, but embody it):**
    - What is the Industry? -> Insights, trends.
    - What is it for Me? -> Roles, specific skills.
    - How do I enter? -> Actionable roadmaps.

    **REQUIRED E-BOOK STRUCTURE (Strictly follow this order):**
    1. PREFACE (Brief executive summary)
    2. TABLE OF CONTENTS (Hyperlinked internally and Indexed Numbering Table)
    3. INTRODUCTION (Definition and scope of {community})
    4. INDUSTRY EVALUATION (Market size, demand, global impact)
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
    - Use <div style="background-color: #f0f2f6; padding: 15px; border-left: 5px solid #2c3e50; margin: 10px 0;"> for key takeaways.
    - Do NOT include markdown blocks (```html). Just return the raw HTML code.
    """

# --- MAIN APP LOGIC ---
st.markdown("<h1 class='main-header'>📘 Professional E-Book Generator</h1>", unsafe_allow_html=True)
st.markdown("Generate comprehensive, industry-standard guides for any professional community.")

col1, col2 = st.columns([2, 1])

with col1:
    target_community = st.text_input("Target Community / Job Role", placeholder="e.g., Data Scientists, Full Stack Developers, Nursing Staff")

with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    generate_btn = st.button("Generate E-Book")

# --- GENERATION PROCESS ---
if generate_btn:
    if GEMINI_API_KEY == "YOUR_ACTUAL_API_KEY_HERE" or not GEMINI_API_KEY:
        st.error("⚠️ API Key Error: Please replace 'YOUR_ACTUAL_API_KEY_HERE' in the code with your real Gemini API key.")
    elif not target_community:
        st.warning("Please specify a target community.")
    else:
        try:
            # 1. Configure Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Using Gemini 1.5 Pro or Flash for larger context window
            model = genai.GenerativeModel('gemini-2.5-flash') 

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
            
            # 4. Process Response
            ebook_content = response.text
            
            # Strip markdown code blocks if the model accidentally includes them
            ebook_content = ebook_content.replace("```html", "").replace("```", "")
            
            progress_bar.progress(100)
            status_text.success("E-Book Generated Successfully!")

            # 5. Display & Download
            st.divider()
            
            # Create a download button
            st.download_button(
                label="📥 Download E-Book as HTML",
                data=ebook_content,
                file_name=f"{target_community.replace(' ', '_')}_Career_Guide.html",
                mime="text/html"
            )

            # Preview Section
            with st.expander("📖 Preview E-Book Content", expanded=True):
                st.components.v1.html(ebook_content, height=800, scrolling=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey; font-size: 12px;'>"
    f"Generated by Gemini AI • {datetime.now().year} • HR Professional Suite"
    "</div>", 
    unsafe_allow_html=True
)





