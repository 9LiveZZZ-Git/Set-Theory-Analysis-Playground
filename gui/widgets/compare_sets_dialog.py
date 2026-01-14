"""
Compare Sets Dialog
Compare two pitch class sets side-by-side
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QGroupBox, QTableWidget,
                              QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification


class CompareSetsDialog(QDialog):
    """
    Dialog for comparing two pitch class sets
    """

    def __init__(self, current_set: PitchClassSet = None, parent=None):
        super().__init__(parent)

        self.current_set = current_set
        self.forte_classification = ForteClassification()

        self.setWindowTitle("Compare Pitch Class Sets")
        self.resize(800, 600)
        self._setup_ui()

        # Pre-fill Set A if current_set is provided
        if self.current_set:
            self.set_a_input.setText(' '.join(map(str, sorted(self.current_set.pitch_classes))))

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("<h2>Compare Two Pitch Class Sets</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Input section
        input_group = QGroupBox("Input Sets")
        input_layout = QVBoxLayout()

        # Set A
        set_a_layout = QHBoxLayout()
        set_a_layout.addWidget(QLabel("<b>Set A:</b>"))
        self.set_a_input = QLineEdit()
        self.set_a_input.setPlaceholderText("Enter pitch classes (e.g., 0 4 7)")
        set_a_layout.addWidget(self.set_a_input)
        input_layout.addLayout(set_a_layout)

        # Set B
        set_b_layout = QHBoxLayout()
        set_b_layout.addWidget(QLabel("<b>Set B:</b>"))
        self.set_b_input = QLineEdit()
        self.set_b_input.setPlaceholderText("Enter pitch classes (e.g., 0 3 7)")
        set_b_layout.addWidget(self.set_b_input)
        input_layout.addLayout(set_b_layout)

        # Compare button
        compare_btn_layout = QHBoxLayout()
        compare_btn_layout.addStretch()
        self.compare_button = QPushButton("Compare Sets")
        self.compare_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.compare_button.clicked.connect(self._compare_sets)
        compare_btn_layout.addWidget(self.compare_button)
        compare_btn_layout.addStretch()
        input_layout.addLayout(compare_btn_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Comparison table
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(3)
        self.comparison_table.setHorizontalHeaderLabels(["Property", "Set A", "Set B"])
        self.comparison_table.horizontalHeader().setStretchLastSection(True)
        self.comparison_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.comparison_table)

        # Relationship label
        self.relationship_label = QLabel("")
        self.relationship_label.setStyleSheet("font-size: 11pt; padding: 10px; background-color: #f0f0f0; border-radius: 4px;")
        self.relationship_label.setWordWrap(True)
        self.relationship_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.relationship_label)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _compare_sets(self):
        """Compare the two sets and display results"""
        try:
            # Parse Set A
            set_a_str = self.set_a_input.text().strip()
            if not set_a_str:
                QMessageBox.warning(self, "Input Error", "Please enter Set A")
                return

            set_a_pcs = [int(x) for x in set_a_str.split()]
            set_a = PitchClassSet(set_a_pcs)

            # Parse Set B
            set_b_str = self.set_b_input.text().strip()
            if not set_b_str:
                QMessageBox.warning(self, "Input Error", "Please enter Set B")
                return

            set_b_pcs = [int(x) for x in set_b_str.split()]
            set_b = PitchClassSet(set_b_pcs)

            # Build comparison table
            self._build_comparison_table(set_a, set_b)

            # Analyze relationship
            self._analyze_relationship(set_a, set_b)

        except ValueError as e:
            QMessageBox.warning(self, "Input Error",
                              f"Invalid pitch class values. Use integers 0-11.\n{str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _build_comparison_table(self, set_a: PitchClassSet, set_b: PitchClassSet):
        """Build the comparison table"""
        # Define properties to compare
        properties = [
            ("Pitch Classes", lambda s: str(sorted(s.pitch_classes))),
            ("Cardinality", lambda s: str(len(s.pitch_classes))),
            ("Prime Form", lambda s: str(s.prime_form())),
            ("Forte Number", lambda s: self.forte_classification.get_forte_number(s) or "-"),
            ("Interval Vector", lambda s: '<' + ''.join(map(str, s.interval_vector())) + '>'),
            ("Normal Form", lambda s: str(s.normal_form())),
            ("Z-Partner", lambda s: self.forte_classification.get_z_partner(
                self.forte_classification.get_forte_number(s)) or "None"),
        ]

        self.comparison_table.setRowCount(len(properties))

        # Populate table
        for row, (prop_name, prop_func) in enumerate(properties):
            # Property name
            name_item = QTableWidgetItem(prop_name)
            name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.comparison_table.setItem(row, 0, name_item)

            # Set A value
            try:
                set_a_value = prop_func(set_a)
            except:
                set_a_value = "-"
            set_a_item = QTableWidgetItem(set_a_value)
            self.comparison_table.setItem(row, 1, set_a_item)

            # Set B value
            try:
                set_b_value = prop_func(set_b)
            except:
                set_b_value = "-"
            set_b_item = QTableWidgetItem(set_b_value)
            self.comparison_table.setItem(row, 2, set_b_item)

            # Highlight matching values
            if set_a_value == set_b_value and set_a_value != "-":
                set_a_item.setBackground(Qt.GlobalColor.lightGray)
                set_b_item.setBackground(Qt.GlobalColor.lightGray)

        # Auto-resize columns
        self.comparison_table.resizeColumnsToContents()

    def _analyze_relationship(self, set_a: PitchClassSet, set_b: PitchClassSet):
        """Analyze and display the relationship between the two sets"""
        relationships = []

        # Check if identical
        if sorted(set_a.pitch_classes) == sorted(set_b.pitch_classes):
            relationships.append("<b>Identical Sets</b>")

        # Check if transpositionally related
        for i in range(12):
            if sorted(set_a.transposition(i).pitch_classes) == sorted(set_b.pitch_classes):
                relationships.append(f"<b>Transpositionally Related:</b> Set B = T{i}(Set A)")
                break

        # Check if inversionally related
        for i in range(12):
            if sorted(set_a.inversion(i).pitch_classes) == sorted(set_b.pitch_classes):
                relationships.append(f"<b>Inversionally Related:</b> Set B = I{i}(Set A)")
                break

        # Check if same prime form
        if set_a.prime_form() == set_b.prime_form():
            relationships.append("<b>Same Prime Form</b> (related by T or I)")

        # Check if same interval vector (Z-related or same set class)
        if set_a.interval_vector() == set_b.interval_vector():
            forte_a = self.forte_classification.get_forte_number(set_a)
            forte_b = self.forte_classification.get_forte_number(set_b)
            if forte_a != forte_b:
                relationships.append("<b>Z-Related Sets</b> (same interval vector, different prime form)")
            elif not any("Same Prime Form" in r for r in relationships):
                relationships.append("<b>Same Interval Vector</b>")

        # Check complement relation
        if len(set_a.pitch_classes) + len(set_b.pitch_classes) == 12:
            all_pcs = set(set_a.pitch_classes) | set(set_b.pitch_classes)
            if len(all_pcs) == 12:
                relationships.append("<b>Complementary Sets</b> (together form the aggregate)")

        # Display relationships
        if relationships:
            self.relationship_label.setText("<br>".join(relationships))
            self.relationship_label.setStyleSheet(
                "font-size: 11pt; padding: 10px; background-color: #E3F2FD; "
                "border: 2px solid #2196F3; border-radius: 4px;"
            )
        else:
            self.relationship_label.setText("<b>No Common Relationships Detected</b>")
            self.relationship_label.setStyleSheet(
                "font-size: 11pt; padding: 10px; background-color: #FFEBEE; "
                "border: 2px solid #F44336; border-radius: 4px;"
            )


# Test dialog
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test with C major triad
    test_set = PitchClassSet([0, 4, 7])
    dialog = CompareSetsDialog(test_set)

    dialog.exec()

    sys.exit(0)
