from typing import List

import requests
from bs4 import BeautifulSoup, PageElement
import pandas as pd
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler


class ScraperArXiv:
    def __init__(self, url: str):
        self.url = url

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
    def save_article(self, article):
        self.cur.execute('INSERT INTO Articles (arXiv_id, title, authors, subjects, pdf_link) VALUES (?, ?, ?, ?, ?)',
                         (article['arXiv_id'], article['title'], article['authors'], article['subjects'],
                          article['pdf_link']))
        self.conn.commit()

    @staticmethod
    def extract_article_data(item: PageElement) -> dict:
        title_tag = item.find_previous_sibling('dt')
        arXiv_id = title_tag.find('a', title='Abstract')['id']
        title = item.find('div', class_='list-title').get_text(strip=True).replace('Title:', '').strip()
        authors = item.find('div', class_='list-authors').get_text(strip=True)
        subjects = item.find('div', class_='list-subjects').get_text(strip=True).replace('Subjects:', '').strip()
        pdf_link = "https://arxiv.org" + title_tag.find('a', title='Download PDF')['href']

        article_data = {
            'arXiv_id': arXiv_id,
            'title': title,
            'authors': authors,
            'subjects': subjects,
            'pdf_link': pdf_link
        }

        return article_data

    # Function to fetch and parse HTML content from arXiv
    def fetch_articles(self, num_articles: int) -> list[dict] | None:
        try:
            response = requests.get(self.url)  # Send an HTTP GET request
            response.raise_for_status()  # Check for HTTP errors

            soup = BeautifulSoup(response.text, 'html.parser')  # Parse HTML content

            # Extract metadata for each article
            articles = []
            items = soup.find_all('dd')  # Content of articles is in <dd> tags
            for item in items:
                new_article = self.extract_article_data(item)

                if self.is_new_article(new_article['arXiv_id']):
                    articles.append(new_article)
                    self.save_article(new_article)  # Save the new article to the database

                # Stop collecting if we have the number of articles expected to have.
                if len(articles) == num_articles:
                    break

            print("Scraper: Fetched new articles successfully!")
            return articles

        except requests.RequestException as e:
            print(f"Error fetching data from arXiv: {e}")
            return None
        except Exception as e:
            print(f"Error parsing data: {e}")
            return None

