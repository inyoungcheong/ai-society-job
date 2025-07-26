
const linkedIn = require('linkedin-jobs-api');
const fs = require('fs');
const { spawn } = require('child_process');

async function scrapeLinkedInJobsWithGemini() {
    const searchCombinations = [
  {
    "keyword": "AI ethics",
    "location": "United States",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI ethics",
    "location": "Remote",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI ethics",
    "location": "Europe",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "responsible AI",
    "location": "United States",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "responsible AI",
    "location": "Remote",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "responsible AI",
    "location": "Europe",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI policy",
    "location": "United States",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI policy",
    "location": "Remote",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI policy",
    "location": "Europe",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI governance",
    "location": "United States",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI governance",
    "location": "Remote",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI governance",
    "location": "Europe",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "algorithmic fairness",
    "location": "United States",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "algorithmic fairness",
    "location": "Remote",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "algorithmic fairness",
    "location": "Europe",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI safety",
    "location": "United States",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI safety",
    "location": "Remote",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  },
  {
    "keyword": "AI safety",
    "location": "Europe",
    "experienceLevel": "",
    "jobType": "full time",
    "dateSincePosted": "past month",
    "limit": "25",
    "priority": "high"
  }
];
    
    let allJobs = [];
    let processedCount = 0;
    
    console.log(`🔍 Starting LinkedIn + Gemini scraping with ${searchCombinations.length} combinations...`);
    
    // Phase 1: Collect LinkedIn data
    for (const combo of searchCombinations) {
        processedCount++;
        console.log(`[${processedCount}/${searchCombinations.length}] LinkedIn: "${combo.keyword}" in "${combo.location}"`);
        
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
            
            const processedJobs = jobs.map(job => ({
                title: job.position || 'Unknown Position',
                company: job.company || 'Unknown Company',
                location: job.location || combo.location,
                job_type: determineJobType(job.company),
                category: 'research', // Will be updated by Gemini
                description: `LinkedIn: ${job.position} at ${job.company}. Query: ${combo.keyword}`,
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
            }));
            
            allJobs = allJobs.concat(processedJobs);
            console.log(`   ✅ Found ${jobs.length} jobs`);
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            
        } catch (error) {
            console.log(`   ❌ Error: ${error.message}`);
        }
    }
    
    // Save raw LinkedIn data first
    fs.writeFileSync('data/linkedin_raw.json', JSON.stringify(allJobs, null, 2));
    console.log(`\n💾 Raw LinkedIn data saved: ${allJobs.length} jobs`);
    
    // Phase 2: Gemini Analysis
    console.log(`\n🤖 Starting Gemini analysis phase...`);
    
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python3', ['linkedin_gemini_analyzer.py']);
        
        pythonProcess.stdout.on('data', (data) => {
            console.log(data.toString());
        });
        
        pythonProcess.stderr.on('data', (data) => {
            console.error(data.toString());
        });
        
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                console.log(`\n✅ Gemini analysis completed!`);
                
                // Load Gemini-enhanced results
                if (fs.existsSync('data/linkedin_gemini_jobs.json')) {
                    const enhancedData = JSON.parse(fs.readFileSync('data/linkedin_gemini_jobs.json'));
                    console.log(`🎯 Final Results: ${enhancedData.jobs.length} relevant jobs`);
                    resolve(enhancedData);
                } else {
                    reject(new Error('Gemini analysis failed - no output file'));
                }
            } else {
                reject(new Error(`Gemini analysis failed with code ${code}`));
            }
        });
    });
}

function determineJobType(company) {
    const companyLower = company.toLowerCase();
    if (companyLower.includes('university') || companyLower.includes('college')) return 'faculty';
    if (companyLower.includes('government') || companyLower.includes('federal')) return 'government';
    if (companyLower.includes('united nations') || companyLower.includes('oecd')) return 'international';
    if (companyLower.includes('foundation') || companyLower.includes('nonprofit')) return 'nonprofit';
    return 'industry';
}

function generateTags(title, searchQuery) {
    const tags = [searchQuery];
    const content = title.toLowerCase();
    if (content.includes('ai') || content.includes('artificial intelligence')) tags.push('AI');
    if (content.includes('ethics')) tags.push('Ethics');
    if (content.includes('policy')) tags.push('Policy');
    if (content.includes('research')) tags.push('Research');
    if (content.includes('senior') || content.includes('lead')) tags.push('Senior');
    return [...new Set(tags)];
}

scrapeLinkedInJobsWithGemini().catch(console.error);
