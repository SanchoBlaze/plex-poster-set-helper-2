"""Plex service for managing Plex server connections and operations."""

from typing import List, Optional, Tuple
import xml.etree.ElementTree

from plexapi.server import PlexServer
import plexapi.exceptions
import requests

from ..core.config import Config


class PlexService:
    """Service for interacting with Plex Media Server."""
    
    def __init__(self, config: Config = None):
        """Initialize Plex service.
        
        Args:
            config: Configuration object containing Plex settings.
        """
        self.config = config
        self.plex: Optional[PlexServer] = None
        self.tv_libraries: List = []
        self.movie_libraries: List = []
    
    def setup(self, gui_mode: bool = False) -> Tuple[List, List]:
        """Setup Plex server connection and libraries.
        
        Args:
            gui_mode: Whether running in GUI mode for error handling.
            
        Returns:
            Tuple of (tv_libraries, movie_libraries).
        """
        if not self.config or not self.config.base_url or not self.config.token:
            error_msg = "Invalid Plex token or base URL. Please provide valid values in config.json or via the GUI."
            self._handle_error(error_msg, gui_mode)
            return None, None
        
        try:
            self.plex = PlexServer(self.config.base_url, self.config.token)
        except requests.exceptions.RequestException as e:
            self._handle_error(f"Unable to connect to Plex server: {str(e)}", gui_mode)
            return None, None
        except plexapi.exceptions.Unauthorized as e:
            self._handle_error(f"Invalid Plex token: {str(e)}", gui_mode)
            return None, None
        except xml.etree.ElementTree.ParseError as e:
            self._handle_error(f"Received invalid XML from Plex server: {str(e)}", gui_mode)
            return None, None
        except Exception as e:
            self._handle_error(f"Unexpected error: {str(e)}", gui_mode)
            return None, None
        
        # Setup TV libraries
        self.tv_libraries = self._setup_libraries(
            self.config.tv_library, 
            "TV library",
            gui_mode
        )
        
        # Setup movie libraries
        self.movie_libraries = self._setup_libraries(
            self.config.movie_library,
            "Movie library",
            gui_mode
        )
        
        return self.tv_libraries, self.movie_libraries
    
    def _setup_libraries(self, library_names: any, library_type: str, gui_mode: bool) -> List:
        """Setup library sections.
        
        Args:
            library_names: String or list of library names.
            library_type: Type description for error messages.
            gui_mode: Whether in GUI mode.
            
        Returns:
            List of library objects.
        """
        if isinstance(library_names, str):
            library_names = [library_names]
        elif not isinstance(library_names, list):
            error_msg = f"{library_type} must be either a string or a list"
            self._handle_error(error_msg, gui_mode)
            return []
        
        libraries = []
        for lib_name in library_names:
            try:
                plex_lib = self.plex.library.section(lib_name)
                libraries.append(plex_lib)
            except plexapi.exceptions.NotFound as e:
                error_msg = f'{library_type} named "{lib_name}" not found: {str(e)}'
                self._handle_error(error_msg, gui_mode)
        
        return libraries
    
    def find_in_library(self, libraries: List, title: str, year: Optional[int] = None) -> Optional[List]:
        """Find item in library by title and optional year.
        
        Args:
            libraries: List of library objects to search.
            title: Title to search for.
            year: Optional year to filter by.
            
        Returns:
            List of found items or None.
        """
        from difflib import get_close_matches
        
        # Check if there's a manual mapping for this title
        mapped_title = self.config.title_mappings.get(title, title)
        if mapped_title != title:
            print(f"ℹ Using title mapping: '{title}' -> '{mapped_title}'")
        
        items = []
        
        # Try exact match first with mapped title
        for lib in libraries:
            try:
                if year is not None:
                    library_item = lib.get(mapped_title, year=year)
                else:
                    library_item = lib.get(mapped_title)
                
                if library_item:
                    items.append(library_item)
            except:
                pass
        
        if items:
            return items
        
        # Try fuzzy matching if exact match failed
        for lib in libraries:
            try:
                all_titles = [item.title for item in lib.all()]
                matches = get_close_matches(mapped_title, all_titles, n=1, cutoff=0.8)
                
                if matches:
                    print(f"ℹ Fuzzy matched '{mapped_title}' to '{matches[0]}'")
                    library_item = None
                    
                    # Try with year first if provided
                    if year is not None:
                        try:
                            library_item = lib.get(matches[0], year=year)
                        except:
                            # Year mismatch, try without year
                            print(f"ℹ Year mismatch for '{matches[0]}', trying without year filter")
                            library_item = lib.get(matches[0])
                    else:
                        library_item = lib.get(matches[0])
                    
                    if library_item:
                        items.append(library_item)
            except Exception as e:
                pass
        
        if items:
            return items
        
        print(f"{title} not found, skipping.")
        return None
    
    def find_collection(self, libraries: List, title: str) -> Optional[List]:
        """Find collection in library by title.
        
        Args:
            libraries: List of library objects to search.
            title: Collection title to search for.
            
        Returns:
            List of found collections or None.
        """
        collections = []
        for lib in libraries:
            try:
                movie_collections = lib.collections()
                for plex_collection in movie_collections:
                    if plex_collection.title == title:
                        collections.append(plex_collection)
            except:
                pass
        
        if collections:
            return collections
        
        return None
    
    def _handle_error(self, message: str, gui_mode: bool):
        """Handle errors consistently.
        
        Args:
            message: Error message.
            gui_mode: Whether in GUI mode.
        """
        if gui_mode:
            # In GUI mode, we'll need to handle this with a callback
            # For now, just print
            print(message)
        else:
            print(message)
