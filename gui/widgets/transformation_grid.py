"""
Transformation Grid Widget
Displays a grid of mini pitch class clocks for transformations
"""

from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
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


class MiniClockWidget(QWidget):
    """
    Mini pitch class clock for grid display
    """

    clicked = pyqtSignal(int)  # Emits index when clicked

    def __init__(self, index=0, parent=None):
        super().__init__(parent)

        self.index = index
        self.current_set = None

        # Create matplotlib figure
        self.figure = Figure(figsize=(2, 2), dpi=50)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Make clickable
        self.canvas.mpl_connect('button_press_event', self._on_click)

        self._draw_empty()

    def _draw_empty(self):
        """Draw empty clock"""
        self.ax.clear()
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')

        # Draw circle
        circle = plt.Circle((0, 0), 1.0, fill=False, color='lightgray', linewidth=1)
        self.ax.add_patch(circle)

        self.canvas.draw()

    def update_set(self, pcs: PitchClassSet, label: str = ""):
        """Update with a pitch class set"""
        self.current_set = pcs
        self.ax.clear()
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis('off')

        # Draw circle
        circle = plt.Circle((0, 0), 1.0, fill=False, color='black', linewidth=1.5)
        self.ax.add_patch(circle)

        if pcs:
            # Draw pitch class dots
            for pc in pcs.pitch_classes:
                angle = (90 - pc * 30) * np.pi / 180
                x = 0.75 * np.cos(angle)
                y = 0.75 * np.sin(angle)

                # Dot
                self.ax.plot([x], [y], 'ro', markersize=6)

                # Line to center
                self.ax.plot([0, x], [0, y], 'b-', linewidth=1, alpha=0.3)

        # Add label
        if label:
            self.ax.text(0, -1.5, label, ha='center', va='top',
                        fontsize=8, fontweight='bold')

        self.canvas.draw()

    def _on_click(self, event):
        """Handle click on canvas"""
        self.clicked.emit(self.index)


class TransformationGrid(QWidget):
    """
    Grid of mini pitch class clocks showing transformations
    """

    transformationClicked = pyqtSignal(str, int)  # (type, value)

    def __init__(self, rows=3, cols=4, parent=None):
        super().__init__(parent)

        self.rows = rows
        self.cols = cols
        self.current_set = None
        self.transformation_type = 'T'  # 'T', 'I', 'R', or 'RI'

        self.clocks = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup grid layout"""
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Create mini clocks
        index = 0
        for row in range(self.rows):
            for col in range(self.cols):
                clock = MiniClockWidget(index=index)
                clock.clicked.connect(self._on_clock_clicked)
                layout.addWidget(clock, row, col)
                self.clocks.append(clock)
                index += 1

        self.setLayout(layout)

    def _on_clock_clicked(self, index):
        """Handle clock clicked"""
        self.transformationClicked.emit(self.transformation_type, index)

    def set_transformation_type(self, trans_type: str):
        """Set transformation type ('T', 'I', 'R', 'RI')"""
        self.transformation_type = trans_type
        if self.current_set:
            self.update_transformations(self.current_set)

    def update_transformations(self, pcs: PitchClassSet):
        """Update grid with transformations of given set"""
        self.current_set = pcs

        if not pcs:
            # Clear all clocks
            for clock in self.clocks:
                clock._draw_empty()
            return

        # Generate transformations
        for i in range(12):
            if i < len(self.clocks):
                if self.transformation_type == 'T':
                    transformed = pcs.transposition(i)
                    label = f"T{i}"
                elif self.transformation_type == 'I':
                    transformed = pcs.inversion(i)
                    label = f"I{i}"
                elif self.transformation_type == 'R':
                    # Retrograde + transposition (RT)
                    # RT0 = retrograde of original, RT1 = retrograde + transpose by 1, etc.
                    transformed = pcs.retrograde().transposition(i)
                    label = f"RT{i}"
                elif self.transformation_type == 'RI':
                    # Retrograde inversion
                    transformed = pcs.retrograde_inversion(i)
                    label = f"RI{i}"
                else:
                    transformed = pcs
                    label = str(i)

                self.clocks[i].update_set(transformed, label)


# Test grid
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Transformation Grid Test")

    grid = TransformationGrid()

    # Connect signal
    grid.transformationClicked.connect(
        lambda t, v: print(f"Clicked: {t}{v}")
    )

    # Test with C major triad
    test_set = PitchClassSet([0, 4, 7])
    grid.set_transformation_type('T')
    grid.update_transformations(test_set)

    window.setCentralWidget(grid)
    window.resize(600, 450)
    window.show()

    sys.exit(app.exec())
