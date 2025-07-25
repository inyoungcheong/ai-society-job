#!/usr/bin/env python3
"""
JSearch API Job Scraper for AI & Society Positions
Optimized for 200 monthly API calls limit
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import re

class JSearchJobScraper:
    def __init__(self):
        # JSearch API configuration (via RapidAPI)
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }
        
        # Optimized search queries for AI & Society field
        self.search_queries = [
    "responsible ai", "ai governance", "algorithmic fairness", "ai ethics", 
    "digital ethics", "ai policy"
        ]
        
        # Priority countries for job search
        self.priority_countries = ["US", "GB", "CA"]
        
        # Track API usage
        self.api_calls_made = 0
        self.max_calls_per_session = 25  # Conservative limit
        
        # AI & Society keywords for relevance scoring
        self.high_value_keywords = [
            'ai ethics', 'responsible ai', 'ai governance', 'algorithmic fairness',
            'ai safety', 'digital rights', 'technology policy', 'ai regulation'
        ]
        
        self.medium_value_keywords = [
            'artificial intelligence', 'machine learning', 'data ethics',
            'policy', 'governance', 'privacy', 'algorithm', 'transparency'
        ]

    def search_jobs(self, query: str, country: str = "US", limit: int = 25) -> List[Dict]:
        """Search jobs using JSearch API with rate limiting"""
        jobs = []
        
        # Check API call limit
        if self.api_calls_made >= self.max_calls_per_session:
            print(f"⚠️ API call limit reached ({self.max_calls_per_session}), returning mock data")
            return self.get_mock_jobs(query, country)
        
        try:
            if not self.api_key:
                print("⚠️ RAPIDAPI_KEY not found, using mock data")
                return self.get_mock_jobs(query, country)
            
            params = {
                'query': query,
                'page': '1',
                'num_pages': '1',
                'country': country,
                'date_posted': 'month',  # Last month
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
                        if job and job['relevance_score'] >= 30:  # Filter by relevance
                            jobs.append(job)
                    
                    print(f"✅ Found {len(jobs)} relevant jobs")
                else:
                    print(f"⚠️ No data in response")
            else:
                print(f"❌ API error {response.status_code}")
                jobs = self.get_mock_jobs(query, country)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            jobs = self.get_mock_jobs(query, country)
        
        return jobs

    def parse_job(self, job_data: Dict, search_query: str, country: str) -> Dict:
        """Parse job data from JSearch API response"""
        try:
            title = job_data.get('job_title', 'Unknown Position')
            company = job_data.get('employer_name', 'Unknown Company')
            location = self.format_location(job_data, country)
            description = job_data.get('job_description', '')
            
            # URLs
            apply_url = job_data.get('job_apply_link', '')
            job_url = job_data.get('job_google_link', apply_url)
            
            # Date processing
            posted_date = self.parse_date(job_data.get('job_posted_at_datetime_utc', ''))
            
            # Salary information
            salary_info = self.extract_salary(job_data)
            
            # Job categorization
            category = self.determine_category(title, description, company)
            job_type = self.determine_job_type(company)
            
            # Remote work detection
            is_remote = job_data.get('job_is_remote', False)
            if is_remote:
                location = f"{location} (Remote)"
            
            # Calculate relevance score
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
            
        except Exception as e:
            print(f"⚠️ Error parsing job: {e}")
            return None

    def format_location(self, job_data: Dict, country: str) -> str:
        """Format job location"""
        city = job_data.get('job_city', '')
        state = job_data.get('job_state', '')
        job_country = job_data.get('job_country', country)
        
        location_parts = [part for part in [city, state] if part]
        location = ', '.join(location_parts)
        
        if location:
            return f"{location}, {job_country}"
        else:
            return job_country

    def parse_date(self, date_str: str) -> str:
        """Parse date string to standard format"""
        try:
            if not date_str:
                return datetime.now().strftime("%Y-%m-%d")
            
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime("%Y-%m-%d")
            
            return datetime.now().strftime("%Y-%m-%d")
            
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def extract_salary(self, job_data: Dict) -> str:
        """Extract salary information"""
        try:
            salary_min = job_data.get('job_min_salary')
            salary_max = job_data.get('job_max_salary')
            currency = job_data.get('job_salary_currency', 'USD')
            
            if salary_min and salary_max:
                return f"{currency} {salary_min:,} - {salary_max:,}"
            elif salary_min:
                return f"{currency} {salary_min:,}+"
            else:
                return ""
        except:
            return ""

    def determine_job_type(self, company: str) -> str:
        """Determine job type based on company name"""
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
        """Determine job category based on content"""
        content = f"{title} {description} {company}".lower()
        
        if any(term in content for term in ['law', 'legal', 'attorney', 'regulation', 'compliance']):
            return 'law'
        elif any(term in content for term in ['policy', 'governance', 'government', 'regulatory']):
            return 'policy'
        elif any(term in content for term in ['engineer', 'engineering', 'developer', 'technical']):
            return 'technical'
        else:
            return 'research'

    def clean_description(self, description: str) -> str:
        """Clean job description"""
        # Remove HTML tags
        clean_desc = re.sub(r'<[^>]+>', '', description)
        
        # Multiple spaces to single space
        clean_desc = re.sub(r'\s+', ' ', clean_desc)
        
        # Limit length
        if len(clean_desc) > 500:
            clean_desc = clean_desc[:500] + "..."
        
        return clean_desc.strip()

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
        
        return list(set(tags))

    def calculate_relevance(self, title: str, description: str) -> int:
        """Calculate job relevance score"""
        content = f"{title} {description}".lower()
        score = 60  # Base score for Google Jobs results
        
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

    def get_mock_jobs(self, query: str, country: str) -> List[Dict]:
        """Generate mock job data when API is unavailable"""
        mock_templates = {
            "US": [
                {
                    "title": f"Senior {query}",
                    "company": "Google",
                    "location": "Mountain View, CA, US",
                    "salary_info": "USD 150,000 - 250,000"
                },
                {
                    "title": f"{query} Program Manager",
                    "company": "Meta",
                    "location": "Menlo Park, CA, US",
                    "salary_info": "USD 140,000 - 220,000"
                }
            ],
            "GB": [
                {
                    "title": f"{query} Research Scientist",
                    "company": "DeepMind",
                    "location": "London, GB",
                    "salary_info": "GBP 80,000 - 120,000"
                }
            ],
            "CA": [
                {
                    "title": f"{query} Lead",
                    "company": "Vector Institute",
                    "location": "Toronto, ON, CA",
                    "salary_info": "CAD 100,000 - 150,000"
                }
            ]
        }
        
        templates = mock_templates.get(country, mock_templates["US"])
        jobs = []
        
        for template in templates:
            job = {
                **template,
                "job_type": "industry",
                "category": "research",
                "description": f"Work on {query} initiatives. Focus on responsible AI development and ethical technology deployment.",
                "posting_date": datetime.now().strftime("%Y-%m-%d"),
                "deadline": None,
                "source_url": f"https://www.google.com/search?q={query.replace(' ', '+')}&ibp=htl;jobs",
                "source_site": "google_jobs",
                "tags": [query.title(), "Google Jobs"],
                "relevance_score": 80,
                "country": country,
                "is_remote": False
            }
            jobs.append(job)
        
        return jobs

    def scrape_all(self) -> List[Dict]:
        """Execute complete scraping session"""
        all_jobs = []
        
        print("🌍 Starting JSearch API scraping...")
        print(f"📊 Max API calls this session: {self.max_calls_per_session}")
        print("=" * 60)
        
        for query in self.search_queries:
            print(f"\n🔍 Query: '{query}'")
            
            for country in self.priority_countries:
                jobs = self.search_jobs(query, country)
                all_jobs.extend(jobs)
                
                print(f"   🌍 {country}: {len(jobs)} jobs")
                
                # Rate limiting
                time.sleep(0.5)
                
                # Check if we hit API limit
                if self.api_calls_made >= self.max_calls_per_session:
                    print(f"\n⚠️ Reached API call limit ({self.max_calls_per_session})")
                    break
            
            if self.api_calls_made >= self.max_calls_per_session:
                break
        
        # Remove duplicates
        unique_jobs = self.remove_duplicates(all_jobs)
        
        # Sort by relevance
        unique_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"\n🎯 Scraping completed:")
        print(f"   Total jobs found: {len(all_jobs)}")
        print(f"   Unique jobs: {len(unique_jobs)}")
        print(f"   API calls made: {self.api_calls_made}")
        print(f"   Duplicates removed: {len(all_jobs) - len(unique_jobs)}")
        
        return unique_jobs

    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on URL"""
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            url = job['source_url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)
        
        return unique_jobs

    def save_results(self, jobs: List[Dict], filename: str = "jsearch_jobs.json"):
        """Save results to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        result_data = {
            "jobs": jobs,
            "metadata": {
                "total_jobs": len(jobs),
                "api_calls_used": self.api_calls_made,
                "last_update": datetime.now().isoformat(),
                "queries_searched": self.search_queries,
                "countries_searched": self.priority_countries
            },
            "stats": self.calculate_stats(jobs)
        }
        
        filepath = f"data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to {filepath}")
        return result_data

    def calculate_stats(self, jobs: List[Dict]) -> Dict:
        """Calculate job statistics"""
        if not jobs:
            return {}
        
        stats = {
            "total": len(jobs),
            "by_job_type": {},
            "by_category": {},
            "by_country": {},
            "average_relevance": sum(job['relevance_score'] for job in jobs) // len(jobs),
            "high_relevance_jobs": len([j for j in jobs if j['relevance_score'] >= 80]),
            "remote_jobs": len([j for j in jobs if j['is_remote']]),
            "with_salary": len([j for j in jobs if j['salary_info']])
        }
        
        # Count by job type
        for job in jobs:
            job_type = job['job_type']
            stats['by_job_type'][job_type] = stats['by_job_type'].get(job_type, 0) + 1
        
        # Count by category
        for job in jobs:
            category = job['category']
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Count by country
        for job in jobs:
            country = job['country']
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
        
        return stats


def main():
    """Main execution function"""
    scraper = JSearchJobScraper()
    
    try:
        # Execute scraping
        jobs = scraper.scrape_all()
        
        # Save results
        result_data = scraper.save_results(jobs)
        
        # Print summary
        stats = result_data['stats']
        print("\n📊 Final Summary:")
        print(f"   Total jobs: {stats['total']}")
        print(f"   High relevance (80+): {stats['high_relevance_jobs']}")
        print(f"   Remote jobs: {stats['remote_jobs']}")
        print(f"   With salary info: {stats['with_salary']}")
        print(f"   Average relevance: {stats['average_relevance']}%")
        
        print(f"\n🏢 By Job Type:")
        for job_type, count in stats['by_job_type'].items():
            print(f"   {job_type}: {count}")
        
        print(f"\n📂 By Category:")
        for category, count in stats['by_category'].items():
            print(f"   {category}: {count}")
        
        # Show top jobs
        top_jobs = sorted(jobs, key=lambda x: x['relevance_score'], reverse=True)[:3]
        if top_jobs:
            print(f"\n⭐ Top Jobs:")
            for i, job in enumerate(top_jobs, 1):
                print(f"   {i}. {job['title']} - {job['company']} ({job['relevance_score']}%)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
