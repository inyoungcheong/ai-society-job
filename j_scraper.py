#!/usr/bin/env python3
"""
JSearch API Job Scraper for AI & Society Positions
With Gemini filtering for semantic relevance - DEBUGGED VERSION
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
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

class JSearchJobScraper:
    def __init__(self):
        # API Configuration
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }
        
        # Search configuration
        self.search_queries = [
            "responsible ai", "ai governance", "algorithmic fairness", 
            "ai ethics", "digital ethics", "ai policy"
        ]
        self.priority_countries = ["US", "GB", "CA"]
        
        # API tracking
        self.api_calls_made = 0
        self.max_calls_per_session = 25
        
        # Keywords for relevance scoring
        self.high_value_keywords = [
            'ai ethics', 'responsible ai', 'ai governance', 'algorithmic fairness',
            'ai safety', 'digital rights', 'technology policy', 'ai regulation'
        ]
        self.medium_value_keywords = [
            'artificial intelligence', 'machine learning', 'data ethics',
            'policy', 'governance', 'privacy', 'algorithm', 'transparency'
        ]

        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                print("✅ Gemini model initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize Gemini: {e}")
        else:
            print("⚠️ Gemini not available (missing library or API key)")

    def search_jobs(self, query: str, country: str = "US", limit: int = 25) -> List[Dict]:
        """Search jobs using JSearch API with error handling"""
        jobs = []
        
        # Check API limit
        if self.api_calls_made >= self.max_calls_per_session:
            print(f"⚠️ API call limit reached ({self.max_calls_per_session})")
            return []

        try:
            if not self.api_key:
                print("❌ No RAPIDAPI_KEY found")
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
            
            print(f"🔍 Searching: '{query}' in {country}")
            
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
            self.api_calls_made += 1

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and 'data' in data:
                    for job_data in data['data']:
                        job = self.parse_job(job_data, query, country)
                        if job and job['relevance_score'] >= 30:
                            jobs.append(job)
                    print(f"✅ Found {len(jobs)} relevant jobs")
                else:
                    print(f"⚠️ No data in API response: {data.get('status', 'unknown')}")
            else:
                print(f"❌ API error {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout for '{query}' in {country}")
        except requests.exceptions.RequestException as e:
            print(f"🌐 Network error for '{query}' in {country}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error for '{query}' in {country}: {e}")

        return jobs

    def parse_job(self, job_data: Dict, search_query: str, country: str) -> Dict:
        """Parse job data with comprehensive error handling"""
        try:
            # Extract basic fields with fallbacks
            title = job_data.get('job_title', 'Unknown Position')
            company = job_data.get('employer_name', 'Unknown Company')
            location = self.format_location(job_data, country)
            description = job_data.get('job_description', '')
            
            # URL handling
            apply_url = job_data.get('job_apply_link', '')
            job_url = job_data.get('job_google_link', apply_url)
            
            # Date processing
            posted_date = self.parse_date(job_data.get('job_posted_at_datetime_utc', ''))
            
            # Salary extraction
            salary_info = self.extract_salary(job_data)
            
            # Categorization
            category = self.determine_category(title, description, company)
            job_type = self.determine_job_type(company)
            
            # Remote work detection
            is_remote = job_data.get('job_is_remote', False)
            if is_remote:
                location = f"{location} (Remote)"

            # Calculate relevance
            relevance_score = self.calculate_relevance(title, description)

            job = {
                "title": title,
                "company": company,
                "location": location,
                "job_type": job_type,
                "category": category,
                "description": self.clean_description(description),
                "full_description": description,  # Keep for Gemini
                "posting_date": posted_date,
                "deadline": None,
                "source_url": job_url,
                "source_site": "google_jobs",
                "tags": self.generate_tags(title, description, search_query, is_remote),
                "relevance_score": relevance_score,
                "salary_info": salary_info,
                "country": country,
                "is_remote": is_remote,
                "search_query": search_query
            }

            return job
            
        except Exception as e:
            print(f"⚠️ Error parsing job: {e}")
            return None

    def format_location(self, job_data: Dict, country: str) -> str:
        """Format location with fallbacks"""
        city = job_data.get('job_city', '')
        state = job_data.get('job_state', '')
        job_country = job_data.get('job_country', country)
        
        location_parts = [part for part in [city, state] if part]
        location = ', '.join(location_parts)
        
        return f"{location}, {job_country}" if location else job_country

    def parse_date(self, date_str: str) -> str:
        """Parse date with multiple format support"""
        try:
            if not date_str:
                return datetime.now().strftime("%Y-%m-%d")
                
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime("%Y-%m-%d")
            
            return datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            print(f"⚠️ Date parsing error: {e}")
            return datetime.now().strftime("%Y-%m-%d")

    def extract_salary(self, job_data: Dict) -> str:
        """Extract salary information safely"""
        try:
            salary_min = job_data.get('job_min_salary')
            salary_max = job_data.get('job_max_salary')
            currency = job_data.get('job_salary_currency', 'USD')
            
            if salary_min and salary_max:
                return f"{currency} {salary_min:,} - {salary_max:,}"
            elif salary_min:
                return f"{currency} {salary_min:,}+"
            return ""
        except Exception as e:
            print(f"⚠️ Salary extraction error: {e}")
            return ""

    def determine_job_type(self, company: str) -> str:
        """Determine job type based on company"""
        company_lower = company.lower()
        
        if any(term in company_lower for term in ['university', 'college', 'institute of technology']):
            return 'faculty'
        elif any(term in company_lower for term in ['government', 'federal', 'department', 'agency']):
            return 'government'
        elif any(term in company_lower for term in ['united nations', 'world bank', 'oecd', 'unesco']):
            return 'international'
        elif any(term in company_lower for term in ['foundation', 'nonprofit', 'ngo', 'institute']):
            return 'nonprofit'
        else:
            return 'industry'

    def determine_category(self, title: str, description: str, company: str) -> str:
        """Determine category based on content"""
        content = f"{title} {description} {company}".lower()
        
        if any(term in content for term in ['law', 'legal', 'attorney', 'regulation', 'compliance']):
            return 'legal'
        elif any(term in content for term in ['policy', 'governance', 'government', 'regulatory']):
            return 'policy'
        elif any(term in content for term in ['engineer', 'engineering', 'developer', 'technical']):
            return 'technical'
        else:
            return 'research'

    def clean_description(self, description: str) -> str:
        """Clean description for display"""
        try:
            # Remove HTML tags
            clean_desc = re.sub(r'<[^>]+>', '', description)
            # Normalize whitespace
            clean_desc = re.sub(r'\s+', ' ', clean_desc)
            # Limit length
            if len(clean_desc) > 500:
                clean_desc = clean_desc[:500] + "..."
            return clean_desc.strip()
        except Exception as e:
            print(f"⚠️ Description cleaning error: {e}")
            return description[:500] if description else ""

    def generate_tags(self, title: str, description: str, search_query: str, is_remote: bool) -> List[str]:
        """Generate relevant tags"""
        tags = [search_query.title()]
        content = f"{title} {description}".lower()
        
        # Technology tags
        if any(term in content for term in ['artificial intelligence', 'ai ']):
            tags.append("AI")
        if any(term in content for term in ['machine learning', 'ml ']):
            tags.append("Machine Learning")
        if 'data science' in content:
            tags.append("Data Science")
        
        # Field tags
        if 'ethics' in content:
            tags.append("Ethics")
        if any(term in content for term in ['policy', 'governance']):
            tags.append("Policy")
        if 'safety' in content:
            tags.append("AI Safety")
        if 'research' in content:
            tags.append("Research")
        
        # Work type
        if is_remote:
            tags.append("Remote")
        
        return list(set(tags))  # Remove duplicates

    def calculate_relevance(self, title: str, description: str) -> int:
        """Calculate relevance score"""
        content = f"{title} {description}".lower()
        score = 60  # Base score
        
        # High value keywords
        for keyword in self.high_value_keywords:
            if keyword in content:
                score += 15
        
        # Medium value keywords
        for keyword in self.medium_value_keywords:
            if keyword in content:
                score += 8
        
        # Title bonus
        title_keywords = ['ai', 'ethics', 'policy', 'responsible']
        for keyword in title_keywords:
            if keyword in title.lower():
                score += 5
        
        return min(100, score)

    def scrape_all(self) -> List[Dict]:
        """Execute complete scraping session"""
        all_jobs = []
        
        print(f"🚀 Starting JSearch scraping...")
        print(f"📊 Max API calls: {self.max_calls_per_session}")
        print("=" * 50)
        
        for query in self.search_queries:
            print(f"\n🔍 Query: '{query}'")
            
            for country in self.priority_countries:
                jobs = self.search_jobs(query, country)
                all_jobs.extend(jobs)
                
                print(f"   🌍 {country}: {len(jobs)} jobs")
                
                # Rate limiting
                time.sleep(0.5)
                
                # Check API limit
                if self.api_calls_made >= self.max_calls_per_session:
                    print(f"\n⚠️ Reached API call limit")
                    break
            
            if self.api_calls_made >= self.max_calls_per_session:
                break
        
        # Remove duplicates
        unique_jobs = self.remove_duplicates(all_jobs)
        
        print(f"\n📊 Scraping Summary:")
        print(f"   Total jobs found: {len(all_jobs)}")
        print(f"   Unique jobs: {len(unique_jobs)}")
        print(f"   API calls used: {self.api_calls_made}/{self.max_calls_per_session}")
        print(f"   Duplicates removed: {len(all_jobs) - len(unique_jobs)}")
        
        return unique_jobs

    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on URL"""
        seen = set()
        unique = []
        
        for job in jobs:
            url = job.get('source_url', '')
            # Use title+company as backup identifier
            identifier = url if url else f"{job.get('title', '')}-{job.get('company', '')}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique.append(job)
        
        return unique

    def gemini_filter(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs using Gemini AI for relevance"""
        if not self.gemini_model:
            print("⚠️ Gemini model not available - skipping AI filtering")
            return jobs

        print(f"\n🤖 Starting Gemini filtering of {len(jobs)} jobs...")
        
        prompt_template = """
Analyze this job posting for relevance to "AI & Society" field.

Job Title: {title}
Company: {company}
Description: {description}

AI & Society includes: AI ethics, responsible AI, AI policy, algorithmic fairness, 
AI governance, technology law, digital rights, AI safety, data ethics.

Is this job HIGHLY RELEVANT to AI & Society? Consider:
- Does it focus on societal impacts of AI?
- Does it involve AI ethics, policy, or governance?
- Is it about responsible AI development?

Respond with only: YES or NO
"""
        
        filtered_jobs = []
        
        for i, job in enumerate(jobs):
            try:
                print(f"[{i+1}/{len(jobs)}] Analyzing: {job['title'][:40]}...")
                
                # Prepare prompt
                prompt = prompt_template.format(
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    description=job.get('full_description', job.get('description', ''))[:800]
                )
                
                # Get Gemini response
                response = self.gemini_model.generate_content(prompt)
                response_text = response.text.strip().lower()
                
                if "yes" in response_text:
                    # Update job with Gemini analysis
                    job['gemini_analyzed'] = True
                    job['gemini_approved'] = True
                    filtered_jobs.append(job)
                    print(f"   ✅ Approved by Gemini")
                else:
                    print(f"   ❌ Rejected by Gemini")
                
                # Rate limiting for Gemini
                time.sleep(1)
                
            except Exception as e:
                print(f"   ⚠️ Gemini error: {e}")
                # Include job if Gemini fails
                job['gemini_analyzed'] = False
                job['gemini_error'] = str(e)
                filtered_jobs.append(job)
        
        print(f"\n🎯 Gemini Filtering Results:")
        print(f"   Original jobs: {len(jobs)}")
        print(f"   Gemini approved: {len(filtered_jobs)}")
        print(f"   Rejection rate: {(len(jobs) - len(filtered_jobs))/len(jobs)*100:.1f}%")
        
        return filtered_jobs

    def save_results(self, jobs: List[Dict], filename: str):
        """Save results with comprehensive metadata"""
        os.makedirs('data', exist_ok=True)
        
        # Calculate statistics
        stats = {
            "total": len(jobs),
            "by_job_type": {},
            "by_category": {},
            "by_country": {},
            "gemini_analyzed": len([j for j in jobs if j.get('gemini_analyzed', False)]),
            "gemini_approved": len([j for j in jobs if j.get('gemini_approved', False)]),
            "remote_jobs": len([j for j in jobs if j.get('is_remote', False)]),
            "with_salary": len([j for j in jobs if j.get('salary_info', '')])
        }
        
        # Count by categories
        for job in jobs:
            job_type = job.get('job_type', 'unknown')
            stats['by_job_type'][job_type] = stats['by_job_type'].get(job_type, 0) + 1
            
            category = job.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            country = job.get('country', 'unknown')
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
        
        result_data = {
            "jobs": jobs,
            "metadata": {
                "total_jobs": len(jobs),
                "api_calls_used": self.api_calls_made,
                "last_update": datetime.now().isoformat(),
                "queries_searched": self.search_queries,
                "countries_searched": self.priority_countries,
                "gemini_available": self.gemini_model is not None
            },
            "stats": stats
        }
        
        filepath = f"data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {filename} with {len(jobs)} jobs")
        return result_data

def main():
    """Main execution function"""
    scraper = JSearchJobScraper()
    
    try:
        # Phase 1: Scrape raw jobs
        print("Phase 1: Scraping jobs from JSearch API...")
        raw_jobs = scraper.scrape_all()
        
        if not raw_jobs:
            print("❌ No jobs found - check API key and network connection")
            return 1
        
        # Save raw results
        scraper.save_results(raw_jobs, "jsearch_jobs_raw.json")

        # Phase 2: Gemini filtering
        print("\nPhase 2: Filtering with Gemini AI...")
        filtered_jobs = scraper.gemini_filter(raw_jobs)
        
        # Save filtered results
        final_data = scraper.save_results(filtered_jobs, "jsearch_gemini_jobs.json")
        
        # Print final summary
        print(f"\n🎉 JSearch + Gemini Scraping Complete!")
        print(f"   Raw jobs collected: {len(raw_jobs)}")
        print(f"   Gemini filtered jobs: {len(filtered_jobs)}")
        print(f"   API calls used: {scraper.api_calls_made}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

