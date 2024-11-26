import asyncio
from asyncio import Queue
from asyncio.exceptions import TimeoutError, CancelledError
from aiohttp import ClientError
from bs4 import BeautifulSoup

from other_scripts.exceptions import MaxRetriesExceeded
from settings import BASE_URL, CATEGORIES, TIMEOUT, MAX_RETRIES, DELAY, MAX_WORKERS


async def get_page_text(session, url, worker_name, max_retries=MAX_RETRIES, initial_delay=DELAY):
    retries = 1
    while retries < max_retries:
        try:
            async with session.get(url=url, timeout=TIMEOUT) as response:
                if response.status != 200:
                    print(f"Invalid response from {url}")
                    return
                return await response.text()

        except TimeoutError:
            print(f"{worker_name}: Timeout error while trying to obtain the page's text from {url}.\nRetrying {retries}/{max_retries}")
            retries += 1
            await asyncio.sleep(initial_delay)
            initial_delay *= 2

        except ClientError as e:
            print(f"Couldn't connect to the server: {e}")
            raise

        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise

    # If all retries fail
    raise MaxRetriesExceeded(url)

async def worker(session,input_queue, output_queue, task_func, worker_name):
    # try:
    while True:
        try:
            url = await input_queue.get()
            if url is None:  # Sentinel value for shutdown
                print(f"{worker_name} is shutting down...")
                break
            print(f"{worker_name} is connecting to {url} and extracting its HTML...")
            # Call the provided task function and get the result
            html = await get_page_text(worker_name=worker_name, session=session, url=url)
            if not html:
                raise ValueError(f"Failed to fetch valid content from {url}")
            print(f"{worker_name} is scraping {url}...")
            result = await task_func(html)

            if isinstance(result,dict): #iterate through the items if the result is a dictionary (scrape_title_and_upc task)
                result = result.items()
            for r in result:
                output_queue.put_nowait(r)

        except ValueError as e:
            print(f"{worker_name} encountered an error: {e}")
            raise
        except Exception as e:
            print(f"{worker_name} failed processing {url}: {type(e).__name__}, {e}")
        finally:
            input_queue.task_done()

    # except CancelledError:
    #     print(f"{worker_name} received cancellation signal.")
    #     raise  # Re-raise the exception to propagate it


async def process_tasks(session, input_queue, output_queue, task_func):
    # Start workers
    tasks = [
        asyncio.create_task(worker(session, input_queue, output_queue, task_func, f"Worker {i + 1}"))
        for i in range(MAX_WORKERS)
    ]

    try:
        # Wait for all tasks to be processed
        await input_queue.join()

    finally:
        # Send shutdown signals to workers
        for _ in range(MAX_WORKERS):
            input_queue.put_nowait(None)

        # Await worker completion
        await asyncio.gather(*tasks, return_exceptions=True)


async def scrape_categories(html) -> Queue[str]:
    # Locate the container with the class 'nav nav-list'

    q = Queue()
    print("Scraping the base URL page...")
    try:
        soup = BeautifulSoup(html, "lxml")
        container = soup.find('ul', class_='nav nav-list')
        # Locate the inner <ul> within this main container
        categories_container = container.find('ul') if container else None

        for link in categories_container.find_all('a', href=True):
            await q.put("".join(
                [BASE_URL,link['href']]
            ))
        print(f"Scraped {q.qsize()} categories")
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
