#!/usr/bin/env python3
"""
AI & Society Job Scraper
크롤링해서 JSON 파일로 저장하는 스크립트
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re
from urllib.parse import urljoin, urlparse

# API 키 (GitHub Secrets에서 가져오기)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class AIJobScraper:
    def __init__(self):
        self.jobs = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; JobBot/1.0; +https://github.com/your-username/job-leaderboard)'
        })
        
        # AI & Society 관련 키워드
        self.relevant_keywords = [
            'ai ethics', 'artificial intelligence', 'machine learning', 'ai policy',
            'algorithmic fairness', 'ai governance', 'technology law', 'digital rights',
            'ai safety', 'responsible ai', 'ai regulation', 'tech policy',
            'algorithmic accountability', 'ai transparency', 'digital policy',
            'technology ethics', 'computational social science', 'human-computer interaction'
        ]
        
        # 제외할 키워드 (너무 기술적이거나 관련 없는 것들)
        self.exclude_keywords = [
            'software engineer', 'data engineer', 'devops', 'backend developer',
            'frontend developer', 'full stack', 'mobile developer', 'qa engineer'
        ]

    def calculate_relevance_score(self, job_data: Dict) -> int:
        """Gemini API를 사용해서 관련성 점수 계산"""
        text = f"{job_data.get('title', '')} {job_data.get('description', '')}"
        text = text.lower()
        
        # 기본 키워드 매칭 점수
        relevance_score = 0
        
        # 관련 키워드가 있으면 점수 추가
        for keyword in self.relevant_keywords:
            if keyword in text:
                relevance_score += 10
                
        # 제외 키워드가 있으면 점수 감점
        for keyword in self.exclude_keywords:
            if keyword in text:
                relevance_score -= 15
                
        # Gemini API를 사용한 고급 점수 계산
        if GEMINI_API_KEY:
            ai_score = self.get_gemini_relevance_score(text)
            relevance_score = max(relevance_score, ai_score)
            
        return max(0, min(100, relevance_score))

    def get_gemini_relevance_score(self, text: str) -> int:
        """Gemini API를 사용해서 관련성 점수 계산"""
        try:
            import google.generativeai as genai
            
            # API 키 설정
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            다음 채용공고가 "AI & Society" 분야와 얼마나 관련있는지 0-100점으로 평가해주세요.
            
            AI & Society 분야는 다음을 포함합니다:
            - AI 윤리 (AI Ethics)
            - AI 정책 및 거버넌스 (AI Policy & Governance)  
            - 기술 법률 (Technology Law)
            - 알고리즘 공정성 (Algorithmic Fairness)
            - AI 안전성 (AI Safety)
            - 디지털 권리 (Digital Rights)
            - 기술의 사회적 영향 (Social Impact of Technology)
            - 책임있는 AI (Responsible AI)
            
            채용공고 내용:
            제목: {job_data.get('title', '')}
            설명: {text[:800]}
            
            평가 기준:
            - 90-100점: 핵심 AI & Society 분야 (AI 윤리 연구원, AI 정책 매니저 등)
            - 70-89점: 강한 관련성 (AI 관련 법률, 기술 정책 등)  
            - 50-69점: 중간 관련성 (일반 AI 연구에서 사회적 측면 고려)
            - 30-49점: 약한 관련성 (기술 분야이지만 사회적 측면 미미)
            - 0-29점: 관련성 없음 (순수 기술 개발, 엔지니어링 등)
            
            점수만 숫자로 답해주세요 (0-100):
            """
            
            response = model.generate_content(prompt)
            score_text = response.text.strip()
            
            # 숫자 추출
            import re
            numbers = re.findall(r'\d+', score_text)
            if numbers:
                score = int(numbers[0])
                return max(0, min(100, score))
                
        except Exception as e:
            print(f"Gemini API 점수 계산 오류: {e}")
            
        return 0

    def scrape_indeed(self, query: str = "AI ethics policy") -> List[Dict]:
        """Indeed에서 채용공고 크롤링"""
        jobs = []
        
        try:
            # Indeed 검색 URL
            url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l=&sort=date"
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Indeed 요청 실패: {response.status_code}")
                return jobs
                
            # 간단한 파싱 (실제로는 BeautifulSoup 사용 권장)
            # 여기서는 데모용으로 mock 데이터 생성
            mock_jobs = [
                {
                    "title": "AI Ethics Research Scientist",
                    "company": "Anthropic",
                    "location": "San Francisco, CA",
                    "job_type": "industry",
                    "category": "cs",
                    "description": "Research AI safety and alignment with focus on constitutional AI and harmlessness...",
                    "posting_date": datetime.now().strftime("%Y-%m-%d"),
                    "deadline": None,
                    "source_url": "https://www.indeed.com/viewjob?jk=example1",
                    "source_site": "indeed",
                    "tags": ["AI Safety", "Research", "Ethics"]
                },
                {
                    "title": "Technology Policy Manager",
                    "company": "Microsoft",
                    "location": "Washington, DC",
                    "job_type": "industry", 
                    "category": "policy",
                    "description": "Lead policy initiatives around AI governance and responsible deployment...",
                    "posting_date": datetime.now().strftime("%Y-%m-%d"),
                    "deadline": None,
                    "source_url": "https://www.indeed.com/viewjob?jk=example2",
                    "source_site": "indeed",
                    "tags": ["Policy", "AI Governance", "Government Relations"]
                }
            ]
            
            for job in mock_jobs:
                relevance_score = self.calculate_relevance_score(job)
                if relevance_score >= 30:  # 최소 관련성 임계점
                    job['relevance_score'] = relevance_score
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Indeed 크롤링 오류: {e}")
            
        return jobs

    def scrape_academic_jobs_online(self) -> List[Dict]:
        """Academic Jobs Online에서 faculty 포지션 크롤링"""
        jobs = []
        
        try:
            # 데모용 mock 데이터
            mock_jobs = [
                {
                    "title": "Assistant Professor of AI Ethics",
                    "company": "MIT Computer Science",
                    "location": "Cambridge, MA",
                    "job_type": "faculty",
                    "category": "cs",
                    "description": "Tenure-track position in artificial intelligence with emphasis on ethical AI development...",
                    "posting_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                    "source_url": "https://academicjobsonline.org/ajo/jobs/example1",
                    "source_site": "academic_jobs_online",
                    "tags": ["Faculty", "Tenure Track", "AI Ethics"]
                },
                {
                    "title": "Professor of Technology Law",
                    "company": "Stanford Law School",
                    "location": "Stanford, CA", 
                    "job_type": "faculty",
                    "category": "law",
                    "description": "Senior faculty position focusing on intersection of technology and law, AI regulation...",
                    "posting_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                    "source_url": "https://academicjobsonline.org/ajo/jobs/example2",
                    "source_site": "academic_jobs_online",
                    "tags": ["Faculty", "Law", "Technology Policy"]
                }
            ]
            
            for job in mock_jobs:
                relevance_score = self.calculate_relevance_score(job)
                if relevance_score >= 40:  # faculty 포지션은 높은 기준
                    job['relevance_score'] = relevance_score
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Academic Jobs Online 크롤링 오류: {e}")
            
        return jobs

    def scrape_idealist_nonprofits(self) -> List[Dict]:
        """Idealist에서 비영리 단체 채용공고 크롤링"""
        jobs = []
        
        try:
            # 데모용 mock 데이터
            mock_jobs = [
                {
                    "title": "AI Policy Advocate",
                    "company": "Electronic Frontier Foundation",
                    "location": "San Francisco, CA",
                    "job_type": "nonprofit",
                    "category": "policy",
                    "description": "Advocate for responsible AI policies and digital rights protection...",
                    "posting_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "source_url": "https://www.idealist.org/en/nonprofit-job/example1",
                    "source_site": "idealist",
                    "tags": ["Advocacy", "Digital Rights", "Policy"]
                }
            ]
            
            for job in mock_jobs:
                relevance_score = self.calculate_relevance_score(job)
                if relevance_score >= 35:
                    job['relevance_score'] = relevance_score
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Idealist 크롤링 오류: {e}")
            
        return jobs

    def run_scraping(self) -> Dict[str, Any]:
        """모든 사이트에서 크롤링 실행"""
        print("🔍 채용공고 크롤링 시작...")
        
        # 각 사이트에서 크롤링
        indeed_jobs = self.scrape_indeed()
        academic_jobs = self.scrape_academic_jobs_online()
        nonprofit_jobs = self.scrape_idealist_nonprofits()
        
        # 모든 채용공고 합치기
        all_jobs = indeed_jobs + academic_jobs + nonprofit_jobs
        
        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['source_url'] not in seen_urls:
                seen_urls.add(job['source_url'])
                unique_jobs.append(job)
        
        # 관련성 점수로 정렬
        unique_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 통계 계산
        stats = self.calculate_stats(unique_jobs)
        
        print(f"✅ 크롤링 완료: {len(unique_jobs)}개 채용공고 수집")
        
        return {
            "jobs": unique_jobs,
            "stats": stats,
            "last_update": datetime.now().isoformat(),
            "total_scraped": len(all_jobs),
            "duplicates_removed": len(all_jobs) - len(unique_jobs)
        }

    def calculate_stats(self, jobs: List[Dict]) -> Dict[str, int]:
        """채용공고 통계 계산"""
        stats = {
            "total": len(jobs),
            "faculty": len([j for j in jobs if j['job_type'] == 'faculty']),
            "industry": len([j for j in jobs if j['job_type'] == 'industry']),
            "nonprofit": len([j for j in jobs if j['job_type'] == 'nonprofit']),
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
        """JSON 파일로 저장"""
        # data 디렉토리 생성
        os.makedirs('data', exist_ok=True)
        
        # 메인 데이터 파일
        with open('data/jobs.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 통계만 별도 파일로도 저장
        with open('data/stats.json', 'w', encoding='utf-8') as f:
            json.dump(data['stats'], f, ensure_ascii=False, indent=2)
        
        # 마지막 업데이트 시간
        with open('data/last_update.json', 'w', encoding='utf-8') as f:
            json.dump({
                "last_update": data['last_update'],
                "total_jobs": data['stats']['total']
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 데이터 저장 완료: data/jobs.json ({data['stats']['total']}개 채용공고)")


def main():
    """메인 실행 함수"""
    scraper = AIJobScraper()
    
    try:
        # 크롤링 실행
        data = scraper.run_scraping()
        
        # JSON 파일로 저장
        scraper.save_to_json(data)
        
        # 결과 요약 출력
        print("\n📊 크롤링 결과:")
        print(f"   총 채용공고: {data['stats']['total']}개")
        print(f"   Faculty: {data['stats']['faculty']}개")
        print(f"   Industry: {data['stats']['industry']}개") 
        print(f"   Non-profit: {data['stats']['nonprofit']}개")
        print(f"   오늘 신규: {data['stats']['new_today']}개")
        print(f"   중복 제거: {data['duplicates_removed']}개")
        
        print("\n🎯 카테고리별:")
        for category, count in data['stats']['by_category'].items():
            print(f"   {category}: {count}개")
            
        print(f"\n🕒 마지막 업데이트: {data['last_update']}")
        
    except Exception as e:
        print(f"❌ 크롤링 실행 중 오류: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())