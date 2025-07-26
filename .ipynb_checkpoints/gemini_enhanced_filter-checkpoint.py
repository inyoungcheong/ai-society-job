#!/usr/bin/env python3
"""
Gemini API를 활용한 고도화된 AI & Society 필터링
"""


import json
import os
import time
from typing import Dict, List

from dotenv import load_dotenv
import os

# 파일 맨 앞에서 환경변수 로드
load_dotenv()

class GeminiEnhancedFilter:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            print("⚠️ GEMINI_API_KEY not found in environment variables")
        
        # 1차 키워드 필터링 (빠른 제거용)
        self.quick_exclude = [
            'cattle', 'dairy', 'agriculture', 'farming', 'animal husbandry',
            'experimental physics', 'quantum physics', 'pure chemistry',
            'organic chemistry', 'pure mathematics', 'clinical trial'
        ]
        
        # 1차 포함 키워드 (Gemini 분석 대상 선별)
        self.quick_include = [
            'artificial intelligence', 'machine learning', 'ai', 'algorithmic',
            'data science', 'computational', 'digital', 'information',
            'ethics', 'policy', 'governance', 'technology', 'human-computer'
        ]

    def quick_relevance_check(self, job: Dict) -> bool:
        """1차 빠른 관련성 체크 (Gemini API 호출 전)"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        content = f"{title} {description}"
        
        # 명확히 제외할 것들
        for exclude_term in self.quick_exclude:
            if exclude_term in content:
                return False
        
        # 포함 키워드 하나라도 있으면 Gemini 분석 대상
        return any(keyword in content for keyword in self.quick_include)

    def get_gemini_analysis(self, job: Dict) -> Dict:
        """Gemini API로 정밀 분석"""
        if not self.gemini_api_key:
            # API 키 없으면 기본값 반환
            return {
                "is_relevant": True,
                "relevance_score": 70,
                "category": "research",
                "reasoning": "API key not available - using default values"
            }
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Analyze this academic job posting for relevance to "AI & Society" field.

            Job Title: {job.get('title', '')}
            Institution: {job.get('company', '')}
            Description: {job.get('description', '')[:1000]}

            AI & Society field includes:
            - AI Ethics and Responsible AI
            - AI Policy and Governance
            - Algorithmic Fairness and Bias
            - Technology Law and Regulation
            - Digital Rights and Privacy
            - Human-Computer Interaction with social focus
            - Computational Social Science
            - Digital Humanities
            - AI Safety with societal implications
            - Data Science with ethical/policy considerations

            Please provide analysis in this EXACT JSON format:
            {{
                "is_relevant": true/false,
                "relevance_score": 0-100,
                "category": "research/policy/legal/technical",
                "reasoning": "brief explanation",
                "key_topics": ["topic1", "topic2"]
            }}

            Guidelines:
            - Score 0-30: Not related (pure tech/unrelated fields)
            - Score 30-60: Somewhat related (tech with minor social aspects)
            - Score 60-80: Related (clear AI & Society connections)
            - Score 80-100: Highly related (core AI & Society positions)

            Categories:
            - research: Academic research, studies, analysis
            - policy: Governance, regulation, public policy
            - legal: Law, regulation, compliance, rights
            - technical: AI/ML engineering with social considerations

            Respond with ONLY the JSON object:
            """
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSON 파싱 시도
            try:
                # JSON만 추출 (```json 제거)
                if '```json' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                
                analysis = json.loads(json_text)
                
                # 필수 필드 확인 및 기본값 설정
                if 'is_relevant' not in analysis:
                    analysis['is_relevant'] = analysis.get('relevance_score', 0) >= 30
                
                if 'category' not in analysis:
                    analysis['category'] = 'research'
                
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error for {job['title']}: {e}")
                print(f"Response: {response_text[:200]}...")
                
                # 파싱 실패시 응답에서 정보 추출
                return self.parse_fallback_response(response_text, job)
                
        except Exception as e:
            print(f"❌ Gemini API error for {job['title']}: {e}")
            return {
                "is_relevant": True,
                "relevance_score": 50,
                "category": "research",
                "reasoning": f"API error: {str(e)}"
            }

    def parse_fallback_response(self, response_text: str, job: Dict) -> Dict:
        """Gemini 응답 파싱 실패시 대안 분석"""
        response_lower = response_text.lower()
        
        # 관련성 판단
        relevant_indicators = ['relevant', 'related', 'yes', 'true', 'ai', 'society']
        irrelevant_indicators = ['not relevant', 'not related', 'no', 'false', 'unrelated']
        
        is_relevant = any(indicator in response_lower for indicator in relevant_indicators)
        if any(indicator in response_lower for indicator in irrelevant_indicators):
            is_relevant = False
        
        # 점수 추출 시도
        import re
        score_matches = re.findall(r'(\d+)', response_text)
        relevance_score = 50  # 기본값
        
        for match in score_matches:
            score = int(match)
            if 0 <= score <= 100:
                relevance_score = score
                break
        
        # 카테고리 추정
        content = f"{job.get('title', '')} {job.get('description', '')}".lower()
        if any(term in content for term in ['law', 'legal', 'regulation']):
            category = 'legal'
        elif any(term in content for term in ['policy', 'governance', 'government']):
            category = 'policy'
        elif any(term in content for term in ['engineer', 'technical', 'development']):
            category = 'technical'
        else:
            category = 'research'
        
        return {
            "is_relevant": is_relevant,
            "relevance_score": relevance_score,
            "category": category,
            "reasoning": "Fallback parsing used"
        }

