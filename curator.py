import re
def score_article(article):
    # Simple scoring based on keywords and length
    tech_keywords = ['AI', 'blockchain', 'quantum', 'VR', 'AR', 'robotics', '5G']
    score = 0
    title = article['title'].lower()
    summary = article['summary'].lower()
    
    # Keyword matching
    for keyword in tech_keywords:
        if keyword.lower() in title or keyword.lower() in summary:
            score += 10
    # Length-based scoring
    score += min(len(summary) / 10, 20)  # Cap at 20 points
    article['score'] = score
    return score

def curate_articles(articles):
    # Score and sort articles
    for article in articles:
        article['score'] = score_article(article)
    
    # Return top 3
    return sorted(articles, key=lambda x: x['score'], reverse=True)[:3]
