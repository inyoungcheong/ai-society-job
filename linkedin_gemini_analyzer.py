
"""
Gemini AI Analyzer for LinkedIn Job Data
"""
import json
import os
import time
from typing import Dict, List

class LinkedInGeminiAnalyzer:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
    def quick_relevance_check(self, job: Dict) -> bool:
        """Quick pre-filter"""
        title = job.get('title', '').lower()
        
        exclude_terms = {repr(self.quick_exclude)}
        for term in exclude_terms:
            if term in title:
                return False
        
        include_terms = ['ai', 'ethics', 'policy', 'governance', 'algorithmic', 'responsible']
        return any(term in title for term in include_terms)
    
    def get_gemini_analysis(self, job: Dict) -> Dict:
        """Gemini analysis with LinkedIn-specific enhancements"""
        if not self.gemini_api_key:
            return {{
                "is_relevant": True,
                "relevance_score": 70,
                "category": "research",
                "reasoning": "No API key available"
            }}
            
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Analyze this LinkedIn job for AI & Society field relevance:

            Title: {{job.get('title', '')}}
            Company: {{job.get('company', '')}}
            Location: {{job.get('location', '')}}
            Experience: {{job.get('experience_level', '')}}
            Posted: {{job.get('ago_time', '')}}
            
            Return JSON with relevance analysis focused on AI & Society intersection.
            
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
                    json_start = response_text.find('{{')
                    json_end = response_text.rfind('}}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                    
                return json.loads(json_text)
            except:
                return {{"is_relevant": True, "relevance_score": 60, "category": "research"}}
                
        except Exception as e:
            print(f"Gemini error: {{e}}")
            return {{"is_relevant": True, "relevance_score": 50, "category": "research"}}

def main():
    analyzer = LinkedInGeminiAnalyzer()
    
    # Load raw LinkedIn data
    with open('data/linkedin_raw.json', 'r') as f:
        jobs = json.load(f)
    
    print(f"🤖 Analyzing {{len(jobs)}} LinkedIn jobs with Gemini...")
    
    enhanced_jobs = []
    for i, job in enumerate(jobs):
        print(f"[{{i+1}}/{{len(jobs)}}] {{job['title'][:40]}}...")
        
        if not analyzer.quick_relevance_check(job):
            continue
            
        analysis = analyzer.get_gemini_analysis(job)
        
        if analysis['is_relevant'] and analysis['relevance_score'] >= 30:
            job.update(analysis)
            enhanced_jobs.append(job)
            print(f"  ✅ {{analysis['relevance_score']}}% - {{analysis['category']}}")
        else:
            print(f"  ❌ {{analysis['relevance_score']}}% - Not relevant")
            
        time.sleep(0.5)  # Rate limiting
    
    # Save results
    result = {{
        "jobs": enhanced_jobs,
        "metadata": {{
            "total_jobs": len(enhanced_jobs),
            "original_count": len(jobs),
            "gemini_enhanced": True,
            "last_update": "{{datetime.now().isoformat()}}"
        }}
    }}
    
    os.makedirs('data', exist_ok=True)
    with open('data/linkedin_gemini_jobs.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n🎯 Enhanced {{len(enhanced_jobs)}} LinkedIn jobs saved!")

if __name__ == "__main__":
    main()
