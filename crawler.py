import requests
from bs4 import BeautifulSoup
import os

def crawl_tech_news():
    articles = []
    
    # Try scraping Techmeme
    url = "https://www.techmeme.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        print(f"Response status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('div.ii a')
        
        for item in items[:50]:
            title = item.text.strip()
            link = item.get('href', '')
            summary_elem = item.select_one('p, .summary')
            if title and link:  # Ensure both title and link are non-empty
                if not link.startswith('http'):
                    link = f"https://www.techmeme.com{link}"
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                articles.append({"title": title, "link": link, 'summary':summary})
                print(f"Found article: {title}")
        if not articles:
            print("No articles found with either selector.")
    except requests.RequestException as e:
        print(f"Error fetching Techmeme: {e}")
    return articles
