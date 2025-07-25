#!/usr/bin/env python3
"""
JSearch API + Gemini AI Enhanced Scraper
Optimized for 200 monthly API calls with precision filtering
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
import re

class JSearchGeminiScraper:
    def __init__(self):
        # JSearch API configuration
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
        }
        
        # Broader search queries for maximum coverage
        self.search_queries = [
            "AI ethics",           # Broad AI ethics coverage
            "AI policy",           # AI policy and governance
            "responsible AI",      # Responsible AI development
            "algorithmic",         # Algorithmic fairness, bias, accountability
            "technology policy",   # Tech policy, digital transformation
            "digital governance",  # Digital governance and regulation
            "AI safety",          # AI safety and alignment
            "data ethics"         # Data ethics and privacy
        ]
        
        # Priority countries
        self.priority_countries = ["US", "GB", "CA"]
        
        # API tracking
        self.api_calls_made = 0
        self.max_calls_per_session = 25
        
        # Gemini analysis tracking
        self.gemini_analyses = 0
        self.gemini_filtered_jobs = []

    def search_jobs(self, query: str, country: str = "US", limit: int = 25) -> List[Dict]:
        """Search jobs using JSearch API with broader coverage"""
        jobs = []
        
        # Check API call limit
        if self.api_calls_made >= self.max_calls_per_session:
            print(f"⚠️ API call limit reached ({self.max_calls_per_session})")
            return []
        
        try:
            if not self.api_key:
                print("⚠️ RAPIDAPI_KEY not found, using mock data")
                return self.get_mock_jobs(query, country)
            
            params = {
                'query': query,
                'page': '1',
                'num_pages': '1',
                'country': country,
                'date_posted': 'month',  # Last month for freshness
                'employment_types': 'FULLTIME',
                'job_requirements': 'under_3_years_experience,more_than_3_years_experience'
            }
            
            print(f"🔍 JSearch: '{query}' in {country}")
            
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=15)
            self.api_calls_made += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and 'data' in data:
                    for job_data in data['data']:
                        job = self.parse_job(job_data, query, country)
                        if job:  # Don't filter here, let Gemini decide
                            jobs.append(job)
                    
                    print(f"✅ Found {len(jobs)} jobs (pre-Gemini)")
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
            
            # Basic categorization (will be enhanced by Gemini)
            category = self.determine_category(title, description, company)
            job_type = self.determine_job_type(company)
            
            # Remote work detection
            is_remote = job_data.get('job_is_remote', False)
            if is_remote:
                location = f"{location} (Remote)"
            
            # Basic relevance score (will be enhanced by Gemini)
            basic_relevance = self.calculate_basic_relevance(title, description)
            
            job = {
                "title": title,
                "company": company,
                "location": location,
                "job_type": job_type,
                "category": category,
                "description": self.clean_description(description),
                "full_description": description,  # Keep full for Gemini
                "posting_date": posted_date,
                "deadline": None,
                "source_url": job_url,
                "source_site": "google_jobs",
                "tags": self.generate_basic_tags(title, description, search_query, is_remote),
                "basic_relevance_score": basic_relevance,
                "salary_info": salary_info,
                "country": country,
                "is_remote": is_remote,
                "search_query": search_query,
                "gemini_analyzed": False
            }
            
            return job
            
        except Exception as e:
            print(f"⚠️ Error parsing job: {e}")
            return None

    def get_gemini_analysis(self, job: Dict) -> Dict:
        """Enhanced Gemini analysis for JSearch jobs"""
        if not self.gemini_api_key:
            return {
                "is_relevant": True,
                "relevance_score": job.get('basic_relevance_score', 70),
                "category": job.get('category', 'research'),
                "reasoning": "No Gemini API key available",
                "key_topics": [],
                "confidence": "low"
            }
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Analyze this Google Jobs posting for "AI & Society" field relevance.

            Job Title: {job.get('title', '')}
            Company: {job.get('company', '')}
            Location: {job.get('location', '')}
            Search Query Used: {job.get('search_query', '')}
            Salary: {job.get('salary_info', 'Not specified')}
            Description: {job.get('full_description', '')[:1200]}

            AI & Society field encompasses:
            - AI Ethics and Responsible AI Development
            - AI Policy, Governance, and Regulation  
            - Algorithmic Fairness and Bias Mitigation
            - Technology Law and Digital Rights
            - AI Safety and Alignment Research
            - Computational Social Science
            - Human-Computer Interaction (societal focus)
            - Digital Transformation Policy
            - Public Interest Technology
            - AI Risk Management and Compliance

            Provide detailed analysis in JSON format:
            {{
                "is_relevant": true/false,
                "relevance_score": 0-100,
                "category": "research/policy/legal/technical",
                "reasoning": "detailed explanation of relevance assessment",
                "key_topics": ["topic1", "topic2", "topic3"],
                "confidence": "high/medium/low",
                "career_level": "entry/mid/senior/executive",
                "societal_impact_focus": "high/medium/low",
                "google_jobs_quality": {{
                    "company_reputation": "high/medium/low",
                    "role_clarity": "clear/moderate/unclear",
                    "growth_potential": "high/medium/low"
                }}
            }}

            Scoring Guidelines:
            - 90-100: Core AI & Society roles (AI Ethics Lead, Policy Director, etc.)
            - 75-89: Strong relevance (AI roles with clear societal components)
            - 60-74: Good relevance (Tech roles with meaningful social considerations)
            - 45-59: Moderate relevance (Some AI & Society elements)
            - 30-44: Weak relevance (Tangential connection)
            - 0-29: Not relevant (Pure engineering, unrelated fields)

            Consider:
            - Job description depth and specificity
            - Company's commitment to responsible AI
            - Role's potential for societal impact
            - Alignment with AI & Society research areas

            Respond with ONLY the JSON object:
            """
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            try:
                # Parse JSON response
                if '```json' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                
                analysis = json.loads(json_text)
                
                # Ensure required fields
                if 'is_relevant' not in analysis:
                    analysis['is_relevant'] = analysis.get('relevance_score', 0) >= 30
                
                analysis['gemini_enhanced'] = True
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error: {e}")
                return self.fallback_analysis(job)
                
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self.fallback_analysis(job)

    def fallback_analysis(self, job: Dict) -> Dict:
        """Fallback analysis when Gemini fails"""
        return {
            "is_relevant": True,
            "relevance_score": job.get('basic_relevance_score', 60),
            "category": job.get('category', 'research'),
            "reasoning": "Fallback analysis - Gemini unavailable",
            "key_topics": [],
            "confidence": "low",
            "gemini_enhanced": False
        }

    def enhance_with_gemini(self, jobs: List[Dict]) -> List[Dict]:
        """Enhance job list with Gemini analysis"""
        if not jobs:
            return []
        
        print(f"\n🤖 Starting Gemini analysis of {len(jobs)} jobs...")
        print("=" * 60)
        
        enhanced_jobs = []
        
        for i, job in enumerate(jobs):
            print(f"[{i+1}/{len(jobs)}] Analyzing: {job['title'][:50]}...")
            
            # Get Gemini analysis
            analysis = self.get_gemini_analysis(job)
            self.gemini_analyses += 1
            
            # Apply Gemini results
            if analysis['is_relevant'] and analysis['relevance_score'] >= 30:
                # Update job with Gemini insights
                job.update({
                    'relevance_score': analysis['relevance_score'],
                    'category': analysis['category'],
                    'gemini_reasoning': analysis.get('reasoning', ''),
                    'key_topics': analysis.get('key_topics', []),
                    'confidence': analysis.get('confidence', 'medium'),
                    'career_level': analysis.get('career_level', 'unknown'),
                    'societal_impact_focus': analysis.get('societal_impact_focus', 'medium'),
                    'gemini_analyzed': True,
                    'gemini_enhanced': analysis.get('gemini_enhanced', True)
                })
                
                # Update tags with Gemini insights
                if analysis.get('key_topics'):
                    job['tags'].extend(analysis['key_topics'][:3])
                    job['tags'] = list(set(job['tags']))  # Remove duplicates
                
                enhanced_jobs.append(job)
                print(f"   ✅ Relevant: {analysis['relevance_score']}% ({analysis['category']})")
                print(f"   🎯 {analysis.get('reasoning', '')[:80]}...")
            else:
                print(f"   ❌ Not relevant: {analysis['relevance_score']}%")
            
            # Rate limiting for Gemini API
            time.sleep(1)
        
        # Sort by Gemini relevance score
        enhanced_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        print(f"\n🎯 Gemini Analysis Complete:")
        print(f"   Original jobs: {len(jobs)}")
        print(f"   Gemini-approved: {len(enhanced_jobs)}")
        print(f"   Filtered out: {len(jobs) - len(enhanced_jobs)}")
        print(f"   Success rate: {len(enhanced_jobs)/len(jobs)*100:.1f}%")
        
        return enhanced_jobs

    def scrape_all_with_gemini(self) -> List[Dict]:
        """Execute complete scraping with Gemini enhancement"""
        all_jobs = []
        
        print("🌍 Starting JSearch + Gemini AI scraping...")
        print(f"📊 Max API calls: {self.max_calls_per_session}")
        print(f"🤖 Gemini API: {'Available' if self.gemini_api_key else 'Not configured'}")
        print("=" * 70)
        
        # Phase 1: JSearch collection
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
                    print(f"\n⚠️ Reached API call limit ({self.max_calls_per_session})")
                    break
            
            if self.api_calls_made >= self.max_calls_per_session:
                break
        
        # Remove duplicates
        unique_jobs = self.remove_duplicates(all_jobs)
        
        print(f"\n📊 Phase 1 (JSearch) Results:")
        print(f"   Total jobs collected: {len(all_jobs)}")
        print(f"   Unique jobs: {len(unique_jobs)}")
        print(f"   API calls used: {self.api_calls_made}")
        print(f"   Duplicates removed: {len(all_jobs) - len(unique_jobs)}")
        
        # Phase 2: Gemini enhancement
        enhanced_jobs = self.enhance_with_gemini(unique_jobs)
        
        return enhanced_jobs

    # Keep all the utility methods from original
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
        """Basic category determination (enhanced by Gemini)"""
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
        """Clean job description for display"""
        clean_desc = re.sub(r'<[^>]+>', '', description)
        clean_desc = re.sub(r'\s+', ' ', clean_desc)
        
        if len(clean_desc) > 500:
            clean_desc = clean_desc[:500] + "..."
        
        return clean_desc.strip()

    def generate_basic_tags(self, title: str, description: str, search_query: str, is_remote: bool) -> List[str]:
        """Generate basic tags (enhanced by Gemini)"""
        tags = [search_query.title()]
        
        content = f"{title} {description}".lower()
        
        if any(term in content for term in ['artificial intelligence', 'ai ']):
            tags.append("AI")
        if any(term in content for term in ['machine learning', 'ml ']):
            tags.append("Machine Learning")
        if 'ethics' in content:
            tags.append("Ethics")
        if any(term in content for term in ['policy', 'governance']):
            tags.append("Policy")
        if 'safety' in content:
            tags.append("AI Safety")
        if is_remote:
            tags.append("Remote")
        
        return list(set(tags))

    def calculate_basic_relevance(self, title: str, description: str) -> int:
        """Basic relevance calculation (enhanced by Gemini)"""
        content = f"{title} {description}".lower()
        score = 50  # Lower base score, let Gemini decide
        
        # Basic scoring for pre-filtering
        high_value = ['ai ethics', 'responsible ai', 'ai governance', 'algorithmic fairness']
        for keyword in high_value:
            if keyword in content:
                score += 15
        
        medium_value = ['artificial intelligence', 'machine learning', 'policy', 'ethics']
        for keyword in medium_value:
            if keyword in content:
                score += 8
        
        return min(100, score)

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

    def get_mock_jobs(self, query: str, country: str) -> List[Dict]:
        """Generate mock job data when API is unavailable"""
        mock_templates = {
            "US": [
                {
                    "title": f"Senior {query} Specialist",
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
            ]
        }
        
        templates = mock_templates.get(country, mock_templates["US"])
        jobs = []
        
        for template in templates:
            job = {
                **template,
                "job_type": "industry",
                "category": "research",
                "description": f"Work on {query} initiatives focusing on responsible AI development.",
                "full_description": f"Detailed role working on {query} initiatives with focus on ethical AI development and societal impact.",
                "posting_date": datetime.now().strftime("%Y-%m-%d"),
                "deadline": None,
                "source_url": f"https://www.google.com/search?q={query.replace(' ', '+')}&ibp=htl;jobs",
                "source_site": "google_jobs",
                "tags": [query.title(), "Google Jobs"],
                "basic_relevance_score": 75,
                "country": country,
                "is_remote": False,
                "search_query": query,
                "gemini_analyzed": False
            }
            jobs.append(job)
        
        return jobs

    def save_results(self, jobs: List[Dict], filename: str = "jsearch_gemini_jobs.json"):
        """Save enhanced results to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        result_data = {
            "jobs": jobs,
            "metadata": {
                "total_jobs": len(jobs),
                "api_calls_used": self.api_calls_made,
                "gemini_analyses": self.gemini_analyses,
                "last_update": datetime.now().isoformat(),
                "queries_searched": self.search_queries,
                "countries_searched": self.priority_countries,
                "gemini_enhanced": True
            },
            "stats": self.calculate_stats(jobs)
        }
        
        filepath = f"data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Enhanced results saved to {filepath}")
        return result_data

    def calculate_stats(self, jobs: List[Dict]) -> Dict:
        """Calculate enhanced job statistics"""
        if not jobs:
            return {}
        
        stats = {
            "total": len(jobs),
            "by_job_type": {},
            "by_category": {},
            "by_country": {},
            "average_relevance": sum(job.get('relevance_score', 0) for job in jobs) // len(jobs) if jobs else 0,
            "high_relevance_jobs": len([j for j in jobs if j.get('relevance_score', 0) >= 80]),
            "gemini_analyzed": len([j for j in jobs if j.get('gemini_analyzed', False)]),
            "high_confidence": len([j for j in jobs if j.get('confidence') == 'high']),
            "remote_jobs": len([j for j in jobs if j.get('is_remote', False)]),
            "with_salary": len([j for j in jobs if j.get('salary_info', '')])
        }
        
        # Count distributions
        for job in jobs:
            job_type = job.get('job_type', 'unknown')
            stats['by_job_type'][job_type] = stats['by_job_type'].get(job_type, 0) + 1
            
            category = job.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            country = job.get('country', 'unknown')
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
        
        return stats


def main():
    """Main execution function"""
    scraper = JSearchGeminiScraper()
    
    try:
        # Execute enhanced scraping
        jobs = scraper.scrape_all_with_gemini()
        
        # Save results
        result_data = scraper.save_results(jobs)
        
        # Print enhanced summary
        stats = result_data['stats']
        print("\n🎯 Final Gemini-Enhanced Results:")
        print(f"   Total relevant jobs: {stats['total']}")
        print(f"   Average relevance: {stats['average_relevance']}%")
        print(f"   High relevance (80+): {stats['high_relevance_jobs']}")
        print(f"   Gemini analyzed: {stats['gemini_analyzed']}")
        print(f"   High confidence: {stats['high_confidence']}")
        print(f"   Remote jobs: {stats['remote_jobs']}")
        print(f"   With salary info: {stats['with_salary']}")
        
        print(f"\n🏢 By Job Type:")
        for job_type, count in stats['by_job_type'].items():
            print(f"   {job_type}: {count}")
        
        print(f"\n📂 By Category:")
        for category, count in stats['by_category'].items():
            print(f"   {category}: {count}")
        
        # Show top Gemini-scored jobs
        top_jobs = sorted(jobs, key=lambda x: x.get('relevance_score', 0), reverse=True)[:5]
        if top_jobs:
            print(f"\n⭐ Top Gemini-Scored Jobs:")
            for i, job in enumerate(top_jobs, 1):
                score = job.get('relevance_score', 0)
                confidence = job.get('confidence', 'unknown')
                print(f"   {i}. {job['title']} - {job['company']}")
                print(f"      🎯 {score}% relevance ({confidence} confidence)")
                if job.get('key_topics'):
                    print(f"      🏷️  {', '.join(job['key_topics'][:3])}")
        
        print(f"\n📊 API Usage:")
        print(f"   JSearch calls: {scraper.api_calls_made}/{scraper.max_calls_per_session}")
        print(f"   Gemini analyses: {scraper.gemini_analyses}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
