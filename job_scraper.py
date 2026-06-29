from groq import Groq
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def search_jobs(job_title, location, num_jobs=5):
    try:
        url = f"https://remotive.com/api/remote-jobs?search={job_title}&limit={num_jobs}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        jobs = []
        for job in data.get("jobs", [])[:num_jobs]:
            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "link": job.get("url", ""),
                "snippet": job.get("description", "")[:500],
                "location": job.get("candidate_required_location", "Remote"),
                "salary": job.get("salary", "Not specified")
            })
        return jobs
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_job(job, cv_skills=""):
    prompt = f"""
    Analyze this job offer and return ONLY a JSON object:
    
    Job title: {job['title']}
    Company: {job['company']}
    Description: {job['snippet']}
    Candidate skills: {cv_skills if cv_skills else "Not provided"}
    
    Return ONLY this JSON:
    {{
        "summary": "2 sentence summary of the job",
        "requirements": ["req1", "req2", "req3"],
        "salary_estimate": "{job['salary']}",
        "match_score": 8,
        "why_apply": "one reason to apply"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    result = response.choices[0].message.content.strip()
    if "```" in result:
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
        result = result.strip()
    
    return json.loads(result)