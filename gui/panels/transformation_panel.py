"""
Transformation Preview Panel
Right dock showing transformation previews (T0-T11, I0-I11, etc.)
"""

from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QTabWidget,
                              QLabel, QPushButton, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from pitch_class_set import PitchClassSet

# Import transformation grid
sys.path.insert(0, str(Path(__file__).parent.parent))
from widgets.transformation_grid import TransformationGrid


class TransformationPanel(QDockWidget):
    """
    Dockable panel showing transformation previews.
    Uses tabs for different transformation types.
    """

    transformationSelected = pyqtSignal(str, int)  # (type, value)
    playAllRequested = pyqtSignal(str)  # (transformation_type) - Play all T0-T11, I0-I11, etc.

    def __init__(self, parent=None):
        super().__init__("Transformation Previews", parent)

        self.current_set = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI components"""
        # Main widget
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Info label
        info_label = QLabel("Click any transformation to apply it")
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info_label)

        # Tab widget for different transformation types
        self.tabs = QTabWidget()

        # Transposition tab
        self.t_grid = TransformationGrid(rows=3, cols=4)
        self.t_grid.set_transformation_type('T')
        self.t_grid.transformationClicked.connect(self.transformationSelected)
        t_tab = self._create_tab_with_button(self.t_grid, 'T', "🎵 Play All T0-T11")
        self.tabs.addTab(t_tab, "Transpositions")

        # Inversion tab
        self.i_grid = TransformationGrid(rows=3, cols=4)
        self.i_grid.set_transformation_type('I')
        self.i_grid.transformationClicked.connect(self.transformationSelected)
        i_tab = self._create_tab_with_button(self.i_grid, 'I', "🎵 Play All I0-I11")
        self.tabs.addTab(i_tab, "Inversions")

        # Retrograde tab
        self.r_grid = TransformationGrid(rows=3, cols=4)
        self.r_grid.set_transformation_type('R')
        self.r_grid.transformationClicked.connect(self.transformationSelected)
        r_tab = self._create_tab_with_button(self.r_grid, 'R', "🎵 Play All RT0-RT11")
        self.tabs.addTab(r_tab, "Retrogrades")

        # Retrograde Inversion tab
        self.ri_grid = TransformationGrid(rows=3, cols=4)
        self.ri_grid.set_transformation_type('RI')
        self.ri_grid.transformationClicked.connect(self.transformationSelected)
        ri_tab = self._create_tab_with_button(self.ri_grid, 'RI', "🎵 Play All RI0-RI11")
        self.tabs.addTab(ri_tab, "RI")

        # Only update visible tab (performance optimization)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

        widget.setLayout(layout)
        self.setWidget(widget)

        # Set dockwidget properties
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea |
                            Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                        QDockWidget.DockWidgetFeature.DockWidgetClosable)

    def _create_tab_with_button(self, grid_widget, trans_type: str, button_text: str):
        """Create a tab containing a grid and a Play All button"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(2, 2, 2, 2)

        # Add grid
        tab_layout.addWidget(grid_widget)

        # Add Play All button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        play_all_btn = QPushButton(button_text)
        play_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        play_all_btn.clicked.connect(lambda: self.playAllRequested.emit(trans_type))
        button_layout.addWidget(play_all_btn)
        button_layout.addStretch()

        tab_layout.addLayout(button_layout)
        tab_widget.setLayout(tab_layout)

        return tab_widget

    def _on_tab_changed(self, index):
        """Handle tab change - update visible grid"""
        if self.current_set:
            # Get the grid from the current tab
            grid = self._get_grid_for_tab(index)
            if grid:
                grid.update_transformations(self.current_set)

    def _get_grid_for_tab(self, index):
        """Get the transformation grid for a given tab index"""
        if index == 0:
            return self.t_grid
        elif index == 1:
            return self.i_grid
        elif index == 2:
            return self.r_grid
        elif index == 3:
            return self.ri_grid
        return None

    @pyqtSlot(PitchClassSet)
    def update_transformations(self, pcs: PitchClassSet):
        """
        Update transformation previews for new set.
        Only updates currently visible tab for performance.

        Args:
            pcs: PitchClassSet to show transformations of
        """
        if pcs is None:
            self.current_set = None
            # Clear all grids
            self.t_grid.update_transformations(None)
            self.i_grid.update_transformations(None)
            self.r_grid.update_transformations(None)
            self.ri_grid.update_transformations(None)
            return

        self.current_set = pcs

        # Update currently visible tab
        current_index = self.tabs.currentIndex()
        grid = self._get_grid_for_tab(current_index)
        if grid:
            grid.update_transformations(pcs)


# Test panel
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Transformation Panel Test")

    panel = TransformationPanel()
    window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, panel)

    # Test with a set
    test_set = PitchClassSet([0, 4, 7])
    panel.update_transformations(test_set)

    # Connect signals
    panel.transformationSelected.connect(
        lambda t, v: print(f"Transformation selected: {t}{v}")
    )

    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
