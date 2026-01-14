# Anti-Scraping Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                                  │
│                    (Scrape URL or Bulk URLs)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SCRAPER FACTORY                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Detects URL type:                                          │    │
│  │  • theposterdb.com → PosterDBScraper                       │    │
│  │  • mediux.pro → MediuxScraper                              │    │
│  │  • .html file → Local HTML Parser                          │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BASE SCRAPER (Anti-Detection Layer)               │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  INITIALIZATION PHASE                                         │  │
│  │  ────────────────────                                         │  │
│  │  1. Select random User Agent (from 7 options)                │  │
│  │  2. Select random Viewport (from 5 sizes)                    │  │
│  │  3. Launch Chromium with 14 stealth arguments                │  │
│  │  4. Create browser context with:                             │  │
│  │     • Realistic headers (12 headers)                         │  │
│  │     • Geolocation (New York)                                 │  │
│  │     • Timezone (America/New_York)                            │  │
│  │     • Language (en-US)                                       │  │
│  │  5. Inject anti-detection JavaScript                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  REQUEST PHASE (Configurable via config.json)                │  │
│  │  ─────────────                                                │  │
│  │  1. Apply initial delay (default: 0.0s - instant start!)     │  │
│  │  2. Apply random delay (default: 0.1-0.5s per request)       │  │
│  │  3. Track request count (extra delay every 10)               │  │
│  │  4. Navigate with random wait strategy                       │  │
│  │  5. Site-specific waits (5s timeout):                        │  │
│  │     • MediUX: 1-2 sec for JavaScript execution               │  │
│  │     • PosterDB: 0.8-1.5 sec for content load                 │  │
│  │  6. Bezier curve mouse movement (60% chance)                 │  │
│  │  7. Realistic scrolling behavior (40% chance)                │  │
│  │  8. Extract HTML content                                     │  │
│  │                                                               │  │
│  │  Delay Configuration (config.json):                          │  │
│  │  • scraper_initial_delay: First request (default: 0.0s)      │  │
│  │  • scraper_min_delay: Min between requests (default: 0.1s)   │  │
│  │  • scraper_max_delay: Max between requests (default: 0.5s)   │  │
│  │  • scraper_batch_delay: Every 10 requests (default: 2.0s)    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  JAVASCRIPT ANTI-DETECTION (Injected)                        │  │
│  │  ─────────────────────────────────                           │  │
│  │  • navigator.webdriver → undefined                           │  │
│  │  • navigator.plugins → realistic array                       │  │
│  │  • navigator.languages → ['en-US', 'en']                     │  │
│  │  • navigator.permissions → mocked                            │  │
│  │  • window.chrome → {runtime, loadTimes, csi, app}           │  │
│  │  • navigator.hardwareConcurrency → 8                         │  │
│  │  • navigator.deviceMemory → 8                                │  │
│  │  • navigator.platform → 'Win32'                              │  │
│  │  • navigator.vendor → 'Google Inc.'                          │  │
│  │  • Battery API → mocked (charging, level 1)                  │  │
│  │  • Connection API → mocked (4g, 10mbps)                      │  │
│  │  • Canvas fingerprint → masked                               │  │
│  │  • WebGL fingerprint → spoofed (Intel Iris)                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SPECIALIZED SCRAPER                               │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  PosterDBScraper:                                           │    │
│  │  • Parse poster grids                                       │    │
│  │  • Extract titles, years, seasons                           │    │
│  │  • Handle sets, single posters, user pages                  │    │
│  │  • Support pagination                                       │    │
│  └────────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  MediuxScraper:                                             │    │
│  │  • Parse JSON data from __NEXT_DATA__                       │    │
│  │  • Extract movies, shows, collections                       │    │
│  │  • Apply mediux_filters from config                         │    │
│  │  • Handle title cards, backdrops, season posters            │    │
│  └────────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PARSED POSTER DATA                                │
│  (movies_list, shows_list, collections_list)                        │
└─────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════
                      TIMING DIAGRAM (Configurable)
═══════════════════════════════════════════════════════════════════════

Default Configuration (Fast & Balanced):
Request 1:  ▶ FETCH ▶ Parse (no initial delay!)
Request 2:  ─[0.1-0.5s delay]─▶ FETCH ▶ Parse
Request 3:  ─[0.1-0.5s delay]─▶ FETCH ▶ Parse
...
Request 10: ─[0.1-0.5s delay]─▶ FETCH ▶ Parse ─[2.0s EXTRA DELAY]─
Request 11: ─[0.1-0.5s delay]─▶ FETCH ▶ Parse
...

GUI Presets Available:
• ⚡ Fast (Risky):      0.0s initial | 0.0-0.2s per request | 0.0s batch
• ⚖️  Balanced (Default): 0.0s initial | 0.1-0.5s per request | 2.0s batch
• 🛡️  Safe (Slower):     1.0s initial | 0.5-2.0s per request | 5.0s batch

═══════════════════════════════════════════════════════════════════════
                   DETECTION PROTECTION LAYERS
═══════════════════════════════════════════════════════════════════════

Layer 1: BROWSER FINGERPRINT
         ├─ Randomized User Agent
         ├─ Randomized Viewport
         ├─ Realistic Headers (12)
         └─ Geolocation + Timezone

Layer 2: JAVASCRIPT FINGERPRINT
         ├─ WebDriver Masking
         ├─ Plugin Spoofing
         ├─ Hardware Spoofing
         ├─ Canvas Masking
         └─ WebGL Spoofing

