#!/usr/bin/env python3
"""
Set Theory Analysis - Standalone Application
Allen Forte Pitch Class Set Theory Analysis Tool

Usage:
    python run_analysis.py

Requirements:
    - Python 3.9+
    - PyQt6
    - matplotlib
    - numpy
    - midiutil
    - pyfluidsynth (optional, for audio playback)
"""

import sys
from pathlib import Path

# Ensure the project root is in the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.analysis_main_window import launch_analysis_gui

if __name__ == "__main__":
    print("=" * 50)
    print("Set Theory Analysis")
    print("Allen Forte Pitch Class Set Theory Tool")
    print("=" * 50)
    launch_analysis_gui()
