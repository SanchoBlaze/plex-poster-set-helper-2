"""ThePosterDB scraper implementation."""

import math
from typing import List, Tuple

from ..core.models import PosterInfo
from .base_scraper import BaseScraper


class PosterDBScraper(BaseScraper):
    """Scraper for ThePosterDB website."""
    
    def scrape(self, url: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape posters from ThePosterDB.
        
        Args:
            url: ThePosterDB URL to scrape.
            
        Returns:
            Tuple of (movie_posters, show_posters, collection_posters).
        """
        soup = self.fetch_page(url)
        return self._parse_posterdb(soup)
    
    def scrape_set_from_poster(self, url: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape entire set from a single poster URL.
        
        Args:
            url: Single poster URL.
            
        Returns:
            Tuple of (movie_posters, show_posters, collection_posters).
        """
        soup = self.fetch_page(url)
        set_url = self._get_set_link(soup)
        
        if set_url is None:
            raise Exception("Poster set not found. Check the link you are inputting.")
        
        set_soup = self.fetch_page(set_url)
        return self._parse_posterdb(set_soup)
    
    def scrape_user_uploads(self, url: str) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Scrape all uploads from a user's page.
        
        Args:
            url: User profile URL.
            
        Returns:
            Tuple of (movie_posters, show_posters, collection_posters).
        """
        soup = self.fetch_page(url)
        pages = self._get_user_page_count(soup)
        
        if not pages:
            print(f"Could not determine the number of pages for {url}")
            return [], [], []
        
        # Clean URL
        if "?" in url:
            url = url.split("?")[0]
        
        all_movie_posters = []
        all_show_posters = []
        all_collection_posters = []
        
        for page in range(pages):
            print(f"Scraping page {page + 1} of {pages}.")
            page_url = f"{url}?section=uploads&page={page + 1}"
            movie_posters, show_posters, collection_posters = self.scrape(page_url)
            all_movie_posters.extend(movie_posters)
            all_show_posters.extend(show_posters)
            all_collection_posters.extend(collection_posters)
        
        return all_movie_posters, all_show_posters, all_collection_posters
    
    def _get_set_link(self, soup) -> str:
        """Extract set link from poster page.
        
        Args:
            soup: BeautifulSoup object.
            
        Returns:
            Set URL or None.
        """
        try:
            # Try new structure first (with tooltip)
            view_set_link = soup.find('a', attrs={'data-toggle': 'tooltip', 'title': 'View Set Page'})
            if view_set_link and view_set_link.get('href'):
                return view_set_link['href']
            
            # Fallback to old structure
            view_all_div = soup.find('a', class_='rounded view_all')
            if view_all_div and view_all_div.get('href'):
                return view_all_div['href']
            
            return None
        except:
            return None
    
    def _get_user_page_count(self, soup) -> int:
        """Get number of pages for user uploads.
        
        Args:
            soup: BeautifulSoup object.
            
        Returns:
            Number of pages or None.
        """
        try:
            span_tag = soup.find('span', class_='numCount')
            number_str = span_tag['data-count']
            upload_count = int(number_str)
            pages = math.ceil(upload_count / 24)
            return pages
        except:
            return None
    
    def _parse_posterdb(self, soup) -> Tuple[List[PosterInfo], List[PosterInfo], List[PosterInfo]]:
        """Parse ThePosterDB page for posters.
        
        Args:
            soup: BeautifulSoup object.
            
        Returns:
            Tuple of (movie_posters, show_posters, collection_posters).
        """
        movie_posters = []
        show_posters = []
        collection_posters = []
        
        # Find the poster grid
        poster_div = soup.find('div', class_='row d-flex flex-wrap m-0 w-100 mx-n1 mt-n1')
        if not poster_div:
            return movie_posters, show_posters, collection_posters
        
        # Find all poster divs
        posters = poster_div.find_all('div', class_='col-6 col-lg-2 p-1')
        
        for poster in posters:
            try:
                poster_info = self._parse_poster_element(poster)
                if poster_info:
                    if poster_info.is_tv_show():
                        show_posters.append(poster_info)
                    elif poster_info.is_collection():
                        collection_posters.append(poster_info)
                    else:
                        movie_posters.append(poster_info)
            except Exception as e:
                print(f"Error parsing poster: {str(e)}")
        
        return movie_posters, show_posters, collection_posters
    
    def _parse_poster_element(self, poster_element) -> PosterInfo:
        """Parse a single poster element.
        
        Args:
            poster_element: BeautifulSoup poster element.
            
        Returns:
            PosterInfo object or None.
        """
        # Get media type
        media_type = poster_element.find('a', class_="text-white", attrs={
            'data-toggle': 'tooltip', 
            'data-placement': 'top'
        })['title']
        
        # Get high resolution poster image
        overlay_div = poster_element.find('div', class_='overlay')
        poster_id = overlay_div.get('data-poster-id')
        poster_url = f"https://theposterdb.com/api/assets/{poster_id}"
        
        # Get metadata
        title_p = poster_element.find('p', class_='p-0 mb-1 text-break').string
        
        if media_type == "Show":
            return self._parse_show_poster(title_p, poster_url)
        elif media_type == "Movie":
            return self._parse_movie_poster(title_p, poster_url)
        elif media_type == "Collection":
            return self._parse_collection_poster(title_p, poster_url)
        
        return None
    
    def _parse_show_poster(self, title_p: str, poster_url: str) -> PosterInfo:
        """Parse TV show poster data.
        
        Args:
            title_p: Title string from page.
            poster_url: URL to poster image.
            
        Returns:
            PosterInfo object.
        """
        title = title_p.split(" (")[0]
        
        try:
            year = int(title_p.split(" (")[1].split(")")[0])
        except:
            year = None
        
        # Determine season
        if " - " in title_p:
            split_season = title_p.split(" - ")[-1]
            if split_season == "Specials":
                season = 0
            elif "Season" in split_season:
                season = int(split_season.split(" ")[1])
        else:
            season = "Cover"
        
        return PosterInfo(
            title=title,
            url=poster_url,
            season=season,
            episode=None,
            year=year,
            source="posterdb"
        )
    
    def _parse_movie_poster(self, title_p: str, poster_url: str) -> PosterInfo:
        """Parse movie poster data.
        
        Args:
            title_p: Title string from page.
            poster_url: URL to poster image.
            
        Returns:
            PosterInfo object.
        """
        title_split = title_p.split(" (")
        
        if len(title_split[1]) != 5:
            title = title_split[0] + " (" + title_split[1]
        else:
            title = title_split[0]
        
        year = int(title_split[-1].split(")")[0])
        
        return PosterInfo(
            title=title,
            url=poster_url,
            year=year,
            source="posterdb"
        )
    
    def _parse_collection_poster(self, title_p: str, poster_url: str) -> PosterInfo:
        """Parse collection poster data.
        
        Args:
            title_p: Title string from page.
            poster_url: URL to poster image.
            
        Returns:
            PosterInfo object.
        """
        return PosterInfo(
            title=title_p,
            url=poster_url,
            source="posterdb"
        )
