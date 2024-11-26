import asyncio
from asyncio.exceptions import CancelledError
from aiohttp import ClientSession

from other_scripts.utils import runtime_counter
from tasks.async_tasks import scrape_books, scrape_title_and_upc, process_tasks
from tasks.sync_tasks import sync_worker
from settings import BASE_URL



async def scraper():
    categories = asyncio.Queue()
    books = asyncio.Queue()
    upcs = asyncio.Queue()
    entry_url = BASE_URL

    async with ClientSession() as session:
        try:
            # Synchronously scrape the links to all the categories of the books in a separate thread
            categories_list = await asyncio.to_thread(sync_worker, entry_url)
            for c in categories_list:
                categories.put_nowait(c)

        except Exception as e:
            print(f"Error: {type(e).__name__}, {e}")
            raise

        try:
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
        print("Keyboard interrupt. Stopping...")


if __name__ == "__main__":
    main()

