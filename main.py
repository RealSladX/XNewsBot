from crawler import curate_tech_news, curate_pop_news
from approval import send_approval_email
import json
from database import init_db, show_top_articles, store_post, get_cached_posts, show_top_posts
import time
import pytz
from datetime import datetime
from poster import (
    generate_post_text,
    search_image_pixabay,
    google_image_search,
    download_image,
)

tz = pytz.timezone("US/Pacific")
# Download NLTK data for keyword extraction
with open("config.json", "r") as f:
    config = json.load(f)


if __name__ == "__main__":
    conn, cur = init_db()
    if (datetime.now(tz).hour == 11) or (datetime.now(tz).hour == 0 and datetime.now(tz).minute == 0) or (datetime.now(tz).hour == 6 and datetime.now(tz).minute == 0) or (datetime.now(tz).hour == 12 and datetime.now(tz).minute == 0) or (datetime.now(tz).hour == 18 and datetime.now(tz).minute == 0):
        print("Crawl started at", datetime.now())
        start = time.time()
        curate_pop_news(config["legacy_urls"], config["keywords"], cur, conn)
        curate_tech_news(config["rss_urls"], config["keywords"], cur, conn)
        print(f"{time.time() - start}", "seconds")
        print("Crawl finished at", datetime.now())
    else:
        print("Current Crawl Times: 12AM, 6AM, 12PM, 6PM")
    res = show_top_articles(10, cur)
    for i, r in enumerate(res):
        cached = get_cached_posts(r[0], cur)
        if not cached:
            post_text = generate_post_text(r[3], config["genai_key"])
            store_post(r[0], post_text, r[5], cur, conn)
            img_path = download_image(r[5], filename=f"./imgs/article_{r[0]}.jpg")
    top_posts = show_top_posts(10, cur)
    conn.close()
