#!/usr/bin/env python3
"""
AJO Complete Scraper - 모든 기능을 한 파일에
"""

import requests
import feedparser
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
from urllib.parse import urlparse, parse_qs

class AJORSScraper:
    def __init__(self):
        self.base_url = "https://academicjobsonline.org"
        self.rss_base = "https://academicjobsonline.org/ajo"
        
        # AI & Society 관련 분야 코드 (AJO 카테고리)
        self.relevant_fields = {
            'COMP': 'cs',          # Computer Science
            'INFO': 'ischool',     # Information Science  
            'LAW': 'law',          # Law
            'PHIL': 'cs',          # Philosophy (AI Ethics)
            'POLS': 'policy',      # Political Science
            'ECON': 'policy',      # Economics
            'SOC': 'policy',       # Sociology
        }
        
        # AI & Society 키워드 (필터링용)
        self.ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'ml',
            'ethics', 'policy', 'governance', 'regulation', 'algorithmic',
            'computational', 'digital', 'technology law', 'data science',
            'human-computer', 'hci', 'social computing', 'fairness',
            'transparency', 'accountability', 'bias', 'privacy'
        ]

    def get_rss_url(self, field_code: str = None) -> str:
        """RSS 피드 URL 생성"""
        if field_code:
            return f"{self.rss_base}?joblist-0-0-{field_code}-----rss--"
        else:
            return f"{self.rss_base}?joblist-0-0-0-----rss--"

    def fetch_rss_feed(self, rss_url: str) -> List[Dict]:
        """RSS 피드에서 채용공고 수집"""
        jobs = []
        
        try:
            print(f"🔍 Fetching RSS: {rss_url}")
            
            feed = feedparser.parse(rss_url)
            print(f"📊 Found {len(feed.entries)} entries in RSS feed")
            
            for entry in feed.entries:
                job_data = self.parse_rss_entry(entry)
                if job_data and self.is_ai_society_relevant(job_data):
                    jobs.append(job_data)
            
        except Exception as e:
            print(f"❌ Error fetching RSS feed: {e}")
        
        return jobs

    def parse_rss_entry(self, entry) -> Dict:
        """RSS 엔트리를 job 데이터로 변환"""
        try:
            title = entry.title if hasattr(entry, 'title') else 'Unknown Position'
            description = entry.description if hasattr(entry, 'description') else ''
            link = entry.link if hasattr(entry, 'link') else ''
            
            published_date = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            
            institution, location = self.extract_institution_location(title, description)
            category = self.determine_category_from_content(title, description, institution)
            
            job_data = {
                "title": title,
                "company": institution,
                "location": location,
                "job_type": "faculty",
                "category": category,
                "description": self.clean_description(description),
                "posting_date": published_date.strftime("%Y-%m-%d"),
                "deadline": self.extract_deadline(description),
                "source_url": link,
                "source_site": "academic_jobs_online",
                "tags": self.generate_tags(title, description, category),
                "relevance_score": self.calculate_relevance(title, description)
            }
            
            return job_data
            
        except Exception as e:
            print(f"⚠️ Error parsing RSS entry: {e}")
            return None

    def extract_institution_location(self, title: str, description: str) -> tuple:
        """제목과 설명에서 기관명과 위치 추출"""
        institution_patterns = [
            r'University of ([^,\n]+)',
            r'([^,\n]+) University',
            r'([^,\n]+) College',
            r'([^,\n]+) Institute',
            r'([^,\n]+) School',
        ]
        
        institution = "Unknown Institution"
        for pattern in institution_patterns:
            match = re.search(pattern, title + " " + description, re.IGNORECASE)
            if match:
                institution = match.group(0).strip()
                break
        
        location_patterns = [
            r'([A-Za-z\s]+),\s*([A-Z]{2})',
            r'([A-Za-z\s]+),\s*([A-Za-z]+)',
        ]
        
        location = "Location TBD"
        for pattern in location_patterns:
            match = re.search(pattern, description)
            if match:
                location = match.group(0).strip()
                break
        
        return institution, location

    def determine_category_from_content(self, title: str, description: str, institution: str) -> str:
        """내용 기반으로 카테고리 판단"""
        content = f"{title} {description} {institution}".lower()
        
        if any(term in content for term in ['law', 'legal', 'jurisprudence']):
            return 'law'
        elif any(term in content for term in ['policy', 'governance', 'politics', 'public']):
            return 'policy'
        elif any(term in content for term in ['information', 'library', 'ischool']):
            return 'ischool'
        else:
            return 'cs'

    def clean_description(self, description: str) -> str:
        """HTML 태그 제거 및 설명 정리"""
        clean_desc = re.sub(r'<[^>]+>', '', description)
        clean_desc = re.sub(r'\s+', ' ', clean_desc)
        return clean_desc[:500] + "..." if len(clean_desc) > 500 else clean_desc

    def extract_deadline(self, description: str) -> str:
        """설명에서 마감일 추출"""
        deadline_patterns = [
            r'deadline[:\s]*([A-Za-z]+ \d{1,2}, \d{4})',
            r'due[:\s]*([A-Za-z]+ \d{1,2}, \d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{1,2}-\d{1,2})'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                try:
                    return match.group(1)
                except:
                    continue
        
        return None

    def generate_tags(self, title: str, description: str, category: str) -> List[str]:
        """태그 생성"""
        tags = ["Faculty", "Academic", category.upper()]
        
        content = f"{title} {description}".lower()
        
        if any(term in content for term in ['artificial intelligence', 'ai ']):
            tags.append("AI")
        if any(term in content for term in ['machine learning', 'ml ']):
            tags.append("Machine Learning")
        if 'ethics' in content:
            tags.append("Ethics")
        if any(term in content for term in ['policy', 'governance']):
            tags.append("Policy")
        if 'tenure' in content:
            tags.append("Tenure Track")
        
        return tags

    def is_ai_society_relevant(self, job_data: Dict) -> bool:
        """AI & Society 분야와의 관련성 확인"""
        content = f"{job_data['title']} {job_data['description']}".lower()
        return any(keyword in content for keyword in self.ai_keywords)

    def calculate_relevance(self, title: str, description: str) -> int:
        """관련성 점수 계산"""
        content = f"{title} {description}".lower()
        score = 70
        
        high_value_keywords = ['ai ethics', 'algorithmic fairness', 'responsible ai']
        medium_value_keywords = ['artificial intelligence', 'machine learning', 'data science']
        
        for keyword in high_value_keywords:
            if keyword in content:
                score += 15
        
        for keyword in medium_value_keywords:
            if keyword in content:
                score += 10
        
        return min(100, score)

    def scrape_all_fields(self) -> List[Dict]:
        """모든 관련 분야에서 채용공고 수집"""
        all_jobs = []
        
        print("🚀 Starting AJO RSS scraping...")
        
        for field_code, category in self.relevant_fields.items():
            print(f"\n📚 Scraping field: {field_code} ({category})")
            
            rss_url = self.get_rss_url(field_code)
            jobs = self.fetch_rss_feed(rss_url)
            
            all_jobs.extend(jobs)
            print(f"✅ Found {len(jobs)} relevant jobs in {field_code}")
            
            time.sleep(5)  # robots.txt 준수
        
        # 중복 제거
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['source_url'] not in seen_urls:
                seen_urls.add(job['source_url'])
                unique_jobs.append(job)
        
        print(f"\n🎯 Total unique AI & Society jobs found: {len(unique_jobs)}")
        return unique_jobs

def main():
    """메인 실행 함수"""
    scraper = AJORSScraper()
    
    print("🚀 Starting comprehensive AJO collection...")
    print("=" * 60)
    
    # 모든 분야 수집
    all_jobs = scraper.scrape_all_fields()
    
    # 결과 분석
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Total AI & Society jobs found: {len(all_jobs)}")
    
    # 분야별 통계
    by_category = {}
    by_institution = {}
    
    for job in all_jobs:
        cat = job['category']
        by_category[cat] = by_category.get(cat, 0) + 1
        
        inst = job['company']
        by_institution[inst] = by_institution.get(inst, 0) + 1
    
    print(f"\n📊 By Category:")
    for cat, count in sorted(by_category.items()):
        print(f"   {cat}: {count} positions")
    
    print(f"\n🏛️ Top Institutions:")
    top_institutions = sorted(by_institution.items(), key=lambda x: x[1], reverse=True)[:10]
    for inst, count in top_institutions:
        print(f"   {inst}: {count} positions")
    
    # 높은 관련성 점수 채용공고들
    high_relevance = [job for job in all_jobs if job['relevance_score'] >= 85]
    print(f"\n⭐ High Relevance Jobs (85%+): {len(high_relevance)}")
    
    for i, job in enumerate(high_relevance[:5]):
        print(f"\n{i+1}. {job['title']}")
        print(f"   🏛️ {job['company']}")
        print(f"   📍 {job['location']}")
        print(f"   ⭐ {job['relevance_score']}%")
        print(f"   🏷️ {', '.join(job['tags'])}")
    
    # JSON으로 저장
    with open('ajo_real_jobs.json', 'w', encoding='utf-8') as f:
        json.dump({
            "jobs": all_jobs,
            "stats": {
                "total": len(all_jobs),
                "by_category": by_category,
                "high_relevance_count": len(high_relevance)
            },
            "collection_date": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Data saved to: ajo_real_jobs.json")
    return all_jobs

if __name__ == "__main__":
    main()