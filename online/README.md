# Set Theory Analysis - Online Version

A fully self-contained, browser-based pitch class set analysis tool that runs entirely in your web browser with no installation required.

## Quick Start

Simply open `index.html` in any modern web browser. No server, no installation, no dependencies.

**Try it now:** Just double-click `index.html` or drag it into your browser.

## Features

### Pitch Class Input
- **Text Input**: Enter pitch classes using:
  - Numbers: `0 4 7` or `0, 4, 7`
  - Note names: `C E G` or `c e g`
  - Forte numbers: `3-11` (loads directly from the catalog)
- **Interactive Piano**: Click keys to toggle pitch classes
- **Clock Visualization**: Click nodes on the clock face to add/remove notes

### Analysis Display
- **Prime Form**: Automatically calculated canonical form
- **Forte Number**: Allen Forte's catalog classification
- **Interval Vector**: Six-element vector showing interval content
- **Cardinality**: Number of pitch classes in the set
- **Z-Partner**: Shows Z-related set if one exists

### Visualization Modes
- **Clock Mode**: Traditional pitch class clock with connecting lines showing intervals
- **Graph Mode**: Network graph highlighting interval class relationships

### Transformations
- **Transposition (Tn)**: Transpose by any interval (0-11)
- **Inversion (In)**: Invert around any axis (0-11)
- **Retrograde (R)**: Reverse the pitch class order
- **Complement**: Get the complementary pitch classes (all notes not in the set)
- **Prime Form**: Reduce to canonical prime form

### Transformation Explorer
The right panel shows mini-visualizations of all 12 transpositions and 12 inversions. Click any to load that transformation.

### Subsets & Supersets
- View all subsets of the current set
- View possible supersets (sets containing the current set)
- Find Z-related sets (different sets with the same interval vector)

### Forte Directory
Browse the complete Forte catalog organized by cardinality (2-note through 10-note sets). Click any entry to load it.

### Music Examples
Pre-loaded examples include:
- Traditional chords: Major, Minor, Diminished, Augmented triads
- Seventh chords: Dominant 7th, Major 7th, Diminished 7th
- Scales: Major, Whole Tone, Octatonic, Pentatonic
- Famous sets: Tristan Chord (Wagner), Mystic Chord (Scriabin), Viennese Trichord (Schoenberg)

### Audio Playback
- **Play as Chord**: Hear all pitch classes simultaneously
- **Play Arpeggiated**: Hear pitch classes one at a time
- **Stop**: Stop current playback
- Uses Web Audio API - works in all modern browsers

### MIDI Export
Export the current pitch class set as a standard MIDI file for use in DAWs and notation software.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Stop audio playback |
| `Escape` | Close open modals |
| `Enter` | Apply current pitch class input |

## Technical Details

### Self-Contained
The entire application is a single HTML file with:
- Inline CSS styling (dark theme with purple/blue accent colors)
- Inline JavaScript (PitchClassSet class, ForteClassification, audio engine, visualization)
- p5.js loaded from CDN for visualization
- Google Fonts (Outfit, JetBrains Mono) loaded from CDN

### Browser Requirements
- Any modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Web Audio API support (all modern browsers)

### No Server Required
Runs completely client-side. Can be:
- Opened directly from your file system
- Hosted on any static web server
- Shared via GitHub Pages, Netlify, Vercel, etc.

## Hosting on GitHub Pages

To host this online:

1. Push to a GitHub repository
2. Go to Settings > Pages
3. Select source branch and `/online` folder
4. Your app will be available at `https://username.github.io/repo-name/online/`

## Comparison: Online vs Desktop Version

| Feature | Online | Desktop |
|---------|--------|---------|
| Installation | None | Python + PyQt6 |
| Visualization | p5.js canvas | PyQt6 widgets |
| Audio | Web Audio API | FluidSynth + SoundFonts |
| Audio Quality | Basic synthesis | High-quality SoundFont |
| MIDI Export | Basic | Full-featured |
| Offline Use | Limited (fonts/p5.js) | Full |
| Customization | Limited | Full settings panel |

## License

Part of the Set Theory Analysis project. See main repository for license information.
