import json
import os
from datetime import datetime

def load_json_safely(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'jobs': [], 'metadata': {}}

# Load all data sources
academic_data = load_json_safely('data/ajo_gemini_jobs.json')
# jsearch_data = load_json_safely('data/jsearch_gemini_jobs.json')  # Quota exceeded
rss_data = load_json_safely('data/rss_gemini_jobs.json')  # New RSS source
linkedin_data = load_json_safely('data/linkedin_gemini_jobs.json')

# Combine all jobs
all_jobs = []
all_jobs.extend(academic_data.get('jobs', []))
# all_jobs.extend(jsearch_data.get('jobs', []))  # Skip JSearch due to quota
all_jobs.extend(rss_data.get('jobs', []))  # Add RSS jobs
all_jobs.extend(linkedin_data.get('jobs', []))

# Remove duplicates based on URL and title+company
seen = set()
unique_jobs = []

for job in all_jobs:
    # Create unique identifier
    url = job.get('source_url', '')
    title_company = f"{job.get('title', '')}-{job.get('company', '')}"
    identifier = url if url else title_company
    
    if identifier not in seen:
        seen.add(identifier)
        unique_jobs.append(job)

# Sort by relevance score
unique_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

# Calculate combined statistics
stats = {
    'total_jobs': len(unique_jobs),
    'academic_jobs': len(academic_data.get('jobs', [])),
    'jsearch_jobs': 0,  # len(jsearch_data.get('jobs', [])),  # Quota exceeded
    'rss_jobs': len(rss_data.get('jobs', [])),  # New RSS count
    'linkedin_jobs': len(linkedin_data.get('jobs', [])),
    'duplicates_removed': len(all_jobs) - len(unique_jobs),
    'high_relevance': len([j for j in unique_jobs if j.get('relevance_score', 0) >= 80]),
    'gemini_analyzed': len([j for j in unique_jobs if j.get('gemini_analyzed', False)]),
    'remote_jobs': len([j for j in unique_jobs if j.get('is_remote', False)]),
    'by_job_type': {},
    'by_category': {},
    'sources': {
        'academic': len(academic_data.get('jobs', [])),
        'jsearch': 0,  # len(jsearch_data.get('jobs', [])),  # Quota exceeded
        'rss': len(rss_data.get('jobs', [])),  # New RSS source
        'linkedin': len(linkedin_data.get('jobs', []))
    }
}

# Count by job type and category
for job in unique_jobs:
    job_type = job.get('job_type', 'unknown')
    stats['by_job_type'][job_type] = stats['by_job_type'].get(job_type, 0) + 1
    
    category = job.get('category', 'unknown')  
    stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

# Create master data file
master_data = {
    'jobs': unique_jobs,
    'stats': stats,
    'metadata': {
        'last_update': datetime.now().isoformat(),
        'total_unique_jobs': len(unique_jobs),
        'sources_integrated': ['academic', 'rss', 'linkedin'],  # Updated sources
        'integration_date': datetime.now().isoformat(),
        'note': 'JSearch temporarily disabled due to quota limits'
    }
}

# Save master file
with open('data/all_jobs_integrated.json', 'w', encoding='utf-8') as f:
    json.dump(master_data, f, ensure_ascii=False, indent=2)

# Create summary
print(f'🎯 Data Integration Complete!')
print(f'   Academic jobs: {stats["academic_jobs"]}')
print(f'   JSearch jobs: {stats["jsearch_jobs"]} (quota exceeded)')
print(f'   RSS jobs: {stats["rss_jobs"]} (NEW SOURCE)')
print(f'   LinkedIn jobs: {stats["linkedin_jobs"]}')
print(f'   Total unique: {stats["total_jobs"]}')
print(f'   Duplicates removed: {stats["duplicates_removed"]}')
print(f'   High relevance (80+): {stats["high_relevance"]}')
print(f'   Gemini analyzed: {stats["gemini_analyzed"]}')
print(f'   Remote jobs: {stats["remote_jobs"]}')

print(f'\n📂 By Job Type:')
for job_type, count in stats['by_job_type'].items():
    print(f'   {job_type}: {count}')
    
print(f'\n📂 By Category:')
for category, count in stats['by_category'].items():
    print(f'   {category}: {count}')
    
print(f'\n📡 RSS Sources Breakdown:')
if rss_data.get('stats'):
    rss_stats = rss_data['stats']
    for source, count in rss_stats.get('by_source', {}).items():
        print(f'   {source}: {count}')
