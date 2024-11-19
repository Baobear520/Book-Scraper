import asyncio
from asyncio import Queue
from bs4 import BeautifulSoup

from settings import BASE_URL, CATEGORIES


async def scrape_categories(html) -> Queue[str]:
    # Locate the container with the class 'nav nav-list'

    q = Queue()
    try:
        soup = BeautifulSoup(html, "lxml")
        container = soup.find('ul', class_='nav nav-list')
        # Locate the inner <ul> within this main container
        categories_container = container.find('ul') if container else None

        for link in categories_container.find_all('a', href=True):
            await q.put("".join(
                [BASE_URL,link['href']]
            ))
        return q
    except Exception as e:
        print(f"An {type(e).__name__} occurred: {e}")


async def scrape_books(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        # Find all list items in the specified class
        links = []
        for li in soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3'):
            # Find the anchor tag within the list item
            a_tag = li.find('a')
            if a_tag and 'href' in a_tag.attrs:
                book = a_tag['href'].lstrip("./../../")
                link = "".join([BASE_URL,CATEGORIES,book])
                links.append(link)
        return links
    except Exception as e:
        print(f"An {type(e).__name__} occurred: {e}")


async def scrape_title_and_upc(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        # Find the table row containing the UPC
        table = soup.find('table', {'class': 'table table-striped'})
        upc_row = table.find('th', string='UPC')
        upc_value = upc_row.find_next_sibling('td').text.strip()
        # Find the container with the book's title
        container = soup.find('div',{'class': "col-sm-6 product_main"})
        title = container.find('h1').get_text(strip=True)  # Extract text and strip whitespace
        return {title: upc_value}

    except Exception as e:
            print(f"An {type(e).__name__} occurred: {e}")
            return None
