from groq import Groq
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

def search_jobs(job_title, location, num_jobs=5):
    try:
        # Detect country from location text
        country = "gb"  # default
        location_lower = location.lower()

        if any(x in location_lower for x in ["tunis", "sfax", "sousse", "tunisia"]):
            country = "tn"
        elif any(x in location_lower for x in ["paris", "lyon", "france", "marseille"]):
            country = "fr"
        elif any(x in location_lower for x in ["london", "uk", "england", "britain"]):
            country = "gb"
        elif any(x in location_lower for x in ["usa", "new york", "california", "united states"]):
            country = "us"
        elif any(x in location_lower for x in ["berlin", "germany", "munich"]):
            country = "de"
        elif any(x in location_lower for x in ["canada", "toronto", "montreal"]):
            country = "ca"
        elif any(x in location_lower for x in ["australia", "sydney", "melbourne"]):
            country = "au"
        elif any(x in location_lower for x in ["remote", "worldwide", "anywhere"]):
            country = "gb"

        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": num_jobs,
            "what": job_title,
            "where": location,
            "content-type": "application/json"
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        jobs = []
        for job in data.get("results", [])[:num_jobs]:
            jobs.append({
                "title": job.get("title", ""),
                "company": job.get("company", {}).get("display_name", "Unknown"),
                "link": job.get("redirect_url", ""),
                "snippet": job.get("description", "")[:500],
                "location": job.get("location", {}).get("display_name", location),
                "salary": f"${int(job.get('salary_min', 0)):,} - ${int(job.get('salary_max', 0)):,}"
                          if job.get("salary_min") else "Not specified"
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
    Location: {job['location']}
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