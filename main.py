import asyncio
import time

import aiohttp
from aiohttp import ClientError

from parser.tasks import scrape_categories, scrape_books, scrape_title_and_upc
from settings import MAX_WORKERS, BASE_URL, MAX_RETRIES, DELAY, TIMEOUT



async def get_page_text(session, url, max_retries=MAX_RETRIES, initial_delay=DELAY):
    retries = 0
    while retries < max_retries:
        try:
            async with session.get(url=url, timeout=TIMEOUT) as response:
                if response.status != 200:
                    print(f"Invalid response from {url}")
                    return
                #print(f"Connected to {url}")
                return await response.text()

        except TimeoutError as e:
            if retries == max_retries:
                print(f"Reached maximum number of retries with {url}")
                break
            print(f"Timeout error while trying to obtain the page's text from {url}\nRetrying...")
            retries += 1
            await asyncio.sleep(initial_delay)
            initial_delay *= 2

        except ClientError as e:
            print(f"Couldn't connect to the server: {e}")

        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")


async def worker(session,input_queue, output_queue, task_func, worker_name):
    while True:
        url = await input_queue.get()
        try:
            # Call the provided task function and get the result
            print(f"{worker_name} is scraping {url}...")
            html = await get_page_text(session=session, url=url)
            result = await task_func(html)
            input_queue.task_done()
            if isinstance(result,dict): #iterate through the items if the result is a dictionary (scrape_title_and_upc task)
                result = result.items()
            for r in result:
                output_queue.put_nowait(r)

        except Exception as e:
            print(f"{worker_name} failed processing {url}: {type(e).__name__}, {e}")

async def process_tasks(session,input_queue, output_queue, task_func):
    # Create worker tasks to process the queue concurrently.
    tasks = []
    for i in range(MAX_WORKERS):
        task = asyncio.create_task(worker(
            session,
            input_queue,
            output_queue,
            task_func,
            worker_name=f"Worker {i + 1}"
            )
        )
        tasks.append(task)
    # Cancel our worker tasks.
    await input_queue.join()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    # Start time
    start_time = time.perf_counter()
    books = asyncio.Queue()
    upcs = asyncio.Queue()
    entry_url = BASE_URL

    async with aiohttp.ClientSession() as session:
        try:
            html = await get_page_text(session=session, url=entry_url)
            # Scrape the links to all the categories of the books
            categories = await scrape_categories(html)
        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise
        # Create a loop with concurrent tasks to process categories and scrape all the books
        await process_tasks(
            session=session,
            input_queue=categories,
            output_queue=books,
            task_func=scrape_books)

        # Create a loop with concurrent tasks to process books and scrape their titles and UPC values
        await process_tasks(
            session=session,
            input_queue=books,
            output_queue=upcs,
            task_func=scrape_title_and_upc)
        # End time
        end_time = time.perf_counter()
        duration = end_time - start_time

        # Extract title: upc_value dictionary and print it out
        counter = 1
        while not upcs.empty():
            print(f"{counter}: {await upcs.get()}")
            counter += 1
        print(f"Script runtime: {duration:.2f} seconds")

asyncio.run(main())