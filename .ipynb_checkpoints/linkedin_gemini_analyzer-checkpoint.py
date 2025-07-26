"""
Gemini AI Analyzer for LinkedIn Job Data
"""
import json
import os
import time
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class LinkedInGeminiAnalyzer:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Add quick_exclude list here
        self.quick_exclude = [
            'software engineer', 'data engineer', 'backend developer',
            'frontend developer', 'full stack', 'mobile developer', 'qa engineer',
            'database administrator', 'system administrator', 'network engineer',
            'sales', 'marketing', 'customer success', 'account manager'
        ]
        
    def quick_relevance_check(self, job: Dict) -> bool:
        """Enhanced quick relevance check before Gemini processing"""
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        company = job.get('company', '').lower()
        content = f"{title} {description} {company}"
        
        # Exclude clearly irrelevant positions (강화된 필터)
        exclude_terms = [
            # Technical roles (일반 개발직)
            'software engineer', 'full stack', 
            'mobile developer', 'ios developer', 'android developer',
            'devops engineer', 'site reliability', 'qa engineer', 'test engineer',
            'database administrator', 'system administrator', 'network engineer',
            
            # Business roles  
            'account manager', 'business analyst',
            'project manager', 'product manager', 'operations manager', 'hr manager',
            
            # Manual/service jobs
            'nurse', 'driver', 'cook', 'cashier', 'warehouse', 'technician', 'operator',
            'maintenance', 'security guard', 'janitor', 'cleaner', 'receptionist',
            
            # Finance/accounting (unless policy-related)
            'accountant', 'bookkeeper', 'financial advisor', 'loan officer',
            
            # Other unrelated
            'tutor', 'therapist', 'counselor', 'social worker'
        ]
        
        # Check for exclusion terms
        for exclude_term in exclude_terms:
            if exclude_term in content:
                return False
        
        # Must have at least one AI/tech/policy keyword (강화된 요구사항)
        required_keywords = [
            # AI/ML core terms
            'artificial intelligence', 'ai ', ' ai', 'machine learning', 'deep learning',
            'neural network', 'algorithm', 'data science', 'nlp', 'computer vision', 
            
            # AI & Society specific terms
            'ai ethics', 'responsible ai', 'ai governance', 'ai policy', 'ai safety',
            'algorithmic fairness', 'algorithmic bias', 'data ethics', 'ai regulation',
            'trustworthy ai', 'explainable ai', 'ai transparency', 'ai accountability',
            
            # Policy/governance terms
            'technology policy', 'digital policy', 'tech policy', 'policy analysis',
            'governance', 'regulation', 'compliance', 'privacy policy', 'digital rights',
            
            # Research terms
            'research scientist', 'research engineer', 'principal scientist', 'staff scientist',
            'computational social', 'human computer interaction', 'social computing', 'professor'
        ]
        
        has_required_keyword = any(keyword in content for keyword in required_keywords)
        
        # Additional bonus check for high-value terms in title
        title_bonus_terms = [
            'ethics', 'policy', 'governance', 'responsible', 'safety', 'fairness', 
            'research', 'scientist', 'principal', 'lead', 'director', 'manager'
        ]
        has_title_bonus = any(term in title for term in title_bonus_terms)
        
        # Must have required keyword AND (title bonus OR is from relevant search query)
        search_query = job.get('search_query', '').lower()
        is_targeted_search = any(term in search_query for term in ['ethics', 'policy', 'governance', 'responsible', 'safety'])
        
        return has_required_keyword and (has_title_bonus or is_targeted_search)
    
    def get_gemini_analysis(self, job: Dict) -> Dict:
        """Gemini analysis with LinkedIn-specific enhancements"""
        if not self.gemini_api_key:
            return {
                "is_relevant": True,
                "relevance_score": 70,
                "category": "research",
                "reasoning": "No API key available"
            }
            
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Analyze this LinkedIn job for AI & Society field relevance:

            Title: {job.get('title', '')}
            Company: {job.get('company', '')}
            Location: {job.get('location', '')}
            Experience: {job.get('experience_level', '')}
            Search Query: {job.get('search_query', '')}
            
            AI & Society includes: AI ethics, responsible AI, AI policy, algorithmic fairness, 
            AI governance, technology law, digital rights, AI safety, data ethics, AI research,
            machine learning with social impact, technology policy, privacy, and AI-related roles
            in academia, government, nonprofits, or tech companies.

            Is this job RELEVANT to AI & Society? Be generous - include:
            - Any AI/ML role with potential social impact
            - Technology policy or governance roles
            - Research positions involving AI
            - AI engineering roles at mission-driven companies
            - Data science roles with ethical considerations

            Return JSON with relevance analysis:
            
            {{
                "is_relevant": boolean,
                "relevance_score": 0-100,
                "category": "research/policy/legal/technical",
                "reasoning": "explanation",
                "key_topics": ["topic1", "topic2"],
                "seniority_level": "entry/mid/senior/executive"
            }}
            """
            
            response = model.generate_content(prompt)
            
            # Parse response
            try:
                response_text = response.text.strip()
                if '```json' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                    
                analysis = json.loads(json_text)
                analysis['gemini_analyzed'] = True
                return analysis
            except json.JSONDecodeError:
                return {"is_relevant": True, "relevance_score": 60, "category": "research", "gemini_analyzed": False}
                
        except Exception as e:
            print(f"Gemini error: {e}")
            return {"is_relevant": True, "relevance_score": 50, "category": "research", "gemini_analyzed": False}

def main():
    analyzer = LinkedInGeminiAnalyzer()
    
    # Load raw LinkedIn data
    with open('data/linkedin_raw.json', 'r') as f:
        jobs = json.load(f)
    
    print(f"🤖 Analyzing {len(jobs)} LinkedIn jobs with Gemini...")
    
    enhanced_jobs = []
    for i, job in enumerate(jobs):
        print(f"[{i+1}/{len(jobs)}] {job['title'][:40]}...")
        
        if not analyzer.quick_relevance_check(job):
            print(f"  ❌ Filtered out by quick check")
            continue
            
        analysis = analyzer.get_gemini_analysis(job)
        
        if analysis['is_relevant'] and analysis['relevance_score'] >= 30:
            job.update(analysis)
            enhanced_jobs.append(job)
            print(f"  ✅ {analysis['relevance_score']}% - {analysis['category']}")
        else:
            print(f"  ❌ {analysis['relevance_score']}% - Not relevant")
            
        time.sleep(0.5)  # Rate limiting
    
    # Save results
    result = {
        "jobs": enhanced_jobs,
        "metadata": {
            "total_jobs": len(enhanced_jobs),
            "original_count": len(jobs),
            "gemini_enhanced": True,
            "last_update": f"{time.strftime('%Y-%m-%dT%H:%M:%S')}"
        }
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/linkedin_gemini_jobs.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n🎯 Enhanced {len(enhanced_jobs)} LinkedIn jobs saved!")

if __name__ == "__main__":
    main()