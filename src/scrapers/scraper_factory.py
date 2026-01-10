"""Scraper factory for creating appropriate scraper instances."""

from typing import Tuple, List
from bs4 import BeautifulSoup

from ..core.models import PosterInfo
from ..core.config import Config
from .posterdb_scraper import PosterDBScraper
from .mediux_scraper import MediuxScraper


class ScraperFactory:
    """Factory for creating and managing scrapers."""
    
    def __init__(self, config: Config = None, use_playwright: bool = True):
        """Initialize scraper factory.
        
        Args:
            config: Configuration object.
            use_playwright: Whether to use Playwright for scraping.
        """
        self.config = config
        self.use_playwright = use_playwright
    
    def scrape_url(self, url: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape URL using appropriate scraper.
        
        Args:
            url: URL to scrape.
            
        Returns:
            Tuple of (movie_posters, show_posters, collection_posters).
        """
        if "theposterdb.com" in url:
            return self._scrape_posterdb(url)
        elif "mediux.pro" in url and "sets" in url:
            return self._scrape_mediux(url)
        elif ".html" in url:
            return self._scrape_local_html(url)
        else:
            raise ValueError("Unsupported URL. Must be ThePosterDB, MediUX, or local HTML file.")
    
    def _scrape_posterdb(self, url: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape ThePosterDB URL.
        
        Args:
            url: ThePosterDB URL.
            
        Returns:
            Tuple of poster lists.
        """
        with PosterDBScraper(use_playwright=self.use_playwright) as scraper:
            if "/set/" in url or "/user/" in url:
                # Check if it's a user page
                if "/user/" in url:
                    return scraper.scrape_user_uploads(url)
                else:
                    return scraper.scrape(url)
            elif "/poster/" in url:
                return scraper.scrape_set_from_poster(url)
            else:
                raise ValueError("Unsupported PosterDB URL format.")
    
    def _scrape_mediux(self, url: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape MediUX URL.
        
        Args:
            url: MediUX URL.
            
        Returns:
            Tuple of poster lists.
        """
        with MediuxScraper(config=self.config, use_playwright=self.use_playwright) as scraper:
            return scraper.scrape(url)
    
    def _scrape_local_html(self, file_path: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape local HTML file.
        
        Args:
            file_path: Path to HTML file.
            
        Returns:
            Tuple of poster lists.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Use PosterDB scraper for HTML files (assuming PosterDB format)
        with PosterDBScraper(use_playwright=False) as scraper:
            return scraper._parse_posterdb(soup)
