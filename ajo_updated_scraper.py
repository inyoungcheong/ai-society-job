#!/usr/bin/env python3
"""
개선된 AI & Society 필터링 - 더 엄격한 기준 적용
"""

import json
import re

class ImprovedAIFilter:
    def __init__(self):
        # 핵심 AI & Society 키워드 (더 엄격하게)
        self.core_ai_keywords = [
            'artificial intelligence', 'machine learning', 'deep learning',
            'ai ethics', 'algorithmic', 'computational', 'data science'
        ]
        
        # Society 관련 키워드
        self.society_keywords = [
            'ethics', 'policy', 'governance', 'regulation', 'law', 'legal',
            'fairness', 'bias', 'transparency', 'accountability', 'privacy',
            'digital rights', 'social', 'human-computer', 'technology policy'
        ]
        
        # 제외할 분야 (AI & Society와 관련 없음)
        self.exclude_fields = [
            'agriculture', 'farming', 'cattle', 'dairy', 'nutrition', 'animal',
            'biology', 'chemistry', 'physics', 'medicine', 'clinical',
            'pure mathematics', 'statistics only', 'economics only'
        ]
        
        # 허용할 기관 타입
        self.relevant_institutions = [
            'computer science', 'information', 'law', 'policy', 'government',
            'digital', 'technology', 'ai', 'data science', 'ethics'
        ]

    def is_truly_ai_society_relevant(self, job: dict) -> bool:
        """더 엄격한 AI & Society 관련성 판단"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        institution = job.get('company', '').lower()
        
        content = f"{title} {description} {institution}"
        
        # 1단계: 제외 분야 체크 (먼저 걸러내기)
        for exclude_term in self.exclude_fields:
            if exclude_term in content:
                print(f"❌ Excluded: {job['title']} (contains '{exclude_term}')")
                return False
        
        # 2단계: AI 키워드 체크
        has_ai_keyword = any(keyword in content for keyword in self.core_ai_keywords)
        
        # 3단계: Society 키워드 체크  
        has_society_keyword = any(keyword in content for keyword in self.society_keywords)
        
        # 4단계: 최소 하나씩은 있어야 함
        if not (has_ai_keyword or has_society_keyword):
            print(f"❌ Not relevant: {job['title']} (no AI or Society keywords)")
            return False
        
        # 5단계: 특별 케이스 - 정확한 AI & Society 용어
        exact_matches = [
            'ai and society', 'artificial intelligence and society',
            'ai ethics', 'algorithmic fairness', 'responsible ai',
            'ai governance', 'ai policy', 'technology law',
            'digital humanities', 'computational social science'
        ]
        
        if any(exact in content for exact in exact_matches):
            print(f"✅ Exact match: {job['title']}")
            return True
        
        # 6단계: AI + Society 키워드 조합 필요
        if has_ai_keyword and has_society_keyword:
            print(f"✅ AI + Society: {job['title']}")
            return True
        
        # 7단계: 특정 기관/부서는 허용
        for inst_type in self.relevant_institutions:
            if inst_type in institution:
                print(f"✅ Relevant institution: {job['title']}")
                return True
        
        print(f"❌ Not clearly relevant: {job['title']}")
        return False

    def recalculate_relevance_score(self, job: dict) -> int:
        """더 정확한 관련성 점수 계산"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        content = f"{title} {description}"
        
        score = 0
        
        # 정확한 AI & Society 용어들 (높은 점수)
        exact_terms = {
            'ai and society': 30,
            'artificial intelligence and society': 30,
            'ai ethics': 25,
            'algorithmic fairness': 25,
            'responsible ai': 25,
            'ai governance': 20,
            'technology law': 20,
            'digital rights': 20
        }
        
        for term, points in exact_terms.items():
            if term in content:
                score += points
        
        # 일반 AI 용어들 (중간 점수)
        ai_terms = {
            'artificial intelligence': 15,
            'machine learning': 15,
            'algorithmic': 10,
            'computational': 10,
            'data science': 10
        }
        
        for term, points in ai_terms.items():
            if term in content:
                score += points
        
        # Society 용어들 (중간 점수)
        society_terms = {
            'ethics': 10,
            'policy': 10,
            'governance': 10,
            'fairness': 8,
            'transparency': 8,
            'accountability': 8
        }
        
        for term, points in society_terms.items():
            if term in content:
                score += points
        
        return min(100, score)

