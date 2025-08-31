import sqlite3
from datetime import datetime

DB_FILE = "archive.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawled_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            summary TEXT,
            score REAL,
            crawl_timestamp DATETIME NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            post_text TEXT NOT NULL,
            generation_timestamp DATETIME NOT NULL,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    """)
    conn.commit()
    conn.close()


def is_article_cached(url):
    """Check if an article URL is in the database and recently crawled."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM crawled_articles
        WHERE url = ?
    """,
        (url,),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def store_article(title, url, summary, score):
    """Store a new article in the database and return its ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO crawled_articles (title, url, summary, score, crawl_timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, url, summary, score, datetime.now()),
        )
    except Exception as e:
        print(f"{e}")
    else:
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def store_posts(article_id, posts):
    """Store generated posts in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for post in posts:
        cursor.execute(
            """
            INSERT INTO posts (article_id, post_text, generation_timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (article_id, post, datetime.now()),
        )
    conn.commit()
    conn.close()


def show_top_articles():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    return cursor.execute("SELECT * FROM crawled_articles ORDER BY score DESC")