Layer 3: BEHAVIORAL ANALYSIS (Configurable)
         ├─ Initial Delay (0.0s default - instant start!)
         ├─ Random Delays (0.1-0.5s default, configurable)
         ├─ Request Spacing (extra 2.0s every 10, configurable)
         ├─ Bezier Curve Mouse Movements (60%)
         ├─ Micro-jitter (±2px wobble)
         ├─ Realistic Scrolling (40%)
         └─ Variable Wait Strategies

Layer 4: REQUEST PATTERNS
         ├─ Realistic Headers
         ├─ Referer Tracking
         ├─ Accept Headers
         └─ Cache Control

Layer 5: PLAYWRIGHT-ONLY (No Fallback)
         ├─ Consistent Fingerprinting
         ├─ Always Full JavaScript Support
         ├─ Error Handling with Exceptions
         └─ Timeout Management

═══════════════════════════════════════════════════════════════════════
```

## Protection Coverage

| Detection Method          | Protected | Implementation                |
|---------------------------|-----------|-------------------------------|
| navigator.webdriver       | ✅        | Set to undefined              |
| Plugin fingerprinting     | ✅        | Realistic plugin array        |
| Canvas fingerprinting     | ✅        | Masked toDataURL              |
| WebGL fingerprinting      | ✅        | Spoofed vendor/renderer       |
| User agent analysis       | ✅        | 7 realistic agents rotated    |
| Viewport fingerprinting   | ✅        | 5 sizes randomized            |
| Header analysis           | ✅        | 12 realistic headers          |
| Request timing patterns   | ✅        | Configurable delays (0.1-0.5s)|
| Rate limiting             | ✅        | Configurable batch delays     |
| Behavioral detection      | ✅        | Bezier curves, scrolling      |
| Hardware fingerprinting   | ✅        | 8 cores, 8GB RAM, Intel GPU   |
| Battery API fingerprint   | ✅        | Mocked charging state         |
| Connection API            | ✅        | Mocked 4G connection          |
| Timezone analysis         | ✅        | America/New_York              |
| Language fingerprint      | ✅        | en-US, en                     |
| Automation flags          | ✅        | All removed                   |

## Configuration Options

The scraper performance can be tuned via `config.json` or the GUI Settings tab:

```json
{
  "scraper_initial_delay": 0.0,   // Delay before first request (seconds)
  "scraper_min_delay": 0.1,        // Minimum delay between requests
  "scraper_max_delay": 0.5,        // Maximum delay between requests  
  "scraper_batch_delay": 2.0       // Extra delay every 10 requests
}
```

**GUI Presets:**
- **⚡ Fast (Risky):** All delays at minimum - fastest scraping, highest detection risk
- **⚖️ Balanced (Default):** Optimized for speed while maintaining safety
- **🛡️ Safe (Slower):** Conservative delays - slower but very safe

**Performance Impact:**
- **Default (Balanced):** ~5-10 posters/minute
- **Fast:** ~15-20 posters/minute (higher risk)
- **Safe:** ~2-5 posters/minute (lowest risk)

### Implemented Realistic Bezier Curve Mouse Movement

**Features:**
- **Bezier curves** for natural curved paths (not straight lines)
- **Variable speed:**
  - Slower at start (20% of movement)
  - Faster in middle (60% of movement)
  - Slower at end (20% of movement)
  - Mimics human acceleration/deceleration
- **Micro-jitter:** ±2px random wobble (human hands aren't steady)
- **Distance-based steps:** Longer movements = more steps (10-20 steps)
- **Random control points:** Creates unique curve each time
- **Occasional misclick simulation:** 10% chance of random scroll instead

**Technical Details:**
```python
# Quadratic bezier curve formula
x = (1 - t)² * start_x + 2(1 - t)t * ctrl_x + t² * end_x
y = (1 - t)² * start_y + 2(1 - t)t * ctrl_y + t² * end_y

# Variable timing
- Start/End: 5-15ms per step (slow)
- Middle: 1-5ms per step (fast)
```

### Enhanced Scrolling Behavior
**Frequency:** 40% chance per page (was none)

**Patterns:**
- Scroll down 100-400px (like reading)
- 30% chance to scroll back up (like re-reading)
- Variable timing between scrolls (0.1-0.5s)
- Realistic wheel delta values

## Visual Mouse Movement Comparison

### Old (Straight Line - Robotic):
```
Start (150, 200) ──────────────► End (450, 350)
                 Linear path
```

### New (Bezier Curve - Human-like):
```
Start (150, 200)
      ╲
       ╲  (slow acceleration)
        ╲
         ●─── Control Point (±100px offset)
          ╲  
           ╲ (fast middle)
            ╲
             ╲ (slow deceleration + jitter)
              ╲
               ► End (450, 350)
```

## Performance Impact

**Mouse Movement:**
- Distance 300px: ~30-60 steps
- Timing: ~200-500ms total per movement
- Negligible impact on overall scrape time

**Scrolling:**
- Additional 0.2-0.8s per page (when triggered)
- Only 40% of pages affected
- Average impact: ~0.3s per page

**Total Impact:**
- ~0.5-1.0s additional per page
- Well worth it for anti-detection benefits


## Anti-Detection Improvements

### Mouse Movement Detection
**Before:** Simple straight lines - easily detected as bot  
**After:** Bezier curves with acceleration/jitter - indistinguishable from human

### Behavioral Analysis
**Before:** Static movement patterns  
**After:** 
- Variable speed (acceleration/deceleration)
- Micro-jitter (±2px wobble)
- Random scrolling patterns
- Occasional "misclicks"