def apply_gemini_enhanced_filtering():
    """Gemini API를 활용한 고도화된 필터링"""
    filter_system = GeminiEnhancedFilter()
    
    try:
        # 원본 데이터 로드
        with open('ajo_converted_jobs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📁 Loaded {len(data['jobs'])} jobs")
        print("🤖 Applying Gemini-enhanced AI & Society filtering...")
        print("=" * 70)
        
        enhanced_jobs = []
        processed_count = 0
        
        for job in data['jobs']:
            processed_count += 1
            print(f"\n[{processed_count}/{len(data['jobs'])}] Analyzing: {job['title'][:50]}...")
            
            # 1차 빠른 체크
            if not filter_system.quick_relevance_check(job):
                print(f"❌ Quick filter: Not relevant")
                continue
            
            # 2차 Gemini 정밀 분석
            print(f"🤖 Gemini analysis...")
            analysis = filter_system.get_gemini_analysis(job)
            
            # 결과 적용
            if analysis['is_relevant'] and analysis['relevance_score'] >= 30:
                job['relevance_score'] = analysis['relevance_score']
                job['category'] = analysis['category']
                job['gemini_reasoning'] = analysis.get('reasoning', '')
                job['key_topics'] = analysis.get('key_topics', [])
                
                enhanced_jobs.append(job)
                print(f"✅ Included: Score {analysis['relevance_score']}%, Category: {analysis['category']}")
                print(f"   Reasoning: {analysis.get('reasoning', '')[:80]}...")
            else:
                print(f"❌ Gemini filter: Score {analysis['relevance_score']}%, Not relevant")
            
            # API 호출 제한 (무료 tier 고려)
            time.sleep(1)  # 1초 딜레이
        
        # 점수순 정렬
        enhanced_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 통계 계산
        stats = {
            "total": len(enhanced_jobs),
            "faculty": len([j for j in enhanced_jobs if j['job_type'] == 'faculty']),
            "industry": len([j for j in enhanced_jobs if j['job_type'] == 'industry']),
            "nonprofit": len([j for j in enhanced_jobs if j['job_type'] == 'nonprofit']),
            "government": len([j for j in enhanced_jobs if j['job_type'] == 'government']),
            "international": len([j for j in enhanced_jobs if j['job_type'] == 'international']),
            "by_category": {
                "research": len([j for j in enhanced_jobs if j['category'] == 'research']),
                "policy": len([j for j in enhanced_jobs if j['category'] == 'policy']),
                "legal": len([j for j in enhanced_jobs if j['category'] == 'legal']),
                "technical": len([j for j in enhanced_jobs if j['category'] == 'technical'])
            }
        }
        
        # 최종 데이터 저장
        enhanced_data = {
            "jobs": enhanced_jobs,
            "stats": stats,
            "collection_date": data.get('collection_date'),
            "category_system": "gemini_enhanced",
            "filter_applied": "gemini_ai_analysis",
            "gemini_api_used": bool(filter_system.gemini_api_key)
        }
        
        with open('ajo_gemini_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎯 Gemini-Enhanced Filtering Results:")
        print(f"Original jobs: {len(data['jobs'])}")
        print(f"Gemini-filtered jobs: {len(enhanced_jobs)}")
        print(f"Removed: {len(data['jobs']) - len(enhanced_jobs)} jobs")
        
        print(f"\n📊 Category Distribution (Gemini-classified):")
        for category, count in stats['by_category'].items():
            print(f"   {category}: {count} positions")
        
        # 상위 관련성 채용공고들
        print(f"\n⭐ Top Relevant Jobs (Gemini-scored):")
        for i, job in enumerate(enhanced_jobs[:8]):
            print(f"{i+1}. {job['title']}")
            print(f"   🏛️ {job['company']}")
            print(f"   📂 {job['category'].title()}")
            print(f"   ⭐ {job['relevance_score']}% (Gemini)")
            if 'key_topics' in job and job['key_topics']:
                print(f"   🏷️ {', '.join(job['key_topics'])}")
            print()
        
        print(f"💾 Gemini-enhanced data saved to: ajo_gemini_jobs.json")
        return enhanced_data
        
    except Exception as e:
        print(f"❌ Error in Gemini-enhanced filtering: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Applying Gemini-enhanced AI & Society filtering...")
    print("=" * 60)
    
    result = apply_gemini_enhanced_filtering()
    
    if result:
        print("\n✅ Gemini-enhanced filtering completed!")
        print("📁 Use 'ajo_gemini_jobs.json' for the AI-analyzed data")
        print("🤖 Each job was analyzed by Gemini for precise relevance scoring")
    else:
        print("\n❌ Filtering failed!")