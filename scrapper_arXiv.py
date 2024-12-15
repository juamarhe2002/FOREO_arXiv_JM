import requests
from bs4 import BeautifulSoup, PageElement
import pandas as pd
import sqlite3
from apscheduler.schedulers.blocking import BlockingScheduler


# Function to check if an article is new
def is_new_article(arXiv_id):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT arXiv_id FROM Articles WHERE arXiv_id = ?', (arXiv_id,))
    result = cursor.fetchone()
    conn.close()
    return True if result is None else False


# Function to save new articles to the database
def save_article(article):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Articles (arXiv_id, title, authors, subjects, pdf_link) VALUES (?, ?, ?, ?, ?)',
                   (article['arXiv_id'], article['title'], article['authors'], article['subjects'],
                       article['pdf_link']))
    conn.commit()
    conn.close()


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
def fetch_articles(url: str, ):
    try:
        response = requests.get(url)  # Send an HTTP GET request
        response.raise_for_status()  # Check for HTTP errors

        soup = BeautifulSoup(response.text, 'html.parser')  # Parse HTML content

        # Extract metadata for each article
        articles = []
        items = soup.find_all('dd')  # Content of articles is in <dd> tags
        for item in items:
            new_article = extract_article_data(item)

            if is_new_article(new_article['arXiv_id']):
                articles.append(new_article)
                save_article(new_article)  # Save the new article to the database

            # Stop collecting if we have 3 new articles
            if len(articles) == 3:
                break

        print("Scraper: Fetched new articles successfully!")
        return articles

    except requests.RequestException as e:
        print(f"Error fetching data from arXiv: {e}")
        return None
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None


# Run daily using APScheduler
def schedule_task(hour: str, url: str):
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_articles, 'cron', hour=hour, args=[url])  # Set to run daily at specified hour.
    print(f"Scheduler started. Task is set to run daily at {hour} .")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped manually.")
