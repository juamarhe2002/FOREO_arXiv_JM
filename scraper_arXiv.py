import requests
from bs4 import BeautifulSoup, PageElement
import re
import sqlite3


class ScraperArXiv:
    def __init__(self, url: str):
        self.url = url
        self.articles = []

        self.conn = sqlite3.connect('articles.db')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    # Function to check if an article is new
    def is_new_article(self, arXiv_id) -> bool:
        self.cur.execute('SELECT arXiv_id FROM Articles WHERE arXiv_id = ?', (arXiv_id,))
        result = self.cur.fetchone()
        return True if result is None else False

    # Function to save new articles to the database
    def save_articles(self, articles: list):
        for article in articles:
            self.cur.execute('''INSERT INTO Articles (arXiv_id, title, authors, subjects, comments, popularity, pdf_link)
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             (article['arXiv_id'], article['title'], article['authors'], article['subjects'],
                              article['comments'], article['popularity'], article['pdf_link']))
            self.conn.commit()

    # Function to check if the article was noted by arXiv admin with text overlap.
    @staticmethod
    def has_text_overlap(article_comments: dict) -> bool:
        comments = article_comments['comments']
        return True if 'arxiv admin note: substantial text overlap' in comments else False

    # Function to calculate the popularity of an article.
    @staticmethod
    def calculate_popularity(journal_ref, comments_text: str) -> int:
        if journal_ref is not None:
            return 2

        if len(comments_text) > 0:
            match = re.search(r"([tT]o be ){0}(([aA]ccepted)|([pP]ublished))\s", comments_text)
            if match is not None:
                return 1

        return 0

    # Function to extract the relevant data from an article.
    def extract_article_data(self, item: PageElement) -> dict:
        title_tag = item.find_previous_sibling('dt')
        arXiv_id = title_tag.find('a', title='Abstract')['id']
        title = item.find('div', class_='list-title').get_text(strip=True).replace('Title:', '')
        authors = item.find('div', class_='list-authors').get_text(strip=True)
        subjects = item.find('div', class_='list-subjects').get_text(strip=True).replace('Subjects:', '')
        pdf_link = "https://arxiv.org" + title_tag.find('a', title='Download PDF')['href']

        journal_ref = item.find('div', class_='list-journal-ref')
        comments = item.find('div', 'list-comments')
        comments_text = comments.get_text(strip=True) if comments is not None else ''

        popularity = self.calculate_popularity(journal_ref, comments_text)

        article_data = {
            'arXiv_id': arXiv_id,
            'title': title,
            'authors': authors,
            'subjects': subjects,
            'comments': comments_text,
            'popularity': popularity,
            'pdf_link': pdf_link
        }

        return article_data

    # Function to append new articles if they have a higher popularity than one of the already appended ones.
    def append_by_popularity(self, new_article: dict):
        for article in self.articles:
            if new_article['popularity'] > article['popularity']:
                self.articles.remove(article)
                self.articles.append(new_article)
                return

    # Function to check if all the articles on the list have the highes possible popularity.
    def chk_articles_popularity(self) -> bool:
        for article in self.articles:
            if article['popularity'] < 2:
                return False

        return True

    # Function to fetch and parse HTML content from arXiv
    def fetch_articles(self, num_articles: int) -> list[dict] | None:
        try:
            response = requests.get(self.url)  # Send an HTTP GET request
            response.raise_for_status()  # Check for HTTP errors

            soup = BeautifulSoup(response.text, 'html.parser')  # Parse HTML content

            # Extract metadata for each article
            self.articles = []
            items = soup.find_all('dd')  # Content of articles is in <dd> tags
            for item in items:
                new_article = self.extract_article_data(item)

                if self.is_new_article(new_article['arXiv_id']) and not self.has_text_overlap(new_article):
                    if len(self.articles) < num_articles:
                        self.articles.append(new_article)
                    else:
                        self.append_by_popularity(new_article)

                    if self.chk_articles_popularity():
                        self.save_articles(self.articles)
                        break

            print("Scraper: Fetched new articles successfully!")
            return self.articles

        except requests.RequestException as e:
            print(f"Could not fetch data from url {self.url}:\n {e}")
            return None
        except Exception:
            print(f"Error parsing data in fetch_articles() function:\n")
            raise
