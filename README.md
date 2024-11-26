# Book-Scraper 
A Python script that asynchronously scrapes the website https://books.toscrape.com/ and extracts the book title and UPC (Universal Product Code) values.

## Main Function Points

- Asynchronous scraping of the book website
- Extraction of book titles and UPC values
- Different scraping approaches (purely asynchronous and a combination of synchronous and asynchronous)
- Connection retries logic, graceful task termination and exception handling
- Performance check
  
## Tech Stack
- Python
- asyncio
- aiohttp
- requests
- Beautiful Soup
