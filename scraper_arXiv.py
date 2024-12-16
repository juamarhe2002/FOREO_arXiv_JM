import requests
from bs4 import BeautifulSoup, PageElement
import re
import pandas as pd
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

    # Function to save the subjects of the articles.
    @staticmethod
    def save_articles_subjects(subjects: dict, new_article: dict):
        new_subjects = new_article['subjects'].split(';')

        for new_subject in new_subjects:
            if new_subject not in subjects:
                subjects[new_subject] = [[new_article['arXiv_id'], new_article['popularity']]]
            else:
                subjects[new_subject].append([new_article['arXiv_id'], new_article['popularity']])

    # Function for checking the number of articles of each subject and returning the
    # subject that has an equivalent number of articles as the one required.
    # returns: subject name (str) | (None)
    @staticmethod
    def chk_articles_number(subjects: dict, num_articles: int) -> str | None:
        for subject in subjects:
            if len(subjects[subject]) == num_articles:
                return subject

        return None

    # Function to fetch and parse HTML content from arXiv
    def fetch_articles(self, num_articles: int) -> list[dict] | None:
        try:
            response = requests.get(self.url)  # Send an HTTP GET request
            response.raise_for_status()  # Check for HTTP errors

            soup = BeautifulSoup(response.text, 'html.parser')  # Parse HTML content

            # Extract metadata for each article
            subjects = dict()
            articles = []
            items = soup.find_all('dd')  # Content of articles is in <dd> tags
            for item in items:
                new_article = self.extract_article_data(item)

                if self.is_new_article(new_article['arXiv_id']) and not self.has_text_overlap(new_article):
                    if new_article['popularity'] == 2:
                        articles.append(new_article)

                    if len(articles) == num_articles:
                        self.save_articles(articles)
                        self.articles = articles
                        break

            print("Scraper: Fetched new articles successfully!")
            return self.articles

        except requests.RequestException as e:
            print(f"Error fetching data from url {self.url}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing data: {e}")
            return None
