# Job Board RSS Feeds - 최적화된 쿼리
            "job_boards": [
                # Indeed RSS - 핵심 AI & Society 키워드
                "https://rss.indeed.com/rss?q=%22AI+ethics%22&l=&sort=date",
                "https://rss.indeed.com/rss?q=%22responsible+AI%22&l=&sort=date", 
                "https://rss.indeed.com/rss?q=%22AI#!/usr/bin/env python3
"""
RSS Job Scraper for AI & Society Positions
Aggregates job postings from RSS feeds with Gemini filtering
"""

import requests
import feedparser
import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
from urllib.parse import urljoin, urlparse

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

class RSSJobScraper:
    def __init__(self):
        # API Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # RSS Feed Sources - 실제 작동하는 피드들만
        self.rss_feeds = {
            # TSPA Job Board (확인됨!)
            "tspa": [
                "https://www.tspa.org/explore/job-board/feed",
            ],
            
            # Greenhouse RSS - 확인된 회사들 (확인됨!)
            "greenhouse": [
                "https://boards.greenhouse.io/anthropic/jobs.rss",
                "https://boards.io/openai/jobs.rss",
                "https://boards.greenhouse.io/meta/jobs.rss",    
                "https://boards.greenhouse.io/google/jobs.rss",
            ],
            
            # 실제 작동하는 Job Board RSS
            "job_boards": [
                # SimplyHired RSS - 실제 형식 (valME 검증 기반)
                "http://www.simplyhired.com/a/job-feed/rss/q-AI+ethics",
                "http://www.simplyhired.com/a/job-feed/rss/q-responsible+AI", 
                "http://www.simplyhired.com/a/job-feed/rss/q-AI+policy",
                "http://www.simplyhired.com/a/job-feed/rss/q-algorithmic+fairness",
                "http://www.simplyhired.com/a/job-feed/rss/q-AI+governance", 
                "http://www.simplyhired.com/a/job-feed/rss/q-data+ethics",
                
                # Monster RSS (실제 형식)
                "http://rss.jobsearch.monster.com/rssquery.ashx?q=AI+ethics&cy=us&pp=2000",
                "http://rss.jobsearch.monster.com/rssquery.ashx?q=responsible+AI&cy=us&pp=2000",
                "http://rss.jobsearch.monster.com/rssquery.ashx?q=AI+policy&cy=us&pp=2000",
                "http://rss.jobsearch.monster.com/rssquery.ashx?q=algorithmic+fairness&cy=us&pp=2000",
            ],
            
            # Academic Jobs (기존 - 작동 확인됨)
            "academic": [
                "https://academicjobsonline.org/ajo/jobs/rss/COMP",
                "https://academicjobsonline.org/ajo/jobs/rss/POLICY", 
                "https://academicjobsonline.org/ajo/jobs/rss/LAW",
                "https://academicjobsonline.org/ajo/jobs/rss/PHIL",  # 철학과 (AI 윤리 관련)
                "https://academicjobsonline.org/ajo/jobs/rss/ECON",  # 경제학과 (AI 경제학 관련)
            ],
            
            # 추가 회사들 - Lever 기반 (Greenhouse 대안)
            "lever": [
                # 일부 회사들은 Lever 사용
                "https://jobs.lever.co/nvidia/jobs.rss",  # NVIDIA
                "https://jobs.lever.co/intel/jobs.rss",   # Intel
                "https://jobs.lever.co/ibm/jobs.rss",     # IBM
                "https://jobs.lever.co/uber/jobs.rss",    # Uber
                "https://jobs.lever.co/netflix/jobs.rss", # Netflix
            ]
            
            # University/Academic RSS (기존 확장)
            "academic": [
                "https://academicjobsonline.org/ajo/jobs/rss/COMP",
                "https://academicjobsonline.org/ajo/jobs/rss/POLICY", 
                "https://academicjobsonline.org/ajo/jobs/rss/LAW",
                "https://academicjobsonline.org/ajo/jobs/rss/PHIL",  # 철학과 (AI 윤리 관련)
                
                # HigherEdJobs (테스트 필요)
                "https://www.higheredjobs.com/search/jobs.rss?keyword=AI+ethics",
                "https://www.higheredjobs.com/search/jobs.rss?keyword=digital+policy",
            ],
            
            # Government/NGO RSS
            "government": [
                # USAJobs RSS (테스트 필요)
                "https://www.usajobs.gov/Search/Results.rss?keyword=artificial%20intelligence",
                "https://www.usajobs.gov/Search/Results.rss?keyword=digital%20policy",
                
                # Idealist (비영리 중심, 테스트 필요)
                "https://www.idealist.org/en/jobs?format=rss&q=AI+ethics",
                "https://www.idealist.org/en/jobs?format=rss&q=digital+rights",
            ],
            
            # AngelList/Wellfound (스타트업)
            "startups": [
                # Wellfound RSS (테스트 필요)
                # "https://wellfound.com/jobs?keywords=AI%20ethics&format=rss",
                # "https://wellfound.com/jobs?keywords=responsible%20AI&format=rss",
            ]
            
            # Greenhouse RSS - 확인된 회사들 (확인됨!)
            "greenhouse": [
                "https://boards.greenhouse.io/anthropic/jobs.rss",
                "https://boards.greenhouse.io/openai/jobs.rss",
                "https://boards.greenhouse.io/meta/jobs.rss",    
                "https://boards.greenhouse.io/google/jobs.rss",
            ],
            
            # University/Academic RSS (기존 확장)
            "academic": [
                "https://academicjobsonline.org/ajo/jobs/rss/COMP",
                "https://academicjobsonline.org/ajo/jobs/rss/POLICY", 
                "https://academicjobsonline.org/ajo/jobs/rss/LAW",
                "https://academicjobsonline.org/ajo/jobs/rss/PHIL",  # 철학과 (AI 윤리 관련)
                
                # HigherEdJobs (테스트 필요)
                "https://www.higheredjobs.com/search/jobs.rss?keyword=AI+ethics",
                "https://www.higheredjobs.com/search/jobs.rss?keyword=digital+policy",
            ],
            
            # Government/NGO RSS
            "government": [
                # USAJobs RSS (테스트 필요)
                "https://www.usajobs.gov/Search/Results.rss?keyword=artificial%20intelligence",
                "https://www.usajobs.gov/Search/Results.rss?keyword=digital%20policy",
                
                # Idealist (비영리 중심, 테스트 필요)
                "https://www.idealist.org/en/jobs?format=rss&q=AI+ethics",
                "https://www.idealist.org/en/jobs?format=rss&q=digital+rights",
            ],
            
            # AngelList/Wellfound (스타트업)
            "startups": [
                # Wellfound RSS (테스트 필요)
                # "https://wellfound.com/jobs?keywords=AI%20ethics&format=rss",
                # "https://wellfound.com/jobs?keywords=responsible%20AI&format=rss",
            ]
        }
        
        # Keywords for relevance scoring
        self.high_value_keywords = [
            'ai ethics', 'responsible ai', 'ai governance', 'algorithmic fairness',
            'ai safety', 'digital rights', 'technology policy', 'ai regulation',
            'machine learning ethics', 'algorithmic bias', 'ai transparency',
            'ai accountability', 'ethical ai', 'trustworthy ai'
        ]
        
        self.medium_value_keywords = [
            'artificial intelligence', 'machine learning', 'data ethics',
            'policy', 'governance', 'privacy', 'algorithm', 'transparency',
            'bias', 'fairness', 'ethics', 'regulation', 'compliance'
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

    def scrape_rss_feed(self, feed_url: str, feed_type: str) -> List[Dict]:
        """Scrape a single RSS feed"""
        jobs = []
        
        try:
            print(f"🔍 Scraping RSS feed: {feed_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                print(f"⚠️ RSS parsing warning for {feed_url}: {feed.bozo_exception}")
            
            if not hasattr(feed, 'entries') or not feed.entries:
                print(f"⚠️ No entries found in RSS feed: {feed_url}")
                return []
            
            print(f"📄 Found {len(feed.entries)} entries in RSS feed")
            
            for entry in feed.entries:
                job = self.parse_rss_entry(entry, feed_url, feed_type)
                if job and self.quick_relevance_check(job):
                    jobs.append(job)
            
            print(f"✅ Extracted {len(jobs)} relevant jobs from RSS feed")
            
        except Exception as e:
            print(f"❌ Error scraping RSS feed {feed_url}: {e}")
        
        return jobs

    def parse_rss_entry(self, entry: Any, feed_url: str, feed_type: str) -> Dict:
        """Parse individual RSS entry into job data"""
        try:
            # Extract basic information
            title = getattr(entry, 'title', 'Unknown Position')
            description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
            link = getattr(entry, 'link', '')
            
            # Clean HTML from description
            description = self.clean_html(description)
            
            # Extract date
            published_date = self.parse_date(entry)
            
            # Extract location from title or description
            location = self.extract_location(title, description)
            
            # Extract company name
            company = self.extract_company(title, description, entry)
            
            # Determine job type and category
            job_type = self.determine_job_type(company, description)
            category = self.determine_category(title, description)
            
            # Calculate basic relevance score
            relevance_score = self.calculate_relevance(title, description)
            
            # Generate tags
            tags = self.generate_tags(title, description, feed_type)
            
            job = {
                "title": title,
                "company": company,
                "location": location,
                "job_type": job_type,
                "category": category,
                "description": description[:500] + "..." if len(description) > 500 else description,
                "full_description": description,
                "posting_date": published_date,
                "deadline": None,
                "source_url": link,
                "source_site": f"rss_{feed_type}",
                "tags": tags,
                "relevance_score": relevance_score,
                "salary_info": self.extract_salary(description),
                "is_remote": self.is_remote_job(title, description),
                "rss_source": feed_url
            }
            
            return job
            
        except Exception as e:
            print(f"⚠️ Error parsing RSS entry: {e}")
            return None

    def clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        clean_text = clean_text.replace('&lt;', '<').replace('&gt;', '>')
        clean_text = clean_text.replace('&amp;', '&').replace('&quot;', '"')
        clean_text = clean_text.replace('&#39;', "'").replace('&nbsp;', ' ')
        
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()

    def parse_date(self, entry: Any) -> str:
        """Parse date from RSS entry"""
        try:
            # Try different date fields
            date_fields = ['published', 'updated', 'created']
            
            for field in date_fields:
                if hasattr(entry, field):
                    date_str = getattr(entry, field)
                    if date_str:
                        # Parse date
                        if hasattr(entry, f"{field}_parsed"):
                            date_tuple = getattr(entry, f"{field}_parsed")
                            if date_tuple:
                                date_obj = datetime(*date_tuple[:6])
                                return date_obj.strftime("%Y-%m-%d")
            
            # Fallback to today
            return datetime.now().strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"⚠️ Date parsing error: {e}")
            return datetime.now().strftime("%Y-%m-%d")

    def extract_location(self, title: str, description: str) -> str:
        """Extract location from title or description"""
        content = f"{title} {description}".lower()
        
        # Common location patterns
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
            r'(remote)',
            r'(san francisco|new york|washington|london|boston|seattle|toronto|berlin)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).title()
        
        return "Location TBD"

    def extract_company(self, title: str, description: str, entry: Any) -> str:
        """Extract company name from RSS entry"""
        # Try to get from RSS entry author or other fields
        if hasattr(entry, 'author') and entry.author:
            return entry.author
        
        # Try to extract from title (common pattern: "Job Title at Company")
        at_match = re.search(r'\s+at\s+([^-]+)', title, re.IGNORECASE)
        if at_match:
            company = at_match.group(1).strip()
            if len(company) < 100:  # Reasonable company name length
                return company
        
        # Try to extract from description
        company_patterns = [
            r'Company:\s*([^\n]+)',
            r'Employer:\s*([^\n]+)',
            r'Organization:\s*([^\n]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) < 100:
                    return company
        
        return "Unknown Company"

    def extract_salary(self, description: str) -> str:
        """Extract salary information from description"""
        salary_patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'\$[\d,]+[kK]?\s*-\s*\$[\d,]+[kK]?',
            r'£[\d,]+\s*-\s*£[\d,]+',
            r'€[\d,]+\s*-\s*€[\d,]+',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(0)
        
        return ""

    def is_remote_job(self, title: str, description: str) -> bool:
        """Check if job is remote"""
        content = f"{title} {description}".lower()
        remote_indicators = ['remote', 'work from home', 'telecommute', 'distributed']
        return any(indicator in content for indicator in remote_indicators)

    def determine_job_type(self, company: str, description: str) -> str:
        """Determine job type based on company and description"""
        content = f"{company} {description}".lower()
        
        if any(term in content for term in ['university', 'college', 'institute of technology', 'academic']):
            return 'faculty'
        elif any(term in content for term in ['government', 'federal', 'department', 'agency', '.gov']):
            return 'government'
        elif any(term in content for term in ['united nations', 'world bank', 'oecd', 'unesco']):
            return 'international'
        elif any(term in content for term in ['foundation', 'nonprofit', 'ngo', 'institute', 'think tank']):
            return 'nonprofit'
        else:
            return 'industry'

    def determine_category(self, title: str, description: str) -> str:
        """Determine category based on content"""
        content = f"{title} {description}".lower()
        
        if any(term in content for term in ['law', 'legal', 'attorney', 'regulation', 'compliance']):
            return 'legal'
        elif any(term in content for term in ['policy', 'governance', 'government', 'regulatory']):
            return 'policy'
        elif any(term in content for term in ['engineer', 'engineering', 'developer', 'technical', 'software']):
            return 'technical'
        else:
            return 'research'

    def generate_tags(self, title: str, description: str, feed_type: str) -> List[str]:
        """Generate relevant tags"""
        tags = [feed_type.title()]
        content = f"{title} {description}".lower()
        
        # Technology tags
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
        if 'research' in content:
            tags.append("Research")
        
        return list(set(tags))  # Remove duplicates

    def quick_relevance_check(self, job: Dict) -> bool:
        """Quick relevance check before Gemini processing"""
        content = f"{job.get('title', '')} {job.get('description', '')}".lower()
        
        # Must have at least one AI/tech keyword
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'algorithm', 'data science']
        has_ai_keyword = any(keyword in content for keyword in ai_keywords)
        
        # Must have at least one society/ethics keyword
        society_keywords = ['ethics', 'policy', 'governance', 'fairness', 'bias', 'transparency', 'responsibility', 'regulation']
        has_society_keyword = any(keyword in content for keyword in society_keywords)
        
        # Basic relevance score threshold
        relevance_threshold = job.get('relevance_score', 0) >= 40
        
        return has_ai_keyword and (has_society_keyword or relevance_threshold)

    def calculate_relevance(self, title: str, description: str) -> int:
        """Calculate relevance score"""
        content = f"{title} {description}".lower()
        score = 50  # Base score
        
        # High value keywords
        for keyword in self.high_value_keywords:
            if keyword in content:
                score += 15
        
        # Medium value keywords
        for keyword in self.medium_value_keywords:
            if keyword in content:
                score += 8
        
        # Title bonus
        title_keywords = ['ai', 'ethics', 'policy', 'responsible', 'governance']
        for keyword in title_keywords:
            if keyword in title.lower():
                score += 10
        
        return min(100, score)

    def scrape_all_rss(self) -> List[Dict]:
        """Scrape all RSS feeds"""
        all_jobs = []
        total_feeds = sum(len(feeds) for feeds in self.rss_feeds.values())
        current_feed = 0
        
        print(f"🚀 Starting RSS scraping from {total_feeds} feeds...")
        print("=" * 50)
        
        for feed_type, feed_urls in self.rss_feeds.items():
            if not feed_urls:
                continue
                
            print(f"\n📡 Scraping {feed_type} feeds...")
            
            for feed_url in feed_urls:
                current_feed += 1
                print(f"[{current_feed}/{total_feeds}] Processing: {feed_url}")
                
                jobs = self.scrape_rss_feed(feed_url, feed_type)
                all_jobs.extend(jobs)
                
                # Rate limiting
                time.sleep(1)
        
        # Remove duplicates
        unique_jobs = self.remove_duplicates(all_jobs)
        
        print(f"\n📊 RSS Scraping Summary:")
        print(f"   Total jobs found: {len(all_jobs)}")
        print(f"   Unique jobs: {len(unique_jobs)}")
        print(f"   Duplicates removed: {len(all_jobs) - len(unique_jobs)}")
        
        return unique_jobs

    def remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on URL and title+company"""
        seen = set()
        unique = []
        
        for job in jobs:
            url = job.get('source_url', '')
            title_company = f"{job.get('title', '')}-{job.get('company', '')}"
            identifier = url if url else title_company
            
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
            "by_source": {},
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
            
            source = job.get('source_site', 'unknown')
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
        
        result_data = {
            "jobs": jobs,
            "metadata": {
                "total_jobs": len(jobs),
                "last_update": datetime.now().isoformat(),
                "source": "rss_aggregator",
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
    scraper = RSSJobScraper()
    
    try:
        # Phase 1: Scrape RSS feeds
        print("Phase 1: Scraping RSS feeds...")
        raw_jobs = scraper.scrape_all_rss()
        
        if not raw_jobs:
            print("❌ No jobs found from RSS feeds")
            return 1
        
        # Save raw results
        scraper.save_results(raw_jobs, "rss_jobs_raw.json")

        # Phase 2: Gemini filtering
        print("\nPhase 2: Filtering with Gemini AI...")
        filtered_jobs = scraper.gemini_filter(raw_jobs)
        
        # Save filtered results
        final_data = scraper.save_results(filtered_jobs, "rss_gemini_jobs.json")
        
        # Print final summary
        print(f"\n🎉 RSS + Gemini Scraping Complete!")
        print(f"   Raw jobs collected: {len(raw_jobs)}")
        print(f"   Gemini filtered jobs: {len(filtered_jobs)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
