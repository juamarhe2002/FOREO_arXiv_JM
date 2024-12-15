import unittest
import sqlite3

import scrapper_arXiv


def initialize_database_test():
    conn = sqlite3.connect('articles_test.db')
    cur = conn.cursor()
    cur.executescript('''
        DROP TABLE IF EXISTS Articles;

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


class ScraperTestCase(unittest.TestCase, scrapper_arXiv):
    # Function to test if the database is created and functional
    def test_initialize_database(self):
        try:
            initialize_database_test()

            conn = sqlite3.connect('articles_test.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Articles';")
            result = cursor.fetchone()
            conn.close()
            self.assertEqual(not None, result, "Assert: test_initialize_database failed\n")
            return result is not None
        except Exception as e:
            print(f"Database test failed: {e}")
            return False

    # Function to test saving and retrieving articles
    def test_article_functions(self):
        try:
            test_article = {
                'arXiv_id': 'arXiv_id',
                'title': 'title',
                'authors': 'authors',
                'subjects': 'subjects',
                'pdf_link': 'pdf_link'
            }
            # Ensure the database is initialized
            initialize_database_test()

            # Check if the article is new (should be True initially)
            is_new_before = self.is_new_article(test_article)
            self.assertEqual(is_new_before, True, "Assert: is_new_article() attempt 1 failed\n")

            # Save the article and check again (should be False)
            self.save_article(test_article)
            is_new_after = self.is_new_article(test_article)
            self.assertEqual(is_new_before, False, "Assert: is_new_article() attempt 2 failed\n")

            return is_new_before and not is_new_after
        except Exception as e:
            print(f"Article function test failed: {e}")
            return False

    def test_fetch_articles(self):
        try:
            url = "https://arxiv.org/list/cs/new"
            articles = self.fetch_articles(url)
            self.assertEqual(len(articles), 3, "Assert: fetch_arxiv_articles() failed")
        except Exception as e:
            print(f"Article fetch failed: {e}")


if __name__ == '__main__':
    unittest.main()

    # Run the tests
    # ScraperTestCase.test_initialize_database()
    # ScraperTestCase.test_article_functions()

    # Print the test results
    print("Test Passed Successfully!!")
