"""
Forte Directory Browser
Dialog for browsing all 208 Forte pitch class sets
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget,
                              QTreeWidgetItem, QLabel, QTextEdit, QPushButton,
                              QSplitter, QWidget, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import sys
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification


class ForteSelector(QDialog):
    """
    Modal dialog for browsing Forte classification.
    Shows all 208 pitch class sets organized by cardinality.
    """

    # Signals
    setSelected = pyqtSignal(PitchClassSet, str)  # (set, forte_number)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.forte_classification = ForteClassification()
        self.current_set = None
        self.current_forte = None

        self.setWindowTitle("Forte Directory - All 208 Pitch Class Sets")
        self.resize(900, 600)
        self._setup_ui()
        self._populate_tree()

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Tree view of all Forte sets
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        tree_label = QLabel("<b>Browse by Cardinality</b>")
        left_layout.addWidget(tree_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Forte Number", "Prime Form"])
        self.tree.setColumnWidth(0, 120)
        self.tree.itemClicked.connect(self._on_item_clicked)
        left_layout.addWidget(self.tree)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right: Details panel
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("<b>Set Details</b>")
        right_layout.addWidget(details_label)

        # Details form
        details_group = QGroupBox("Analysis")
        details_form = QFormLayout()

        self.forte_label = QLabel("-")
        self.forte_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Forte Number:", self.forte_label)

        self.prime_label = QLabel("-")
        self.prime_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Prime Form:", self.prime_label)

        self.iv_label = QLabel("-")
        self.iv_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Interval Vector:", self.iv_label)

        self.cardinality_label = QLabel("-")
        details_form.addRow("Cardinality:", self.cardinality_label)

        self.complement_label = QLabel("-")
        self.complement_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Complement:", self.complement_label)

        self.z_partner_label = QLabel("-")
        self.z_partner_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Z-Partner:", self.z_partner_label)

        details_group.setLayout(details_form)
        right_layout.addWidget(details_group)

        # Additional info
        info_group = QGroupBox("Additional Information")
        info_layout = QVBoxLayout()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        info_layout.addWidget(self.info_text)

        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        # Visualization preview
        viz_group = QGroupBox("Pitch Class Clock Preview")
        viz_layout = QVBoxLayout()

        self.viz_figure = Figure(figsize=(3, 3), dpi=80)
        self.viz_canvas = FigureCanvas(self.viz_figure)
        self.viz_ax = self.viz_figure.add_subplot(111)
        self.viz_ax.set_aspect('equal')
        self.viz_ax.axis('off')

        viz_layout.addWidget(self.viz_canvas)
        viz_group.setLayout(viz_layout)
        right_layout.addWidget(viz_group)

        # Draw empty clock initially
        self._draw_empty_clock()

        right_layout.addStretch()

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.use_button = QPushButton("Use This Set")
        self.use_button.setEnabled(False)
        self.use_button.clicked.connect(self._on_use_clicked)
        button_layout.addWidget(self.use_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _populate_tree(self):
        """Populate tree with all Forte sets"""
        # Get all Forte sets organized by cardinality
        for cardinality in range(1, 13):
            # Create parent item for cardinality
            count = self.forte_classification.cardinality_counts.get(cardinality, 0)
            parent_item = QTreeWidgetItem(self.tree)
            parent_item.setText(0, f"Cardinality {cardinality}")
            parent_item.setText(1, f"({count} sets)")
            parent_item.setExpanded(False)

            # Add individual sets
            for num in range(1, count + 1):
                forte_number = f"{cardinality}-{num}"

                # Get prime form
                pcs = self.forte_classification.get_set_from_forte_number(forte_number)
                if pcs:
                    prime_form = sorted(pcs.pitch_classes)

                    # Create child item
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, forte_number)
                    child_item.setText(1, str(prime_form))
                    child_item.setData(0, Qt.ItemDataRole.UserRole, forte_number)
                    child_item.setData(1, Qt.ItemDataRole.UserRole, pcs)

    def _on_item_clicked(self, item, column):
        """Handle item clicked in tree"""
        # Check if it's a child item (not a cardinality header)
        forte_number = item.data(0, Qt.ItemDataRole.UserRole)
        if forte_number:
            pcs = item.data(1, Qt.ItemDataRole.UserRole)
            self._display_set_details(pcs, forte_number)

    def _display_set_details(self, pcs: PitchClassSet, forte_number: str):
        """Display details for a selected set"""
        self.current_set = pcs
        self.current_forte = forte_number

        # Forte number
        self.forte_label.setText(forte_number)

        # Prime form (returns a list, not a PitchClassSet)
        prime = pcs.prime_form()
        self.prime_label.setText(str(prime))

        # Interval vector
        iv = pcs.interval_vector()
        iv_str = ''.join(map(str, iv))
        self.iv_label.setText(f"<{iv_str}>")

        # Cardinality
        self.cardinality_label.setText(str(len(pcs.pitch_classes)))

        # Complement
        complement = pcs.complement()
        complement_forte = self.forte_classification.get_forte_number(complement)
        self.complement_label.setText(f"{sorted(complement.pitch_classes)} ({complement_forte})")

        # Z-partner
        try:
            z_partner = self.forte_classification.get_z_partner(pcs)
            if z_partner:
                self.z_partner_label.setText(z_partner)
            else:
                self.z_partner_label.setText("None")
        except:
            self.z_partner_label.setText("-")

        # Additional info
        info_lines = []

        # Check for symmetries
        try:
            if pcs == pcs.inversion(0):
                info_lines.append("• Inversionally symmetrical")
        except:
            pass

        # Check for special properties
        if len(pcs.pitch_classes) == 6:
            info_lines.append("• Hexachord")

        # Common set names
        common_names = {
            "3-11": "Major/Minor Triad",
            "3-10": "Diminished Triad",
            "3-12": "Augmented Triad",
            "4-27": "Dominant 7th",
            "6-35": "Whole Tone Scale",
            "6-20": "Hexatonic Scale",
            "5-35": "Pentatonic (Black Keys)",
            "7-35": "Diatonic Scale",
            "8-28": "Octatonic Scale"
        }

        if forte_number in common_names:
            info_lines.append(f"• Common name: {common_names[forte_number]}")

        if info_lines:
            self.info_text.setText('\n'.join(info_lines))
        else:
            self.info_text.clear()

        # Enable use button
        self.use_button.setEnabled(True)

        # Update visualization
        self._update_clock_visualization(pcs)

    def _on_use_clicked(self):
        """Handle 'Use This Set' button"""
        if self.current_set and self.current_forte:
            self.setSelected.emit(self.current_set, self.current_forte)
            self.accept()

    def get_selected_set(self):
        """Get currently selected set"""
        return self.current_set, self.current_forte

    def _draw_empty_clock(self):
        """Draw empty pitch class clock"""
        self.viz_ax.clear()
        self.viz_ax.set_xlim(-1.3, 1.3)
        self.viz_ax.set_ylim(-1.3, 1.3)
        self.viz_ax.set_aspect('equal')
        self.viz_ax.axis('off')

        # Draw circle
        circle = plt.Circle((0, 0), 1.0, fill=False, color='lightgray', linewidth=2)
        self.viz_ax.add_patch(circle)

        # Draw pitch class labels
        for pc in range(12):
            angle = (90 - pc * 30) * np.pi / 180
            x = 1.15 * np.cos(angle)
            y = 1.15 * np.sin(angle)
            self.viz_ax.text(x, y, str(pc), ha='center', va='center',
                           fontsize=9, color='gray')

        self.viz_canvas.draw()

    def _update_clock_visualization(self, pcs: PitchClassSet):
        """Update pitch class clock with given set"""
        self.viz_ax.clear()
        self.viz_ax.set_xlim(-1.3, 1.3)
        self.viz_ax.set_ylim(-1.3, 1.3)
        self.viz_ax.set_aspect('equal')
        self.viz_ax.axis('off')

        # Draw circle
        circle = plt.Circle((0, 0), 1.0, fill=False, color='black', linewidth=2)
        self.viz_ax.add_patch(circle)

        # Draw pitch class labels (all)
        for pc in range(12):
            angle = (90 - pc * 30) * np.pi / 180
            x = 1.15 * np.cos(angle)
            y = 1.15 * np.sin(angle)

            # Highlight active pitch classes
            if pc in pcs.pitch_classes:
                color = 'red'
                weight = 'bold'
            else:
                color = 'lightgray'
                weight = 'normal'

            self.viz_ax.text(x, y, str(pc), ha='center', va='center',
                           fontsize=10, color=color, weight=weight)

        # Draw dots and lines for active pitch classes
        for pc in pcs.pitch_classes:
            angle = (90 - pc * 30) * np.pi / 180
            x = 0.85 * np.cos(angle)
            y = 0.85 * np.sin(angle)

            # Dot
            self.viz_ax.plot([x], [y], 'ro', markersize=12)

            # Line to center
            self.viz_ax.plot([0, x], [0, y], 'b-', linewidth=2, alpha=0.4)

        self.viz_canvas.draw()


# Test dialog
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    dialog = ForteSelector()

    # Connect signal
    dialog.setSelected.connect(
        lambda pcs, forte: print(f"Selected: {forte} - {sorted(pcs.pitch_classes)}")
    )

    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        pcs, forte = dialog.get_selected_set()
        print(f"Final selection: {forte}")

    sys.exit(0)
