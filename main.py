import asyncio
from asyncio.exceptions import CancelledError
import aiohttp

from other_scripts.utils import runtime_counter
from tasks.async_tasks import scrape_categories, scrape_books, scrape_title_and_upc, get_page_text, process_tasks
from settings import BASE_URL



"""Fully asynchronous script for scraping and parsing book data"""

async def scraper():
    books = asyncio.Queue()
    upcs = asyncio.Queue()
    entry_url = BASE_URL

    async with aiohttp.ClientSession() as session:
        try:
            html = await get_page_text(worker_name="Worker 1",session=session, url=entry_url)
            categories = await scrape_categories(html)

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
            
        except CancelledError:
            print("Cancelling tasks...")
            raise
        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise

        # Extract title: upc_value dictionary and print it out
        counter = 1
        while not upcs.empty():
            print(f"{counter}: {await upcs.get()}")
            counter += 1


@runtime_counter
def main():
    # Run the async scraper
    try:
        asyncio.run(scraper())
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()