def filter_and_improve_jobs():
    """기존 데이터를 더 엄격하게 필터링"""
    filter_system = ImprovedAIFilter()
    
    try:
        # 기존 변환된 데이터 로드
        with open('ajo_converted_jobs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📁 Loaded {len(data['jobs'])} jobs")
        print("🔍 Applying stricter AI & Society filter...")
        print("=" * 60)
        
        # 엄격한 필터링 적용
        filtered_jobs = []
        
        for job in data['jobs']:
            if filter_system.is_truly_ai_society_relevant(job):
                # 관련성 점수 재계산
                job['relevance_score'] = filter_system.recalculate_relevance_score(job)
                filtered_jobs.append(job)
        
        # 관련성 점수로 정렬
        filtered_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 새로운 통계 계산
        new_stats = calculate_filtered_stats(filtered_jobs)
        
        # 필터링된 데이터 저장
        filtered_data = {
            "jobs": filtered_jobs,
            "stats": new_stats,
            "collection_date": data.get('collection_date'),
            "category_system": "updated_filtered",
            "filter_applied": "strict_ai_society"
        }
        
        with open('ajo_filtered_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎯 Filtering Results:")
        print(f"Original jobs: {len(data['jobs'])}")
        print(f"Filtered jobs: {len(filtered_jobs)}")
        print(f"Removed: {len(data['jobs']) - len(filtered_jobs)} irrelevant jobs")
        
        print(f"\n📊 Filtered Category Distribution:")
        for category, count in new_stats['by_category'].items():
            print(f"   {category}: {count} positions")
        
        # 상위 관련성 채용공고들
        print(f"\n⭐ Top Relevant Jobs (filtered):")
        for i, job in enumerate(filtered_jobs[:5]):
            print(f"{i+1}. {job['title']}")
            print(f"   🏛️ {job['company']}")
            print(f"   📂 {job['category'].title()}")
            print(f"   ⭐ {job['relevance_score']}%")
            print()
        
        print(f"💾 Filtered data saved to: ajo_filtered_jobs.json")
        return filtered_data
        
    except Exception as e:
        print(f"❌ Error filtering jobs: {e}")
        return None

def calculate_filtered_stats(jobs):
    """필터링된 채용공고 통계 계산"""
    stats = {
        "total": len(jobs),
        "faculty": len([j for j in jobs if j['job_type'] == 'faculty']),
        "industry": len([j for j in jobs if j['job_type'] == 'industry']),
        "nonprofit": len([j for j in jobs if j['job_type'] == 'nonprofit']),
        "government": len([j for j in jobs if j['job_type'] == 'government']),
        "international": len([j for j in jobs if j['job_type'] == 'international']),
        "by_category": {
            "research": len([j for j in jobs if j['category'] == 'research']),
            "policy": len([j for j in jobs if j['category'] == 'policy']),
            "legal": len([j for j in jobs if j['category'] == 'legal']),
            "technical": len([j for j in jobs if j['category'] == 'technical'])
        }
    }
    return stats

if __name__ == "__main__":
    print("🔍 Applying strict AI & Society filtering...")
    print("=" * 50)
    
    filtered_data = filter_and_improve_jobs()
    
    if filtered_data:
        print("\n✅ Strict filtering completed!")
        print("📁 Use 'ajo_filtered_jobs.json' for the cleaned data")
    else:
        print("\n❌ Filtering failed!")