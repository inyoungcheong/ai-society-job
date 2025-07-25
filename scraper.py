#!/usr/bin/env python3
"""
AI & Society Job Scraper
Scrapes job postings and saves to JSON files
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re
from urllib.parse import urljoin, urlparse

# API key from GitHub Secrets
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class AIJobScraper:
    def __init__(self):
        self.jobs = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; JobBot/1.0; +https://github.com/your-username/ai-society-job)'
        })
        
        # AI & Society related keywords
        self.relevant_keywords = [
            'ai ethics', 'artificial intelligence', 'machine learning', 'ai policy',
            'algorithmic fairness', 'ai governance', 'technology law', 'digital rights',
            'ai safety', 'responsible ai', 'ai regulation', 'tech policy',
            'algorithmic accountability', 'ai transparency', 'digital policy',
            'technology ethics', 'computational social science', 'human-computer interaction',
            'data ethics', 'privacy policy', 'digital governance', 'tech for good',
            'algorithmic bias', 'ai alignment', 'technology governance', 'digital transformation',
            'innovation policy', 'emerging technology', 'future of work', 'digital society'
        ]
        
        # Exclude too technical or unrelated keywords
        self.exclude_keywords = [
            'software engineer', 'data engineer', 'devops', 'backend developer',
            'frontend developer', 'full stack', 'mobile developer', 'qa engineer',
            'database administrator', 'system administrator', 'network engineer'
        ]

    def calculate_relevance_score(self, job_data: Dict) -> int:
        """Calculate relevance score using Gemini API"""
        text = f"{job_data.get('title', '')} {job_data.get('description', '')}"
        text = text.lower()
        
        # Basic keyword matching score
        relevance_score = 0
        
        # Add points for relevant keywords
        for keyword in self.relevant_keywords:
            if keyword in text:
                relevance_score += 8
                
        # Subtract points for excluded keywords
        for keyword in self.exclude_keywords:
            if keyword in text:
                relevance_score -= 20
                
        # Use Gemini API for advanced scoring
        if GEMINI_API_KEY:
            ai_score = self.get_gemini_relevance_score(text)
            relevance_score = max(relevance_score, ai_score)
            
        return max(0, min(100, relevance_score))

    def get_gemini_relevance_score(self, text: str) -> int:
        """Calculate relevance score using Gemini API"""
        try:
            import google.generativeai as genai
            
            # Configure API key
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Rate how relevant this job posting is to "AI & Society" field on a scale of 0-100.
            
            AI & Society field includes:
            - AI Ethics
            - AI Policy & Governance  
            - Technology Law
            - Algorithmic Fairness
            - AI Safety
            - Digital Rights
            - Social Impact of Technology
            - Responsible AI
            - Data Ethics
            - Technology Governance
            - Innovation Policy
            
            Job posting content:
            {text[:800]}
            
            Scoring criteria:
            - 90-100: Core AI & Society roles (AI Ethics Researcher, AI Policy Manager, etc.)
            - 70-89: Strong relevance (AI-related law, tech policy, etc.)  
            - 50-69: Moderate relevance (general AI research with social considerations)
            - 30-49: Weak relevance (tech field but minimal social aspects)
            - 0-29: Not relevant (pure technical development, engineering, etc.)
            
            Please respond with only a number (0-100):
            """
            
            response = model.generate_content(prompt)
            score_text = response.text.strip()
            
            # Extract number
            import re
            numbers = re.findall(r'\d+', score_text)
            if numbers:
                score = int(numbers[0])
                return max(0, min(100, score))
                
        except Exception as e:
            print(f"Gemini API scoring error: {e}")
            
        return 0

    def scrape_indeed(self, query: str = "AI ethics policy") -> List[Dict]:
        """Scrape job postings from Indeed"""
        jobs = []
        
        try:
            # For demo purposes, create mock data
            # In production, implement actual scraping with BeautifulSoup
            mock_jobs = [
                {
                    "title": "AI Ethics Research Scientist",
                    "company": "Anthropic",
                    "location": "San Francisco, CA",
                    "job_type": "industry",
                    "category": "cs",
                    "description": "Research AI safety and alignment with focus on constitutional AI and responsible AI development. Work on developing frameworks for ethical AI systems and ensuring AI technology benefits humanity.",
                    "posting_date": datetime.now().strftime("%Y-%m-%d"),
                    "deadline": None,
                    "source_url": "https://www.indeed.com/viewjob?jk=ai_ethics_anthropic",
                    "source_site": "indeed",
                    "tags": ["AI Safety", "Research", "Ethics", "Responsible AI"]
                },
                {
                    "title": "Technology Policy Manager",
                    "company": "Microsoft",
                    "location": "Washington, DC",
                    "job_type": "industry", 
                    "category": "policy",
                    "description": "Lead policy initiatives around AI governance and responsible deployment of AI technologies. Engage with policymakers and stakeholders on AI regulation and digital rights.",
                    "posting_date": datetime.now().strftime("%Y-%m-%d"),
                    "deadline": None,
                    "source_url": "https://www.indeed.com/viewjob?jk=policy_microsoft",
                    "source_site": "indeed",
                    "tags": ["Policy", "AI Governance", "Government Relations", "Digital Rights"]
                },
                {
                    "title": "AI Safety Engineer",
                    "company": "Google DeepMind",
                    "location": "London, UK",
                    "job_type": "industry",
                    "category": "cs",
                    "description": "Work on technical AI safety research including alignment, interpretability, and robustness. Collaborate with researchers to ensure AI systems are safe and beneficial.",
                    "posting_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "deadline": None,
                    "source_url": "https://www.indeed.com/viewjob?jk=safety_deepmind",
                    "source_site": "indeed",
                    "tags": ["AI Safety", "Technical Research", "Alignment"]
                }
            ]
            
            for job in mock_jobs:
                relevance_score = self.calculate_relevance_score(job)
                if relevance_score >= 30:  # Minimum relevance threshold
                    job['relevance_score'] = relevance_score
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Indeed scraping error: {e}")
            
        return jobs

    def scrape_80000hours(self) -> List[Dict]:
        """Scrape job postings from 80,000 Hours job board"""
        jobs = []
        
        try:
            # Mock data for 80,000 Hours - high-impact career opportunities
            mock_jobs = [
                {
                    "title": "AI Governance Research Fellow",
                    "company": "Future of Humanity Institute",
                    "location": "Oxford, UK",
                    "job_type": "nonprofit",
                    "category": "policy",
                    "description": "Research AI governance mechanisms and policy frameworks to ensure beneficial AI development. Focus on international cooperation and regulatory approaches to AI safety.",
                    "posting_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
                    "source_url": "https://80000hours.org/job-board/ai-governance-fellow",
                    "source_site": "80000hours",
                    "tags": ["AI Governance", "Research", "Policy", "Global Coordination"]
                },
                {
                    "title": "Technology Ethics Program Manager",
                    "company": "Centre for AI Safety",
                    "location": "Remote",
                    "job_type": "nonprofit",
                    "category": "cs",
                    "description": "Manage programs focused on AI safety research and outreach. Coordinate with researchers, policymakers, and industry leaders on AI risk mitigation strategies.",
                    "posting_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "source_url": "https://80000hours.org/job-board/tech-ethics-manager",
                    "source_site": "80000hours",
                    "tags": ["Program Management", "AI Safety", "Risk Assessment"]
                },
                {
                    "title": "Digital Rights Advocate",
                    "company": "Electronic Frontier Foundation",
                    "location": "San Francisco, CA",
                    "job_type": "nonprofit",
                    "category": "law",
                    "description": "Advocate for digital rights and privacy protections in the age of AI. Work on policy analysis, legal research, and public education on AI and digital rights issues.",
                    "posting_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
                    "source_url": "https://80000hours.org/job-board/digital-rights-eff",
                    "source_site": "80000hours",
                    "tags": ["Digital Rights", "Privacy", "Legal Advocacy", "Public Policy"]
                }
            ]
            
            for job in mock_jobs:
                relevance_score = self.calculate_relevance_score(job)
                if relevance_score >= 40:  # Higher threshold for specialized boards
                    job['relevance_score'] = relevance_score
                    jobs.append(job)
                    
        except Exception as e:
            print(f"80,000 Hours scraping error: {e}")
            
        return jobs

    def scrape_academic_jobs_online(self) -> List[Dict]:
        """Scrape faculty positions from Academic Jobs Online"""
        jobs = []
        
        try:
            # Mock academic job postings
            mock_jobs = [
                {
                    "title": "Assistant Professor of AI Ethics",
                    "company": "MIT Computer Science",
                    "location": "Cambridge, MA",
                    "job_type": "faculty",
                    "category": "cs",
                    "description": "Tenure-track position in artificial intelligence with emphasis on ethical AI development, algorithmic fairness, and social implications of AI systems. Research areas include AI safety, responsible AI design, and interdisciplinary approaches to AI governance.",
                    "posting_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                    "source_url": "https://academicjobsonline.org/ajo/jobs/mit_ai_ethics",
                    "source_site": "academic_jobs_online",
                    "tags": ["Faculty", "Tenure Track", "AI Ethics", "Computer Science"]
                },
                {
                    "title": "Professor of Technology Law",
                    "company": "Stanford Law School",
                    "location": "Stanford, CA", 
                    "job_type": "faculty",
                    "category": "law",
                    "description": "Senior faculty position focusing on intersection of technology and law, AI regulation, algorithmic accountability, and digital rights. Candidates should have expertise in technology policy and legal frameworks for emerging technologies.",
                    "posting_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                    "source_url": "https://academicjobsonline.org/ajo/jobs/stanford_tech_law",
                    "source_site": "academic_jobs_online",
                    "tags": ["Faculty", "Law", "Technology Policy", "Senior Position"]
                },
                {
                    "title": "Postdoctoral Researcher - AI and Society",
                    "company": "UC Berkeley School of Information",
                    "location": "Berkeley, CA",
                    "job_type": "faculty",
                    "category": "ischool",
                    "description": "Postdoctoral research position studying societal impacts of AI systems. Research focus on algorithmic bias, AI transparency, and human-AI interaction. Collaboration with interdisciplinary team on AI ethics and policy.",
                    "posting_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "source_url": "https://academicjobsonline.org/ajo/jobs/berkeley_postdoc",
                    "source_site": "academic_jobs_online",
                    "tags": ["Postdoc", "iSchool", "AI and Society", "Interdisciplinary"]
                }
            ]
            
            for job in mock_jobs:
                relevance_score = self.calculate_relevance_score(job)
                if relevance_score >= 50:  # Higher threshold for faculty positions
                    job['relevance_score'] = relevance_score
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Academic Jobs Online scraping error: {e}")
            
        return jobs

        def scrape_government_positions(self) -> List[Dict]:
            """Scrape government positions related to AI and technology policy"""
            jobs = []
            
            try:
                # Mock government job postings
                mock_jobs = [
                    {
                        "title": "AI Policy Specialist",
                        "company": "National Institute of Standards and Technology (NIST)",
                        "location": "Gaithersburg, MD",
                        "job_type": "government",
                        "category": "policy",
                        "description": "Develop AI risk management frameworks and standards for federal agencies. Work on AI governance policies, risk assessment methodologies, and stakeholder engagement on AI regulation.",
                        "posting_date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                        "deadline": (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
                        "source_url": "https://www.usajobs.gov/job/ai-policy-nist",
                        "source_site": "usajobs",
                        "tags": ["Government", "AI Policy", "Risk Management", "Standards"]
                    },
                    {
                        "title": "Technology Ethics Advisor",
                        "company": "Office of Science and Technology Policy (OSTP)",
                        "location": "Washington, DC",
                        "job_type": "government",
                        "category": "policy",
                        "description": "Advise on ethical implications of emerging technologies including AI, provide policy recommendations on responsible innovation, and coordinate with federal agencies on technology ethics initiatives.",
                        "posting_date": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d"),
                        "deadline": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
                        "source_url": "https://www.usajobs.gov/job/tech-ethics-ostp",
                        "source_site": "usajobs",
                        "tags": ["Government", "Ethics", "Policy Advisory", "Federal"]
                    },
                    {
                        "title": "Digital Rights Legal Counsel",
                        "company": "Federal Trade Commission (FTC)",
                        "location": "Washington, DC",
                        "job_type": "government",
                        "category": "law",
                        "description": "Legal counsel specializing in digital rights, AI regulation, and consumer protection in digital markets. Work on enforcement actions, policy development, and legal analysis of emerging technologies.",
                        "posting_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                        "deadline": (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d"),
                        "source_url": "https://www.usajobs.gov/job/digital-rights-ftc",
                        "source_site": "usajobs",
                        "tags": ["Government", "Legal", "Digital Rights", "Consumer Protection"]
                    }
                ]
                
                for job in mock_jobs:
                    relevance_score = self.calculate_relevance_score(job)
                    if relevance_score >= 45:  # Government positions threshold
                        job['relevance_score'] = relevance_score
                        jobs.append(job)
                        
            except Exception as e:
                print(f"Government positions scraping error: {e}")
                
            return jobs
    
           def scrape_global_opportunities(self) -> List[Dict]: 
        """Global job opportunities and international organizations"""
        jobs = []
        
        try:
            mock_jobs = [
                {
                    "title": "AI Governance Specialist",
                    "company": "OECD",
                    "location": "Paris, France",
                    "job_type": "international",
                    "category": "policy",  # ✅ 새 카테고리
                    "description": "Develop international standards and guidelines for AI governance...",
                    "posting_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=40)).strftime("%Y-%m-%d"),
                    "source_url": "https://www.oecd.org/careers/ai-governance-specialist",
                    "source_site": "oecd",
                    "tags": ["International", "AI Governance", "Policy"],
                    "relevance_score": 90  # 직접 점수 설정 (calculate 함수 호출 안함)
                },
                {
                    "title": "Digital Rights Program Officer",
                    "company": "United Nations",
                    "location": "Geneva, Switzerland",
                    "job_type": "international",
                    "category": "legal",  # ✅ 새 카테고리
                    "description": "Support UN initiatives on digital rights and AI ethics...",
                    "posting_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "source_url": "https://careers.un.org/digital-rights",
                    "source_site": "un_careers",
                    "tags": ["UN", "Digital Rights", "Legal"],
                    "relevance_score": 88
                }
                # 나머지도 동일하게 카테고리 수정...
            ]
            
            # calculate_relevance_score 호출 제거하고 직접 점수 설정
            jobs.extend(mock_jobs)
                    
        except Exception as e:
            print(f"Global opportunities scraping error: {e}")
            
        return jobs

    def run_scraping(self) -> Dict[str, Any]:
        """Execute scraping from all sources"""
        print("🔍 Starting job scraping...")
        
        # Scrape from all sources
        indeed_jobs = self.scrape_indeed()
        hours80k_jobs = self.scrape_80000hours()
        academic_jobs = self.scrape_academic_jobs_online()
        government_jobs = self.scrape_government_positions()
        global_jobs = self.scrape_global_opportunities()
        
        # Combine all job postings
        all_jobs = indeed_jobs + hours80k_jobs + academic_jobs + government_jobs + global_jobs
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['source_url'] not in seen_urls:
                seen_urls.add(job['source_url'])
                unique_jobs.append(job)
        
        # Sort by relevance score
        unique_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Calculate statistics
        stats = self.calculate_stats(unique_jobs)
        
        print(f"✅ Scraping completed: {len(unique_jobs)} job postings collected")
        
        return {
            "jobs": unique_jobs,
            "stats": stats,
            "last_update": datetime.now().isoformat(),
            "total_scraped": len(all_jobs),
            "duplicates_removed": len(all_jobs) - len(unique_jobs)
        }

    def calculate_stats(self, jobs: List[Dict]) -> Dict[str, int]:
        """Calculate job posting statistics"""
        stats = {
            "total": len(jobs),
            "faculty": len([j for j in jobs if j['job_type'] == 'faculty']),
            "industry": len([j for j in jobs if j['job_type'] == 'industry']),
            "nonprofit": len([j for j in jobs if j['job_type'] == 'nonprofit']),
            "government": len([j for j in jobs if j['job_type'] == 'government']),
            "international": len([j for j in jobs if j['job_type'] == 'international']),
            "new_today": len([j for j in jobs if j['posting_date'] == datetime.now().strftime("%Y-%m-%d")]),
            "by_category": {
                "law": len([j for j in jobs if j['category'] == 'law']),
                "policy": len([j for j in jobs if j['category'] == 'policy']),
                "cs": len([j for j in jobs if j['category'] == 'cs']),
                "ischool": len([j for j in jobs if j['category'] == 'ischool'])
            }
        }
        return stats

    def save_to_json(self, data: Dict[str, Any]):
        """Save data to JSON files"""
        # Create data directory
        os.makedirs('data', exist_ok=True)
        
        # Main data file
        with open('data/jobs.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Statistics file
        with open('data/stats.json', 'w', encoding='utf-8') as f:
            json.dump(data['stats'], f, ensure_ascii=False, indent=2)
        
        # Last update time
        with open('data/last_update.json', 'w', encoding='utf-8') as f:
            json.dump({
                "last_update": data['last_update'],
                "total_jobs": data['stats']['total']
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Data saved: data/jobs.json ({data['stats']['total']} job postings)")


def main():
    """Main execution function"""
    scraper = AIJobScraper()
    
    try:
        # Run scraping
        data = scraper.run_scraping()
        
        # Save to JSON files
        scraper.save_to_json(data)
        
        # Print summary
        print("\n📊 Scraping Results:")
        print(f"   Total jobs: {data['stats']['total']}")
        print(f"   Faculty: {data['stats']['faculty']}")
        print(f"   Industry: {data['stats']['industry']}")
        print(f"   Non-profit: {data['stats']['nonprofit']}")
        print(f"   Government: {data['stats']['government']}")
        print(f"   International: {data['stats']['international']}")
        print(f"   New today: {data['stats']['new_today']}")
        print(f"   Duplicates removed: {data['duplicates_removed']}")
        
        print("\n🎯 By Category:")
        for category, count in data['stats']['by_category'].items():
            print(f"   {category}: {count}")
        
        # Gemini 분석 정보 추가 출력
        gemini_analyzed = len([j for j in data['jobs'] if 'gemini_reasoning' in j])
        if gemini_analyzed > 0:
            print(f"\n🤖 Gemini AI Analysis:")
            print(f"   AI-analyzed jobs: {gemini_analyzed}")
            print(f"   Average relevance: {sum(j.get('relevance_score', 0) for j in data['jobs']) // len(data['jobs'])}%")
            
            # 최고 품질 포지션들
            top_jobs = sorted([j for j in data['jobs'] if j.get('relevance_score', 0) >= 80], 
                            key=lambda x: x.get('relevance_score', 0), reverse=True)[:3]
            
            if top_jobs:
                print(f"\n⭐ Top AI & Society Positions:")
                for i, job in enumerate(top_jobs, 1):
                    print(f"   {i}. {job['title']} - {job['company']} ({job['relevance_score']}%)")
            
        print(f"\n🕒 Last update: {data['last_update']}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
