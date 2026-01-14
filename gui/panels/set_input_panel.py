"""
Set Input Panel
Left panel for pitch class set input and transformations
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                              QLabel, QSpinBox, QPushButton, QComboBox,
                              QListWidget, QListWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet

# Import custom widgets
sys.path.insert(0, str(Path(__file__).parent.parent))
from widgets.pitch_class_input import PitchClassInput


class SetInputPanel(QWidget):
    """
    Left panel containing:
    - Pitch class input field
    - Recent sets list
    - Transformation controls (T, I, R)
    - Quick action buttons
    """

    # Signals
    setChanged = pyqtSignal(PitchClassSet)  # Emitted when set changes
    transformationRequested = pyqtSignal(str, int)  # (type, value) - e.g., ('T', 3)
    playRequested = pyqtSignal(bool)  # arpeggiate
    visualizeRequested = pyqtSignal()
    analyzeRequested = pyqtSignal()
    forteDirectoryRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_set = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # === INPUT SECTION ===
        input_group = QGroupBox("Pitch Class Set")
        input_layout = QVBoxLayout()

        # Input field
        input_label = QLabel("Enter pitch classes:")
        input_layout.addWidget(input_label)

        self.input_field = PitchClassInput()
        input_layout.addWidget(self.input_field)

        # Format hint
        hint_label = QLabel("Formats: 0 1 3 6, [0,1,3,6], or 3-11")
        hint_label.setStyleSheet("color: gray; font-size: 9pt;")
        input_layout.addWidget(hint_label)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # === RECENT SETS ===
        recent_group = QGroupBox("Recent Sets")
        recent_layout = QVBoxLayout()

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(100)
        recent_layout.addWidget(self.recent_list)

        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)

        # === TRANSFORMATIONS ===
        transform_group = QGroupBox("Transformations")
        transform_layout = QVBoxLayout()

        # Transposition
        t_layout = QHBoxLayout()
        t_layout.addWidget(QLabel("T:"))
        self.t_spinbox = QSpinBox()
        self.t_spinbox.setRange(0, 11)
        self.t_spinbox.setValue(0)
        t_layout.addWidget(self.t_spinbox)
        self.t_button = QPushButton("Apply")
        self.t_button.setEnabled(False)
        t_layout.addWidget(self.t_button)
        transform_layout.addLayout(t_layout)

        # Inversion
        i_layout = QHBoxLayout()
        i_layout.addWidget(QLabel("I:"))
        self.i_spinbox = QSpinBox()
        self.i_spinbox.setRange(0, 11)
        self.i_spinbox.setValue(0)
        i_layout.addWidget(self.i_spinbox)
        self.i_button = QPushButton("Apply")
        self.i_button.setEnabled(False)
        i_layout.addWidget(self.i_button)
        transform_layout.addLayout(i_layout)

        # Rotation
        r_layout = QHBoxLayout()
        r_layout.addWidget(QLabel("R:"))
        self.r_spinbox = QSpinBox()
        self.r_spinbox.setRange(0, 11)
        self.r_spinbox.setValue(1)
        r_layout.addWidget(self.r_spinbox)
        self.r_button = QPushButton("Apply")
        self.r_button.setEnabled(False)
        r_layout.addWidget(self.r_button)
        transform_layout.addLayout(r_layout)

        transform_group.setLayout(transform_layout)
        layout.addWidget(transform_group)

        # === AUDIO ===
        audio_group = QGroupBox("Audio")
        audio_layout = QVBoxLayout()

        # Play button
        play_layout = QHBoxLayout()
        self.play_button = QPushButton("♪ Play")
        self.play_button.setEnabled(False)
        play_layout.addWidget(self.play_button)

        # Play mode
        self.play_mode = QComboBox()
        self.play_mode.addItems(["Chord", "Arpeggio"])
        self.play_mode.setCurrentIndex(1)  # Default to arpeggio
        play_layout.addWidget(self.play_mode)
        audio_layout.addLayout(play_layout)

        # Audio settings button
        self.audio_settings_button = QPushButton("Settings...")
        audio_layout.addWidget(self.audio_settings_button)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # === QUICK ACTIONS ===
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()

        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.setEnabled(False)
        actions_layout.addWidget(self.visualize_button)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setEnabled(False)
        actions_layout.addWidget(self.analyze_button)

        self.forte_button = QPushButton("Forte Directory")
        actions_layout.addWidget(self.forte_button)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Add stretch to push everything to top
        layout.addStretch()

        self.setLayout(layout)

    def _connect_signals(self):
        """Connect internal signals"""
        # Input field
        self.input_field.setChanged.connect(self._on_set_changed)
        self.input_field.validationChanged.connect(self._on_validation_changed)

        # Transformation buttons
        self.t_button.clicked.connect(lambda: self._apply_transformation('T'))
        self.i_button.clicked.connect(lambda: self._apply_transformation('I'))
        self.r_button.clicked.connect(lambda: self._apply_transformation('R'))

        # Audio
        self.play_button.clicked.connect(self._on_play_clicked)

        # Quick actions
        self.visualize_button.clicked.connect(self.visualizeRequested)
        self.analyze_button.clicked.connect(self.analyzeRequested)
        self.forte_button.clicked.connect(self.forteDirectoryRequested)

        # Recent sets
        self.recent_list.itemClicked.connect(self._on_recent_clicked)

    def _on_set_changed(self, pcs: PitchClassSet):
        """Handle set change from input field"""
        self.current_set = pcs
        self.setChanged.emit(pcs)

    def _on_validation_changed(self, is_valid: bool):
        """Enable/disable buttons based on validation"""
        self.t_button.setEnabled(is_valid)
        self.i_button.setEnabled(is_valid)
        self.r_button.setEnabled(is_valid)
        self.play_button.setEnabled(is_valid)
        self.visualize_button.setEnabled(is_valid)
        self.analyze_button.setEnabled(is_valid)

    def _apply_transformation(self, trans_type: str):
        """Apply a transformation"""
        if trans_type == 'T':
            value = self.t_spinbox.value()
        elif trans_type == 'I':
            value = self.i_spinbox.value()
        elif trans_type == 'R':
            value = self.r_spinbox.value()
        else:
            return

        self.transformationRequested.emit(trans_type, value)

    def _on_play_clicked(self):
        """Handle play button click"""
        arpeggiate = self.play_mode.currentText() == "Arpeggio"
        self.playRequested.emit(arpeggiate)

    def _on_recent_clicked(self, item: QListWidgetItem):
        """Handle recent set clicked"""
        text = item.text()
        # Extract pitch classes from text (format: "[0, 1, 3, 6]")
        if '[' in text:
            pcs_text = text[text.index('['):text.index(']')+1]
            self.input_field.setText(pcs_text)

    def get_current_set(self):
        """Get the current pitch class set"""
        return self.current_set

    def set_current_set(self, pcs: PitchClassSet):
        """Set the current pitch class set"""
        self.input_field.set_pitch_class_set(pcs)

    def add_to_recent(self, pcs: PitchClassSet):
        """Add a set to recent list"""
        # Format: [0, 1, 3, 6]
        text = str(sorted(pcs.pitch_classes))

        # Check if already in list
        for i in range(self.recent_list.count()):
            if text in self.recent_list.item(i).text():
                # Remove it (we'll add to top)
                self.recent_list.takeItem(i)
                break

        # Add to top
        self.recent_list.insertItem(0, text)

        # Keep only last 10
        while self.recent_list.count() > 10:
            self.recent_list.takeItem(self.recent_list.count() - 1)


# Test panel
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Set Input Panel Test")

    panel = SetInputPanel()

    # Connect signals to print
    panel.setChanged.connect(lambda pcs: print(f"Set changed: {pcs}"))
    panel.transformationRequested.connect(lambda t, v: print(f"Transform: {t}{v}"))
    panel.playRequested.connect(lambda a: print(f"Play (arp={a})"))
    panel.visualizeRequested.connect(lambda: print("Visualize"))
    panel.analyzeRequested.connect(lambda: print("Analyze"))
    panel.forteDirectoryRequested.connect(lambda: print("Forte Directory"))

    window.setCentralWidget(panel)
    window.resize(350, 700)
    window.show()

    sys.exit(app.exec())
