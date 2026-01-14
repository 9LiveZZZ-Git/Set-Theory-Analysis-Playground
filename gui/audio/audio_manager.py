"""
Audio Manager for Set Theory Application
High-level API for audio playback and MIDI export

This module coordinates audio playback using FluidSynth and maintains
compatibility with MIDI file export for DAW users.
"""

import os
import time
from typing import List, Optional
from pathlib import Path

try:
    from PyQt6.QtCore import QObject, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Import our audio engine
from .fluidsynth_engine import FluidSynthEngine, AudioSettings, FLUIDSYNTH_AVAILABLE

# Import core set theory modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet

# Optional: music21 for MIDI export
try:
    from music21 import stream, note, tempo, instrument
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False


class AudioManager(QObject if PYQT_AVAILABLE else object):
    """
    High-level audio playback manager.
    Provides easy-to-use methods for playing sets and transformations.
    """

    if PYQT_AVAILABLE:
        playback_started = pyqtSignal()
        playback_finished = pyqtSignal()
        error_occurred = pyqtSignal(str)

    def __init__(self, settings: Optional[AudioSettings] = None):
        if PYQT_AVAILABLE:
            super().__init__()

        self.settings = settings or AudioSettings()
        self.engine = FluidSynthEngine(self.settings) if FLUIDSYNTH_AVAILABLE else None

        # Connect engine signals if available
        if self.engine and PYQT_AVAILABLE:
            self.engine.playback_started.connect(self.playback_started)
            self.engine.playback_finished.connect(self.playback_finished)
            self.engine.error_occurred.connect(self.error_occurred)

    def is_available(self) -> bool:
        """Check if audio engine is available"""
        return self.engine is not None and self.engine.is_available

    def play_set(self, pcs: PitchClassSet, arpeggiate: bool = False):
        """
        Play a pitch class set

        Args:
            pcs: PitchClassSet to play
            arpeggiate: If True, play notes sequentially; if False, play as chord
        """
        if not self.is_available():
            if PYQT_AVAILABLE:
                self.error_occurred.emit("Audio engine not available")
            return

        pitch_classes = sorted(pcs.pitch_classes)
        self.engine.play_pitch_classes(pitch_classes, arpeggiate)

    def play_transformation_sequence(self,
                                     original: PitchClassSet,
                                     transformed: PitchClassSet,
                                     delay: float = 0.5,
                                     arpeggiate: bool = True):
        """
        Play original set, then transformed set with delay

        Args:
            original: Original pitch class set
            transformed: Transformed pitch class set
            delay: Delay between sets in seconds
            arpeggiate: If True, play arpeggiated; if False, play as chords
        """
        if not self.is_available():
            if PYQT_AVAILABLE:
                self.error_occurred.emit("Audio engine not available")
            return

        # Play original
        self.play_set(original, arpeggiate)

        # Wait for playback to finish + delay
        duration = len(original.pitch_classes) * self.settings.duration if arpeggiate else self.settings.duration
        time.sleep(duration + delay)

        # Play transformed
        self.play_set(transformed, arpeggiate)

    def play_comparison(self,
                        set1: PitchClassSet,
                        set2: PitchClassSet,
                        delay: float = 0.5,
                        arpeggiate: bool = True):
        """
        Play two sets sequentially for comparison

        Args:
            set1: First pitch class set
            set2: Second pitch class set
            delay: Delay between sets
            arpeggiate: Play style
        """
        self.play_transformation_sequence(set1, set2, delay, arpeggiate)

    def play_midi_data(self, midi_bytes: bytes):
        """
        Play MIDI file data

        Args:
            midi_bytes: MIDI file data as bytes
        """
        if not self.is_available():
            if PYQT_AVAILABLE:
                self.error_occurred.emit("Audio engine not available")
            return

        self.engine.play_midi_data(midi_bytes)

    def stop(self):
        """Stop current playback"""
        if self.engine:
            self.engine.stop()

    def set_soundfont(self, path: str) -> bool:
        """
        Change soundfont

        Args:
            path: Path to soundfont file (.sf2)

        Returns:
            True if successful, False otherwise
        """
        if self.engine:
            success = self.engine.set_soundfont(path)
            if success:
                self.settings.soundfont_path = path
            return success
        return False

    def update_settings(self, settings: AudioSettings):
        """
        Update audio settings

        Args:
            settings: New AudioSettings object
        """
        self.settings = settings
        if self.engine:
            self.engine.update_settings(settings)

    def export_to_midi(self,
                       pcs: PitchClassSet,
                       filename: str,
                       arpeggiate: bool = False) -> bool:
        """
        Export pitch class set to MIDI file (for DAW users)

        Args:
            pcs: PitchClassSet to export
            filename: Output MIDI filename
            arpeggiate: If True, export as sequence; if False, as chord

        Returns:
            True if successful, False otherwise
        """
        if not MUSIC21_AVAILABLE:
            if PYQT_AVAILABLE:
                self.error_occurred.emit("music21 not available for MIDI export")
            return False

        try:
            # Create stream
            s = stream.Stream()

            # Add tempo
            s.append(tempo.MetronomeMark(number=self.settings.tempo))

            # Add instrument
            s.append(instrument.Piano())

            # Convert pitch classes to MIDI note numbers
            midi_notes = [(self.settings.octave * 12) + pc for pc in sorted(pcs.pitch_classes)]

            if arpeggiate:
                # Add notes sequentially
                for midi_note in midi_notes:
                    n = note.Note(midi=midi_note)
                    n.quarterLength = self.settings.duration * (self.settings.tempo / 60)
                    s.append(n)
            else:
                # Add as chord
                from music21 import chord
                c = chord.Chord(midi_notes)
                c.quarterLength = self.settings.duration * (self.settings.tempo / 60)
                s.append(c)

            # Export to MIDI
            s.write('midi', fp=filename)
            return True

        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"MIDI export failed: {str(e)}")
            return False

    def export_transformations_to_midi(self,
                                       pcs: PitchClassSet,
                                       transformation_type: str,
                                       filename: str) -> bool:
        """
        Export all transformations to multi-track MIDI file

        Args:
            pcs: Original pitch class set
            transformation_type: 'transpose', 'invert', 'retrograde', or 'ri'
            filename: Output MIDI filename

        Returns:
            True if successful, False otherwise
        """
        if not MUSIC21_AVAILABLE:
            if PYQT_AVAILABLE:
                self.error_occurred.emit("music21 not available for MIDI export")
            return False

        try:
            from music21 import stream, note, tempo, instrument

            # Create score (multi-track)
            score = stream.Score()

            # Generate transformations
            for i in range(12):
                if transformation_type == 'transpose':
                    transformed = pcs.transposition(i)
                    track_name = f"T{i}"
                elif transformation_type == 'invert':
                    transformed = pcs.inversion(i)
                    track_name = f"I{i}"
                elif transformation_type == 'retrograde':
                    transformed = pcs.transposition(i)  # Apply transposition to retrograde
                    transformed.pitch_classes = list(reversed(transformed.pitch_classes))
                    track_name = f"RT{i}"
                elif transformation_type == 'ri':
                    transformed = pcs.inversion(i)
                    transformed.pitch_classes = list(reversed(transformed.pitch_classes))
                    track_name = f"RI{i}"
                else:
                    continue

                # Create part
                part = stream.Part()
                part.partName = track_name

                # Add instrument
                part.insert(0, instrument.Piano())

                # Add tempo (only to first part)
                if i == 0:
                    part.insert(0, tempo.MetronomeMark(number=self.settings.tempo))

                # Add notes
                offset = i * 2.0  # Stagger tracks
                midi_notes = [(self.settings.octave * 12) + pc for pc in sorted(transformed.pitch_classes)]

                for midi_note in midi_notes:
                    n = note.Note(midi=midi_note)
                    n.quarterLength = 1.0
                    part.insert(offset, n)
                    offset += 0.25  # Arpeggiate

                score.append(part)

            # Export to MIDI
            score.write('midi', fp=filename)
            return True

        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"MIDI export failed: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources"""
        if self.engine:
            self.engine.cleanup()

    def __del__(self):
        """Destructor"""
        self.cleanup()


def test_audio_manager():
    """Test function for audio manager"""
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    print("Testing Audio Manager...")

    # Create manager
    settings = AudioSettings()
    settings.duration = 0.8
    manager = AudioManager(settings)

    if not manager.is_available():
        print("Audio not available")
        return

    # Test playing a set
    print("\nPlaying C major triad...")
    c_major = PitchClassSet([0, 4, 7])
    manager.play_set(c_major, arpeggiate=True)
    time.sleep(3)

    # Test transformation sequence
    print("\nPlaying transposition (T3)...")
    eb_major = c_major.transposition(3)
    manager.play_transformation_sequence(c_major, eb_major, delay=0.5)
    time.sleep(6)

    # Test MIDI export
    if MUSIC21_AVAILABLE:
        print("\nExporting to MIDI...")
        manager.export_to_midi(c_major, "test_export.mid", arpeggiate=True)
        print("Exported to test_export.mid")

    print("\nCleaning up...")
    manager.cleanup()
    print("Test complete!")


if __name__ == "__main__":
    test_audio_manager()
