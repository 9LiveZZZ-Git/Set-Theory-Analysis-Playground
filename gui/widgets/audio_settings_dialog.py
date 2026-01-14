"""
Audio Settings Dialog
Configure audio playback parameters
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                              QSpinBox, QDoubleSpinBox, QPushButton, QLabel,
                              QGroupBox, QFileDialog, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from audio.fluidsynth_engine import AudioSettings


class AudioSettingsDialog(QDialog):
    """
    Dialog for configuring audio settings.
    """

    settingsChanged = pyqtSignal(AudioSettings)

    def __init__(self, current_settings: AudioSettings, parent=None):
        super().__init__(parent)

        self.current_settings = current_settings
        self.setWindowTitle("Audio Settings")
        self.resize(450, 400)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Playback settings
        playback_group = QGroupBox("Playback Settings")
        playback_form = QFormLayout()

        # Octave
        self.octave_spin = QSpinBox()
        self.octave_spin.setRange(0, 8)
        self.octave_spin.setSuffix(" (0-8)")
        playback_form.addRow("Octave:", self.octave_spin)

        # Tempo
        self.tempo_spin = QSpinBox()
        self.tempo_spin.setRange(1, 300)
        self.tempo_spin.setSuffix(" BPM")
        playback_form.addRow("Tempo:", self.tempo_spin)

        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 5.0)
        self.duration_spin.setSingleStep(0.1)
        self.duration_spin.setSuffix(" seconds")
        self.duration_spin.setDecimals(1)
        playback_form.addRow("Note Duration:", self.duration_spin)

        # Velocity
        self.velocity_spin = QSpinBox()
        self.velocity_spin.setRange(1, 127)
        self.velocity_spin.setSuffix(" (1-127)")
        playback_form.addRow("Velocity:", self.velocity_spin)

        playback_group.setLayout(playback_form)
        layout.addWidget(playback_group)

        # Audio engine settings
        engine_group = QGroupBox("Audio Engine Settings")
        engine_form = QFormLayout()

        # Sample rate
        self.samplerate_spin = QSpinBox()
        self.samplerate_spin.setRange(22050, 96000)
        self.samplerate_spin.setSingleStep(11025)
        self.samplerate_spin.setSuffix(" Hz")
        engine_form.addRow("Sample Rate:", self.samplerate_spin)

        # Buffer size
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(64, 2048)
        self.buffer_spin.setSingleStep(64)
        self.buffer_spin.setSuffix(" samples")
        engine_form.addRow("Buffer Size:", self.buffer_spin)

        engine_group.setLayout(engine_form)
        layout.addWidget(engine_group)

        # Soundfont settings
        soundfont_group = QGroupBox("SoundFont")
        soundfont_layout = QVBoxLayout()

        # Soundfont path
        sf_path_layout = QHBoxLayout()
        self.soundfont_path = QLineEdit()
        self.soundfont_path.setPlaceholderText("Path to .sf2 file (optional)")
        sf_path_layout.addWidget(self.soundfont_path)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_soundfont)
        sf_path_layout.addWidget(browse_button)

        soundfont_layout.addLayout(sf_path_layout)

        # Info label
        sf_info = QLabel("Leave empty to use default system soundfont.\n"
                        "For best quality, download GeneralUser GS soundfont.")
        sf_info.setStyleSheet("color: gray; font-size: 9pt;")
        sf_info.setWordWrap(True)
        soundfont_layout.addWidget(sf_info)

        soundfont_group.setLayout(soundfont_layout)
        layout.addWidget(soundfont_group)

        # Test button
        self.test_button = QPushButton("🎵 Test Audio")
        self.test_button.clicked.connect(self._test_audio)
        layout.addWidget(self.test_button)

        # Note
        note_label = QLabel("<b>Note:</b> Changes to sample rate and buffer size "
                           "require restarting the audio engine.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #666;")
        layout.addWidget(note_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_button)

        button_layout.addStretch()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self._ok_clicked)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_settings(self):
        """Load current settings into widgets"""
        self.octave_spin.setValue(self.current_settings.octave)
        self.tempo_spin.setValue(self.current_settings.tempo)
        self.duration_spin.setValue(self.current_settings.duration)
        self.velocity_spin.setValue(self.current_settings.velocity)
        self.samplerate_spin.setValue(self.current_settings.sample_rate)
        self.buffer_spin.setValue(self.current_settings.buffer_size)

        if self.current_settings.soundfont_path:
            self.soundfont_path.setText(self.current_settings.soundfont_path)

    def _get_settings(self) -> AudioSettings:
        """Get settings from widgets"""
        settings = AudioSettings()
        settings.octave = self.octave_spin.value()
        settings.tempo = self.tempo_spin.value()
        settings.duration = self.duration_spin.value()
        settings.velocity = self.velocity_spin.value()
        settings.sample_rate = self.samplerate_spin.value()
        settings.buffer_size = self.buffer_spin.value()

        sf_path = self.soundfont_path.text().strip()
        if sf_path:
            settings.soundfont_path = sf_path

        return settings

    def _browse_soundfont(self):
        """Browse for soundfont file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select SoundFont",
            "",
            "SoundFont Files (*.sf2);;All Files (*.*)"
        )

        if filename:
            self.soundfont_path.setText(filename)

    def _test_audio(self):
        """Test audio with current settings"""
        settings = self._get_settings()

        # Create temporary audio manager and play C major triad
        try:
            from gui.audio.audio_manager import AudioManager
            from pitch_class_set import PitchClassSet

            test_manager = AudioManager(settings)
            if test_manager.is_available():
                test_set = PitchClassSet([0, 4, 7])  # C major
                test_manager.play_set(test_set, arpeggiate=True)
                QMessageBox.information(self, "Test Audio",
                                       "Playing C major triad (arpeggio)...")
            else:
                QMessageBox.warning(self, "Test Audio",
                                   "Audio engine not available.\n"
                                   "FluidSynth may not be installed.")
        except Exception as e:
            QMessageBox.warning(self, "Test Audio Error", str(e))

    def _reset_defaults(self):
        """Reset to default settings"""
        defaults = AudioSettings()
        self.current_settings = defaults
        self._load_settings()

    def _apply_settings(self):
        """Apply settings without closing"""
        settings = self._get_settings()
        self.current_settings = settings
        self.settingsChanged.emit(settings)

    def _ok_clicked(self):
        """OK button clicked"""
        self._apply_settings()
        self.accept()

    def get_settings(self) -> AudioSettings:
        """Get the configured settings"""
        return self.current_settings


# Test dialog
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test with default settings
    settings = AudioSettings()
    dialog = AudioSettingsDialog(settings)

    dialog.settingsChanged.connect(
        lambda s: print(f"Settings changed: octave={s.octave}, tempo={s.tempo}")
    )

    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        final_settings = dialog.get_settings()
        print(f"Final settings: {final_settings.to_dict()}")

    sys.exit(0)
