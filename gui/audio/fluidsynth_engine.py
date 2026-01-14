"""
FluidSynth Audio Engine for Set Theory Application
Cross-platform MIDI synthesis using FluidSynth

This module provides real-time audio synthesis to replace the GarageBand dependency.
Uses QThread worker pattern to prevent GUI blocking.
"""

import os
import sys
import time
from typing import List, Optional
from pathlib import Path

try:
    from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("Warning: PyQt6 not installed. Audio engine disabled.")

try:
    # Try importing pyfluidsynth
    # Handle conflict where old 'fluidsynth' package (0.2) shadows pyfluidsynth
    import importlib.util
    import sys

    fluidsynth = None

    # First try normal import
    try:
        import fluidsynth as _fs
        if hasattr(_fs, 'Synth'):
            fluidsynth = _fs
    except:
        pass

    # If that didn't work, try to find pyfluidsynth's fluidsynth.py directly
    if fluidsynth is None:
        for site_packages in sys.path:
            if 'site-packages' in site_packages:
                fs_file = os.path.join(site_packages, 'fluidsynth.py')
                if os.path.exists(fs_file):
                    spec = importlib.util.spec_from_file_location("fluidsynth_pyfs", fs_file)
                    if spec and spec.loader:
                        fluidsynth = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(fluidsynth)
                        if hasattr(fluidsynth, 'Synth'):
                            break
                        else:
                            fluidsynth = None

    if fluidsynth is None or not hasattr(fluidsynth, 'Synth'):
        raise ImportError("pyfluidsynth not found or wrong package installed")

    FLUIDSYNTH_AVAILABLE = True
except (ImportError, SyntaxError, Exception) as e:
    FLUIDSYNTH_AVAILABLE = False
    print(f"Warning: pyfluidsynth not available ({type(e).__name__}: {e}). Falling back to python-rtmidi.")
    if isinstance(e, SyntaxError):
        print("Note: pyfluidsynth 1.3.4 is incompatible with Python 3.13. Use Python 3.11 or 3.12.")

try:
    import rtmidi
    from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False
    print("Warning: python-rtmidi not installed. Audio engine disabled.")
    print("Install with: pip install python-rtmidi")

try:
    import mido
    import io
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("Warning: mido not installed. MIDI file playback disabled.")
    print("Install with: pip install mido")


