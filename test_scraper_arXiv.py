import unittest
import sqlite3

from scraper_arXiv import ScraperArXiv


class ScraperTestCase(unittest.TestCase, ScraperArXiv):
    def setUp(self):
        self.url = "https://arxiv.org/list/cs/new"

        self.conn = sqlite3.connect('articles_test.db')
        self.cur = self.conn.cursor()
        self.cur.executescript('''
                DROP TABLE IF EXISTS Articles;

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
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    # Function to test if the database is created and functional
    def test_initialize_database(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Articles';")
        result = self.cur.fetchone()
        self.assertEqual(('Articles',), result, "Assert: test_initialize_database failed in table creation\n")

        self.cur.execute("PRAGMA table_info(Articles);")
        result = self.cur.fetchall()
        columns = ['id', 'arXiv_id', 'title', 'authors', 'subjects', 'comments', 'popularity', 'pdf_link']
        result = [col_info[1] for col_info in result]
        self.assertEqual(columns, result, "Assert: test_initialize_database failed in schema creation.\n")

    # Function to test saving and retrieving articles
    def test_article_functions(self):
        test_article_1 = {
            'arXiv_id': 'arXiv_id_1',
            'title': 'title_1',
            'authors': 'authors',
            'subjects': 'subjects',
            'comments': 'comments',
            'popularity': 0,
            'pdf_link': 'pdf_link'
        }

        test_article_2 = {
            'arXiv_id': 'arXiv_id_2',
            'title': 'title_2',
            'authors': 'authors',
            'subjects': 'subjects',
            'comments': 'comments',
            'popularity': 2,
            'pdf_link': 'pdf_link'
        }

        # Check if the article is new (should be True initially)
        is_new_before = self.is_new_article(test_article_1['arXiv_id'])
        self.assertEqual(is_new_before, True, "Assert: is_new_article(test_article_1) attempt 1 failed\n")
        is_new_before = self.is_new_article(test_article_2['arXiv_id'])
        self.assertEqual(is_new_before, True, "Assert: is_new_article(test_article_2) attempt 1 failed\n")

        # Save the article and check again (should be False)
        test_articles = [test_article_1, test_article_2]
        self.save_articles(test_articles)

        is_new_after = self.is_new_article(test_article_1['arXiv_id'])
        self.assertEqual(is_new_after, False, "Assert: is_new_article(test_article_1) attempt 2 failed\n")
        is_new_after = self.is_new_article(test_article_2['arXiv_id'])
        self.assertEqual(is_new_after, False, "Assert: is_new_article(test_article_2) attempt 2 failed\n")

    # Function to test if the articles are fetched correctly.
    def test_fetch_articles(self):
        articles3 = self.fetch_articles(3)
        self.assertEqual(len(articles3), 3, "Assert: fetch_arxiv_articles(3) failed")

        articles2 = self.fetch_articles(2)
        self.assertEqual(len(articles2), 2, "Assert: fetch_arxiv_articles(2) failed")

        self.assertNotEqual(articles3[0], articles2[0], "Assert: articles3[0] != articles2[0] failed")
        self.assertNotEqual(articles3[1], articles2[1], "Assert: articles3[1] != articles2[1] failed")


if __name__ == '__main__':
    unittest.main()
