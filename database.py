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
            img_url TEXT,
            generated BOOL,
            crawl_timestamp DATETIME NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            post_text TEXT NOT NULL,
            img_url TEXT NOT NULL,
            generation_timestamp DATETIME NOT NULL,
            emailed BOOL,
            posted BOOL,
            FOREIGN KEY (article_id) REFERENCES crawled_articles (id)
        )
    """)
    conn.commit()
    return conn, cursor


def is_article_cached(url, cursor):
    """Check if an article URL is in the database and recently crawled."""
    return cursor.execute(
        """
        SELECT url FROM crawled_articles
        WHERE url = ?
    """,
        (url,),
    ).fetchone()


def store_article(title, url, summary, score, img_url, cursor, conn):
    """Store a new article in the database and return its ID."""
    try:
        cursor.execute(
            """
            INSERT INTO crawled_articles (title, url, summary, score, img_url, generated, crawl_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (title, url, summary, score, img_url, 0, datetime.now()),
        )
    except Exception as e:
        print(f"{e}")
    else:
        conn.commit()
        return cursor.lastrowid


def get_cached_posts(article_id, cursor):
    """Retrieve cached posts for an article ID."""
    return cursor.execute(
        "SELECT post_text, img_url FROM generated_posts WHERE article_id = ?",
        (article_id,),
    ).fetchall()


def store_post(article_id, post, img_url, cursor, conn):
    """Store generated posts in the database."""
    cursor.execute(
        """
        INSERT INTO generated_posts (article_id, post_text, img_url, emailed, posted, generation_timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (article_id, post, img_url, 0, 0, datetime.now()),
    )
    conn.commit()


def clear_posts(cursor, conn):
    cursor.execute("DROP TABLE IF EXISTS generated_posts")
    conn.commit()


def show_ungenerated_articles(size, cursor):
    return cursor.execute(
        "SELECT * FROM crawled_articles WHERE generated == 0 ORDER BY score DESC"
    ).fetchmany(size=size)


def show_unemailed_posts(size, cursor):
    return cursor.execute("SELECT * FROM generated_posts WHERE emailed == 0").fetchmany(
        size=size
    )


def show_unposted_posts(size, cursor):
    return cursor.execute("SELECT * FROM generated_posts WHERE posted == 0").fetchmany(
        size=size
    )
