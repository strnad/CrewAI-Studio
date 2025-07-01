from typing import Any, Dict, Optional
import logging
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)

class ScrapflyScrapeWebsiteTool(BaseTool):
    """
    Tool to scrape websites using Scrapfly API.
    
    This tool leverages Scrapfly's web scraping API to extract content from websites in various formats.
    It provides advanced web scraping capabilities with headless browser support, proxies, and anti-bot bypass features.
    """
    
    name: str = "Scrapfly web scraping API tool"
    description: str = (
        "Scrape a webpage url using Scrapfly and return its content as markdown or text"
    )
    
    def __init__(
        self,
        api_key: str,
        **kwargs,
    ):
        """
        Initialize the Scrapfly tool with API key.
        
        Args:
            api_key: Your Scrapfly API key
        """
        super().__init__(**kwargs)
        from scrapfly import ScrapflyClient
        
        self.api_key = api_key
        self.scrapfly = ScrapflyClient(key=api_key)
    
    def _run(
        self,
        url: str,
        scrape_format: str = "markdown",
        scrape_config: Optional[Dict[str, Any]] = None,
        ignore_scrape_failures: Optional[bool] = None,
    ) -> str:
        """
        Run the Scrapfly scraping tool.
        
        Args:
            url: The URL of the website to scrape
            scrape_format: Format to extract the content in ("raw", "markdown", or "text"). Default is "markdown"
            scrape_config: Additional Scrapfly scraping configuration options
            ignore_scrape_failures: Whether to ignore failures during scraping
            
        Returns:
            Scraped content in the specified format
        """
        from scrapfly import ScrapeApiResponse, ScrapeConfig

        scrape_config = scrape_config if scrape_config is not None else {}
        try:
            response: ScrapeApiResponse = self.scrapfly.scrape(
                ScrapeConfig(url, format=scrape_format, **scrape_config)
            )
            return response.scrape_result["content"]
        except Exception as e:
            if ignore_scrape_failures:
                logger.error(f"Error fetching data from {url}, exception: {e}")
                return None
            else:
                raise e 