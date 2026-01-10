"""GUI application for Plex Poster Set Helper."""

import os
import threading
import webbrowser
import tkinter as tk
from typing import List

import customtkinter as ctk
from PIL import Image

from ..core.config import ConfigManager, Config
from ..services.plex_service import PlexService
from ..services.poster_upload_service import PosterUploadService
from ..scrapers.scraper_factory import ScraperFactory
from ..utils.helpers import resource_path, get_exe_dir
from ..utils.text_utils import parse_urls


class PlexPosterGUI:
    """Main GUI application."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        
        self.plex_service: PlexService = None
        self.upload_service: PosterUploadService = None
        self.scraper_factory: ScraperFactory = None
        
        # GUI widgets (to be initialized)
        self.app = None
        self.status_label = None
        self.url_entry = None
        self.bulk_import_text = None
        self.base_url_entry = None
        self.token_entry = None
        self.tv_library_text = None
        self.movie_library_text = None
        self.mediux_filters_text = None
        self.bulk_txt_entry = None
        self.scrape_button = None
        self.clear_button = None
        self.bulk_import_button = None
        self.global_context_menu = None
    
    def run(self):
        """Run the GUI application."""
        self._create_ui()
        self.app.mainloop()
    
    def _create_ui(self):
        """Create the main UI window."""
        self.app = ctk.CTk()
        ctk.set_appearance_mode("dark")
        
        self.app.title("Plex Poster Upload Helper")
        self.app.geometry("850x600")
        
        try:
            self.app.iconbitmap(resource_path("icons/Plex.ico"))
        except:
            pass  # Icon file not found
        
        self.app.configure(fg_color="#2A2B2B")
        
        self._create_context_menu()
        self._create_link_bar()
        self._create_tabview()
        self._create_status_label()
        
        self._load_and_update_ui()
    
    def _create_context_menu(self):
        """Create right-click context menu."""
        self.global_context_menu = tk.Menu(self.app, tearoff=0)
        self.global_context_menu.add_command(label="Cut")
        self.global_context_menu.add_command(label="Copy")
        self.global_context_menu.add_command(label="Paste")
    
    def _create_link_bar(self):
        """Create the link bar at the top."""
        link_bar = ctk.CTkFrame(self.app, fg_color="transparent")
        link_bar.pack(fill="x", pady=5, padx=10)
        
        # Plex link
        base_url = self.config.base_url if self.config.base_url else "https://www.plex.tv"
        
        try:
            plex_icon = ctk.CTkImage(
                light_image=Image.open(resource_path("icons/Plex.ico")),
                size=(24, 24)
            )
            icon_label = ctk.CTkLabel(link_bar, image=plex_icon, text="", anchor="w")
            icon_label.pack(side="left", padx=0, pady=0)
        except:
            pass
        
        url_text = self.config.base_url if self.config.base_url else "Plex Media Server"
        url_label = ctk.CTkLabel(
            link_bar,
            text=url_text,
            anchor="w",
            font=("Roboto", 14, "bold"),
            text_color="#CECECE"
        )
        url_label.pack(side="left", padx=(5, 10))
        
        # External links
        mediux_button = self._create_button(
            link_bar,
            text="MediUX.pro",
            command=lambda: webbrowser.open("https://mediux.pro"),
            color="#945af2",
            height=30
        )
        mediux_button.pack(side="right", padx=5)
        
        posterdb_button = self._create_button(
            link_bar,
            text="ThePosterDB",
            command=lambda: webbrowser.open("https://theposterdb.com"),
            color="#FA6940",
            height=30
        )
        posterdb_button.pack(side="right", padx=5)
    
    def _create_tabview(self):
        """Create the tabbed interface."""
        tabview = ctk.CTkTabview(self.app)
        tabview.pack(fill="both", expand=True, padx=10, pady=0)
        
        tabview.configure(
            fg_color="#2A2B2B",
            segmented_button_fg_color="#1C1E1E",
            segmented_button_selected_color="#2A2B2B",
            segmented_button_selected_hover_color="#2A2B2B",
            segmented_button_unselected_color="#1C1E1E",
            segmented_button_unselected_hover_color="#1C1E1E",
            text_color="#CECECE",
            text_color_disabled="#777777",
            border_color="#484848",
            border_width=1,
        )
        
        self._create_settings_tab(tabview)
        self._create_bulk_import_tab(tabview)
        self._create_poster_scrape_tab(tabview)
        
        self._set_default_tab(tabview)
    
    def _create_settings_tab(self, tabview):
        """Create settings tab."""
        settings_tab = tabview.add("Settings")
        settings_tab.grid_columnconfigure(0, weight=0)
        settings_tab.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Plex Base URL
        self.base_url_entry = self._create_form_row(
            settings_tab, row, "Plex Base URL", "Enter Plex Base URL"
        )
        row += 1
        
        # Plex Token
        self.token_entry = self._create_form_row(
            settings_tab, row, "Plex Token", "Enter Plex Token"
        )
        row += 1
        
        # Bulk Import File
        self.bulk_txt_entry = self._create_form_row(
            settings_tab, row, "Bulk Import File", "Enter bulk import file path"
        )
        row += 1
        
        # TV Library Names
        self.tv_library_text = self._create_form_row(
            settings_tab, row, "TV Library Names", ""
        )
        row += 1
        
        # Movie Library Names
        self.movie_library_text = self._create_form_row(
            settings_tab, row, "Movie Library Names", ""
        )
        row += 1
        
        # Mediux Filters
        self.mediux_filters_text = self._create_form_row(
            settings_tab, row, "Mediux Filters", ""
        )
        row += 1
        
        # Spacer
        settings_tab.grid_rowconfigure(row, weight=1)
        row += 1
        
        # Buttons
        reload_button = self._create_button(settings_tab, text="Reload", command=self._load_and_update_ui)
        reload_button.grid(row=row, column=0, pady=5, padx=5, ipadx=30, sticky="ew")
        
        save_button = self._create_button(settings_tab, text="Save", command=self._save_config, primary=True)
        save_button.grid(row=row, column=1, pady=5, padx=5, sticky="ew")
    
    def _create_bulk_import_tab(self, tabview):
        """Create bulk import tab."""
        bulk_import_tab = tabview.add("Bulk Import")
        
        bulk_import_tab.grid_columnconfigure(0, weight=0)
        bulk_import_tab.grid_columnconfigure(1, weight=3)
        bulk_import_tab.grid_columnconfigure(2, weight=0)
        
        self.bulk_import_text = ctk.CTkTextbox(
            bulk_import_tab,
            height=15,
            wrap="none",
            state="normal",
            fg_color="#1C1E1E",
            text_color="#A1A1A1",
            font=("Courier", 14)
        )
        self.bulk_import_text.grid(row=0, column=0, padx=10, pady=5, sticky="nsew", columnspan=3)
        self._bind_context_menu(self.bulk_import_text)
        
        bulk_import_tab.grid_rowconfigure(0, weight=1)
        
        # Buttons
        reload_button = self._create_button(bulk_import_tab, text="Reload", command=self._load_bulk_import_file)
        reload_button.grid(row=1, column=0, pady=5, padx=5, ipadx=30, sticky="ew")
        
        save_button = self._create_button(bulk_import_tab, text="Save", command=self._save_bulk_import_file)
        save_button.grid(row=1, column=1, pady=5, padx=5, sticky="ew", columnspan=2)
        
        self.bulk_import_button = self._create_button(
            bulk_import_tab,
            text="Run Bulk Import",
            command=self._run_bulk_import_thread,
            primary=True
        )
        self.bulk_import_button.grid(row=2, column=0, pady=5, padx=5, sticky="ew", columnspan=3)
    
    def _create_poster_scrape_tab(self, tabview):
        """Create poster scrape tab."""
        poster_scrape_tab = tabview.add("Poster Scrape")
        
        poster_scrape_tab.grid_columnconfigure(0, weight=0)
        poster_scrape_tab.grid_columnconfigure(1, weight=1)
        
        url_label = ctk.CTkLabel(
            poster_scrape_tab,
            text="Enter a ThePosterDB set URL, MediUX set URL, or ThePosterDB user URL",
            text_color="#696969",
            font=("Roboto", 15)
        )
        url_label.grid(row=0, column=0, columnspan=2, pady=5, padx=5, sticky="w")
        
        self.url_entry = ctk.CTkEntry(
            poster_scrape_tab,
            placeholder_text="e.g., https://mediux.pro/sets/6527",
            fg_color="#1C1E1E",
            text_color="#A1A1A1",
            border_width=0,
            height=40
        )
        self.url_entry.grid(row=1, column=0, columnspan=2, pady=5, padx=5, sticky="ew")
        self._bind_context_menu(self.url_entry)
        
        poster_scrape_tab.grid_rowconfigure(2, weight=1)
        
        self.clear_button = self._create_button(poster_scrape_tab, text="Clear", command=self._clear_url)
        self.clear_button.grid(row=3, column=0, pady=5, padx=5, ipadx=30, sticky="ew")
        
        self.scrape_button = self._create_button(
            poster_scrape_tab,
            text="Run URL Scrape",
            command=self._run_url_scrape_thread,
            primary=True
        )
        self.scrape_button.grid(row=3, column=1, pady=5, padx=5, sticky="ew", columnspan=2)
    
    def _create_status_label(self):
        """Create status label at bottom."""
        self.status_label = ctk.CTkLabel(self.app, text="", text_color="#E5A00D")
        self.status_label.pack(side="bottom", fill="x", pady=(5))
    
    def _create_form_row(self, parent, row: int, label_text: str, placeholder: str) -> ctk.CTkEntry:
        """Create a form row with label and entry.
        
        Args:
            parent: Parent widget.
            row: Row number.
            label_text: Label text.
            placeholder: Placeholder text for entry.
            
        Returns:
            Entry widget.
        """
        label = ctk.CTkLabel(parent, text=label_text, text_color="#696969", font=("Roboto", 15))
        label.grid(row=row, column=0, pady=5, padx=10, sticky="w")
        
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color="#1C1E1E",
            text_color="#A1A1A1",
            border_width=0,
            height=40
        )
        entry.grid(row=row, column=1, pady=5, padx=10, sticky="ew")
        self._bind_context_menu(entry)
        
        return entry
    
    def _create_button(self, container, text: str, command, color: str = None, primary: bool = False, height: int = 35) -> ctk.CTkButton:
        """Create a styled button.
        
        Args:
            container: Parent widget.
            text: Button text.
            command: Button command.
            color: Optional color.
            primary: Whether button is primary style.
            height: Button height.
            
        Returns:
            Button widget.
        """
        button_fg = "#2A2B2B" if color else "#1C1E1E"
        button_border = "#484848"
        button_text_color = "#CECECE" if color else "#696969"
        plex_orange = "#E5A00D"
        
        if primary:
            button_fg = plex_orange
            button_text_color, button_border = "#1C1E1E", "#1C1E1E"
        
        button = ctk.CTkButton(
            container,
            text=text,
            command=command,
            border_width=1,
            text_color=button_text_color,
            fg_color=button_fg,
            border_color=button_border,
            hover_color="#333333",
            width=80,
            height=height,
            font=("Roboto", 13, "bold"),
        )
        
        return button
    
    def _bind_context_menu(self, widget):
        """Bind context menu to widget.
        
        Args:
            widget: Widget to bind to.
        """
        widget.bind("<Button-3>", self._show_context_menu)
        widget.bind("<Control-1>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """Show context menu.
        
        Args:
            event: Event object.
        """
        widget = event.widget
        widget.focus()
        
        self.global_context_menu.entryconfigure("Cut", command=lambda: widget.event_generate("<<Cut>>"))
        self.global_context_menu.entryconfigure("Copy", command=lambda: widget.event_generate("<<Copy>>"))
        self.global_context_menu.entryconfigure("Paste", command=lambda: widget.event_generate("<<Paste>>"))
        self.global_context_menu.tk_popup(event.x_root, event.y_root)
    
    def _update_status(self, message: str, color: str = "white"):
        """Update status label.
        
        Args:
            message: Status message.
            color: Text color.
        """
        self.app.after(0, lambda: self.status_label.configure(text=message, text_color=color))
    
    def _clear_url(self):
        """Clear URL entry field."""
        self.url_entry.delete(0, ctk.END)
        self._update_status("URL cleared.", color="orange")
    
    def _set_default_tab(self, tabview):
        """Set default tab based on configuration.
        
        Args:
            tabview: Tabview widget.
        """
        if self.config.base_url and self.config.token:
            tabview.set("Bulk Import")
        else:
            tabview.set("Settings")
    
    def _load_and_update_ui(self):
        """Load configuration and update UI fields."""
        self.config = self.config_manager.load()
        
        if self.base_url_entry:
            self.base_url_entry.delete(0, ctk.END)
            self.base_url_entry.insert(0, self.config.base_url)
        
        if self.token_entry:
            self.token_entry.delete(0, ctk.END)
            self.token_entry.insert(0, self.config.token)
        
        if self.bulk_txt_entry:
            self.bulk_txt_entry.delete(0, ctk.END)
            self.bulk_txt_entry.insert(0, self.config.bulk_txt)
        
        if self.tv_library_text:
            self.tv_library_text.delete(0, ctk.END)
            self.tv_library_text.insert(0, ", ".join(self.config.tv_library))
        
        if self.movie_library_text:
            self.movie_library_text.delete(0, ctk.END)
            self.movie_library_text.insert(0, ", ".join(self.config.movie_library))
        
        if self.mediux_filters_text:
            self.mediux_filters_text.delete(0, ctk.END)
            self.mediux_filters_text.insert(0, ", ".join(self.config.mediux_filters))
        
        self._load_bulk_import_file()
    
    def _save_config(self):
        """Save configuration from UI fields."""
        new_config = Config(
            base_url=self.base_url_entry.get().strip(),
            token=self.token_entry.get().strip(),
            tv_library=[item.strip() for item in self.tv_library_text.get().strip().split(",")],
            movie_library=[item.strip() for item in self.movie_library_text.get().strip().split(",")],
            mediux_filters=[item.strip() for item in self.mediux_filters_text.get().strip().split(",")],
            bulk_txt=self.bulk_txt_entry.get().strip()
        )
        
        if self.config_manager.save(new_config):
            self.config = new_config
            self._load_and_update_ui()
            self._update_status("Configuration saved successfully!", color="#E5A00D")
        else:
            self._update_status("Error saving configuration.", color="red")
    
    def _load_bulk_import_file(self):
        """Load bulk import file content."""
        try:
            bulk_txt_path = os.path.join(get_exe_dir(), self.config.bulk_txt)
            
            if not os.path.exists(bulk_txt_path):
                self.bulk_import_text.delete(1.0, ctk.END)
                self.bulk_import_text.insert(ctk.END, "Bulk import file path is not set or file does not exist.")
                return
            
            with open(bulk_txt_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            self.bulk_import_text.delete(1.0, ctk.END)
            self.bulk_import_text.insert(ctk.END, content)
        except Exception as e:
            self.bulk_import_text.delete(1.0, ctk.END)
            self.bulk_import_text.insert(ctk.END, f"Error loading file: {str(e)}")
    
    def _save_bulk_import_file(self):
        """Save bulk import text content to file."""
        try:
            bulk_txt_path = os.path.join(get_exe_dir(), self.config.bulk_txt)
            os.makedirs(os.path.dirname(bulk_txt_path), exist_ok=True)
            
            with open(bulk_txt_path, "w", encoding="utf-8") as file:
                file.write(self.bulk_import_text.get(1.0, ctk.END).strip())
            
            self._update_status("Bulk import file saved!", color="#E5A00D")
        except Exception as e:
            self._update_status(f"Error saving bulk import file: {str(e)}", color="red")
    
    def _run_url_scrape_thread(self):
        """Run URL scrape in separate thread."""
        url = self.url_entry.get()
        
        if not url:
            self._update_status("Please enter a valid URL.", color="red")
            return
        
        self._disable_buttons()
        threading.Thread(target=self._process_scrape_url, args=(url,)).start()
    
    def _run_bulk_import_thread(self):
        """Run bulk import in separate thread."""
        bulk_import_list = self.bulk_import_text.get(1.0, ctk.END).strip().split("\n")
        valid_urls = parse_urls(bulk_import_list)
        
        if not valid_urls:
            self._update_status("No bulk import entries found.", color="red")
            return
        
        self._disable_buttons()
        threading.Thread(target=self._process_bulk_import, args=(valid_urls,)).start()
    
    def _process_scrape_url(self, url: str):
        """Process single URL scrape.
        
        Args:
            url: URL to scrape.
        """
        try:
            self._setup_services()
            
            if not self.plex_service.tv_libraries and not self.plex_service.movie_libraries:
                self._update_status("Plex setup incomplete. Please configure your settings.", color="red")
                return
            
            self._update_status(f"Scraping: {url}", color="#E5A00D")
            
            movie_posters, show_posters, collection_posters = self.scraper_factory.scrape_url(url)
            
            # Upload posters
            for poster in collection_posters:
                self.upload_service.process_poster(poster)
            
            for poster in movie_posters:
                self.upload_service.process_poster(poster)
            
            for poster in show_posters:
                self.upload_service.process_poster(poster)
            
            self._update_status(f"Posters successfully set for: {url}", color="#E5A00D")
        
        except Exception as e:
            self._update_status(f"Error: {e}", color="red")
        
        finally:
            self._enable_buttons()
    
    def _process_bulk_import(self, valid_urls: List[str]):
        """Process bulk import URLs.
        
        Args:
            valid_urls: List of URLs to process.
        """
        try:
            self._setup_services()
            
            if not self.plex_service.tv_libraries and not self.plex_service.movie_libraries:
                self._update_status("Plex setup incomplete. Please configure your settings.", color="red")
                return
            
            for i, url in enumerate(valid_urls):
                status_text = f"Processing item {i+1} of {len(valid_urls)}: {url}"
                self._update_status(status_text, color="#E5A00D")
                
                try:
                    movie_posters, show_posters, collection_posters = self.scraper_factory.scrape_url(url)
                    
                    for poster in collection_posters:
                        self.upload_service.process_poster(poster)
                    
                    for poster in movie_posters:
                        self.upload_service.process_poster(poster)
                    
                    for poster in show_posters:
                        self.upload_service.process_poster(poster)
                    
                    self._update_status(f"Completed: {url}", color="#E5A00D")
                except Exception as e:
                    self._update_status(f"Error processing {url}: {e}", color="red")
            
            self._update_status("Bulk import scraping completed.", color="#E5A00D")
        
        except Exception as e:
            self._update_status(f"Error during bulk import: {e}", color="red")
        
        finally:
            self._enable_buttons()
    
    def _setup_services(self):
        """Setup Plex and scraper services."""
        self.plex_service = PlexService(self.config)
        self.plex_service.setup(gui_mode=True)
        
        self.upload_service = PosterUploadService(self.plex_service)
        self.scraper_factory = ScraperFactory(self.config, use_playwright=True)
    
    def _disable_buttons(self):
        """Disable action buttons during processing."""
        self.app.after(0, lambda: [
            self.scrape_button.configure(state="disabled"),
            self.clear_button.configure(state="disabled"),
            self.bulk_import_button.configure(state="disabled"),
        ])
    
    def _enable_buttons(self):
        """Enable action buttons after processing."""
        self.app.after(0, lambda: [
            self.scrape_button.configure(state="normal"),
            self.clear_button.configure(state="normal"),
            self.bulk_import_button.configure(state="normal"),
        ])
