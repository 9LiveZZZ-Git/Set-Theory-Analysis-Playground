"""
Interval Vector Visualization Dialog
Shows a bar chart of the interval vector for a pitch class set
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                              QHBoxLayout, QWidget)
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet


class IntervalVectorDialog(QDialog):
    """
    Dialog showing interval vector as a bar chart
    """

    def __init__(self, pcs: PitchClassSet, parent=None):
        super().__init__(parent)

        self.pcs = pcs
        self.setWindowTitle("Interval Vector Visualization")
        self.resize(700, 500)
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI layout"""
        layout = QVBoxLayout()

        # Title
        title = QLabel(f"<h2>Interval Vector for Set: {sorted(self.pcs.pitch_classes)}</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Interval vector text
        iv = self.pcs.interval_vector()
        iv_str = ''.join(map(str, iv))
        iv_label = QLabel(f"<b>Interval Vector:</b> &lt;{iv_str}&gt;")
        iv_label.setStyleSheet("font-size: 14pt; padding: 10px;")
        iv_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(iv_label)

        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Draw the chart
        self._draw_chart()

        # Info text
        info_text = QLabel(
            "<p style='color: gray;'>"
            "<b>Interval Classes:</b><br>"
            "IC1 = minor 2nd / major 7th<br>"
            "IC2 = major 2nd / minor 7th<br>"
            "IC3 = minor 3rd / major 6th<br>"
            "IC4 = major 3rd / minor 6th<br>"
            "IC5 = perfect 4th / perfect 5th<br>"
            "IC6 = tritone (augmented 4th / diminished 5th)"
            "</p>"
        )
        info_text.setWordWrap(True)
        layout.addWidget(info_text)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _draw_chart(self):
        """Draw the interval vector bar chart"""
        iv = self.pcs.interval_vector()

        # Create subplot
        ax = self.figure.add_subplot(111)
        ax.clear()

        # Interval class labels
        ic_labels = ['IC1\n(m2/M7)', 'IC2\n(M2/m7)', 'IC3\n(m3/M6)',
                     'IC4\n(M3/m6)', 'IC5\n(P4/P5)', 'IC6\n(Tritone)']

        # Colors (similar to the graph visualization)
        colors = ['#FF6B6B', '#FFA06B', '#FFD93D', '#6BCF7F', '#6BAFCF', '#9B6BCF']

        # Create bar chart
        x = np.arange(len(iv))
        bars = ax.bar(x, iv, color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)

        # Customize chart
        ax.set_xlabel('Interval Class', fontsize=12, fontweight='bold')
        ax.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax.set_title(f'Interval Vector Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(ic_labels, fontsize=10)
        ax.set_ylim(0, max(iv) + 1)
        ax.set_yticks(range(0, max(iv) + 2))
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, iv)):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, value + 0.1,
                       str(value),
                       ha='center', va='bottom',
                       fontsize=12, fontweight='bold')

        # Add set info as subtitle
        ax.text(0.5, -0.15, f"Pitch Class Set: {sorted(self.pcs.pitch_classes)}  |  "
                f"Cardinality: {len(self.pcs.pitch_classes)}",
                ha='center', va='top',
                transform=ax.transAxes,
                fontsize=10, style='italic', color='gray')

        self.figure.tight_layout()
        self.canvas.draw()


# Test dialog
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test with C major triad
    test_set = PitchClassSet([0, 4, 7])
    dialog = IntervalVectorDialog(test_set)

    dialog.exec()

    sys.exit(0)
