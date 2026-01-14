"""
Music Examples Browser Dialog
Browse and load famous pitch class sets from classical and popular music
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget,
                              QTreeWidgetItem, QLabel, QTextEdit, QPushButton,
                              QSplitter, QWidget, QGroupBox, QFormLayout,
                              QComboBox, QLineEdit)
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
from music_examples import MusicExamplesDatabase, MusicExample


class MusicExamplesDialog(QDialog):
    """
    Dialog for browsing and loading music examples.
    Shows famous pitch class sets from classical and popular music.
    """

    # Signals
    exampleSelected = pyqtSignal(PitchClassSet, str)  # (set, example_name)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.database = MusicExamplesDatabase()
        self.forte_classification = ForteClassification()
        self.current_example = None

        self.setWindowTitle("Music Examples - Famous Pitch Class Sets")
        self.resize(1000, 700)
        self._setup_ui()
        self._populate_tree()

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("<h2>Music Examples from Classical & Popular Music</h2>"
                      "<p>All examples are from public domain works</p>")
        layout.addWidget(title)

        # Filter controls
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Filter by composer:"))

        self.composer_filter = QComboBox()
        self.composer_filter.addItem("All Composers")
        composers = self.database.get_composers()
        self.composer_filter.addItems(composers)
        self.composer_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.composer_filter)

        filter_layout.addStretch()

        filter_layout.addWidget(QLabel("Search:"))

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by name or piece...")
        self.search_box.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_box)

        layout.addLayout(filter_layout)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Tree view of examples
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        tree_label = QLabel(f"<b>Browse Examples ({len(self.database.get_all_examples())} total)</b>")
        left_layout.addWidget(tree_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Composer", "Year"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setColumnWidth(1, 150)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        left_layout.addWidget(self.tree)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right: Details panel
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("<b>Example Details</b>")
        right_layout.addWidget(details_label)

        # Details form
        details_group = QGroupBox("Information")
        details_form = QFormLayout()

        self.name_label = QLabel("-")
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.name_label.setWordWrap(True)
        details_form.addRow("Name:", self.name_label)

        self.composer_label = QLabel("-")
        self.composer_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Composer:", self.composer_label)

        self.piece_label = QLabel("-")
        self.piece_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.piece_label.setWordWrap(True)
        details_form.addRow("Piece:", self.piece_label)

        self.year_label = QLabel("-")
        details_form.addRow("Year:", self.year_label)

        self.pitch_classes_label = QLabel("-")
        self.pitch_classes_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Pitch Classes:", self.pitch_classes_label)

        self.forte_label = QLabel("-")
        self.forte_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Forte Number:", self.forte_label)

        self.iv_label = QLabel("-")
        self.iv_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details_form.addRow("Interval Vector:", self.iv_label)

        details_group.setLayout(details_form)
        right_layout.addWidget(details_group)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        desc_layout.addWidget(self.description_text)

        desc_group.setLayout(desc_layout)
        right_layout.addWidget(desc_group)

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

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()

        self.info_label = QLabel(f"{len(self.database.get_all_examples())} examples available")
        self.info_label.setStyleSheet("color: gray;")
        button_layout.addWidget(self.info_label)

        button_layout.addStretch()

        self.load_button = QPushButton("Load This Example")
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self._on_load_clicked)
        button_layout.addWidget(self.load_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _populate_tree(self, filter_composer=None, search_text=None):
        """Populate tree with music examples"""
        self.tree.clear()

        # Get examples
        examples = self.database.get_all_examples()

        # Apply composer filter
        if filter_composer and filter_composer != "All Composers":
            examples = [ex for ex in examples if ex.composer == filter_composer]

        # Apply search filter
        if search_text:
            search_lower = search_text.lower()
            examples = [ex for ex in examples
                       if search_lower in ex.name.lower()
                       or search_lower in ex.piece.lower()
                       or search_lower in ex.composer.lower()]

        # Group by composer
        composers_dict = {}
        for example in examples:
            if example.composer not in composers_dict:
                composers_dict[example.composer] = []
            composers_dict[example.composer].append(example)

        # Create tree items
        for composer in sorted(composers_dict.keys()):
            # Create parent item for composer
            parent_item = QTreeWidgetItem(self.tree)
            parent_item.setText(0, composer)
            parent_item.setText(2, f"({len(composers_dict[composer])} examples)")
            parent_item.setExpanded(True)

            # Add examples
            for example in sorted(composers_dict[composer], key=lambda x: x.name):
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, example.name)
                child_item.setText(1, example.composer)
                child_item.setText(2, example.year)
                child_item.setData(0, Qt.ItemDataRole.UserRole, example)

        # Update info label
        self.info_label.setText(f"{len(examples)} examples shown")

    def _on_filter_changed(self, composer):
        """Handle composer filter changed"""
        search_text = self.search_box.text()
        self._populate_tree(
            filter_composer=composer if composer != "All Composers" else None,
            search_text=search_text if search_text else None
        )

    def _on_search_changed(self, text):
        """Handle search text changed"""
        composer = self.composer_filter.currentText()
        self._populate_tree(
            filter_composer=composer if composer != "All Composers" else None,
            search_text=text if text else None
        )

    def _on_item_clicked(self, item, column):
        """Handle item clicked in tree"""
        # Check if it's a child item (not a composer header)
        example = item.data(0, Qt.ItemDataRole.UserRole)
        if example:
            self._display_example_details(example)

    def _on_item_double_clicked(self, item, column):
        """Handle item double-clicked - load the example"""
        example = item.data(0, Qt.ItemDataRole.UserRole)
        if example:
            self._load_example(example)

    def _display_example_details(self, example: MusicExample):
        """Display details for a selected example"""
        self.current_example = example

        # Basic info
        self.name_label.setText(example.name)
        self.composer_label.setText(example.composer)
        self.piece_label.setText(example.piece)
        self.year_label.setText(example.year)

        # Pitch class info
        self.pitch_classes_label.setText(str(example.pitch_classes))

        # Forte number
        forte = self.forte_classification.get_forte_number(example.pitch_class_set)
        self.forte_label.setText(forte or "Unknown")

        # Interval vector
        iv = example.pitch_class_set.interval_vector()
        iv_str = ''.join(map(str, iv))
        self.iv_label.setText(f"<{iv_str}>")

        # Description
        self.description_text.setText(example.description)

        # Enable load button
        self.load_button.setEnabled(True)

        # Update visualization
        self._update_clock_visualization(example.pitch_class_set)

    def _on_load_clicked(self):
        """Handle 'Load This Example' button"""
        if self.current_example:
            self._load_example(self.current_example)

    def _load_example(self, example: MusicExample):
        """Load an example into the main window"""
        self.exampleSelected.emit(example.pitch_class_set, example.name)
        self.accept()

    def get_selected_example(self):
        """Get currently selected example"""
        return self.current_example

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

    dialog = MusicExamplesDialog()

    # Connect signal
    dialog.exampleSelected.connect(
        lambda pcs, name: print(f"Selected: {name} - {pcs.pitch_classes}")
    )

    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        example = dialog.get_selected_example()
        if example:
            print(f"Final selection: {example.name}")

    sys.exit(0)
