import time
import requests
from bs4 import BeautifulSoup
from requests import ReadTimeout

from other_scripts.exceptions import MaxRetriesExceeded
from settings import TIMEOUT, BASE_URL, MAX_RETRIES, DELAY


def sync_get_page(url,max_retries,initial_delay):
    retries = 1
    while retries < max_retries:
        try:
            response = requests.get(url,timeout=TIMEOUT)
            if response.status_code != 200:
                print(f"Invalid response from {url}")
                return
            print(f"Connected to the base url: {url}")
            return response.text

        except (TimeoutError, ReadTimeout) as e:
            print(f"Timeout error while trying to obtain the page's text from {url}.\nRetrying {retries}/{max_retries}")
            retries += 1
            time.sleep(initial_delay)
            initial_delay *= 2

        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise

    # If all retries fail
    raise MaxRetriesExceeded(url)


def sync_scrape_categories(html):
    categories = []
    try:
        soup = BeautifulSoup(html, "lxml")
        container = soup.find('ul', class_='nav nav-list')
        # Locate the inner <ul> within this main container
        categories_container = container.find('ul') if container else None

        for link in categories_container.find_all('a', href=True):
            categories.append("".join(
                [BASE_URL, link['href']]
            ))
        print(f"Scraped {len(categories)} categories")
        return categories

    except Exception as e:
        print(f"An {type(e).__name__} occurred: {e}")

def sync_worker(url):
    html = sync_get_page(url,max_retries=MAX_RETRIES,initial_delay=DELAY)
    return sync_scrape_categories(html)