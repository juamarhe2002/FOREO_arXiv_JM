import unittest
import sqlite3

from scraper_arXiv import ScraperArXiv
from bs4 import BeautifulSoup, PageElement


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
    def test_is_new_article(self):
        test_article_1 = {
            'arXiv_id': 'arXiv_id_1',
            'title': 'title_1',
            'authors': 'authors_1',
            'subjects': 'subjects_1',
            'comments': 'comments_1',
            'popularity': 1,
            'pdf_link': 'pdf_link_1'
        }

        test_article_2 = {
            'arXiv_id': 'arXiv_id_2',
            'title': 'title_2',
            'authors': 'authors_2',
            'subjects': 'subjects_2',
            'comments': 'comments_2',
            'popularity': 2,
            'pdf_link': 'pdf_link_2'
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

    def test_extract_article_data(self):
        test_arxiv_info = open('test_arxiv_info.html', 'r')
        soup = BeautifulSoup(test_arxiv_info, 'html.parser')
        test_arxiv_info.close()
        items = soup.find_all('dd')

        item1 = items[0]
        article_1 = {
            'arXiv_id': '2412.08648',
            'title': 'Detecting Visual Triggers in Cannabis Imagery: A CLIP-Based Multi-Labeling Framework with ' +
                     'Local-Global Aggregation',
            'authors': 'Linqi Lu,Xianshi Yu,Akhil Perumal Reddy',
            'subjects': 'Computers and Society (cs.CY); Computer Vision and Pattern Recognition (cs.CV)',
            'comments': 'This project was initiated in September 2023',
            'popularity': 0,
            'pdf_link': 'https://arxiv.org/pdf/2412.08648'
        }

        extracted_article_1 = self.extract_article_data(item1)
        self.assertEqual(extracted_article_1, article_1, "Assert: extract_article_data(item1) failed in "
                                                         "extracted_article_1.\n")

        item22 = items[21]  # 22
        article_22 = {
            'arXiv_id': '2412.09044',
            'title': 'Motif Guided Graph Transformer with Combinatorial Skeleton Prototype Learning for ' +
                     'Skeleton-Based Person Re-Identification',
            'authors': 'Haocong Rao,Chunyan Miao',
            'subjects': 'Computer Vision and Pattern Recognition (cs.CV); Artificial Intelligence (cs.AI)',
            'comments': 'Accepted by AAAI 2025. Codes are available atthis https URL',
            'popularity': 1,
            'pdf_link': 'https://arxiv.org/pdf/2412.09044'
        }

        extracted_article_22 = self.extract_article_data(item22)
        self.assertEqual(extracted_article_22, article_22, "Assert: extract_article_data(item22) failed in "
                                                           "extracted_article_22.\n")

        item8 = items[7]  # 8
        article_8 = {
            'arXiv_id': '2402.06126',
            'title': 'Learn To be Efficient: Build Structured Sparsity in Large Language Models',
            'authors': 'Haizhong Zheng,Xiaoyan Bai,Xueshen Liu,Z. Morley Mao,Beidi Chen,Fan Lai,Atul Prakash',
            'subjects': 'Computation and Language (cs.CL); Artificial Intelligence (cs.AI); Machine Learning (cs.LG)',
            'comments': '',
            'popularity': 2,
            'pdf_link': 'https://arxiv.org/pdf/2402.06126'
        }

        extracted_article_8 = self.extract_article_data(item8)
        self.assertEqual(extracted_article_8, article_8, "Assert: extract_article_data(item8) failed in "
                                                         "extracted_article_8.\n")

        item32 = items[32]  # 32
        article_32 = {
            'arXiv_id': '2412.09152',
            'title': 'herakoi: a sonification experiment for astronomical data',
            'authors': 'Michele Ginolfi,Luca Di Mascolo,Anita Zanella',
            'subjects': 'Instrumentation and Methods for Astrophysics (astro-ph.IM); Human-Computer Interaction (' +
                        'cs.HC); Physics Education (physics.ed-ph)',
            'comments': 'to be published in the proceedings of "Various Innovative Technological Experiences '
                        '- VITE II" by MemSAIt',
            'popularity': 0,
            'pdf_link': 'https://arxiv.org/pdf/2412.09152'
        }

        extracted_article_32 = self.extract_article_data(item32)
        self.assertEqual(extracted_article_32, article_32, "Assert: extract_article_data(item32) failed in "
                         "extracted_article_32.\n")

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
