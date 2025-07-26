#!/usr/bin/env python3
"""
최소 RSS 테스트 - 빠른 디버깅용
"""

import feedparser
import requests
import time

def test_feeds():
    test_feeds = [
        "https://aijobs.net/feed/",
        "http://rss.jobsearch.monster.com/rssquery.ashx?q=AI+ethics&cy=us&pp=2000",
        "https://remoteok.io/api?tags=ai",
    ]
    
    for i, feed_url in enumerate(test_feeds):
        print(f"\n[{i+1}/3] Testing: {feed_url}")
        
        try:
            if 'remoteok.io/api' in feed_url:
                # Test RemoteOK API
                response = requests.get(feed_url, timeout=5)
                data = response.json()
                print(f"✅ RemoteOK API: {len(data)} jobs")
            else:
                # Test RSS
                feed = feedparser.parse(feed_url)
                print(f"✅ RSS: {len(feed.entries)} entries")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_feeds()