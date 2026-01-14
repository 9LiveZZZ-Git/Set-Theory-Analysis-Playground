"""
Settings Manager for Set Theory Application
Persistent settings using QSettings (platform-native storage)
"""

try:
    from PyQt6.QtCore import QSettings
    QSETTINGS_AVAILABLE = True
except ImportError:
    QSETTINGS_AVAILABLE = False

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from audio.fluidsynth_engine import AudioSettings


class SettingsManager:
    """
    Manages application settings with persistent storage.
    Uses Qt's QSettings for platform-native storage:
    - Windows: Registry (HKEY_CURRENT_USER\\Software\\SetTheory)
    - macOS: ~/Library/Preferences/com.settheory.SetTheory.plist
    - Linux: ~/.config/SetTheory/settings.conf
    """

    def __init__(self):
        if QSETTINGS_AVAILABLE:
            self.settings = QSettings('SetTheory', 'SetTheoryApp')
        else:
            self.settings = None

        # Default values
        # Get default soundfont path
        default_soundfont = str(Path(__file__).parent.parent / 'resources' / 'soundfonts' / 'GeneralUser_GS.sf2')

        self.defaults = {
            # Audio settings
            'audio/octave': 4,
            'audio/tempo': 120,
            'audio/duration': 0.5,
            'audio/velocity': 80,
            'audio/sample_rate': 44100,
            'audio/buffer_size': 512,
            'audio/soundfont_path': default_soundfont,

            # UI settings
            'ui/theme': 'light',
            'ui/window_width': 1200,
            'ui/window_height': 800,
            'ui/left_panel_width': 300,
            'ui/show_analysis_panel': True,
            'ui/show_transformation_panel': True,
            'ui/visualization_mode': 'clock',  # 'clock' or 'graph'

            # Recent data
            'history/recent_sets': [],  # List of recent pitch class sets
            'history/recent_forte': [],  # List of recent Forte numbers
        }

    def get(self, key: str, default=None):
        """
        Get a setting value

        Args:
            key: Setting key (e.g., 'audio/octave')
            default: Default value if key doesn't exist

        Returns:
            Setting value or default
        """
        if not self.settings:
            return default or self.defaults.get(key)

        # Use default from defaults dict if no custom default provided
        if default is None:
            default = self.defaults.get(key)

        return self.settings.value(key, default)

    def set(self, key: str, value):
        """
        Set a setting value

        Args:
            key: Setting key
            value: Value to store
        """
        if self.settings:
            self.settings.setValue(key, value)

    def get_audio_settings(self) -> AudioSettings:
        """
        Get AudioSettings object from stored settings

        Returns:
            AudioSettings instance
        """
        settings = AudioSettings()
        settings.octave = int(self.get('audio/octave'))
        settings.tempo = int(self.get('audio/tempo'))
        settings.duration = float(self.get('audio/duration'))
        settings.velocity = int(self.get('audio/velocity'))
        settings.sample_rate = int(self.get('audio/sample_rate'))
        settings.buffer_size = int(self.get('audio/buffer_size'))
        settings.soundfont_path = self.get('audio/soundfont_path')
        return settings

    def set_audio_settings(self, settings: AudioSettings):
        """
        Store AudioSettings object

        Args:
            settings: AudioSettings instance to store
        """
        self.set('audio/octave', settings.octave)
        self.set('audio/tempo', settings.tempo)
        self.set('audio/duration', settings.duration)
        self.set('audio/velocity', settings.velocity)
        self.set('audio/sample_rate', settings.sample_rate)
        self.set('audio/buffer_size', settings.buffer_size)
        self.set('audio/soundfont_path', settings.soundfont_path)

    def add_recent_set(self, pitch_classes: list):
        """
        Add a pitch class set to recent history

        Args:
            pitch_classes: List of pitch classes
        """
        recent = self.get('history/recent_sets', [])
        if not isinstance(recent, list):
            recent = []

        # Remove if already exists
        if pitch_classes in recent:
            recent.remove(pitch_classes)

        # Add to front
        recent.insert(0, pitch_classes)

        # Keep only last 10
        recent = recent[:10]

        self.set('history/recent_sets', recent)

    def get_recent_sets(self) -> list:
        """
        Get recent pitch class sets

        Returns:
            List of pitch class lists
        """
        recent = self.get('history/recent_sets', [])
        return recent if isinstance(recent, list) else []

    def add_recent_forte(self, forte_number: str):
        """
        Add a Forte number to recent history

        Args:
            forte_number: Forte number (e.g., '3-11')
        """
        recent = self.get('history/recent_forte', [])
        if not isinstance(recent, list):
            recent = []

        # Remove if already exists
        if forte_number in recent:
            recent.remove(forte_number)

        # Add to front
        recent.insert(0, forte_number)

        # Keep only last 5
        recent = recent[:5]

        self.set('history/recent_forte', recent)

    def get_recent_forte(self) -> list:
        """
        Get recent Forte numbers

        Returns:
            List of Forte number strings
        """
        recent = self.get('history/recent_forte', [])
        return recent if isinstance(recent, list) else []

    def clear_history(self):
        """Clear all history"""
        self.set('history/recent_sets', [])
        self.set('history/recent_forte', [])

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if self.settings:
            self.settings.clear()


def test_settings_manager():
    """Test settings manager"""
    print("Testing Settings Manager...")

    manager = SettingsManager()

    # Test audio settings
    print("\nTesting audio settings...")
    audio_settings = manager.get_audio_settings()
    print(f"  Octave: {audio_settings.octave}")
    print(f"  Tempo: {audio_settings.tempo}")

    # Modify and save
    audio_settings.octave = 5
    audio_settings.tempo = 140
    manager.set_audio_settings(audio_settings)
    print("  Settings saved")

    # Reload and verify
    reloaded = manager.get_audio_settings()
    print(f"  Reloaded octave: {reloaded.octave}")
    print(f"  Reloaded tempo: {reloaded.tempo}")

    # Test recent sets
    print("\nTesting recent sets...")
    manager.add_recent_set([0, 4, 7])
    manager.add_recent_set([0, 3, 7])
    manager.add_recent_set([0, 4, 8])
    recent = manager.get_recent_sets()
    print(f"  Recent sets: {recent}")

    # Test recent Forte numbers
    print("\nTesting recent Forte numbers...")
    manager.add_recent_forte('3-11')
    manager.add_recent_forte('4-9')
    recent_forte = manager.get_recent_forte()
    print(f"  Recent Forte: {recent_forte}")

    print("\nTest complete!")


if __name__ == "__main__":
    test_settings_manager()
