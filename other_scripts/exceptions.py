

class MaxRetriesExceeded(Exception):
    """Custom exception raised when maximum retries are reached."""
    def __init__(self, url, message="Maximum retries reached"):
        self.url = url
        self.message = message
        super().__init__(f"{message} for URL: {url}")