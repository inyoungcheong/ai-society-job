#!/usr/bin/env python3
"""
JSearch API Job Scraper for AI & Society Positions
With Gemini filtering for semantic relevance
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import re

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class JSearchJobScraper:
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }
        self.search_queries = [
            "responsible ai", "ai governance", "algorithmic fairness", "ai ethics",
            "digital ethics", "ai policy"
        ]
        self.priority_countries = ["US", "GB", "CA"]
        self.api_calls_made = 0
        self.max_calls_per_session = 25
        self.high_value_keywords = [
            'ai ethics', 'responsible ai', 'ai governance', 'algorithmic fairness',
            'ai safety', 'digital rights', 'technology policy', 'ai regulation'
        ]
        self.medium_value_keywords = [
            'artificial intelligence', 'machine learning', 'data ethics',
            'policy', 'governance', 'privacy', 'algorithm', 'transparency'
        ]

        if genai and self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-pro")
        else:
            self.gemini_model = None

    def search_jobs(self, query: str, country: str = "US", limit: int = 25) -> List[Dict]:
        jobs = []
        if self.api_calls_made >= self.max_calls_per_session:
            return []

        try:
            if not self.api_key:
                return []

            params = {
                'query': query,
                'page': '1',
                'num_pages': '1',
                'country': country,
                'date_posted': 'month',
                'employment_types': 'FULLTIME',
                'job_requirements': 'under_3_years_experience,more_than_3_years_experience'
            }
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
            self.api_calls_made += 1

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and 'data' in data:
                    for job_data in data['data']:
                        job = self.parse_job(job_data, query, country)
                        if job and job['relevance_score'] >= 30:
                            jobs.append(job)
        except:
            pass

        return jobs

    def parse_job(self, job_data: Dict, search_query: str, country: str) -> Dict:
        try:
            title = job_data.get('job_title', 'Unknown Position')
            company = job_data.get('employer_name', 'Unknown Company')
            location = self.format_location(job_data, country)
            description = job_data.get('job_description', '')
            apply_url = job_data.get('job_apply_link', '')
            job_url = job_data.get('job_google_link', apply_url)
            posted_date = self.parse_date(job_data.get('job_posted_at_datetime_utc', ''))
            salary_info = self.extract_salary(job_data)
            category = self.determine_category(title, description, company)
            job_type = self.determine_job_type(company)
            is_remote = job_data.get('job_is_remote', False)
            if is_remote:
                location = f"{location} (Remote)"

            relevance_score = self.calculate_relevance(title, description)

            job = {
                "title": title,
                "company": company,
                "location": location,
                "job_type": job_type,
                "category": category,
                "description": self.clean_description(description),
                "posting_date": posted_date,
                "deadline": None,
                "source_url": job_url,
                "source_site": "google_jobs",
                "tags": self.generate_tags(title, description, search_query, is_remote),
                "relevance_score": relevance_score,
                "salary_info": salary_info,
                "country": country,
                "is_remote": is_remote
            }

            return job
        except:
            return None

    def format_location(self, job_data: Dict, country: str) -> str:
        city = job_data.get('job_city', '')
        state = job_data.get('job_state', '')
        job_country = job_data.get('job_country', country)
        location_parts = [part for part in [city, state] if part]
        location = ', '.join(location_parts)
        return f"{location}, {job_country}" if location else job_country

    def parse_date(self, date_str: str) -> str:
        try:
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime("%Y-%m-%d")
            return datetime.now().strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def extract_salary(self, job_data: Dict) -> str:
        try:
            salary_min = job_data.get('job_min_salary')
            salary_max = job_data.get('job_max_salary')
            currency = job_data.get('job_salary_currency', 'USD')
            if salary_min and salary_max:
                return f"{currency} {salary_min:,} - {salary_max:,}"
            elif salary_min:
                return f"{currency} {salary_min:,}+"
            return ""
        except:
            return ""

    def determine_job_type(self, company: str) -> str:
        company_lower = company.lower()
        if any(term in company_lower for term in ['university', 'college', 'institute of technology']):
            return 'faculty'
        elif any(term in company_lower for term in ['government', 'federal', 'department', 'agency']):
            return 'government'
        elif any(term in company_lower for term in ['united nations', 'world bank', 'oecd', 'unesco']):
            return 'international'
        elif any(term in company_lower for term in ['foundation', 'nonprofit', 'ngo', 'institute']):
            return 'nonprofit'
        return 'industry'

    def determine_category(self, title: str, description: str, company: str) -> str:
        content = f"{title} {description} {company}".lower()
        if any(term in content for term in ['law', 'legal', 'attorney', 'regulation', 'compliance']):
            return 'law'
        elif any(term in content for term in ['policy', 'governance', 'government', 'regulatory']):
            return 'policy'
        elif any(term in content for term in ['engineer', 'engineering', 'developer', 'technical']):
            return 'technical'
        return 'research'

    def clean_description(self, description: str) -> str:
        clean_desc = re.sub(r'<[^>]+>', '', description)
        clean_desc = re.sub(r'\s+', ' ', clean_desc)
        return (clean_desc[:500] + "...") if len(clean_desc) > 500 else clean_desc.strip()

    def generate_tags(self, title: str, description: str, search_query: str, is_remote: bool) -> List[str]:
        tags = [search_query.title()]
        content = f"{title} {description}".lower()
        if 'artificial intelligence' in content or 'ai ' in content:
            tags.append("AI")
        if 'machine learning' in content or 'ml ' in content:
            tags.append("Machine Learning")
        if 'data science' in content:
            tags.append("Data Science")
        if 'ethics' in content:
            tags.append("Ethics")
        if 'policy' in content or 'governance' in content:
            tags.append("Policy")
        if 'safety' in content:
            tags.append("AI Safety")
        if 'research' in content:
            tags.append("Research")
        if is_remote:
            tags.append("Remote")
        return list(set(tags))

    def calculate_relevance(self, title: str, description: str) -> int:
        content = f"{title} {description}".lower()
        score = 60
        for keyword in self.high_value_keywords:
            if keyword in content:
                score += 15
        for keyword in self.medium_value_keywords:
            if keyword in content:
                score += 8
        for keyword in ['ai', 'ethics', 'policy', 'responsible']:
            if keyword in title.lower():
                score += 5
        return min(100, score)

    def scrape_all(self) -> List[Dict]:
        all_jobs = []
        for query in self.search_queries:
            for country in self.priority_countries:
                jobs = self.search_jobs(query, country)
                all_jobs.extend(jobs)
                time.sleep(0.5)
                if self.api_calls_made >= self.max_calls_per_session:
                    break
            if self.api_calls_made >= self.max_calls_per_session:
                break
        return self.remove_duplicates(all_jobs)

    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for job in jobs:
            url = job['source_url']
            if url not in seen:
                seen.add(url)
                unique.append(job)
        return unique

    def gemini_filter(self, jobs: List[Dict]) -> List[Dict]:
        if not self.gemini_model:
            print("⚠️ Gemini model not configured")
            return []

        prompt_template = """
