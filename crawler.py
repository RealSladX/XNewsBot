import feedparser
from newspaper import Article
from newspaper import popular_urls
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def extract_keywords(text):
    """Extract relevant keywords from text using NLTK."""
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text.lower())
    # Filter out stopwords, punctuation, and short words
    keywords = [word for word in tokens if word.isalnum() and word not in stop_words]
    return keywords


def score_article(text, keywords):
    # Simple scoring based on keywords and length
    score = 0
    # Keyword matching
    for keyword in keywords:
        if keyword.lower() in text:
            score += 10
    # Length-based scoring
    score += min(len(text) / 10, 20)  # Cap at 20 points
    return score


def parse_article(url, score_keywords):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()  # For summary
    title = article.title
    authors = article.authors
    summary = article.summary  # Truncate if needed
    image_url = article.top_image
    article_keywords = set(extract_keywords(title)).union(
        set(extract_keywords(summary))
    )
    score = score_article(article_keywords, score_keywords)
    parsing = {
        "title": title,
        "author(s)": authors,
        "summary": summary,
        "img": image_url,
        "keywords": article_keywords,
        "score": score,
    }
    return parsing


def curate_tech_news(rss_urls, keywords):
    articles = []
    print(keywords)
    for rss in rss_urls:
        try:
            feed = feedparser.parse(rss)
        except Exception as e:
            print(f"{e}")
            continue
        else:
            for entry in feed.entries:
                try:
                    parse = parse_article(entry.link, keywords)
                    print(parse["score"], entry.link)
                except Exception as e:
                    print(f"{e}")
                    continue
                else:
                    articles.append(parse)
    try:
        return sorted(articles, key=lambda x: x["score"], reverse=True)[:10]
    except Exception as e:
        print(f"Nothing to sort {e}")
        return articles
