"""
Subset Explorer Panel
Browse subsets and supersets of a pitch class set
"""

from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QTreeWidget,
                              QTreeWidgetItem, QLabel, QPushButton, QSpinBox,
                              QHBoxLayout, QGroupBox)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification


class SubsetExplorer(QDockWidget):
    """
    Dockable panel for exploring subsets and supersets.
    """

    setSelected = pyqtSignal(PitchClassSet)  # Emitted when user selects a subset/superset

    def __init__(self, parent=None):
        super().__init__("Subset Explorer", parent)

        self.forte_classification = ForteClassification()
        self.current_set = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Main widget
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Subset size:"))

        self.subset_size_spin = QSpinBox()
        self.subset_size_spin.setRange(1, 11)
        self.subset_size_spin.setValue(3)
        controls_layout.addWidget(self.subset_size_spin)

        self.find_subsets_button = QPushButton("Find Subsets")
        self.find_subsets_button.setEnabled(False)
        self.find_subsets_button.clicked.connect(self._find_subsets)
        controls_layout.addWidget(self.find_subsets_button)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Set", "Forte Number", "Interval Vector"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 80)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree)

        # Info label
        self.info_label = QLabel("Enter a pitch class set to explore subsets")
        self.info_label.setStyleSheet("color: gray; font-size: 9pt;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.use_button = QPushButton("Use Selected Set")
        self.use_button.setEnabled(False)
        self.use_button.clicked.connect(self._use_selected)
        button_layout.addWidget(self.use_button)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        self.setWidget(widget)

        # Set dockwidget properties
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea |
                            Qt.DockWidgetArea.LeftDockWidgetArea |
                            Qt.DockWidgetArea.BottomDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                        QDockWidget.DockWidgetFeature.DockWidgetClosable)

    @pyqtSlot(PitchClassSet)
    def update_set(self, pcs: PitchClassSet):
        """Update explorer with new set"""
        self.current_set = pcs
        self.tree.clear()

        if pcs is None:
            self.find_subsets_button.setEnabled(False)
            self.info_label.setText("Enter a pitch class set to explore subsets")
            return

        self.find_subsets_button.setEnabled(True)

        cardinality = len(pcs.pitch_classes)
        self.info_label.setText(f"Current set: {sorted(pcs.pitch_classes)} "
                               f"(Cardinality: {cardinality})")

        # Set subset size range
        self.subset_size_spin.setRange(1, max(1, cardinality - 1))
        if cardinality > 1:
            self.subset_size_spin.setValue(cardinality - 1)

        # Auto-display subsets of size n-1
        if cardinality > 1:
            self._find_subsets()

    def _find_subsets(self):
        """Find and display subsets"""
        if not self.current_set:
            return

        self.tree.clear()

        subset_size = self.subset_size_spin.value()
        cardinality = len(self.current_set.pitch_classes)

        # Find subsets
        if subset_size < cardinality:
            subsets = self.current_set.find_subsets(subset_size)

            # Create subsets group
            subset_parent = QTreeWidgetItem(self.tree)
            subset_parent.setText(0, f"Subsets (size {subset_size})")
            subset_parent.setText(1, f"({len(subsets)} sets)")
            subset_parent.setExpanded(True)

            for subset in subsets:
                item = QTreeWidgetItem(subset_parent)
                item.setText(0, str(sorted(subset.pitch_classes)))

                # Forte number
                forte_num = self.forte_classification.get_forte_number(subset)
                item.setText(1, forte_num or "-")

                # Interval vector
                iv = subset.interval_vector()
                iv_str = ''.join(map(str, iv))
                item.setText(2, f"<{iv_str}>")

                # Store set in item data
                item.setData(0, Qt.ItemDataRole.UserRole, subset)

        # Find supersets
        superset_size = cardinality + 1
        if superset_size <= 12:
            supersets = self.current_set.find_supersets(superset_size)

            # Create supersets group
            superset_parent = QTreeWidgetItem(self.tree)
            superset_parent.setText(0, f"Supersets (size {superset_size})")
            superset_parent.setText(1, f"({len(supersets)} sets)")
            superset_parent.setExpanded(False)

            for superset in supersets:
                item = QTreeWidgetItem(superset_parent)
                item.setText(0, str(sorted(superset.pitch_classes)))

                # Forte number
                forte_num = self.forte_classification.get_forte_number(superset)
                item.setText(1, forte_num or "-")

                # Interval vector
                iv = superset.interval_vector()
                iv_str = ''.join(map(str, iv))
                item.setText(2, f"<{iv_str}>")

                # Store set in item data
                item.setData(0, Qt.ItemDataRole.UserRole, superset)

        self.info_label.setText(f"Found {self.tree.topLevelItemCount()} groups")

    def _on_item_clicked(self, item, column):
        """Handle item clicked"""
        # Check if it's a child item (not a group header)
        pcs = item.data(0, Qt.ItemDataRole.UserRole)
        if pcs:
            self.use_button.setEnabled(True)
        else:
            self.use_button.setEnabled(False)

    def _on_item_double_clicked(self, item, column):
        """Handle item double-clicked - use the set"""
        pcs = item.data(0, Qt.ItemDataRole.UserRole)
        if pcs:
            self.setSelected.emit(pcs)

    def _use_selected(self):
        """Use the selected set"""
        current_item = self.tree.currentItem()
        if current_item:
            pcs = current_item.data(0, Qt.ItemDataRole.UserRole)
            if pcs:
                self.setSelected.emit(pcs)


# Test panel
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Subset Explorer Test")

    panel = SubsetExplorer()
    window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, panel)

    # Test with a tetrachord
    test_set = PitchClassSet([0, 1, 3, 6])
    panel.update_set(test_set)

    # Connect signals
    panel.setSelected.connect(
        lambda pcs: print(f"Set selected: {sorted(pcs.pitch_classes)}")
    )

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