class AudioSettings:
    """Configuration for audio playback"""

    def __init__(self):
        self.octave = 4              # Default octave (0-8)
        self.tempo = 120             # BPM (1-300)
        self.duration = 0.5          # Note duration in seconds
        self.velocity = 80           # MIDI velocity (0-127)
        self.sample_rate = 44100     # Audio sample rate
        self.buffer_size = 512       # Audio buffer size
        self.soundfont_path = None   # Path to soundfont file

    def to_dict(self):
        """Convert to dictionary for QSettings"""
        return {
            'octave': self.octave,
            'tempo': self.tempo,
            'duration': self.duration,
            'velocity': self.velocity,
            'sample_rate': self.sample_rate,
            'buffer_size': self.buffer_size,
            'soundfont_path': self.soundfont_path
        }

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary (QSettings)"""
        settings = cls()
        for key, value in data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        return settings


class AudioWorker(QObject if PYQT_AVAILABLE else object):
    """
    FluidSynth worker that runs in a separate thread.
    Handles all audio synthesis operations.
    """

    if PYQT_AVAILABLE:
        playback_started = pyqtSignal()
        playback_finished = pyqtSignal()
        error_occurred = pyqtSignal(str)
        initialization_complete = pyqtSignal(bool)  # True if successful, False if failed

    def __init__(self, settings: AudioSettings):
        if PYQT_AVAILABLE:
            super().__init__()
        self.settings = settings
        self.fs = None  # FluidSynth synthesizer
        self.sfid = None  # SoundFont ID
        self.is_initialized = False
        self.is_playing = False

    @pyqtSlot() if PYQT_AVAILABLE else lambda x: x
    def initialize(self):
        """Initialize FluidSynth synthesizer"""
        if not FLUIDSYNTH_AVAILABLE:
            error_msg = "FluidSynth not available. Install with: pip install pyfluidsynth"
            print(f"Audio Error: {error_msg}")
            if PYQT_AVAILABLE:
                self.error_occurred.emit(error_msg)
                self.initialization_complete.emit(False)
            return False

        try:
            print("Initializing FluidSynth audio engine...")

            # Create FluidSynth instance
            self.fs = fluidsynth.Synth(
                samplerate=float(self.settings.sample_rate),
                gain=0.8  # Master volume (0.0 - 1.0)
            )
            print(f"  Created synthesizer (sample rate: {self.settings.sample_rate})")

            # Start audio driver
            driver = 'dsound' if sys.platform == 'win32' else 'coreaudio' if sys.platform == 'darwin' else 'alsa'
            print(f"  Starting audio driver: {driver}")
            self.fs.start(driver=driver)
            print("  Audio driver started successfully")

            # Load soundfont
            soundfont_path = self.settings.soundfont_path
            if not soundfont_path or not os.path.exists(soundfont_path):
                # Try to find default soundfont
                soundfont_path = self._find_default_soundfont()
                print(f"  Using default soundfont: {soundfont_path}")
            else:
                print(f"  Using configured soundfont: {soundfont_path}")

            if soundfont_path and os.path.exists(soundfont_path):
                print(f"  Loading soundfont...")
                self.sfid = self.fs.sfload(soundfont_path)
                if self.sfid >= 0:
                    self.fs.program_select(0, self.sfid, 0, 0)  # Channel 0, bank 0, preset 0 (piano)
                    self.is_initialized = True
                    print("  FluidSynth initialization complete!")
                    if PYQT_AVAILABLE:
                        self.initialization_complete.emit(True)
                    return True
                else:
                    error_msg = f"Failed to load soundfont: {soundfont_path}"
                    print(f"Audio Error: {error_msg}")
                    if PYQT_AVAILABLE:
                        self.error_occurred.emit(error_msg)
                        self.initialization_complete.emit(False)
                    return False
            else:
                error_msg = f"No soundfont found at: {soundfont_path}"
                print(f"Audio Error: {error_msg}")
                if PYQT_AVAILABLE:
                    self.error_occurred.emit(error_msg)
                    self.initialization_complete.emit(False)
                return False

        except Exception as e:
            error_msg = f"Failed to initialize FluidSynth: {str(e)}"
            print(f"Audio Error: {error_msg}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()
            if PYQT_AVAILABLE:
                self.error_occurred.emit(error_msg)
                self.initialization_complete.emit(False)
            return False

    def _find_default_soundfont(self) -> Optional[str]:
        """Try to find a default soundfont"""
        # Check bundled soundfont
        script_dir = Path(__file__).parent.parent
        bundled_sf = script_dir / "resources" / "soundfonts" / "GeneralUser_GS.sf2"
        if bundled_sf.exists():
            return str(bundled_sf)

        # Check common system locations
        common_paths = [
            "/usr/share/soundfonts/FluidR3_GM.sf2",  # Linux
            "/usr/share/soundfonts/default.sf2",
            "C:\\soundfonts\\FluidR3_GM.sf2",  # Windows
            "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls",  # macOS (DLS)
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def set_soundfont(self, path: str):
        """Load a different soundfont"""
        if not self.fs or not os.path.exists(path):
            return False

        try:
            # Unload previous soundfont if exists
            if self.sfid is not None:
                self.fs.sfunload(self.sfid)

            # Load new soundfont
            self.sfid = self.fs.sfload(path)
            self.fs.program_select(0, self.sfid, 0, 0)  # Piano
            self.settings.soundfont_path = path
            return True
        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"Failed to load soundfont: {str(e)}")
            return False

    @pyqtSlot(list, bool) if PYQT_AVAILABLE else lambda x: x
    def play_pitch_classes(self, pitch_classes: List[int], arpeggiate: bool = False):
        """
        Play a list of pitch classes

        Args:
            pitch_classes: List of pitch classes (0-11)
            arpeggiate: If True, play sequentially; if False, play as chord
        """
        if not self.is_initialized or not self.fs:
            return

        try:
            if PYQT_AVAILABLE:
                self.playback_started.emit()
            self.is_playing = True

            # Convert pitch classes to MIDI note numbers
            midi_notes = [(self.settings.octave * 12) + pc for pc in pitch_classes]

            if arpeggiate:
                # Play notes sequentially
                for note in midi_notes:
                    if not self.is_playing:  # Check if playback was stopped
                        break
                    self.fs.noteon(0, note, self.settings.velocity)
                    time.sleep(self.settings.duration)
                    self.fs.noteoff(0, note)
                    time.sleep(0.05)  # Small gap between notes
            else:
                # Play as chord
                for note in midi_notes:
                    self.fs.noteon(0, note, self.settings.velocity)

                time.sleep(self.settings.duration)

                for note in midi_notes:
                    self.fs.noteoff(0, note)

        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"Playback error: {str(e)}")
        finally:
            self.is_playing = False
            if PYQT_AVAILABLE:
                self.playback_finished.emit()

    @pyqtSlot(bytes) if PYQT_AVAILABLE else lambda x: x
    def play_midi_data(self, midi_bytes: bytes):
        """
        Play MIDI file data

        Args:
            midi_bytes: MIDI file data as bytes
        """
        if not self.is_initialized or not self.fs:
            return

        if not MIDO_AVAILABLE:
            if PYQT_AVAILABLE:
                self.error_occurred.emit("mido library not available for MIDI playback")
            return

        try:
            if PYQT_AVAILABLE:
                self.playback_started.emit()
            self.is_playing = True

            # Parse MIDI file
            midi_file = mido.MidiFile(file=io.BytesIO(midi_bytes))

            # Play all messages
            for msg in midi_file.play():
                if not self.is_playing:  # Check if playback was stopped
                    break

                if msg.type == 'note_on' and msg.velocity > 0:
                    self.fs.noteon(msg.channel, msg.note, msg.velocity)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    self.fs.noteoff(msg.channel, msg.note)
                elif msg.type == 'program_change':
                    # Select instrument for this channel (bank 0)
                    self.fs.program_select(msg.channel, self.sfid, 0, msg.program)
                elif msg.type == 'control_change':
                    self.fs.cc(msg.channel, msg.control, msg.value)

        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"MIDI playback error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Turn off all notes on all channels
            if self.fs:
                for channel in range(16):
                    for note in range(128):
                        self.fs.noteoff(channel, note)
            self.is_playing = False
            if PYQT_AVAILABLE:
                self.playback_finished.emit()

    def stop_playback(self):
        """Stop current playback immediately"""
        self.is_playing = False
        if self.fs:
            # Turn off all notes on all channels (MIDI has 16 channels)
            for channel in range(16):
                for note in range(128):
                    self.fs.noteoff(channel, note)

    def cleanup(self):
        """Clean up FluidSynth resources"""
        if self.fs:
            self.stop_playback()
            if self.sfid is not None:
                self.fs.sfunload(self.sfid)
            self.fs.delete()
            self.fs = None
        self.is_initialized = False


class RTMidiWorker(QObject if PYQT_AVAILABLE else object):
    """
    python-rtmidi worker that runs in a separate thread.
    Fallback audio engine when FluidSynth is unavailable.
    """

    if PYQT_AVAILABLE:
        playback_started = pyqtSignal()
        playback_finished = pyqtSignal()
        error_occurred = pyqtSignal(str)
        initialization_complete = pyqtSignal(bool)

    def __init__(self, settings: AudioSettings):
        if PYQT_AVAILABLE:
            super().__init__()
        self.settings = settings
        self.midi_out = None
        self.is_initialized = False
        self.is_playing = False

    @pyqtSlot() if PYQT_AVAILABLE else lambda x: x
    def initialize(self):
        """Initialize python-rtmidi MIDI output"""
        if not RTMIDI_AVAILABLE:
            error_msg = "python-rtmidi not available. Install with: pip install python-rtmidi"
            print(f"Audio Error: {error_msg}")
            if PYQT_AVAILABLE:
                self.error_occurred.emit(error_msg)
                self.initialization_complete.emit(False)
            return False

        try:
            print("Initializing python-rtmidi audio engine...")

            # Create MIDI output
            self.midi_out = rtmidi.MidiOut()

            # Get available ports
            available_ports = self.midi_out.get_ports()
            print(f"  Available MIDI ports: {available_ports}")

            # Try to open a port
            if available_ports:
                # Use first available port
                self.midi_out.open_port(0)
                print(f"  Opened MIDI port: {available_ports[0]}")
            else:
                # Create virtual port
                self.midi_out.open_virtual_port("SetTheory Audio")
                print("  Created virtual MIDI port: SetTheory Audio")

            # Set program to Acoustic Grand Piano (program 0)
            program_change = [0xC0, 0]  # Program Change on channel 0
            self.midi_out.send_message(program_change)

            self.is_initialized = True
            print("  python-rtmidi initialization complete!")
            if PYQT_AVAILABLE:
                self.initialization_complete.emit(True)
            return True

        except Exception as e:
            error_msg = f"Failed to initialize python-rtmidi: {str(e)}"
            print(f"Audio Error: {error_msg}")
            import traceback
            traceback.print_exc()
            if PYQT_AVAILABLE:
                self.error_occurred.emit(error_msg)
                self.initialization_complete.emit(False)
            return False

    @pyqtSlot(list, bool) if PYQT_AVAILABLE else lambda x: x
    def play_pitch_classes(self, pitch_classes: List[int], arpeggiate: bool = False):
        """
        Play a list of pitch classes using MIDI

        Args:
            pitch_classes: List of pitch classes (0-11)
            arpeggiate: If True, play sequentially; if False, play as chord
        """
        if not self.is_initialized or not self.midi_out:
            return

        try:
            if PYQT_AVAILABLE:
                self.playback_started.emit()
            self.is_playing = True

            # Convert pitch classes to MIDI note numbers
            midi_notes = [(self.settings.octave * 12) + pc for pc in pitch_classes]

            if arpeggiate:
                # Play notes sequentially
                for note in midi_notes:
                    if not self.is_playing:
                        break
                    # Note On
                    note_on = [NOTE_ON, note, self.settings.velocity]
                    self.midi_out.send_message(note_on)
                    time.sleep(self.settings.duration)
                    # Note Off
                    note_off = [NOTE_OFF, note, 0]
                    self.midi_out.send_message(note_off)
                    time.sleep(0.05)  # Small gap between notes
            else:
                # Play as chord
                for note in midi_notes:
                    note_on = [NOTE_ON, note, self.settings.velocity]
                    self.midi_out.send_message(note_on)

                time.sleep(self.settings.duration)

                for note in midi_notes:
                    note_off = [NOTE_OFF, note, 0]
                    self.midi_out.send_message(note_off)

        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"Playback error: {str(e)}")
        finally:
            self.is_playing = False
            if PYQT_AVAILABLE:
                self.playback_finished.emit()

    @pyqtSlot(bytes) if PYQT_AVAILABLE else lambda x: x
    def play_midi_data(self, midi_bytes: bytes):
        """
        Play MIDI file data using RTMidi

        Args:
            midi_bytes: MIDI file data as bytes
        """
        if not self.is_initialized or not self.midi_out:
            return

        if not MIDO_AVAILABLE:
            if PYQT_AVAILABLE:
                self.error_occurred.emit("mido library not available for MIDI playback")
            return

        try:
            if PYQT_AVAILABLE:
                self.playback_started.emit()
            self.is_playing = True

            # Parse MIDI file
            midi_file = mido.MidiFile(file=io.BytesIO(midi_bytes))

            # Play all messages
            for msg in midi_file.play():
                if not self.is_playing:  # Check if playback was stopped
                    break

                if msg.type == 'note_on' and msg.velocity > 0:
                    note_on = [NOTE_ON, msg.note, msg.velocity]
                    self.midi_out.send_message(note_on)
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    note_off = [NOTE_OFF, msg.note, 0]
                    self.midi_out.send_message(note_off)
                # Handle other MIDI messages if needed

        except Exception as e:
            if PYQT_AVAILABLE:
                self.error_occurred.emit(f"MIDI playback error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            # Turn off all notes
            if self.midi_out:
                for note in range(128):
                    note_off = [NOTE_OFF, note, 0]
                    self.midi_out.send_message(note_off)
            self.is_playing = False
            if PYQT_AVAILABLE:
                self.playback_finished.emit()

    def stop_playback(self):
        """Stop current playback immediately"""
        self.is_playing = False
        if self.midi_out:
            # Send All Notes Off message
            for note in range(128):
                note_off = [NOTE_OFF, note, 0]
                self.midi_out.send_message(note_off)

    def cleanup(self):
        """Clean up python-rtmidi resources"""
        if self.midi_out:
            self.stop_playback()
            self.midi_out.close_port()
            del self.midi_out
            self.midi_out = None
        self.is_initialized = False


class FluidSynthEngine(QObject if PYQT_AVAILABLE else object):
    """
    Main FluidSynth engine interface.
    Manages audio worker thread and provides high-level API.
    """

    if PYQT_AVAILABLE:
        playback_started = pyqtSignal()
        playback_finished = pyqtSignal()
        error_occurred = pyqtSignal(str)
        play_request = pyqtSignal(list, bool)  # Signal to request playback
        play_midi_request = pyqtSignal(bytes)  # Signal to request MIDI file playback

    def __init__(self, settings: Optional[AudioSettings] = None):
        if PYQT_AVAILABLE:
            super().__init__()

        self.settings = settings or AudioSettings()
        self.worker = None
        self.thread = None
        self.engine_type = None  # 'fluidsynth' or 'rtmidi'
        self.is_available = (FLUIDSYNTH_AVAILABLE or RTMIDI_AVAILABLE) and PYQT_AVAILABLE
        self.is_initialized = False

        if self.is_available:
            self._setup_worker()

    def _setup_worker(self):
        """Setup worker thread for audio playback"""
        if not PYQT_AVAILABLE:
            return

        # Try FluidSynth first, then fall back to RTMidi
        if FLUIDSYNTH_AVAILABLE:
            print("Attempting to use FluidSynth audio engine...")
            self.engine_type = 'fluidsynth'
            self.worker = AudioWorker(self.settings)
        elif RTMIDI_AVAILABLE:
            print("FluidSynth not available, using python-rtmidi fallback...")
            self.engine_type = 'rtmidi'
            self.worker = RTMidiWorker(self.settings)
        else:
            print("No audio engine available!")
            return

        # Create thread
        self.thread = QThread()

        # Move worker to thread
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.playback_started.connect(self.playback_started)
        self.worker.playback_finished.connect(self.playback_finished)
        self.worker.error_occurred.connect(self.error_occurred)
        self.worker.initialization_complete.connect(self._on_initialization_complete)

        # Connect play request signals to worker methods
        self.play_request.connect(self.worker.play_pitch_classes)
        self.play_midi_request.connect(self.worker.play_midi_data)

        # Start thread and initialize
        self.thread.started.connect(self.worker.initialize)
        self.thread.start()

        # Wait a bit for initialization
        time.sleep(1.0)

    def _on_initialization_complete(self, success: bool):
        """Handle initialization completion"""
        print(f"[DEBUG] _on_initialization_complete called: success={success}, engine_type={self.engine_type}", flush=True)
        self.is_initialized = success
        if success:
            engine_name = "FluidSynth" if self.engine_type == 'fluidsynth' else "python-rtmidi"
            print(f"Audio engine ready! Using: {engine_name}", flush=True)
        else:
            print(f"Audio engine initialization failed ({self.engine_type})", flush=True)
            # If FluidSynth failed, try RTMidi as fallback
            if self.engine_type == 'fluidsynth' and RTMIDI_AVAILABLE:
                print("Attempting fallback to python-rtmidi...", flush=True)
                self._try_rtmidi_fallback()

    def _try_rtmidi_fallback(self):
        """Try to fall back to RTMidi if FluidSynth fails"""
        if not RTMIDI_AVAILABLE:
            return

        # Clean up failed FluidSynth worker
        if self.worker:
            self.worker.cleanup()
        if self.thread:
            self.thread.quit()
            self.thread.wait()

        # Setup RTMidi worker
        print("Setting up python-rtmidi fallback...")
        self.engine_type = 'rtmidi'
        self.worker = RTMidiWorker(self.settings)
        self.thread = QThread()

        # Move worker to thread
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.worker.playback_started.connect(self.playback_started)
        self.worker.playback_finished.connect(self.playback_finished)
        self.worker.error_occurred.connect(self.error_occurred)
        self.worker.initialization_complete.connect(self._on_initialization_complete)

        # Connect play request signals
        self.play_request.connect(self.worker.play_pitch_classes)
        self.play_midi_request.connect(self.worker.play_midi_data)

        # Start thread and initialize
        self.thread.started.connect(self.worker.initialize)
        self.thread.start()

    def play_pitch_classes(self, pitch_classes: List[int], arpeggiate: bool = False):
        """
        Play pitch classes

        Args:
            pitch_classes: List of pitch classes (0-11)
            arpeggiate: If True, play sequentially; if False, play as chord
        """
        if not self.is_available or not self.worker or not self.is_initialized:
            if PYQT_AVAILABLE:
                error_msg = "Audio engine not initialized" if not self.is_initialized else "Audio engine not available"
                self.error_occurred.emit(error_msg)
            return

        # Emit signal to play in worker thread (thread-safe)
        self.play_request.emit(pitch_classes, arpeggiate)

    def play_midi_data(self, midi_bytes: bytes):
        """
        Play MIDI file data

        Args:
            midi_bytes: MIDI file data as bytes
        """
        if not self.is_available or not self.worker or not self.is_initialized:
            if PYQT_AVAILABLE:
                error_msg = "Audio engine not initialized" if not self.is_initialized else "Audio engine not available"
                self.error_occurred.emit(error_msg)
            return

        # Emit signal to play MIDI in worker thread (thread-safe)
        self.play_midi_request.emit(midi_bytes)

    def stop(self):
        """Stop current playback"""
        if self.worker:
            self.worker.stop_playback()

    def set_soundfont(self, path: str):
        """Change soundfont (FluidSynth only)"""
        if self.worker and self.engine_type == 'fluidsynth':
            return self.worker.set_soundfont(path)
        return False

    def update_settings(self, settings: AudioSettings):
        """Update audio settings"""
        self.settings = settings
        if self.worker:
            self.worker.settings = settings

    def cleanup(self):
        """Clean up resources"""
        if self.worker:
            self.worker.cleanup()
        if self.thread:
            self.thread.quit()
            self.thread.wait()

    def __del__(self):
        """Destructor"""
        self.cleanup()


def test_audio_engine():
    """Test function for audio engine"""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    print("Testing FluidSynth Audio Engine...")
    print(f"FluidSynth available: {FLUIDSYNTH_AVAILABLE}")

    if not FLUIDSYNTH_AVAILABLE:
        print("Please install pyfluidsynth: pip install pyfluidsynth")
        return

    # Create engine
    settings = AudioSettings()
    engine = FluidSynthEngine(settings)

    # Connect signals
    engine.error_occurred.connect(lambda msg: print(f"Error: {msg}"))
    engine.playback_started.connect(lambda: print("Playback started"))
    engine.playback_finished.connect(lambda: print("Playback finished"))

    # Wait for initialization
    time.sleep(1)

    if not engine.is_available:
        print("Audio engine not available")
        return

    print("\nPlaying C major triad (chord)...")
    engine.play_pitch_classes([0, 4, 7], arpeggiate=False)
    time.sleep(2)

    print("\nPlaying C major triad (arpeggiated)...")
    engine.play_pitch_classes([0, 4, 7], arpeggiate=True)
    time.sleep(3)

    print("\nPlaying chromatic scale...")
    engine.play_pitch_classes(list(range(12)), arpeggiate=True)
    time.sleep(8)

    print("\nCleaning up...")
    engine.cleanup()
    print("Test complete!")


if __name__ == "__main__":
    test_audio_engine()
