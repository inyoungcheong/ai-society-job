#!/usr/bin/env python3
"""
LinkedIn Jobs API + Gemini AI Enhanced Scraper
High-quality AI & Society job filtering with LinkedIn data
"""

import json
import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Any

class LinkedInGeminiScraper:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Comprehensive AI & Society search queries
        self.queries = [
            # Core AI Ethics & Governance
            "AI ethics researcher",
            "AI ethics specialist", 
            "responsible AI",
            "responsible AI engineer",
            "AI governance",
            "AI governance specialist",
            "AI policy analyst",
            "AI policy researcher",
            "AI policy manager",
            "algorithmic fairness",
            "algorithmic accountability",
            "algorithmic bias researcher",
            "AI safety researcher",
            "AI safety engineer",
            "AI alignment researcher",
            
            # Technology Policy & Law
            "technology policy",
            "technology policy analyst",
            "digital policy",
            "digital rights",
            "digital rights advocate",
            "technology law",
            "tech policy",
            "AI regulation",
            "AI legal counsel",
            "technology ethics",
            "data ethics",
            "privacy policy",
            "cybersecurity policy",
            
            # Academic & Research
            "computational social science",
            "digital humanities",
            "human-computer interaction",
            "AI and society",
            "technology and society",
            "social computing",
            "AI social impact",
            "algorithmic justice",
            "digital equity",
            "tech for good",
            "social AI",
            
            # Government & International
            "AI strategy",
            "digital transformation policy",
            "innovation policy",
            "emerging technology policy",
            "science policy",
            "technology assessment",
            "AI standards",
            "AI compliance",
            "digital government",
            "e-governance",
            
            # Interdisciplinary Roles
            "AI product manager ethics",
            "responsible technology",
            "ethical AI consultant",
            "AI risk management",
            "AI audit",
            "AI transparency",
            "explainable AI policy",
            "AI fairness engineer",
            "bias detection",
            "AI oversight",
            
            # Emerging Areas
            "AI democratization",
            "AI accessibility",
            "inclusive AI",
            "AI for social good",
            "civic technology",
            "public interest technology",
            "technology justice",
            "digital inclusion",
            "AI education policy",
            "AI workforce development"
        ]
        
        # Global locations covering major AI hubs and policy centers
        self.locations = [
            # North America - United States
            "San Francisco Bay Area",
            "Silicon Valley",
            "Mountain View, California",
            "Palo Alto, California", 
            "San Jose, California",
            "Los Angeles, California",
            "Seattle, Washington",
            "Redmond, Washington",
            "Boston, Massachusetts",
            "Cambridge, Massachusetts",
            "New York City",
            "New York, New York",
            "Washington, DC",
            "Washington DC-Baltimore Area",
            "Austin, Texas",
            "Chicago, Illinois",
            "Atlanta, Georgia",
            "Denver, Colorado",
            "Portland, Oregon",
            "Philadelphia, Pennsylvania",
            "Pittsburgh, Pennsylvania",
            "Research Triangle, North Carolina",
            "Miami, Florida",
            
            # North America - Canada
            "Toronto, Ontario",
            "Vancouver, British Columbia", 
            "Montreal, Quebec",
            "Ottawa, Ontario",
            "Waterloo, Ontario",
            "Calgary, Alberta",
            
            # Europe - United Kingdom
            "London, England",
            "Cambridge, England",
            "Oxford, England",
            "Edinburgh, Scotland",
            "Manchester, England",
            
            # Europe - Continental
            "Paris, France",
            "Berlin, Germany",
            "Munich, Germany",
            "Amsterdam, Netherlands",
            "The Hague, Netherlands",
            "Zurich, Switzerland",
            "Geneva, Switzerland",
            "Stockholm, Sweden",
            "Copenhagen, Denmark",
            "Helsinki, Finland",
            "Oslo, Norway",
            "Dublin, Ireland",
            "Brussels, Belgium",
            "Vienna, Austria",
            "Barcelona, Spain",
            "Madrid, Spain",
            "Milan, Italy",
            "Rome, Italy",
            
            # Asia-Pacific
            "Singapore",
            "Tokyo, Japan",
            "Seoul, South Korea",
            "Hong Kong",
            "Sydney, Australia",
            "Melbourne, Australia",
            "Canberra, Australia",
            "Beijing, China",
            "Shanghai, China",
            "Shenzhen, China",
            "Bangalore, India",
            "Mumbai, India",
            "New Delhi, India",
            "Tel Aviv, Israel",
            
            # Remote Work
            "Remote",
            "Remote - US",
            "Remote - Europe", 
            "Remote - Global",
            "Work from home",
            "Hybrid",
            "Flexible location"
        ]
        
        # Quick filtering for Gemini optimization
        self.quick_exclude = [
            'software engineer', 'data engineer', 'devops', 'backend developer',
            'frontend developer', 'full stack', 'mobile developer', 'qa engineer',
            'database administrator', 'system administrator', 'network engineer',
            'sales', 'marketing', 'customer success', 'account manager'
        ]

    def quick_relevance_check(self, job: Dict) -> bool:
        """Quick pre-filter before Gemini analysis"""
        title = job.get('title', '').lower()
        company = job.get('company', '').lower()
        content = f"{title} {company}"
        
        # Exclude clearly irrelevant positions
        for exclude_term in self.quick_exclude:
            if exclude_term in content:
                return False
        
        # Include if any AI/policy/ethics terms present
        include_terms = [
            'ai', 'artificial intelligence', 'ethics', 'policy', 'governance',
            'algorithmic', 'digital', 'technology', 'responsible', 'safety'
        ]
        return any(term in content for term in include_terms)

    def get_gemini_analysis(self, job: Dict) -> Dict:
        """Enhanced Gemini analysis for LinkedIn jobs"""
        if not self.gemini_api_key:
            return {
                "is_relevant": True,
                "relevance_score": 70,
                "category": "research",
                "reasoning": "No Gemini API key - using default",
                "key_topics": [],
                "linkedin_enhanced": False
            }
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Analyze this LinkedIn job posting for "AI & Society" field relevance.

            Job Title: {job.get('title', '')}
            Company: {job.get('company', '')}
            Location: {job.get('location', '')}
            Search Query: {job.get('search_query', '')}
            Experience Level: {job.get('experience_level', '')}
            Company Logo Available: {bool(job.get('company_logo'))}
            Posted: {job.get('ago_time', '')}

            AI & Society field encompasses:
            - AI Ethics and Responsible AI Development
            - AI Policy, Governance, and Regulation
            - Algorithmic Fairness and Bias Mitigation
            - Technology Law and Digital Rights
            - AI Safety and Alignment Research
            - Human-Computer Interaction (social focus)
            - Computational Social Science
            - Public Interest Technology
            - AI Risk Management and Oversight
            - Digital Transformation Policy

            Provide analysis in this JSON format:
            {{
                "is_relevant": true/false,
                "relevance_score": 0-100,
                "category": "research/policy/legal/technical",
                "reasoning": "detailed explanation",
                "key_topics": ["topic1", "topic2", "topic3"],
                "career_level": "entry/mid/senior/executive",
                "linkedin_insights": {{
                    "company_type": "tech/academic/government/nonprofit/consulting",
                    "role_focus": "individual_contributor/management/leadership",
                    "growth_potential": "high/medium/low"
                }}
            }}

            Scoring Guidelines:
            - 90-100: Core AI & Society roles (AI Ethics Lead, AI Policy Director)
            - 70-89: Strong relevance (AI with clear societal components)
            - 50-69: Moderate relevance (Tech roles with ethics/policy aspects)
            - 30-49: Weak relevance (General tech with minimal social focus)
            - 0-29: Not relevant (Pure engineering, sales, unrelated)

            Categories:
            - research: Academic research, R&D, analysis roles
            - policy: Governance, regulation, public policy, strategy
            - legal: Law, compliance, rights, regulatory affairs
            - technical: AI/ML engineering with social considerations

            Career Levels:
            - entry: 0-2 years, junior, associate roles
            - mid: 3-7 years, senior individual contributor
            - senior: 8+ years, principal, staff, lead roles
            - executive: Director, VP, C-level positions

            Respond with ONLY the JSON object:
            """
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            try:
                if '```json' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                else:
                    json_text = response_text
                
                analysis = json.loads(json_text)
                
                # Ensure required fields
                analysis['linkedin_enhanced'] = True
                if 'is_relevant' not in analysis:
                    analysis['is_relevant'] = analysis.get('relevance_score', 0) >= 30
                
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error: {e}")
                return self.fallback_analysis(job)
                
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self.fallback_analysis(job)

    def fallback_analysis(self, job: Dict) -> Dict:
        """Fallback analysis when Gemini fails"""
        title = job.get('title', '').lower()
        company = job.get('company', '').lower()
        
        # Simple scoring
        score = 50
        if any(term in title for term in ['ai', 'ethics', 'policy', 'governance']):
            score += 20
        if any(term in title for term in ['responsible', 'safety', 'fair']):
            score += 15
        
        return {
            "is_relevant": score >= 30,
            "relevance_score": min(100, score),
            "category": "research",
            "reasoning": "Fallback analysis - Gemini unavailable",
            "key_topics": [],
            "linkedin_enhanced": False
        }

    def create_search_combinations(self) -> List[Dict]:
        """Create strategic search combinations optimized for Gemini analysis"""
        combinations = []
        
        # High-priority combinations (core terms + major locations)
        priority_queries = [
            "AI ethics", "responsible AI", "AI policy", "AI governance",
            "algorithmic fairness", "AI safety", "technology policy", 
            "digital rights", "AI regulation", "AI risk management"
        ]
        
        priority_locations = [
            "San Francisco Bay Area", "Washington, DC", "New York City",
            "London, England", "Boston, Massachusetts", "Seattle, Washington",
            "Toronto, Ontario", "Berlin, Germany", "Singapore", "Remote"
        ]
        
        # Priority combinations - will get Gemini analysis
        for query in priority_queries:
            for location in priority_locations[:6]:  # Top 6 locations
                combinations.append({
                    "keyword": query,
                    "location": location,
                    "experienceLevel": "senior",
                    "jobType": "full time",
                    "dateSincePosted": "past week",
                    "limit": "20",
                    "priority": "high",
                    "gemini_analyze": True
                })
        
        # Extended combinations - selective Gemini analysis
        for query in self.queries[15:35]:  # Middle-tier queries
            combinations.append({
                "keyword": query,
                "location": "Remote",
                "experienceLevel": "",
                "jobType": "full time", 
                "dateSincePosted": "past month",
                "limit": "15",
                "priority": "medium",
                "gemini_analyze": True
            })
        
        return combinations

    def generate_node_script_with_gemini(self) -> str:
        """Generate Node.js script with Python Gemini integration"""
        node_script = f'''
const linkedIn = require('linkedin-jobs-api');
const fs = require('fs');
const {{ spawn }} = require('child_process');

async function scrapeLinkedInJobsWithGemini() {{
    const searchCombinations = {json.dumps(self.create_search_combinations(), indent=2)};
    
    let allJobs = [];
    let processedCount = 0;
    
    console.log(`🔍 Starting LinkedIn + Gemini scraping with ${{searchCombinations.length}} combinations...`);
    
    // Phase 1: Collect LinkedIn data
    for (const combo of searchCombinations) {{
        processedCount++;
        console.log(`[${{processedCount}}/${{searchCombinations.length}}] LinkedIn: "${{combo.keyword}}" in "${{combo.location}}"`);
        
        try {{
            const queryOptions = {{
                keyword: combo.keyword,
                location: combo.location,
                dateSincePosted: combo.dateSincePosted,
                jobType: combo.jobType,
                experienceLevel: combo.experienceLevel,
                limit: combo.limit,
                remoteFilter: combo.location === 'Remote' ? 'remote' : '',
                sortBy: 'recent'
            }};
            
            const jobs = await linkedIn.query(queryOptions);
            
            const processedJobs = jobs.map(job => ({{
                title: job.position || 'Unknown Position',
                company: job.company || 'Unknown Company',
                location: job.location || combo.location,
                job_type: determineJobType(job.company),
                category: 'research', // Will be updated by Gemini
                description: `LinkedIn: ${{job.position}} at ${{job.company}}. Query: ${{combo.keyword}}`,
                posting_date: job.date || new Date().toISOString().split('T')[0],
                deadline: null,
                source_url: job.jobUrl || '',
                source_site: 'linkedin',
                tags: generateTags(job.position, combo.keyword),
                relevance_score: 60, // Will be updated by Gemini
                salary_info: job.salary || '',
                is_remote: combo.location === 'Remote' || job.location?.toLowerCase().includes('remote'),
                search_query: combo.keyword,
                experience_level: combo.experienceLevel,
                company_logo: job.companyLogo || '',
                ago_time: job.agoTime || '',
                gemini_analyze: combo.gemini_analyze || false
            }}));
            
            allJobs = allJobs.concat(processedJobs);
            console.log(`   ✅ Found ${{jobs.length}} jobs`);
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        }} catch (error) {{
            console.log(`   ❌ Error: ${{error.message}}`);
        }}
    }}
    
    // Save raw LinkedIn data first
    fs.writeFileSync('data/linkedin_raw.json', JSON.stringify(allJobs, null, 2));
    console.log(`\\n💾 Raw LinkedIn data saved: ${{allJobs.length}} jobs`);
    
    // Phase 2: Gemini Analysis
    console.log(`\\n🤖 Starting Gemini analysis phase...`);
    
    return new Promise((resolve, reject) => {{
        const pythonProcess = spawn('python3', ['linkedin_gemini_analyzer.py']);
        
        pythonProcess.stdout.on('data', (data) => {{
            console.log(data.toString());
        }});
        
        pythonProcess.stderr.on('data', (data) => {{
            console.error(data.toString());
        }});
        
        pythonProcess.on('close', (code) => {{
            if (code === 0) {{
                console.log(`\\n✅ Gemini analysis completed!`);
                
                // Load Gemini-enhanced results
                if (fs.existsSync('data/linkedin_gemini_jobs.json')) {{
                    const enhancedData = JSON.parse(fs.readFileSync('data/linkedin_gemini_jobs.json'));
                    console.log(`🎯 Final Results: ${{enhancedData.jobs.length}} relevant jobs`);
                    resolve(enhancedData);
                }} else {{
                    reject(new Error('Gemini analysis failed - no output file'));
                }}
            }} else {{
                reject(new Error(`Gemini analysis failed with code ${{code}}`));
            }}
        }});
    }});
}}

function determineJobType(company) {{
    const companyLower = company.toLowerCase();
    if (companyLower.includes('university') || companyLower.includes('college')) return 'faculty';
    if (companyLower.includes('government') || companyLower.includes('federal')) return 'government';
    if (companyLower.includes('united nations') || companyLower.includes('oecd')) return 'international';
    if (companyLower.includes('foundation') || companyLower.includes('nonprofit')) return 'nonprofit';
    return 'industry';
}}

function generateTags(title, searchQuery) {{
    const tags = [searchQuery];
    const content = title.toLowerCase();
    if (content.includes('ai') || content.includes('artificial intelligence')) tags.push('AI');
    if (content.includes('ethics')) tags.push('Ethics');
    if (content.includes('policy')) tags.push('Policy');
    if (content.includes('research')) tags.push('Research');
    if (content.includes('senior') || content.includes('lead')) tags.push('Senior');
    return [...new Set(tags)];
}}

scrapeLinkedInJobsWithGemini().catch(console.error);
'''
        return node_script

    def create_gemini_analyzer(self) -> str:
        """Create Python script for Gemini analysis of LinkedIn data"""
        analyzer_script = f'''#!/usr/bin/env python3
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
    
    print(f"\\n🎯 Enhanced {{len(enhanced_jobs)}} LinkedIn jobs saved!")

if __name__ == "__main__":
    main()
'''
        return analyzer_script

    def setup_complete_linkedin_scraper(self):
        """Set up complete LinkedIn + Gemini system"""
        # Create package.json
        package_json = {
            "name": "ai-society-linkedin-gemini-scraper",
            "version": "1.0.0",
            "description": "LinkedIn + Gemini AI scraper for AI & Society jobs",
            "dependencies": {
                "linkedin-jobs-api": "^2.3.0"
            },
            "scripts": {
                "scrape": "node linkedin_scraper.js"
            }
        }
        
        with open('package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create Node.js script
        with open('linkedin_scraper.js', 'w') as f:
            f.write(self.generate_node_script_with_gemini())
        
        # Create Python Gemini analyzer
        with open('linkedin_gemini_analyzer.py', 'w') as f:
            f.write(self.create_gemini_analyzer())
        
        print("🚀 LinkedIn + Gemini scraper setup completed!")
        print("   📦 Created: package.json")
        print("   🔗 Created: linkedin_scraper.js") 
        print("   🤖 Created: linkedin_gemini_analyzer.py")
        print("   💾 Output: data/linkedin_gemini_jobs.json")
        print("   🎯 Ready for index.html integration!")

def main():
    scraper = LinkedInGeminiScraper()
    
    print("🚀 LinkedIn + Gemini Job Scraper for AI & Society")
    print("=" * 60)
    print(f"📋 Queries: {len(scraper.queries)}")
    print(f"🌍 Locations: {len(scraper.locations)}")
    print(f"🔍 Search combinations: {len(scraper.create_search_combinations())}")
    print(f"🤖 Gemini API: {'Available' if scraper.gemini_api_key else 'Not configured'}")
    
    scraper.setup_complete_linkedin_scraper()

if __name__ == "__main__":
    main()", 
            "digital rights", "AI regulation"
        ]
        
        priority_locations = [
            "San Francisco Bay Area", "Washington, DC", "New York City",
            "London, England", "Boston, Massachusetts", "Seattle, Washington",
            "Toronto, Ontario", "Berlin, Germany", "Singapore", "Remote"
        ]
        
        # Priority combinations
        for query in priority_queries:
            for location in priority_locations:
                combinations.append({
                    "keyword": query,
                    "location": location,
                    "experienceLevel": "senior",
                    "jobType": "full time",
                    "dateSincePosted": "past week",
                    "limit": "25",
                    "priority": "high"
                })
        
        # Extended combinations (all queries + selected locations)
        extended_locations = [
            "Cambridge, Massachusetts", "Palo Alto, California", 
            "Paris, France", "Amsterdam, Netherlands", "Sydney, Australia",
            "Tokyo, Japan", "Tel Aviv, Israel"
        ]
        
        for query in self.queries[10:30]:  # Middle-tier queries
            for location in extended_locations:
                combinations.append({
                    "keyword": query,
                    "location": location, 
                    "experienceLevel": "associate",
                    "jobType": "full time",
                    "dateSincePosted": "past month",
                    "limit": "15",
                    "priority": "medium"
                })
        
        # Specialized combinations (unique queries + remote)
        for query in self.queries[30:]:  # Specialized queries
            combinations.append({
                "keyword": query,
                "location": "Remote",
                "experienceLevel": "",  # Any level
                "jobType": "full time",
                "dateSincePosted": "past week", 
                "limit": "20",
                "priority": "low"
            })
        
        return combinations

    def generate_node_script(self) -> str:
        """Generate Node.js script for LinkedIn API calls"""
        node_script = '''
const linkedIn = require('linkedin-jobs-api');
const fs = require('fs');

async function scrapeLinkedInJobs() {
    const searchCombinations = ''' + json.dumps(self.create_search_combinations(), indent=2) + ''';
    
    let allJobs = [];
    let processedCount = 0;
    
    console.log(`🔍 Starting LinkedIn scraping with ${searchCombinations.length} search combinations...`);
    
    for (const combo of searchCombinations) {
        processedCount++;
        console.log(`[${processedCount}/${searchCombinations.length}] Searching: "${combo.keyword}" in "${combo.location}"`);
        
        try {
            const queryOptions = {
                keyword: combo.keyword,
                location: combo.location,
                dateSincePosted: combo.dateSincePosted,
                jobType: combo.jobType,
                experienceLevel: combo.experienceLevel,
                limit: combo.limit,
                remoteFilter: combo.location === 'Remote' ? 'remote' : '',
                sortBy: 'recent'
            };
            
            const jobs = await linkedIn.query(queryOptions);
            
            // Process and standardize job data
            const processedJobs = jobs.map(job => ({
                title: job.position || 'Unknown Position',
                company: job.company || 'Unknown Company',
                location: job.location || combo.location,
                job_type: determineJobType(job.company),
                category: determineCategory(job.position, job.company),
                description: `LinkedIn job posting. Search query: ${combo.keyword}`,
                posting_date: job.date || new Date().toISOString().split('T')[0],
                deadline: null,
                source_url: job.jobUrl || '',
                source_site: 'linkedin',
                tags: generateTags(job.position, combo.keyword),
                relevance_score: calculateRelevance(job.position, combo.keyword),
                salary_info: job.salary || '',
                is_remote: combo.location === 'Remote' || job.location?.toLowerCase().includes('remote'),
                search_query: combo.keyword,
                experience_level: combo.experienceLevel,
                company_logo: job.companyLogo || '',
                ago_time: job.agoTime || ''
            }));
            
            allJobs = allJobs.concat(processedJobs);
            console.log(`   ✅ Found ${jobs.length} jobs`);
            
            // Rate limiting
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            console.log(`   ❌ Error: ${error.message}`);
        }
    }
    
    // Remove duplicates
    const uniqueJobs = removeDuplicates(allJobs);
    
    // Calculate statistics
    const stats = calculateStats(uniqueJobs);
    
    // Save results
    const result = {
        jobs: uniqueJobs,
        stats: stats,
        metadata: {
            total_jobs: uniqueJobs.length,
            last_update: new Date().toISOString(),
            search_combinations: searchCombinations.length,
            api_calls_made: processedCount
        }
    };
    
    fs.writeFileSync('data/linkedin_jobs.json', JSON.stringify(result, null, 2));
    
    console.log(`\\n🎯 LinkedIn Scraping Results:`);
    console.log(`   Total unique jobs: ${uniqueJobs.length}`);
    console.log(`   Search combinations: ${searchCombinations.length}`);
    console.log(`   Duplicates removed: ${allJobs.length - uniqueJobs.length}`);
    
    return result;
}

function determineJobType(company) {
    const companyLower = company.toLowerCase();
    if (companyLower.includes('university') || companyLower.includes('college')) return 'faculty';
    if (companyLower.includes('government') || companyLower.includes('federal')) return 'government';
    if (companyLower.includes('united nations') || companyLower.includes('oecd')) return 'international';
    if (companyLower.includes('foundation') || companyLower.includes('nonprofit')) return 'nonprofit';
    return 'industry';
}

function determineCategory(title, company) {
    const content = `${title} ${company}`.toLowerCase();
    if (content.includes('law') || content.includes('legal')) return 'law';
    if (content.includes('policy') || content.includes('governance')) return 'policy';
    if (content.includes('engineer') || content.includes('technical')) return 'technical';
    return 'research';
}

function generateTags(title, searchQuery) {
    const tags = [searchQuery];
    const content = title.toLowerCase();
    if (content.includes('ai') || content.includes('artificial intelligence')) tags.push('AI');
    if (content.includes('ethics')) tags.push('Ethics');
    if (content.includes('policy')) tags.push('Policy');
    if (content.includes('research')) tags.push('Research');
    return tags;
}

function calculateRelevance(title, searchQuery) {
    const content = title.toLowerCase();
    let score = 60; // Base LinkedIn score
    
    if (content.includes('ai ethics')) score += 20;
    if (content.includes('responsible ai')) score += 20;
    if (content.includes('policy')) score += 15;
    if (content.includes('governance')) score += 15;
    if (content.includes('ethics')) score += 10;
    
    return Math.min(100, score);
}

function removeDuplicates(jobs) {
    const seen = new Set();
    return jobs.filter(job => {
        const key = job.source_url || `${job.title}-${job.company}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}

function calculateStats(jobs) {
    return {
        total: jobs.length,
        by_job_type: jobs.reduce((acc, job) => {
            acc[job.job_type] = (acc[job.job_type] || 0) + 1;
            return acc;
        }, {}),
        by_category: jobs.reduce((acc, job) => {
            acc[job.category] = (acc[job.category] || 0) + 1;
            return acc;
        }, {}),
        high_relevance: jobs.filter(j => j.relevance_score >= 80).length,
        remote_jobs: jobs.filter(j => j.is_remote).length,
        with_salary: jobs.filter(j => j.salary_info).length
    };
}

scrapeLinkedInJobs().catch(console.error);
'''
        return node_script

    def setup_linkedin_scraper(self):
        """Set up LinkedIn scraper with Node.js"""
        # Create package.json if it doesn't exist
        package_json = {
            "name": "ai-society-linkedin-scraper",
            "version": "1.0.0",
            "description": "LinkedIn job scraper for AI & Society positions",
            "main": "linkedin_scraper.js",
            "dependencies": {
                "linkedin-jobs-api": "^2.3.0"
            },
            "scripts": {
                "scrape": "node linkedin_scraper.js"
            }
        }
        
        with open('package.json', 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Generate Node.js script
        node_script = self.generate_node_script()
        with open('linkedin_scraper.js', 'w') as f:
            f.write(node_script)
        
        print("📦 LinkedIn scraper setup completed!")
        print("   Created: package.json")
        print("   Created: linkedin_scraper.js")
        print("   Run: npm install && npm run scrape")

def main():
    scraper = LinkedInJobScraper()
    
    print("🚀 LinkedIn Job Scraper for AI & Society")
    print("=" * 50)
    print(f"📋 Queries: {len(scraper.queries)}")
    print(f"🌍 Locations: {len(scraper.locations)}")
    print(f"🔍 Total combinations: {len(scraper.create_search_combinations())}")
    
    scraper.setup_linkedin_scraper()

if __name__ == "__main__":
    main()
