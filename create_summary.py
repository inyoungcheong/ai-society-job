import json
from datetime import datetime

try:
    with open('data/all_jobs_integrated.json', 'r') as f:
        data = json.load(f)
    
    summary = {
        'last_update': data['metadata']['last_update'],
        'total_jobs': data['stats']['total_jobs'],
        'sources': data['stats']['sources'],
        'quality': {
            'high_relevance': data['stats']['high_relevance'],
            'gemini_analyzed': data['stats']['gemini_analyzed']
        }
    }
    
    with open('data/scraping_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
        
    print('✅ Created scraping summary')
except Exception as e:
    print(f'⚠️ Could not create summary: {e}')
