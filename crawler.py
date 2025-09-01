import feedparser
from newspaper import Article, build
import requests
from bs4 import BeautifulSoup
from database import is_article_cached, store_article


def score_article(text, keywords):
    # Simple scoring based on keywords and length
    score = 0
    # Keyword matching
    for keyword in keywords:
        if keyword.lower() in text:
            score += 10
    score *= (score + 1) / (len(text)+1)
    return score


def parse_article(url, score_keywords):
    article = Article(url)
    if not article:
        return None
    try:
        article.download()
    except Exception as e:
        print(f"{e}")
        return None
    else:
        article.parse()
        if article.publish_date and article.publish_date.year < 2025:
            return None
        else:
            article.nlp()  # For summary
            title = article.title
            authors = article.authors
            summary = article.summary  # Truncate if needed
            image_url = article.top_image
            article_keywords = article.keywords
            score = score_article(summary, score_keywords)
            if score < 60:
                return None
            else:
                parsing = {
                    "title": title,
                    "author(s)": authors,
                    "summary": summary,
                    "img": image_url,
                    "keywords": article_keywords,
                    "score": score,
                }
                return parsing


def soup_crawl(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all("article"):
        print(link.find_all("a")[0])
        print("\n")


def curate_tech_news(rss_urls, keywords, cur, conn):
    for rss in rss_urls:
        try:
            feed = feedparser.parse(rss)
        except Exception as e:
            print(f"{e}")
            continue
        else:
            for entry in feed.entries:
                try:
                    if is_article_cached(entry.link, cur):
                        continue
                    else:
                        parse = parse_article(entry.link, keywords)
                        if parse:
                            print(parse["score"], entry.link)
                            parse["url"] = entry.link
                            store_article(
                                parse["title"],
                                parse["url"],
                                parse["summary"],
                                parse["score"],
                                parse["img"],
                                cur,
                                conn
                            )
                except Exception as e:
                    print(f"{e}")
                    continue

def curate_pop_news(legacy_urls, keywords, cur, conn):
    for source in legacy_urls:
        try:
            paper = build(source)
        except Exception as e:
            print(f"Cannot build source{e}")
            continue
        else:
            for url in paper.article_urls():
                try:
                    if is_article_cached(url, cur):
                        continue
                    else:
                        parse = parse_article(url, keywords)
                        if parse:
                            print(parse["score"], url)
                            parse["url"] = url
                            store_article(
                                parse["title"],
                                parse["url"],
                                parse["summary"],
                                parse["score"],
                                cur,
                                conn
                            )
                except Exception as e:
                    print(f"{e}")
                    continue
