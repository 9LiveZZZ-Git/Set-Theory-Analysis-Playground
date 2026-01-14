# Set Theory Analysis

A comprehensive **Allen Forte Pitch Class Set Theory** analysis tool. Available as both a desktop application and a browser-based web app. This tool allows musicians, composers, and music theorists to explore, analyze, and aurally examine pitch class sets.

## Quick Start

### Option 1: Online Version (No Installation)

Simply open `online/index.html` in any web browser. No installation required!

### Option 2: Desktop Application

```bash
# Install dependencies
pip install PyQt6 matplotlib numpy midiutil pyfluidsynth

# Run the application
python run_analysis.py
```

---

## Table of Contents

1. [Overview](#overview)
2. [Online Version](#online-version)
3. [Installation](#installation)
4. [Features](#features)
5. [User Interface Guide](#user-interface-guide)
6. [Pitch Class Set Theory Basics](#pitch-class-set-theory-basics)
7. [File Structure](#file-structure)
8. [Architecture](#architecture)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This application provides an interactive environment for working with **pitch class sets** - a foundational concept in post-tonal music theory developed by Allen Forte. It allows you to:

- **Input** pitch class sets in multiple formats
- **Visualize** sets as clock diagrams or interval graphs
- **Analyze** sets to find their prime form, Forte number, and interval vector
- **Transform** sets using transposition (T), inversion (I), and retrograde (R) operations
- **Compare** sets and find relationships between them
- **Play** sets through audio synthesis
- **Export** sets to MIDI files

---

## Online Version

The `online/` folder contains a fully self-contained, browser-based version of the Set Theory Analysis tool.

### Features

- **Zero installation** - just open `index.html` in any browser
- **Interactive piano keyboard** for pitch class input
- **Clock and graph visualizations** using p5.js
- **Complete Forte directory** with all 208 set classes
- **Audio playback** via Web Audio API
- **MIDI export** directly from the browser
- **Transformation explorer** showing all T/I operations
- **Subset/superset finder** and Z-relation display

### Usage

```bash
# Local use - just open the file
open online/index.html

# Or host on any web server
# Works with GitHub Pages, Netlify, Vercel, etc.
```

### Comparison

| Feature | Online | Desktop |
|---------|--------|---------|
| Installation | None | Python + PyQt6 |
| Audio Quality | Basic synthesis | High-quality SoundFont |
| Offline Use | Limited | Full |
| Customization | Limited | Full settings |

See `online/README.md` for complete documentation of the web version.

---

## Installation

### Prerequisites

- **Python 3.9** or higher
- **pip** (Python package manager)

### Required Packages

```bash
pip install PyQt6 matplotlib numpy midiutil
```

### Optional (for audio playback)

```bash
pip install pyfluidsynth
```

**Note:** FluidSynth requires the FluidSynth library to be installed on your system:
- **Windows:** The application includes FluidSynth binaries
- **macOS:** `brew install fluid-synth`
- **Linux:** `sudo apt-get install fluidsynth libfluidsynth-dev`

### Running the Application

```bash
cd SetTheoryAnalysis
python run_analysis.py
```

---

## Features

### 1. Pitch Class Set Input

Enter sets in multiple formats:
- **Space-separated:** `0 4 7` (C major triad)
- **Comma-separated:** `0, 3, 7` (C minor triad)
- **Forte number:** `3-11` (loads the canonical form)
- **Note names:** `C E G` (converts to pitch classes)

### 2. Visualization Modes

- **Clock Diagram:** Shows pitch classes on a chromatic circle (0-11)
- **Graph View:** Displays interval relationships as a network

### 3. Analysis Panel

Displays:
- **Prime Form:** The most compact representation (e.g., [0,3,7])
- **Forte Number:** Classification in Forte's catalog (e.g., 3-11)
- **Interval Vector:** Six-element vector showing interval class content
- **Set Properties:** Cardinality, symmetry, Z-relation status

### 4. Transformations

Apply operations to the current set:
- **Transposition (Tn):** Shift all pitch classes by n semitones
- **Inversion (In):** Reflect around pitch class n
- **Retrograde (R):** Reverse the ordering
- **Retrograde Inversion (RIn):** Combine R and I operations

The **Transformation Panel** shows all 12 transpositions and inversions as mini-clocks. Click any to apply instantly.

### 5. Subset Explorer

Browse all subsets and supersets of the current set:
- Shows Forte numbers and prime forms
- Double-click to load any subset/superset

### 6. Forte Directory

Browse all 208 pitch class sets organized by cardinality (size):
- Filter by cardinality (3-note, 4-note, etc.)
- Search by Forte number or prime form
- View interval vectors and properties

### 7. Music Examples

Load famous pitch class sets from classical and popular music:
- Scriabin's Mystic Chord
- Messiaen's Modes of Limited Transposition
- Stravinsky's Petrushka Chord
- Berg's Lyric Suite row
- And many more

### 8. Audio Playback

- **Play as chord:** All notes simultaneously (Ctrl+P)
- **Play arpeggiated:** Notes in sequence (Ctrl+Shift+P)
- Configurable octave, tempo, and velocity

### 9. MIDI Export

Export sets to MIDI files:
- Single set export
- All transpositions (T0-T11)
- All inversions (I0-I11)
- All retrogrades (RT0-RT11)
- All retrograde inversions (RI0-RI11)

---

## User Interface Guide

```
+------------------------------------------------------------------+
|  File  Edit  Operations  Analysis  Tools  Audio  View  Help      |  <- Menu Bar
+------------------------------------------------------------------+
|                                                                   |
|  +-------------+  +------------------------------------------+   |
|  | SET INPUT   |  |                                          |   |
|  |             |  |         VISUALIZATION CANVAS             |   |
|  | [0 4 7    ] |  |                                          |   |
|  |             |  |              (Clock or Graph)            |   |
|  | [T] [I] [R] |  |                                          |   |
|  |             |  |                                          |   |
|  | Recent:     |  +------------------------------------------+   |
|  | - 0,3,7     |                                                 |
|  | - 0,4,7     |  +------------------------------------------+   |
|  +-------------+  |  TRANSFORMATION PANEL / SUBSET EXPLORER  |   |
|                   |  (Dockable panels on right side)          |   |
|                   +------------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
|  ANALYSIS PANEL (Bottom Dock)                                     |
|  Prime: [0,4,7]  |  Forte: 3-11  |  IV: <001110>  |  Card: 3    |
+------------------------------------------------------------------+
|  Hover help...                            Audio: FluidSynth Ready |  <- Status Bar
+------------------------------------------------------------------+
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New/Clear set |
| Ctrl+P | Play as chord |
| Ctrl+Shift+P | Play arpeggiated |
| Ctrl+M | Export to MIDI |
| Ctrl+T | Transpose |
| Ctrl+I | Invert |
| Ctrl+R | Rotate |
| Ctrl+A | Analyze |
| Ctrl+F | Forte Directory |
| Ctrl+E | Music Examples |
| Ctrl+Q | Quit |

---

## Pitch Class Set Theory Basics

### Pitch Classes

A **pitch class** represents all pitches with the same name, regardless of octave:
- C, C', C'', C''' are all **pitch class 0**
- The 12 pitch classes: C=0, C#=1, D=2, D#=3, E=4, F=5, F#=6, G=7, G#=8, A=9, A#=10, B=11

### Pitch Class Sets

A **pitch class set** is an unordered collection of pitch classes:
- {0, 4, 7} = C major triad
- {0, 3, 7} = C minor triad

### Prime Form

The **prime form** is the most compact representation of a set, transposed to start on 0:
- All major triads reduce to prime form [0,3,7]
- All minor triads also reduce to [0,3,7]

### Forte Number

Allen Forte catalogued all possible pitch class sets (up to transposition and inversion) and assigned each a number:
- Format: `cardinality-ordinal` (e.g., **3-11** = set #11 among 3-note sets)
- There are 208 unique set classes

### Interval Vector

The **interval vector** counts how many of each interval class (1-6) appear in a set:
- Format: `<ic1, ic2, ic3, ic4, ic5, ic6>`
- Major triad [0,4,7] has interval vector `<0,0,1,1,1,0>`

### Transformations

- **Transposition Tn:** Add n to each pitch class (mod 12)
  - T5({0,4,7}) = {5,9,0} = F major

- **Inversion In:** Subtract each pitch class from n (mod 12)
  - I0({0,4,7}) = {0,8,5} = F minor

- **Retrograde R:** Reverse the ordering (for ordered sets)

---

## File Structure

```
SetTheoryAnalysis/
├── run_analysis.py              # Entry point - run this to start
├── README.md                    # This file
├── requirements.txt             # Python dependencies
│
├── pitch_class_set.py           # Core PitchClassSet class
├── forte_classification.py      # Forte number lookup and classification
├── set_analysis.py              # SetAnalyzer class
├── music_examples.py            # Famous pitch class sets from music
│
├── online/                      # Browser-based version
│   ├── index.html               # Self-contained web app
│   └── README.md                # Online version documentation
│
└── gui/
    ├── __init__.py
    ├── analysis_main_window.py  # Main application window
    │
    ├── panels/                  # Main UI panels
    │   ├── __init__.py
    │   ├── set_input_panel.py   # Left panel - set input
    │   ├── analysis_panel.py    # Bottom panel - analysis display
    │   ├── transformation_panel.py  # Right panel - T/I/R previews
    │   └── subset_explorer.py   # Right panel - subset browser
    │
    ├── widgets/                 # Reusable UI components
    │   ├── __init__.py
    │   ├── pitch_class_input.py     # Input field for pitch classes
    │   ├── visualization_canvas.py  # Clock/graph visualization
    │   ├── forte_selector.py        # Forte directory browser
    │   ├── transformation_grid.py   # Grid of mini-clocks
    │   ├── audio_settings_dialog.py # Audio configuration
    │   ├── full_analysis_dialog.py  # Detailed analysis popup
    │   ├── music_examples_dialog.py # Music examples browser
    │   ├── interval_vector_dialog.py # IV visualization
    │   ├── compare_sets_dialog.py   # Set comparison tool
    │   └── find_similar_dialog.py   # Find similar sets
    │
    ├── audio/                   # Audio playback
    │   ├── __init__.py
    │   ├── audio_manager.py     # High-level audio control
    │   └── fluidsynth_engine.py # FluidSynth integration
    │
    ├── utils/                   # Utility modules
    │   ├── __init__.py
    │   ├── settings_manager.py  # Save/load preferences
    │   ├── midi_export.py       # MIDI file generation
    │   ├── debouncer.py         # Input debouncing
    │   └── validators.py        # Input validation
    │
    └── resources/
        └── soundfonts/          # Sound samples for playback
            └── GeneralUser_GS.sf2
```

---

## Architecture

### Core Classes

#### `PitchClassSet` (pitch_class_set.py)

The fundamental data structure representing a pitch class set:

```python
from pitch_class_set import PitchClassSet

# Create a set
pcs = PitchClassSet([0, 4, 7])  # C major triad

# Properties
pcs.pitch_classes    # frozenset({0, 4, 7})
pcs.cardinality      # 3
pcs.prime_form       # (0, 3, 7)
pcs.interval_vector  # (0, 0, 1, 1, 1, 0)
pcs.normal_form      # (0, 4, 7)

# Transformations
pcs.transposition(5)  # T5 = F major
pcs.inversion(0)      # I0 = F minor
pcs.complement()      # All pitch classes NOT in the set
```

#### `ForteClassification` (forte_classification.py)

Handles Forte number lookup and set classification:

```python
from forte_classification import ForteClassification

forte = ForteClassification()
forte.get_forte_number(pcs)  # "3-11"
forte.get_set_by_forte("3-11")  # Returns PitchClassSet
forte.get_all_sets_of_cardinality(3)  # All trichords
```

### GUI Architecture

The application follows a **Model-View-Controller** pattern:

1. **Model:** `PitchClassSet`, `ForteClassification`
2. **View:** PyQt6 widgets in `gui/widgets/` and `gui/panels/`
3. **Controller:** `AnalysisMainWindow` coordinates everything

### Signal Flow

```
User Input → SetInputPanel → PitchClassSet created
                                    ↓
                            AnalysisMainWindow._on_set_changed()
                                    ↓
            ┌───────────────────────┼───────────────────────┐
            ↓                       ↓                       ↓
    VisualizationCanvas     AnalysisPanel          TransformationPanel
    (update clock/graph)    (update analysis)      (generate previews)
```

---

## Troubleshooting

### "No module named 'PyQt6'"

Install PyQt6:
```bash
pip install PyQt6
```

### "Audio not working"

1. Check FluidSynth is installed
2. Verify soundfont exists at `gui/resources/soundfonts/GeneralUser_GS.sf2`
3. Check Audio menu → Audio Settings

### "Visualization not showing"

Install matplotlib:
```bash
pip install matplotlib numpy
```

### Application crashes on startup

Check Python version (requires 3.9+):
```bash
python --version
```

### MIDI export fails

Install midiutil:
```bash
pip install midiutil
```

---

## Credits

- **Allen Forte** - Developed pitch class set theory
- **PyQt6** - GUI framework
- **FluidSynth** - Audio synthesis
- **GeneralUser GS** - Soundfont by S. Christian Collins

---

## License

This software is provided for educational and research purposes in music theory.
