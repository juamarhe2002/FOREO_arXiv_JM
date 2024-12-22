import sqlite3
import scraper_arXiv as sp
from apscheduler.schedulers.blocking import BlockingScheduler


def initialize_database():
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arXiv_id TEXT UNIQUE NOT NULL,
            title TEXT UNIQUE NOT NULL,
            authors TEXT NOT NULL,
            subjects TEXT NOT NULL,
            comments TEXT,
            popularity INTEGER DEFAULT 0,
            pdf_link TEXT NOT NULL);
        ''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    url = "https://arxiv.org/list/cs/new"
    num_articles = 3
    hour = 9

    scraper = sp.ScraperArXiv(url)

    # Fetch articles immediately for testing
    articles = scraper.fetch_articles(num_articles)
    if articles is not None:
        print(articles)

    # Schedule the daily task
    scheduler = BlockingScheduler()
    scheduler.add_job(scraper.fetch_articles, 'cron', hour=hour, args=[num_articles])  # Set to run daily at specified hour.
    print(f"Scheduler started. Task is set to run daily at {hour} .")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped manually.")
