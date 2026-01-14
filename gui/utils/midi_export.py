"""
MIDI Export Utilities
Export pitch class sets and transformations to MIDI files using music21
"""

import os
from typing import List, Optional
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet

try:
    from music21 import stream, note, tempo, instrument
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False
    print("Warning: music21 not available. Install with: pip install music21")


class MIDIExporter:
    """Handles MIDI file export for pitch class sets"""

    def __init__(self, octave=4, bpm=120, duration=1.0):
        """
        Initialize MIDI exporter

        Args:
            octave: Base octave for playback (0-8)
            bpm: Tempo in beats per minute
            duration: Note duration in quarter note lengths
        """
        if not MUSIC21_AVAILABLE:
            raise ImportError("music21 is required for MIDI export")

        self.octave = octave
        self.bpm = bpm
        self.duration = duration

    def export_set_to_midi(self, pcs: PitchClassSet, filename: str,
                           arpeggiate: bool = True) -> bool:
        """
        Export a single pitch class set to MIDI

        Args:
            pcs: PitchClassSet to export
            filename: Output filename
            arpeggiate: If True, play notes sequentially; if False, as chord

        Returns:
            True if successful, False otherwise
        """
        try:
            s = stream.Stream()

            # Set tempo
            s.append(tempo.MetronomeMark(number=self.bpm))

            # Set instrument (piano)
            s.append(instrument.Piano())

            # Convert pitch classes to MIDI note numbers
            midi_notes = [(self.octave * 12) + pc for pc in sorted(pcs.pitch_classes)]

            if arpeggiate:
                # Sequential notes
                for midi_num in midi_notes:
                    n = note.Note(midi_num)
                    n.quarterLength = self.duration
                    s.append(n)
            else:
                # Chord
                chord_notes = [note.Note(midi_num) for midi_num in midi_notes]
                c = stream.Chord(chord_notes)
                c.quarterLength = self.duration * 2
                s.append(c)

            # Write MIDI file
            s.write('midi', fp=filename)
            return True

        except Exception as e:
            print(f"Error exporting MIDI: {e}")
            return False

    def export_all_transpositions(self, pcs: PitchClassSet, filename: str,
                                   arpeggiate: bool = True) -> bool:
        """
        Export all 12 transpositions to a multi-track MIDI file

        Args:
            pcs: Original pitch class set
            filename: Output filename
            arpeggiate: If True, arpeggiate notes; if False, play as chords

        Returns:
            True if successful, False otherwise
        """
        try:
            score = stream.Score()

            # Set tempo
            score.append(tempo.MetronomeMark(number=self.bpm))

            # Create a part for each transposition
            for i in range(12):
                part = stream.Part()
                part.partName = f"T{i}"

                # Set instrument (piano)
                part.append(instrument.Piano())

                # Get transposed set
                transposed = pcs.transposition(i)
                midi_notes = [(self.octave * 12) + pc for pc in sorted(transposed.pitch_classes)]

                if arpeggiate:
                    for midi_num in midi_notes:
                        n = note.Note(midi_num)
                        n.quarterLength = self.duration
                        part.append(n)
                else:
                    chord_notes = [note.Note(midi_num) for midi_num in midi_notes]
                    c = stream.Chord(chord_notes)
                    c.quarterLength = self.duration * 2
                    part.append(c)

                score.append(part)

            # Write MIDI file
            score.write('midi', fp=filename)
            return True

        except Exception as e:
            print(f"Error exporting all transpositions: {e}")
            return False

    def export_all_inversions(self, pcs: PitchClassSet, filename: str,
                              arpeggiate: bool = True) -> bool:
        """
        Export all 12 inversions to a multi-track MIDI file

        Args:
            pcs: Original pitch class set
            filename: Output filename
            arpeggiate: If True, arpeggiate notes; if False, play as chords

        Returns:
            True if successful, False otherwise
        """
        try:
            score = stream.Score()
            score.append(tempo.MetronomeMark(number=self.bpm))

            for i in range(12):
                part = stream.Part()
                part.partName = f"I{i}"
                part.append(instrument.Piano())

                inverted = pcs.inversion(i)
                midi_notes = [(self.octave * 12) + pc for pc in sorted(inverted.pitch_classes)]

                if arpeggiate:
                    for midi_num in midi_notes:
                        n = note.Note(midi_num)
                        n.quarterLength = self.duration
                        part.append(n)
                else:
                    chord_notes = [note.Note(midi_num) for midi_num in midi_notes]
                    c = stream.Chord(chord_notes)
                    c.quarterLength = self.duration * 2
                    part.append(c)

                score.append(part)

            score.write('midi', fp=filename)
            return True

        except Exception as e:
            print(f"Error exporting all inversions: {e}")
            return False

    def export_all_retrogrades(self, pcs: PitchClassSet, filename: str,
                               arpeggiate: bool = True) -> bool:
        """
        Export all 12 retrogrades to a multi-track MIDI file

        Args:
            pcs: Original pitch class set
            filename: Output filename
            arpeggiate: If True, arpeggiate notes; if False, play as chords

        Returns:
            True if successful, False otherwise
        """
        try:
            score = stream.Score()
            score.append(tempo.MetronomeMark(number=self.bpm))

            for i in range(12):
                part = stream.Part()
                part.partName = f"RT{i}"
                part.append(instrument.Piano())

                retrograded = pcs.retrograde().transposition(i)
                midi_notes = [(self.octave * 12) + pc for pc in sorted(retrograded.pitch_classes)]

                if arpeggiate:
                    for midi_num in midi_notes:
                        n = note.Note(midi_num)
                        n.quarterLength = self.duration
                        part.append(n)
                else:
                    chord_notes = [note.Note(midi_num) for midi_num in midi_notes]
                    c = stream.Chord(chord_notes)
                    c.quarterLength = self.duration * 2
                    part.append(c)

                score.append(part)

            score.write('midi', fp=filename)
            return True

        except Exception as e:
            print(f"Error exporting all retrogrades: {e}")
            return False

    def export_all_retrograde_inversions(self, pcs: PitchClassSet, filename: str,
                                          arpeggiate: bool = True) -> bool:
        """
        Export all 12 retrograde inversions to a multi-track MIDI file

        Args:
            pcs: Original pitch class set
            filename: Output filename
            arpeggiate: If True, arpeggiate notes; if False, play as chords

        Returns:
            True if successful, False otherwise
        """
        try:
            score = stream.Score()
            score.append(tempo.MetronomeMark(number=self.bpm))

            for i in range(12):
                part = stream.Part()
                part.partName = f"RI{i}"
                part.append(instrument.Piano())

                ri = pcs.retrograde_inversion(i)
                midi_notes = [(self.octave * 12) + pc for pc in sorted(ri.pitch_classes)]

                if arpeggiate:
                    for midi_num in midi_notes:
                        n = note.Note(midi_num)
                        n.quarterLength = self.duration
                        part.append(n)
                else:
                    chord_notes = [note.Note(midi_num) for midi_num in midi_notes]
                    c = stream.Chord(chord_notes)
                    c.quarterLength = self.duration * 2
                    part.append(c)

                score.append(part)

            score.write('midi', fp=filename)
            return True

        except Exception as e:
            print(f"Error exporting all retrograde inversions: {e}")
            return False


# Test function
if __name__ == "__main__":
    print("Testing MIDI Export...")

    if not MUSIC21_AVAILABLE:
        print("music21 not available. Install with: pip install music21")
        sys.exit(1)

    # Test with C major triad
    test_set = PitchClassSet([0, 4, 7])
    exporter = MIDIExporter(octave=4, bpm=120, duration=0.5)

    print("\nExporting all transpositions...")
    success = exporter.export_all_transpositions(test_set, "test_transpositions.mid", arpeggiate=True)
    print(f"Success: {success}")

    print("\nExporting all inversions...")
    success = exporter.export_all_inversions(test_set, "test_inversions.mid", arpeggiate=True)
    print(f"Success: {success}")

    print("\nTest complete!")
