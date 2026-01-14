"""
Pitch Class Input Widget
Custom QLineEdit with real-time validation and visual feedback
"""

from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet

# Import validators from utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.validators import PitchClassValidator, parse_pitch_classes
from utils.debouncer import Debouncer


class PitchClassInput(QLineEdit):
    """
    Enhanced input field for pitch class sets with:
    - Real-time validation (green=valid, red=invalid, yellow=intermediate)
    - Auto-complete for Forte numbers
    - Debounced change signals
    - Parsing multiple input formats
    """

    # Signals
    setChanged = pyqtSignal(PitchClassSet)  # Emitted when valid set is entered (debounced)
    validationChanged = pyqtSignal(bool)     # Emitted when validation state changes

    def __init__(self, parent=None, debounce_ms=300):
        super().__init__(parent)

        # Setup validator
        self.validator = PitchClassValidator()
        self.setValidator(self.validator)

        # Setup debouncer
        self.debouncer = Debouncer(delay_ms=debounce_ms)
        self.debouncer.triggered.connect(self._on_debounced)

        # Setup auto-complete for Forte numbers
        self._setup_autocomplete()

        # Visual styling
        self.setPlaceholderText("e.g., 0 1 3 6 or Forte 3-11")
        self._default_palette = self.palette()
        self._valid_color = QColor(200, 255, 200)      # Light green
        self._invalid_color = QColor(255, 200, 200)    # Light red
        self._intermediate_color = QColor(255, 255, 200)  # Light yellow

        # Connect signals
        self.textChanged.connect(self._on_text_changed)

        # Current state
        self.current_set = None
        self.is_valid = False

    def _setup_autocomplete(self):
        """Setup auto-complete for Forte numbers"""
        try:
            from forte_classification import ForteClassification
            fc = ForteClassification()

            # Get all Forte numbers
            forte_numbers = []
            for card in range(1, 13):
                count = fc.cardinality_counts.get(card, 0)
                for num in range(1, count + 1):
                    forte_numbers.append(f"{card}-{num}")

            # Create completer
            completer = QCompleter(forte_numbers, self)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.setCompleter(completer)
        except Exception:
            # If forte classification fails, just skip autocomplete
            pass

    def _on_text_changed(self, text):
        """Handle text changes with validation"""
        # Update visual feedback immediately
        self._update_visual_feedback(text)

        # Trigger debouncer for set parsing
        self.debouncer.trigger()

    def _update_visual_feedback(self, text):
        """Update background color based on validation state"""
        if not text.strip():
            # Empty - default color
            self.setPalette(self._default_palette)
            self.is_valid = False
            self.validationChanged.emit(False)
            return

        # Validate
        state, _, _ = self.validator.validate(text, 0)

        palette = self.palette()
        if state == self.validator.State.Acceptable:
            # Valid
            palette.setColor(QPalette.ColorRole.Base, self._valid_color)
            self.is_valid = True
            self.validationChanged.emit(True)
        elif state == self.validator.State.Intermediate:
            # Typing in progress
            palette.setColor(QPalette.ColorRole.Base, self._intermediate_color)
            self.is_valid = False
            self.validationChanged.emit(False)
        else:
            # Invalid
            palette.setColor(QPalette.ColorRole.Base, self._invalid_color)
            self.is_valid = False
            self.validationChanged.emit(False)

        self.setPalette(palette)

    def _on_debounced(self):
        """Handle debounced text input - parse and emit signal"""
        text = self.text().strip()

        if not text:
            self.current_set = None
            return

        # Parse pitch classes
        pcs = parse_pitch_classes(text)

        if pcs:
            # Create PitchClassSet
            try:
                pitch_class_set = PitchClassSet(pcs)
                self.current_set = pitch_class_set
                self.setChanged.emit(pitch_class_set)
            except Exception as e:
                print(f"Error creating PitchClassSet: {e}")
                self.current_set = None
        else:
            self.current_set = None

    def get_pitch_class_set(self):
        """
        Get current pitch class set (immediate, not debounced)

        Returns:
            PitchClassSet or None if invalid
        """
        text = self.text().strip()
        if not text:
            return None

        pcs = parse_pitch_classes(text)
        if pcs:
            try:
                return PitchClassSet(pcs)
            except Exception:
                return None
        return None

    def set_pitch_class_set(self, pcs: PitchClassSet):
        """
        Set the input to a pitch class set

        Args:
            pcs: PitchClassSet to display
        """
        if pcs is None:
            self.clear()
            return

        # Format as space-separated
        text = ' '.join(map(str, sorted(pcs.pitch_classes)))
        self.setText(text)

    def set_forte_number(self, forte_number: str):
        """
        Set input to a Forte number

        Args:
            forte_number: Forte number (e.g., '3-11')
        """
        self.setText(forte_number)


# Test widget
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    import sys

    app = QApplication(sys.argv)

    # Create test window
    window = QWidget()
    window.setWindowTitle("Pitch Class Input Widget Test")
    layout = QVBoxLayout()

    # Instructions
    label = QLabel("Enter pitch classes:\n"
                   "- Space-separated: 0 1 3 6\n"
                   "- Comma-separated: 0,1,3,6\n"
                   "- Forte number: 3-11\n\n"
                   "Color feedback:\n"
                   "- Green = Valid\n"
                   "- Yellow = Typing...\n"
                   "- Red = Invalid")
    layout.addWidget(label)

    # Input widget
    input_widget = PitchClassInput()
    layout.addWidget(input_widget)

    # Result label
    result_label = QLabel("Waiting for input...")
    layout.addWidget(result_label)

    # Connect to display results
    def on_set_changed(pcs):
        result_label.setText(f"Set: {pcs}\n"
                            f"Prime Form: {pcs.prime_form()}\n"
                            f"Interval Vector: {pcs.interval_vector()}")

    input_widget.setChanged.connect(on_set_changed)

    window.setLayout(layout)
    window.resize(400, 250)
    window.show()

    sys.exit(app.exec())
