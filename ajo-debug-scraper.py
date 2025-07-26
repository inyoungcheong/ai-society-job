#!/usr/bin/env python3
"""
AJO Debug Scraper - 실제 웹사이트 구조 파악
"""

import requests
from bs4 import BeautifulSoup
import time

def debug_ajo_structure():
    """AJO 사이트 구조 디버깅"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    # 1. 메인 jobs 페이지 확인
    print("🔍 Step 1: Checking main jobs page...")
    main_url = "https://academicjobsonline.org/ajo/jobs"
    
    try:
        response = session.get(main_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 페이지 제목 확인
            title = soup.find('title')
            print(f"Page Title: {title.get_text() if title else 'No title found'}")
            
            # 가능한 job listing 클래스들 찾기
            print("\n🔍 Looking for job listings...")
            
            # 다양한 클래스명 시도
            possible_selectors = [
                'div.job-listing',
                'tr.job-row', 
                'div.listing',
                'div.job',
                'table tr',
                'div[class*="job"]',
                'tr[class*="job"]'
            ]
            
            for selector in possible_selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    
                    # 첫 번째 요소의 구조 출력
                    if elements:
                        print("Sample element structure:")
                        print(elements[0].prettify()[:500] + "...")
                        break
                else:
                    print(f"❌ No elements found with: {selector}")
            
            # 전체 HTML 구조 일부 출력 (디버깅용)
            print(f"\n📄 Page HTML sample:")
            print(response.text[:1000] + "...")
            
        else:
            print(f"❌ Failed to access main page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
    
    # 2. 검색 기능 테스트
    print(f"\n🔍 Step 2: Testing search functionality...")
    
    search_urls = [
        "https://academicjobsonline.org/ajo/jobs?keyword=computer+science",
        "https://academicjobsonline.org/ajo/jobs/computer-science",
        "https://academicjobsonline.org/ajo/COMP",  # 컴퓨터 과학 카테고리
    ]
    
    for search_url in search_urls:
        try:
            print(f"\nTrying: {search_url}")
            response = session.get(search_url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 결과 개수 찾기
                result_indicators = soup.find_all(text=lambda text: text and ('job' in text.lower() or 'position' in text.lower()))
                if result_indicators:
                    print(f"Found text mentioning jobs: {result_indicators[:3]}")
                
        except Exception as e:
            print(f"❌ Error with {search_url}: {e}")
        
        time.sleep(1)

def check_robots_txt():
    """robots.txt 확인"""
    print("\n🤖 Checking robots.txt...")
    try:
        response = requests.get("https://academicjobsonline.org/robots.txt", timeout=5)
        if response.status_code == 200:
            print("Robots.txt content:")
            print(response.text[:500])
        else:
            print(f"No robots.txt found: {response.status_code}")
    except Exception as e:
        print(f"Error checking robots.txt: {e}")

def simple_ajo_test():
    """간단한 AJO 접근 테스트"""
    print("🌐 Simple AJO access test...")
    
    try:
        response = requests.get("https://academicjobsonline.org", timeout=10)
        print(f"Main site status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if "Academic Jobs Online" in response.text:
            print("✅ Successfully accessed AJO!")
        else:
            print("⚠️ Might be accessing wrong site or blocked")
            
    except Exception as e:
        print(f"❌ Cannot access AJO: {e}")

if __name__ == "__main__":
    print("🕵️ AJO Structure Debug Tool")
    print("=" * 50)
    
    simple_ajo_test()
    check_robots_txt() 
    debug_ajo_structure()