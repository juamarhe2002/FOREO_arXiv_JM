import sqlite3
import scrapper_arXiv as sp


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
            pdf_link TEXT NOT NULL);
        ''')
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    url = "https://arxiv.org/list/cs/new"

    # Fetch articles immediately for testing
    articles = sp.fetch_articles(url)
    if articles is not None:
        print(articles)

    # Schedule the daily task
    sp.schedule_task('9', url)
