
# Plex Poster Set Helper

Automatically download and apply poster sets from ThePosterDB and MediUX to your Plex Media Server in seconds. This tool streamlines the process of updating your Plex library with high-quality custom posters, supporting both movies and TV shows with season and episode artwork.

## Features

- **Multiple Source Support**
  - ThePosterDB sets, single posters, and user uploads
  - MediUX sets with full-quality image downloads
  
- **Flexible Usage Modes**
  - Interactive CLI with menu-driven interface
  - Direct command-line execution
  - Modern GUI built with CustomTkinter
  - Bulk import from text files
  
- **Smart Matching**
  - Automatic media detection and matching
  - Support for movies, TV shows, seasons, and collections
  - Multiple library support
  
- **High Performance**
  - Playwright-based scraping for JavaScript-rendered pages
  - Parallel processing capabilities
  - Automatic retry and error handling

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Plex Media Server with API access

### Setup

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/tonywied17/plex-poster-set-helper.git
   cd plex-poster-set-helper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your Plex connection**
   
   Rename `example_config.json` to `config.json` and fill in your details:

   ```json
   {
     "base_url": "http://192.168.1.100:32400",
     "token": "your_plex_token_here",
     "movie_library": "Movies",
     "tv_library": "TV Shows",
     "bulk_txt": "bulk_import.txt",
     "mediux_filters": ["poster", "backdrop", "title_card"],
     "title_mappings": {
       "Pluribus": "PLUR1BUS",
       "The Office": "The Office (US)"
     }
   }
   ```

   **Configuration Options:**
   
   | Option | Description | Example |
   |--------|-------------|---------|
   | `base_url` | Your Plex server URL and port | `"http://192.168.1.100:32400"` |
   | `token` | Plex authentication token ([How to find](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)) | `"aBc123XyZ..."` |
   | `movie_library` | Name of your Movies library | `"Movies"` or `["Movies", "4K Movies"]` |
   | `tv_library` | Name of your TV Shows library | `"TV Shows"` or `["TV", "Anime"]` |
   | `bulk_txt` | Default file for bulk imports | `"bulk_import.txt"` |
   | `mediux_filters` | MediUX media types to download | `["poster", "backdrop", "title_card"]` |
   | `title_mappings` | Manual title overrides for non-matching names | `{"Source Title": "Plex Title"}` |

   > **Multiple Libraries:** You can specify multiple libraries as arrays to apply posters across all of them simultaneously.

---

## Usage

### Interactive CLI Mode

Run the script without arguments to enter interactive mode:

```bash
python main.py
```

