# 🤖 AI & Society Job Leaderboard

An automated dashboard that collects and analyzes job postings in AI ethics, policy, law, and societal impact fields.

## 🎯 Key Features

- **Automated Scraping**: Daily collection of latest job postings from major job sites
- **AI-Powered Analysis**: Automatic relevance scoring using Gemini API
- **Real-time Filtering**: Search by job type, category, and location
- **Mobile Responsive**: Works seamlessly across all devices

## 🔍 Target Sources

### Job Sites
- **Indeed** - Industry positions
- **Academic Jobs Online** - University faculty positions
- **Idealist** - Non-profit organizations
- **LinkedIn Jobs** - Professional roles
- **Other specialized sites**

### Job Categories
- **Faculty**: University professors/researchers (tenure-track, postdoc)
- **Industry**: Corporate research labs, policy teams, consulting
- **Non-profit**: NGOs, think tanks, policy research institutes

### Field Specializations
- **Law**: Technology law, AI regulation, privacy protection
- **Policy**: AI governance, digital policy, regulatory policy
- **Computer Science**: AI ethics, responsible AI, AI safety
- **iSchool**: Information studies, digital society, HCI

## 🚀 Quick Start

### 1. Repository Setup

```bash
# 1. Fork this repository or use as template
# 2. Enable GitHub Pages (Settings > Pages > Source: GitHub Actions)
# 3. Set up API keys (Settings > Secrets and variables > Actions)
```

### 2. API Key Configuration

Add the following to GitHub Secrets:

- `GEMINI_API_KEY`: Google Gemini API key ([Free signup](https://makersuite.google.com/app/apikey))

### 3. Local Testing

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
echo "GEMINI_API_KEY=your_key_here" > .env

# Test scraping
python scraper.py

# Run local server
python -m http.server 8000
# Visit http://localhost:8000 in browser
```

### 4. Automation Verification

- **Daily scraping** runs automatically at **2 AM UTC**
- Check execution status in **Actions tab**
- Verify updated data on **website**

## 📊 Data Structure

### jobs.json
```json
{
  "jobs": [
    {
      "title": "AI Ethics Researcher",
      "company": "Stanford HAI",
      "location": "Stanford, CA",
      "job_type": "faculty",
      "category": "cs",
      "description": "...",
      "posting_date": "2025-07-24",
      "deadline": "2025-09-15",
      "source_url": "https://...",
      "relevance_score": 95,
      "tags": ["AI Ethics", "Research"]
    }
  ],
  "stats": {
    "total": 150,
    "faculty": 45,
    "industry": 80,
    "nonprofit": 25,
    "new_today": 12
  },
  "last_update": "2025-07-24T02:00:00Z"
}
```

## 🛠️ Customization

### Adding New Sites

Add new scraping function in `scraper.py`:

```python
def scrape_new_site(self) -> List[Dict]:
    """Scrape new job site"""
    jobs = []
    
    # Implement scraping logic
    # ...
    
    return jobs

# Call in run_scraping() function
new_jobs = self.scrape_new_site()
all_jobs = indeed_jobs + academic_jobs + nonprofit_jobs + new_jobs
```

### Modifying Filter Criteria

Update `relevant_keywords` and `exclude_keywords` in `scraper.py`:

```python
self.relevant_keywords = [
    # Add/modify relevant keywords
    'your_keyword_here'
]
```

### UI Customization

Modify CSS and JavaScript in `index.html` to change design and functionality.

## 📈 Monitoring

### GitHub Actions Logs
- Check execution history in **Actions tab**
- View scraping results summary in **Summary**
- Monitor **failure alerts** and error logs

### Data Quality Metrics
- **Duplicate removal rate**: Preventing duplicate job postings
- **Relevance accuracy**: Validating AI scoring
- **Collection coverage**: Coverage rate by major sites

## 🚨 Important Considerations

### Web Scraping Ethics
- **Respect robots.txt**: Check crawling policies for each site
- **Appropriate delays**: Prevent server overload (1-2 second intervals)
- **Terms of service**: Comply with each site's terms of service

### API Usage Management
- **Gemini API**: Monitor daily request limits
- **Cost monitoring**: Regular API usage review

### Privacy Protection
- **No personal data collection**: Exclude contact information
- **Public information only**: Target only publicly posted job listings
- **Source attribution**: Provide original links

## 🔧 Troubleshooting

### Scraping Failures
1. **API key verification**: Check Secrets configuration
2. **Dependency check**: Update requirements.txt
3. **Site changes**: Verify target site structure changes

### No Data Issues
1. **Filter criteria**: Check overly strict relevance scores
2. **Keyword updates**: Add/modify relevant keywords
3. **Site additions**: Consider new scraping targets

### Performance Optimization
1. **Scraping speed**: Implement parallel processing
2. **Data size**: JSON file compression
3. **Loading speed**: CDN or caching implementation

## 🤝 Contributing

1. **Fork** the repository
2. Create **feature branch**
3. **Commit** changes
4. Create **Pull Request**

### Contribution Ideas
- Add new job sites
- Improve AI analysis accuracy
- Enhance UI/UX
- Develop mobile app
- Add notification features

## 📄 License

MIT License - Free to use, modify, and distribute

## 🙋‍♀️ Support & Contact

- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and idea sharing
- **Wiki**: Detailed setup guides and FAQ

---

**Created by**: Tools for AI & Society researchers
**Purpose**: Centralize scattered job information in one accessible place
