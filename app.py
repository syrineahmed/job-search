import streamlit as st
from job_scraper import search_jobs, analyze_job

st.set_page_config(
    page_title="Smart Job Search",
    page_icon="💼",
    layout="wide"
)

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title("💼 Smart Job Search")
st.write("Search for jobs and get instant AI-powered analysis!")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    job_title = st.text_input("🔍 Job title", placeholder="Full Stack Developer")
with col2:
    location = st.text_input("📍 Location", placeholder="Tunis, Paris, London...")
with col3:
    num_jobs = st.number_input("📊 Number of results", min_value=1, max_value=20, value=5)
    
cv_skills = st.text_area(
    "💡 Your skills (optional — for better matching)",
    placeholder="React, Spring Boot, Docker, Python...",
    height=80
)

search_btn = st.button("🔍 Search Jobs", use_container_width=True)

if search_btn:
    if job_title and location:
        with st.spinner("Searching for jobs... 🔍"):
            jobs = search_jobs(job_title, location, num_jobs)
        
        if jobs:
            st.success(f"Found {len(jobs)} jobs! Analyzing with AI... 🤖")
            
            for i, job in enumerate(jobs):
                with st.spinner(f"Analyzing job {i+1}/{len(jobs)}..."):
                    try:
                        analysis = analyze_job(job, cv_skills)
                        
                        score = analysis["match_score"]
                        score_class = "score-high" if score >= 7 else "score-mid" if score >= 5 else "score-low"
                        
                        requirements_html = "".join([
                            f'<span class="requirement-tag">{r}</span>'
                            for r in analysis["requirements"]
                        ])
                        
                        st.markdown(f"""
                        <div class="job-card">
                            <div class="job-title">{job['title']}</div>
                            <span class="score-badge {score_class}">Match: {score}/10</span>
                            <p style="font-size:14px;color:#555;">{analysis['summary']}</p>
                            <p style="font-size:13px;color:#888;">💰 {analysis['salary_estimate']}</p>
                            <div>{requirements_html}</div>
                            <div class="why-apply">💡 {analysis['why_apply']}</div>
                            <a href="{job['link']}" target="_blank" style="font-size:13px;color:#3b82f6;">
                                View full job →
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    except Exception as e:
                        st.warning(f"Could not analyze job {i+1}: {e}")
        else:
            st.warning("No jobs found. Try different keywords!")
    else:
        st.warning("⚠️ Please enter a job title and location!")