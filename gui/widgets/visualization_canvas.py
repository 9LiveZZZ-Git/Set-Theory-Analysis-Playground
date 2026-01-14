"""
Visualization Canvas
Wrapper for matplotlib FigureCanvas with live updates
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import pyqtSlot, Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# Try to import NetworkX for graph visualization
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet


class VisualizationCanvas(QWidget):
    """
    Widget containing matplotlib canvas for visualizations.
    Handles live updates with blitting for performance.
    """

    def __init__(self, parent=None, mode='clock'):
        super().__init__(parent)

        self.mode = mode  # 'clock' or 'graph'
        self.current_set = None
        self.background = None

        self._setup_ui()
        self._draw_static_elements()

    def _setup_ui(self):
        """Setup matplotlib canvas"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Create figure and canvas
        self.figure = Figure(figsize=(8, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                 QSizePolicy.Policy.Expanding)

        # Create axes
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')

        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def _draw_static_elements(self):
        """Draw static elements (clock circle, labels, etc.)"""
        self.ax.clear()
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.axis('off')

        if self.mode == 'clock':
            self._draw_clock_static()
        elif self.mode == 'graph':
            self._draw_graph_static()

        self.canvas.draw()
        # Cache background for blitting
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def _draw_clock_static(self):
        """Draw static clock elements"""
        # Draw clock circle
        circle = plt.Circle((0, 0), 1.0, fill=False, color='black', linewidth=2)
        self.ax.add_patch(circle)

        # Draw pitch class labels and tick marks
        for pc in range(12):
            # Angle (0=C at top, clockwise)
            angle = (90 - pc * 30) * np.pi / 180

            # Tick mark
            x1 = 0.95 * np.cos(angle)
            y1 = 0.95 * np.sin(angle)
            x2 = 1.05 * np.cos(angle)
            y2 = 1.05 * np.sin(angle)
            self.ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1)

            # Label
            x_label = 1.2 * np.cos(angle)
            y_label = 1.2 * np.sin(angle)

            # Pitch class names
            pc_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                       'F#', 'G', 'G#', 'A', 'A#', 'B']
            label = f"{pc}\n{pc_names[pc]}"

            self.ax.text(x_label, y_label, label,
                        ha='center', va='center',
                        fontsize=10, fontweight='bold')

    def _draw_graph_static(self):
        """Draw static grid/graph elements"""
        # Draw a 12x12 grid background showing all possible pitch classes
        # This will serve as the static background for the interval graph

        # Draw a subtle grid
        for i in range(13):
            # Horizontal lines
            self.ax.plot([-1.4, 1.4], [-1.4 + i * 0.233, -1.4 + i * 0.233],
                        'lightgray', linewidth=0.5, alpha=0.3)
            # Vertical lines
            self.ax.plot([-1.4 + i * 0.233, -1.4 + i * 0.233], [-1.4, 1.4],
                        'lightgray', linewidth=0.5, alpha=0.3)

        # Add title
        self.ax.text(0, 1.35, "Interval Network Graph",
                    ha='center', va='center', fontsize=12, fontweight='bold')

    @pyqtSlot(PitchClassSet)
    def update_visualization(self, pcs: PitchClassSet):
        """
        Update visualization with new pitch class set.
        Uses blitting for performance.

        Args:
            pcs: PitchClassSet to visualize
        """
        if pcs is None:
            self._clear_visualization()
            return

        self.current_set = pcs

        if self.mode == 'clock':
            self._update_clock(pcs)
        elif self.mode == 'graph':
            self._update_graph(pcs)

        self.canvas.draw()

    def _update_clock(self, pcs: PitchClassSet):
        """Update clock visualization"""
        # Restore background (remove old pitch classes)
        if self.background:
            self.canvas.restore_region(self.background)

        # Draw pitch class dots and lines
        for pc in pcs.pitch_classes:
            angle = (90 - pc * 30) * np.pi / 180
            x = 0.8 * np.cos(angle)
            y = 0.8 * np.sin(angle)

            # Line to center
            line, = self.ax.plot([0, x], [0, y], 'b-', linewidth=2, alpha=0.5)

            # Dot
            dot, = self.ax.plot([x], [y], 'ro', markersize=15)

        # Update canvas
        self.canvas.draw()

    def _update_graph(self, pcs: PitchClassSet):
        """Update graph visualization - shows interval network"""
        self.ax.clear()
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-1.5, 1.5)
        self.ax.axis('off')

        if NETWORKX_AVAILABLE and len(pcs.pitch_classes) > 0:
            # Create a network graph
            G = nx.Graph()

            # Add nodes for each pitch class
            pitch_classes = sorted(pcs.pitch_classes)
            for pc in pitch_classes:
                G.add_node(pc)

            # Add edges between all pitch classes (complete graph)
            # Edge weight = interval class between them
            for i, pc1 in enumerate(pitch_classes):
                for pc2 in pitch_classes[i+1:]:
                    interval = min((pc2 - pc1) % 12, (pc1 - pc2) % 12)
                    if interval > 6:
                        interval = 12 - interval
                    G.add_edge(pc1, pc2, weight=interval)

            # Use circular layout for pitch classes
            pos = {}
            for i, pc in enumerate(pitch_classes):
                angle = 2 * np.pi * i / len(pitch_classes)
                pos[pc] = (np.cos(angle), np.sin(angle))

            # Pitch class names
            pc_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                       'F#', 'G', 'G#', 'A', 'A#', 'B']

            # Draw edges with different colors based on interval class
            interval_colors = {
                1: '#FF6B6B',  # Minor 2nd - red
                2: '#FFA06B',  # Major 2nd - orange
                3: '#FFD93D',  # Minor 3rd - yellow
                4: '#6BCF7F',  # Major 3rd - green
                5: '#6BAFCF',  # Perfect 4th - blue
                6: '#9B6BCF'   # Tritone - purple
            }

            for (u, v, d) in G.edges(data=True):
                interval = d['weight']
                color = interval_colors.get(interval, 'gray')
                x = [pos[u][0], pos[v][0]]
                y = [pos[u][1], pos[v][1]]
                self.ax.plot(x, y, color=color, linewidth=2, alpha=0.6, zorder=1)

            # Draw nodes
            for pc in pitch_classes:
                x, y = pos[pc]
                # Node circle
                circle = plt.Circle((x, y), 0.15, color='steelblue',
                                   ec='darkblue', linewidth=2, zorder=2)
                self.ax.add_patch(circle)

                # Label
                self.ax.text(x, y, f"{pc}\n{pc_names[pc]}",
                           ha='center', va='center',
                           fontsize=9, fontweight='bold',
                           color='white', zorder=3)

            # Add interval class legend
            legend_y = -1.3
            legend_x_start = -1.2
            legend_x_step = 0.4
            for i, (ic, color) in enumerate(interval_colors.items()):
                x = legend_x_start + (i % 3) * legend_x_step
                y = legend_y - (i // 3) * 0.15
                self.ax.plot([x, x + 0.15], [y, y], color=color,
                           linewidth=2, alpha=0.6)
                self.ax.text(x + 0.2, y, f"IC{ic}",
                           fontsize=7, va='center')

            # Title
            self.ax.text(0, 1.3, f"Interval Network ({len(pitch_classes)} nodes)",
                        ha='center', va='center',
                        fontsize=11, fontweight='bold')

        else:
            # Fallback if NetworkX not available - show simple scatter plot
            if len(pcs.pitch_classes) > 0:
                pitch_classes = sorted(pcs.pitch_classes)
                angles = [2 * np.pi * i / len(pitch_classes) for i in range(len(pitch_classes))]
                x = [np.cos(angle) for angle in angles]
                y = [np.sin(angle) for angle in angles]

                # Draw connections
                for i in range(len(pitch_classes)):
                    for j in range(i+1, len(pitch_classes)):
                        self.ax.plot([x[i], x[j]], [y[i], y[j]],
                                   'b-', linewidth=1, alpha=0.3)

                # Draw nodes
                pc_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                           'F#', 'G', 'G#', 'A', 'A#', 'B']
                for i, pc in enumerate(pitch_classes):
                    circle = plt.Circle((x[i], y[i]), 0.15, color='steelblue',
                                       ec='darkblue', linewidth=2)
                    self.ax.add_patch(circle)
                    self.ax.text(x[i], y[i], f"{pc}\n{pc_names[pc]}",
                               ha='center', va='center',
                               fontsize=9, fontweight='bold', color='white')

                self.ax.text(0, 1.3, "Simple Network View",
                           ha='center', va='center',
                           fontsize=11, fontweight='bold')

        self.canvas.draw()

    def _clear_visualization(self):
        """Clear the visualization"""
        self._draw_static_elements()

    def set_mode(self, mode: str):
        """
        Change visualization mode

        Args:
            mode: 'clock' or 'graph'
        """
        if mode != self.mode:
            self.mode = mode
            self._draw_static_elements()
            if self.current_set:
                self.update_visualization(self.current_set)


# Test canvas
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Visualization Canvas Test")

    canvas = VisualizationCanvas(mode='clock')
    window.setCentralWidget(canvas)

    # Test with a set
    test_set = PitchClassSet([0, 4, 7])  # C major triad
    canvas.update_visualization(test_set)

    window.resize(600, 600)
    window.show()

    sys.exit(app.exec())
