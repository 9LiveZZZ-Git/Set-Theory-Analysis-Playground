"""
Analysis Panel
Bottom dock showing live analysis results
"""

from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QFormLayout,
                              QLabel, QPushButton, QTextEdit)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification


class AnalysisPanel(QDockWidget):
    """
    Dockable panel showing analysis results.
    Updates automatically when set changes.
    """

    # Signals
    fullAnalysisRequested = pyqtSignal()
    forteNumberClicked = pyqtSignal(str)  # Clicked on Forte number

    def __init__(self, parent=None):
        super().__init__("Analysis", parent)

        self.forte_classification = ForteClassification()
        self.current_set = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Main widget
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Form layout for analysis results
        form = QFormLayout()

        # Prime Form
        self.prime_form_label = QLabel("-")
        self.prime_form_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow("Prime Form:", self.prime_form_label)

        # Forte Number (clickable)
        self.forte_number_label = QLabel("-")
        self.forte_number_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.forte_number_label.setStyleSheet("QLabel { color: blue; text-decoration: underline; cursor: pointer; }")
        self.forte_number_label.mousePressEvent = self._on_forte_clicked
        form.addRow("Forte Number:", self.forte_number_label)

        # Interval Vector
        self.interval_vector_label = QLabel("-")
        self.interval_vector_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow("Interval Vector:", self.interval_vector_label)

        # Cardinality
        self.cardinality_label = QLabel("-")
        form.addRow("Cardinality:", self.cardinality_label)

        # Complement
        self.complement_label = QLabel("-")
        self.complement_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow("Complement:", self.complement_label)

        layout.addLayout(form)

        # Full analysis button
        self.full_analysis_button = QPushButton("Show Full Analysis")
        self.full_analysis_button.setEnabled(False)
        self.full_analysis_button.clicked.connect(self.fullAnalysisRequested)
        layout.addWidget(self.full_analysis_button)

        # Additional info (collapsible)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        self.info_text.setVisible(False)  # Hidden by default
        layout.addWidget(self.info_text)

        widget.setLayout(layout)
        self.setWidget(widget)

        # Set dockwidget properties
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea |
                            Qt.DockWidgetArea.TopDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                        QDockWidget.DockWidgetFeature.DockWidgetClosable)

    def _on_forte_clicked(self, event):
        """Handle Forte number clicked"""
        forte_num = self.forte_number_label.text()
        if forte_num and forte_num != "-":
            self.forteNumberClicked.emit(forte_num)

    @pyqtSlot(PitchClassSet)
    def update_analysis(self, pcs: PitchClassSet):
        """
        Update analysis for a new pitch class set

        Args:
            pcs: PitchClassSet to analyze
        """
        if pcs is None:
            self._clear_analysis()
            return

        self.current_set = pcs

        try:
            # Prime form (returns a list, not a PitchClassSet)
            prime = pcs.prime_form()
            self.prime_form_label.setText(str(prime))

            # Forte number
            forte_num = self.forte_classification.get_forte_number(pcs)
            self.forte_number_label.setText(forte_num or "Unknown")

            # Interval vector
            iv = pcs.interval_vector()
            iv_str = ''.join(map(str, iv))
            self.interval_vector_label.setText(f"<{iv_str}>")

            # Cardinality
            self.cardinality_label.setText(str(len(pcs.pitch_classes)))

            # Complement
            complement = pcs.complement()
            self.complement_label.setText(str(sorted(complement.pitch_classes)))

            # Enable full analysis button
            self.full_analysis_button.setEnabled(True)

            # Update info text
            self._update_info_text(pcs)

        except Exception as e:
            print(f"Error updating analysis: {e}")
            self._clear_analysis()

    def _clear_analysis(self):
        """Clear all analysis fields"""
        self.prime_form_label.setText("-")
        self.forte_number_label.setText("-")
        self.interval_vector_label.setText("-")
        self.cardinality_label.setText("-")
        self.complement_label.setText("-")
        self.full_analysis_button.setEnabled(False)
        self.info_text.clear()
        self.current_set = None

    def _update_info_text(self, pcs: PitchClassSet):
        """Update additional info text"""
        info_lines = []

        # Z-relation check
        try:
            z_partner = self.forte_classification.get_z_partner(pcs)
            if z_partner:
                info_lines.append(f"Z-related to: {z_partner}")
        except Exception:
            pass

        # Symmetry
        try:
            if pcs == pcs.inversion(0):
                info_lines.append("Symmetrical (inversionally)")
        except Exception:
            pass

        if info_lines:
            self.info_text.setText('\n'.join(info_lines))
            self.info_text.setVisible(True)
        else:
            self.info_text.setVisible(False)


# Test panel
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Analysis Panel Test")

    panel = AnalysisPanel()
    window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, panel)

    # Test with a set
    test_set = PitchClassSet([0, 1, 3, 6])
    panel.update_analysis(test_set)

    # Connect signals
    panel.fullAnalysisRequested.connect(lambda: print("Full analysis requested"))
    panel.forteNumberClicked.connect(lambda f: print(f"Forte clicked: {f}"))

    window.resize(600, 400)
    window.show()

    sys.exit(app.exec())
