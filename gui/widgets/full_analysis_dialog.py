"""
Full Analysis Dialog
Shows comprehensive analysis of a pitch class set
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                              QPushButton, QTabWidget, QWidget, QLabel)
from PyQt6.QtCore import Qt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification
from set_analysis import SetAnalyzer


class FullAnalysisDialog(QDialog):
    """
    Dialog showing comprehensive analysis of a pitch class set.
    """

    def __init__(self, pcs: PitchClassSet, parent=None):
        super().__init__(parent)

        self.pcs = pcs
        self.forte_classification = ForteClassification()
        self.analyzer = SetAnalyzer()

        self.setWindowTitle(f"Full Analysis: {sorted(pcs.pitch_classes)}")
        self.resize(700, 600)
        self._setup_ui()
        self._perform_analysis()

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Title
        forte_num = self.forte_classification.get_forte_number(self.pcs)
        title = QLabel(f"<h2>Pitch Class Set: {sorted(self.pcs.pitch_classes)}</h2>"
                      f"<p><b>Forte Number:</b> {forte_num}</p>")
        layout.addWidget(title)

        # Tab widget for different analysis views
        self.tabs = QTabWidget()

        # Basic properties tab
        self.basic_text = QTextEdit()
        self.basic_text.setReadOnly(True)
        self.tabs.addTab(self.basic_text, "Basic Properties")

        # Transformations tab
        self.transformations_text = QTextEdit()
        self.transformations_text.setReadOnly(True)
        self.tabs.addTab(self.transformations_text, "Transformations")

        # Relations tab
        self.relations_text = QTextEdit()
        self.relations_text.setReadOnly(True)
        self.tabs.addTab(self.relations_text, "Relations")

        # All operations tab
        self.operations_text = QTextEdit()
        self.operations_text.setReadOnly(True)
        self.tabs.addTab(self.operations_text, "All Operations")

        layout.addWidget(self.tabs)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _perform_analysis(self):
        """Perform comprehensive analysis"""
        # Basic properties
        basic_analysis = self._analyze_basic()
        self.basic_text.setPlainText(basic_analysis)

        # Transformations
        transformations_analysis = self._analyze_transformations()
        self.transformations_text.setPlainText(transformations_analysis)

        # Relations
        relations_analysis = self._analyze_relations()
        self.relations_text.setPlainText(relations_analysis)

        # All operations
        operations_analysis = self._analyze_operations()
        self.operations_text.setPlainText(operations_analysis)

    def _analyze_basic(self) -> str:
        """Analyze basic properties"""
        lines = []

        lines.append("=== BASIC PROPERTIES ===\n")

        # Pitch classes
        lines.append(f"Pitch Classes: {sorted(self.pcs.pitch_classes)}")

        # Cardinality
        lines.append(f"Cardinality: {len(self.pcs.pitch_classes)}")

        # Prime form (returns a list, not a PitchClassSet)
        prime = self.pcs.prime_form()
        lines.append(f"Prime Form: {prime}")

        # Normal form
        normal = self.pcs.normal_form()
        lines.append(f"Normal Form: {normal.pitch_classes}")

        # Forte number
        forte_num = self.forte_classification.get_forte_number(self.pcs)
        lines.append(f"Forte Number: {forte_num}")

        # Interval vector
        iv = self.pcs.interval_vector()
        iv_str = ''.join(map(str, iv))
        lines.append(f"Interval Vector: <{iv_str}>")
        lines.append(f"  IC1 (minor 2nd / major 7th): {iv[0]}")
        lines.append(f"  IC2 (major 2nd / minor 7th): {iv[1]}")
        lines.append(f"  IC3 (minor 3rd / major 6th): {iv[2]}")
        lines.append(f"  IC4 (major 3rd / minor 6th): {iv[3]}")
        lines.append(f"  IC5 (perfect 4th / 5th): {iv[4]}")
        lines.append(f"  IC6 (tritone): {iv[5]}")

        # Complement
        complement = self.pcs.complement()
        complement_forte = self.forte_classification.get_forte_number(complement)
        lines.append(f"\nComplement: {sorted(complement.pitch_classes)} ({complement_forte})")

        # Z-partner
        try:
            z_partner = self.forte_classification.get_z_partner(self.pcs)
            if z_partner:
                lines.append(f"Z-Partner: {z_partner}")
            else:
                lines.append("Z-Partner: None")
        except:
            pass

        # Symmetry
        lines.append("\n=== SYMMETRY ===\n")
        if self.pcs == self.pcs.inversion(0):
            lines.append("Inversionally symmetrical (I0 = original)")

        return '\n'.join(lines)

    def _analyze_transformations(self) -> str:
        """Analyze transformations"""
        lines = []

        lines.append("=== TRANSPOSITIONS ===\n")
        for i in range(12):
            t = self.pcs.transposition(i)
            lines.append(f"T{i}: {sorted(t.pitch_classes)}")

        lines.append("\n=== INVERSIONS ===\n")
        for i in range(12):
            inv = self.pcs.inversion(i)
            lines.append(f"I{i}: {sorted(inv.pitch_classes)}")

        return '\n'.join(lines)

    def _analyze_relations(self) -> str:
        """Analyze set relations"""
        lines = []

        lines.append("=== SUBSET ANALYSIS ===\n")

        cardinality = len(self.pcs.pitch_classes)

        for size in range(cardinality - 1, 0, -1):
            subsets = self.pcs.find_subsets(size)
            lines.append(f"\nSubsets of size {size}: ({len(subsets)} sets)")

            for subset in subsets[:10]:  # Limit to first 10
                forte_num = self.forte_classification.get_forte_number(subset)
                lines.append(f"  {sorted(subset.pitch_classes)} ({forte_num})")

            if len(subsets) > 10:
                lines.append(f"  ... and {len(subsets) - 10} more")

        lines.append("\n=== SUPERSET ANALYSIS ===\n")

        for size in range(cardinality + 1, min(cardinality + 3, 13)):
            supersets = self.pcs.find_supersets(size)
            lines.append(f"\nSupersets of size {size}: ({len(supersets)} sets)")

            for superset in supersets[:10]:  # Limit to first 10
                forte_num = self.forte_classification.get_forte_number(superset)
                lines.append(f"  {sorted(superset.pitch_classes)} ({forte_num})")

            if len(supersets) > 10:
                lines.append(f"  ... and {len(supersets) - 10} more")

        return '\n'.join(lines)

    def _analyze_operations(self) -> str:
        """Analyze all operations"""
        lines = []

        lines.append("=== COMPREHENSIVE OPERATIONS ===\n")

        # Rotations
        lines.append("\nRotations:")
        cardinality = len(self.pcs.pitch_classes)
        for i in range(cardinality):
            r = self.pcs.rotation(i)
            lines.append(f"  R{i}: {r.pitch_classes}")

        # Matrix operations (if useful)
        lines.append("\n\n=== TRANSFORMATION MATRIX ===\n")
        lines.append("T\\I  |  0     1     2     3     4     5")
        lines.append("-----|------------------------------------")
        for t in range(6):
            line = f" T{t}  | "
            for i in range(6):
                ti = self.pcs.transposition(t).inversion(i)
                line += f"{sorted(ti.pitch_classes)[:3]}... "
            lines.append(line)

        lines.append("\n(Showing only T0-T5 and I0-I5 for space)")

        return '\n'.join(lines)


# Test dialog
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test with C major triad
    test_set = PitchClassSet([0, 4, 7])
    dialog = FullAnalysisDialog(test_set)

    dialog.exec()

    sys.exit(0)
