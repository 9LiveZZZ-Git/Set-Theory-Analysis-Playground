"""
Find Similar Sets Dialog
Find pitch class sets similar to a given set based on interval vector
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
                              QListWidgetItem, QPushButton, QHBoxLayout,
                              QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification


class FindSimilarDialog(QDialog):
    """
    Dialog for finding sets similar to a given pitch class set
    """

    setSelected = pyqtSignal(PitchClassSet, str)  # (pcs, forte_number)

    def __init__(self, current_set: PitchClassSet, parent=None):
        super().__init__(parent)

        self.current_set = current_set
        self.forte_classification = ForteClassification()

        self.setWindowTitle("Find Similar Sets")
        self.resize(600, 700)
        self._setup_ui()
        self._find_similar()

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Title
        title = QLabel(f"<h2>Sets Similar to: {sorted(self.current_set.pitch_classes)}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Current set info
        info_group = QGroupBox("Current Set Properties")
        info_layout = QVBoxLayout()

        forte_num = self.forte_classification.get_forte_number(self.current_set)
        iv = self.current_set.interval_vector()
        iv_str = ''.join(map(str, iv))

        info_text = f"""
        <b>Forte Number:</b> {forte_num or 'Unknown'}<br>
        <b>Cardinality:</b> {len(self.current_set.pitch_classes)}<br>
        <b>Interval Vector:</b> &lt;{iv_str}&gt;<br>
        <b>Prime Form:</b> {self.current_set.prime_form()}
        """
        info_label = QLabel(info_text)
        info_label.setStyleSheet("padding: 10px; background-color: #E3F2FD; border-radius: 4px;")
        info_layout.addWidget(info_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Results section
        results_label = QLabel("<h3>Similar Sets:</h3>")
        layout.addWidget(results_label)

        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.results_list)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: gray; font-size: 9pt;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.use_button = QPushButton("Use Selected Set")
        self.use_button.setEnabled(False)
        self.use_button.clicked.connect(self._use_selected)
        button_layout.addWidget(self.use_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect selection change
        self.results_list.itemSelectionChanged.connect(self._on_selection_changed)

    def _find_similar(self):
        """Find similar sets"""
        forte_num = self.forte_classification.get_forte_number(self.current_set)

        if not forte_num:
            self.info_label.setText("⚠ Could not determine Forte number for current set")
            return

        # Get similar sets from ForteClassification
        similar_forte_nums = ForteClassification.find_similar_sets(forte_num)

        if not similar_forte_nums:
            self.info_label.setText("No similar sets found")
            return

        # Populate results list
        for sim_forte in similar_forte_nums:
            # Get the representative set for this Forte number
            sim_pcs = self.forte_classification.get_pitch_class_set(sim_forte)

            if sim_pcs:
                # Calculate similarity score (based on interval vector distance)
                current_iv = self.current_set.interval_vector()
                sim_iv = sim_pcs.interval_vector()

                # Hamming distance
                distance = sum(abs(a - b) for a, b in zip(current_iv, sim_iv))

                # Create list item
                iv_str = ''.join(map(str, sim_iv))
                item_text = f"{sim_forte}  |  {sorted(sim_pcs.pitch_classes)}  |  <{iv_str}>  |  Distance: {distance}"

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, (sim_pcs, sim_forte))

                # Color code by distance
                if distance == 0:
                    item.setBackground(Qt.GlobalColor.lightGray)  # Identical
                elif distance <= 2:
                    item.setBackground(Qt.GlobalColor.green)  # Very similar
                elif distance <= 4:
                    item.setBackground(Qt.GlobalColor.yellow)  # Somewhat similar

                self.results_list.addItem(item)

        self.info_label.setText(f"Found {len(similar_forte_nums)} similar sets. "
                               "Double-click to use a set.")

    def _on_selection_changed(self):
        """Handle selection changed"""
        self.use_button.setEnabled(len(self.results_list.selectedItems()) > 0)

    def _on_item_double_clicked(self, item):
        """Handle item double-clicked"""
        self._use_selected()

    def _use_selected(self):
        """Use the selected set"""
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            return

        pcs, forte_num = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.setSelected.emit(pcs, forte_num)
        self.accept()


# Test dialog
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test with C major triad
    test_set = PitchClassSet([0, 4, 7])
    dialog = FindSimilarDialog(test_set)

    dialog.setSelected.connect(
        lambda pcs, fn: print(f"Selected: {sorted(pcs.pitch_classes)} ({fn})")
    )

    dialog.exec()

    sys.exit(0)
