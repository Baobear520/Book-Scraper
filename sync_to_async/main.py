import asyncio
from aiohttp import ClientSession

from tasks.async_tasks import process_tasks, scrape_books, scrape_title_and_upc
from tasks.sync_tasks import sync_worker
from settings import BASE_URL
from other_scripts.utils import runtime_counter


"""Imitating the structure of a tasks that cannot be fully asynchronous 
and depends of the results pf synchronous operations"""

async def scraper(input_list):
    categories = asyncio.Queue()
    books = asyncio.Queue()
    upcs = asyncio.Queue()

    async with ClientSession() as session:
        for c in input_list:
                categories.put_nowait(c)

        try:
            # Create a loop with concurrent tasks to process categories and scrape all the books
            await process_tasks(
                session=session,
                input_queue= categories,
                output_queue=books,
                task_func=scrape_books)

            # Create a loop with concurrent tasks to process books and scrape their titles and UPC values
            await process_tasks(
                session=session,
                input_queue=books,
                output_queue=upcs,
                task_func=scrape_title_and_upc)
            # End time
            #end_time = time.perf_counter()
            #duration = end_time - start_time

        except asyncio.CancelledError:
            print("Cancelling tasks")
            raise

        # Extract title: upc_value dictionary and print it out
        counter = 1
        while not upcs.empty():
            print(f"{counter}: {await upcs.get()}")
            counter += 1


@runtime_counter
def main():
    try:
        # Assuming that the list of categories may be only obtained synchronously
        categories_list = sync_worker(url=BASE_URL)

        # #Running asynchronous parsing script
        asyncio.run(scraper(input_list=categories_list))

    except KeyboardInterrupt:
        print("Stopping...")


if __name__ == "__main__":
    main()