![CLI Overview](https://raw.githubusercontent.com/tonywied17/plex-poster-set-helper/refs/heads/main/assets/cli_overview.png)

**Menu Options:**
1. **Single URL Import** - Paste a ThePosterDB or MediUX link to import that set
2. **Bulk Import** - Process multiple URLs from a text file
3. **Launch GUI** - Open the graphical interface
4. **Exit** - Close the application

### Command-Line Arguments

**Single URL:**
```bash
python main.py https://theposterdb.com/set/12345
```

**Bulk Import:**
```bash
python main.py bulk bulk_import.txt
```

**Launch GUI:**
```bash
python main.py gui
```

### GUI Mode

Launch the graphical interface for a more visual experience:

```bash
python main.py gui
```

![GUI Overview](https://raw.githubusercontent.com/tonywied17/plex-poster-set-helper/refs/heads/main/assets/gui_overview.png)

The GUI provides:
- Easy URL input with real-time validation
- Visual progress tracking
- Status updates and error reporting
- Bulk import file management

---

## Supported URLs

### ThePosterDB

| URL Type | Example | Description |
|----------|---------|-------------|
| **Set** | `https://theposterdb.com/set/12345` | Downloads all posters in a set |
| **Single Poster** | `https://theposterdb.com/poster/66055` | Finds and downloads the entire set from a single poster |
| **User Profile** | `https://theposterdb.com/user/username` | Downloads all uploads from a user |

### MediUX

| URL Type | Example | Description |
|----------|---------|-------------|
| **Set** | `https://mediux.pro/sets/24522` | Downloads all posters in a set with original quality |

> **Note:** MediUX downloads use direct API URLs for maximum image quality (~2MB originals instead of ~116KB compressed versions).

---

## Advanced Features

### Bulk Import

Create a text file with one URL per line:

```text
# Movies
https://theposterdb.com/set/12345
https://mediux.pro/sets/24522

// TV Shows
https://theposterdb.com/set/67890
https://theposterdb.com/poster/11111
```

Lines starting with `#` or `//` are treated as comments and ignored.

**Run bulk import:**
```bash
python main.py bulk my_posters.txt
```

Or use the default file specified in `config.json`:
```bash
python main.py bulk
```

### MediUX Filters

Control which types of media are downloaded from MediUX by editing the `mediux_filters` in `config.json`:

```json
"mediux_filters": ["poster", "background", "season_cover", "title_card"]
```

**Available filters:**
- `poster` - Standard movie/show posters and season covers
- `backdrop` - Background/backdrop images
- `title_card` - Episode title cards

Remove any filter to skip that media type during import.

### Title Matching

The tool uses intelligent matching to find media in your Plex library:

**1. Manual Title Mappings** (Exact overrides)
For cases where poster source names don't match your Plex library, use `title_mappings` in `config.json`:

```json
"title_mappings": {
  "Pluribus": "PLUR1BUS",
  "The Office": "The Office (US)",
  "Star Wars Episode IV": "Star Wars"
}
```

When the scraper finds "Pluribus", it will automatically look for "PLUR1BUS" in your library.

**2. Fuzzy Matching** (Automatic fallback)
If exact matching fails, the tool automatically tries fuzzy matching with 80% similarity:
- "The Batman" might match "Batman (2022)"
- "Star Wars: A New Hope" might match "Star Wars Episode IV"

The tool will notify you when fuzzy matching is used: `ℹ Fuzzy matched 'Title A' to 'Title B'`

### Multiple Libraries

Apply posters to multiple Plex libraries simultaneously:

```json
{
  "movie_library": ["Movies", "4K Movies", "Kids Movies"],
  "tv_library": ["TV Shows", "Anime", "Kids TV"]
}
```

The tool will find and update the same media across all specified libraries.

---

## Building the Executable

A pre-built Windows executable is available in the `dist/` folder. To build it yourself:

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build using the spec file**
   ```bash
   pyinstaller _PlexPosterSetHelper.spec
   ```

> **Tip:** Set `interactive_cli = False` in the main script before building to make the executable launch in GUI mode by default.

---

## Troubleshooting

### "Poster set not found" Error

**Problem:** Error when using ThePosterDB single poster URLs  
**Solution:** This has been fixed in the latest version. The scraper now properly handles the updated page structure where set links are in tooltip elements.

### MediUX Images Not Downloading

**Problem:** Images appear blank or fail to download  
**Solution:** The scraper now uses direct API URLs (`https://api.mediux.pro/assets/`) instead of the Next.js proxy. Ensure you have network access to this domain.

### Posters Not Applying to Plex

**Problem:** Tool downloads posters but they don't appear in Plex  
**Solutions:**
- Verify library names in `config.json` match exactly (case-sensitive)
- Ensure media exists in Plex with matching titles and years
- Check that your Plex token has write permissions
- Confirm the Plex server is accessible at the configured URL

### Connection Errors

**Problem:** Cannot connect to scraping sources  
**Solutions:**
- Check your internet connection
- Ensure Playwright browser is properly installed: `playwright install chromium`
- Some networks may block automated access; try from a different network
- Check if the source website is accessible in your browser

### Media Not Found in Library

**Problem:** Tool reports media not found even though it exists  
**Solutions:**
- Verify the media title and year match between the poster source and Plex
- Check for special characters or formatting differences
- Ensure the media is properly scanned and visible in your Plex library
- Try refreshing metadata in Plex before running the tool

---

## Requirements

- **Python 3.8+**
- **Dependencies:** (automatically installed via `requirements.txt`)
  - `plexapi` - Plex API interaction
  - `requests` - HTTP requests
  - `beautifulsoup4` - HTML parsing
  - `playwright` - Modern web scraping
  - `customtkinter` - Modern GUI framework
  - `pillow` - Image processing

---

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

## License

This project is open source and available under the MIT License.

---

## Credits

- **ThePosterDB** - Community-driven poster database
- **MediUX** - High-quality media artwork source
- Built with ❤️ for the Plex community