You are an expert in AI policy, ethics, and governance.

Here is a job description:
---
{desc}
---

Would this position be considered *highly relevant* to the field of \"AI & Society\"? 
Respond with YES or NO.
"""
        filtered = []
        for job in jobs:
            try:
                prompt = prompt_template.format(desc=job["description"])
                response = self.gemini_model.generate_content(prompt)
                if "yes" in response.text.strip().lower():
                    filtered.append(job)
            except Exception as e:
                print(f"⚠️ Gemini error: {e}")
        return filtered

    def save_results(self, jobs: List[Dict], filename: str):
        os.makedirs('data', exist_ok=True)
        result = {
            "jobs": jobs,
            "metadata": {
                "total_jobs": len(jobs),
                "api_calls_used": self.api_calls_made,
                "last_update": datetime.now().isoformat(),
                "queries_searched": self.search_queries,
                "countries_searched": self.priority_countries
            }
        }
        with open(f"data/{filename}", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {filename} ({len(jobs)} jobs)")

def main():
    scraper = JSearchJobScraper()
    raw_jobs = scraper.scrape_all()
    scraper.save_results(raw_jobs, "jsearch_jobs_raw.json")

    filtered_jobs = scraper.gemini_filter(raw_jobs)
    scraper.save_results(filtered_jobs, "jsearch_gemini_jobs.json")
    return 0

if __name__ == "__main__":
    exit(main())

