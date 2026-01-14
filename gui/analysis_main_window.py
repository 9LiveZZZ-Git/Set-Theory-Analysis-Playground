"""
Analysis-Only Main Window for Set Theory GUI Application
Stripped-down version without the Composer tab
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QSplitter, QMessageBox,
                              QStatusBar, QMenuBar, QMenu, QFileDialog, QLabel,
                              QVBoxLayout, QHBoxLayout, QPushButton)
from PyQt6.QtCore import Qt, pyqtSlot, QEvent
from PyQt6.QtGui import QAction, QKeySequence
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification

# Import GUI components (analysis only - no composer)
from gui.panels.set_input_panel import SetInputPanel
from gui.panels.analysis_panel import AnalysisPanel
from gui.panels.transformation_panel import TransformationPanel
from gui.panels.subset_explorer import SubsetExplorer
from gui.widgets.visualization_canvas import VisualizationCanvas
from gui.widgets.forte_selector import ForteSelector
from gui.widgets.audio_settings_dialog import AudioSettingsDialog
from gui.widgets.full_analysis_dialog import FullAnalysisDialog
from gui.widgets.music_examples_dialog import MusicExamplesDialog
from gui.widgets.interval_vector_dialog import IntervalVectorDialog
from gui.widgets.compare_sets_dialog import CompareSetsDialog
from gui.widgets.find_similar_dialog import FindSimilarDialog
from gui.audio.audio_manager import AudioManager
from gui.utils.settings_manager import SettingsManager
from gui.utils.midi_export import MIDIExporter


class AnalysisMainWindow(QMainWindow):
    """
    Analysis-only application window with:
    - Menu bar
    - Left panel (set input)
    - Central visualization canvas
    - Bottom dock (analysis)
    - Status bar

    No Composer tab included.
    """

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.settings_manager = SettingsManager()
        audio_settings = self.settings_manager.get_audio_settings()
        self.audio_manager = AudioManager(audio_settings)
        self.forte_classification = ForteClassification()

        # Current state
        self.current_set = None
        self.is_playing_queue = False

        # Setup UI
        self.setWindowTitle("Allen Forte Set Theory - Analysis")
        self._setup_ui()
        self._create_menu_bar()
        self._create_status_bar()
        self._connect_signals()
        self._restore_settings()

    def _setup_ui(self):
        """Setup main UI layout (analysis only - no tabs)"""
        # Create main splitter directly (no tab widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel (set input)
        self.input_panel = SetInputPanel()
        self.input_panel.setMaximumWidth(350)
        splitter.addWidget(self.input_panel)

        # Center (visualization canvas)
        self.visualization_canvas = VisualizationCanvas(mode='clock')
        splitter.addWidget(self.visualization_canvas)

        # Set splitter proportions (30% left, 70% right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        # Set splitter as central widget
        self.setCentralWidget(splitter)

        # Bottom dock (analysis panel)
        self.analysis_panel = AnalysisPanel()
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.analysis_panel)

        # Right dock (transformation preview panel)
        self.transformation_panel = TransformationPanel()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.transformation_panel)

        # Right dock (subset explorer) - tabify with transformation panel
        self.subset_explorer = SubsetExplorer()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.subset_explorer)
        self.tabifyDockWidget(self.transformation_panel, self.subset_explorer)

        # Show transformation panel by default
        self.transformation_panel.raise_()

        # Set initial size
        self.resize(1400, 900)

    def _create_menu_bar(self):
        """Create menu bar with all commands"""
        menubar = self.menuBar()

        # === FILE MENU ===
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Set", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_set)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        export_midi_action = QAction("Export to &MIDI...", self)
        export_midi_action.setShortcut(QKeySequence("Ctrl+M"))
        export_midi_action.triggered.connect(self._on_export_midi)
        file_menu.addAction(export_midi_action)

        # Export All Transformations submenu
        export_all_menu = QMenu("Export All &Transformations", self)
        file_menu.addMenu(export_all_menu)

        export_all_t_action = QAction("All Transpositions (T0-T11)...", self)
        export_all_t_action.triggered.connect(lambda: self._on_export_all_transformations('T'))
        export_all_menu.addAction(export_all_t_action)

        export_all_i_action = QAction("All Inversions (I0-I11)...", self)
        export_all_i_action.triggered.connect(lambda: self._on_export_all_transformations('I'))
        export_all_menu.addAction(export_all_i_action)

        export_all_r_action = QAction("All Retrogrades (RT0-RT11)...", self)
        export_all_r_action.triggered.connect(lambda: self._on_export_all_transformations('R'))
        export_all_menu.addAction(export_all_r_action)

        export_all_ri_action = QAction("All Retrograde Inversions (RI0-RI11)...", self)
        export_all_ri_action.triggered.connect(lambda: self._on_export_all_transformations('RI'))
        export_all_menu.addAction(export_all_ri_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # === EDIT MENU ===
        edit_menu = menubar.addMenu("&Edit")

        preferences_action = QAction("&Preferences...", self)
        preferences_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(preferences_action)

        # === OPERATIONS MENU ===
        operations_menu = menubar.addMenu("&Operations")

        transpose_action = QAction("&Transpose...", self)
        transpose_action.setShortcut(QKeySequence("Ctrl+T"))
        transpose_action.triggered.connect(lambda: self._on_transformation('T'))
        operations_menu.addAction(transpose_action)

        invert_action = QAction("&Invert...", self)
        invert_action.setShortcut(QKeySequence("Ctrl+I"))
        invert_action.triggered.connect(lambda: self._on_transformation('I'))
        operations_menu.addAction(invert_action)

        rotate_action = QAction("&Rotate...", self)
        rotate_action.setShortcut(QKeySequence("Ctrl+R"))
        rotate_action.triggered.connect(lambda: self._on_transformation('R'))
        operations_menu.addAction(rotate_action)

        # === ANALYSIS MENU ===
        analysis_menu = menubar.addMenu("&Analysis")

        analyze_action = QAction("&Analyze Set", self)
        analyze_action.setShortcut(QKeySequence("Ctrl+A"))
        analyze_action.triggered.connect(self._on_analyze)
        analysis_menu.addAction(analyze_action)

        iv_viz_action = QAction("Show &Interval Vector Chart", self)
        iv_viz_action.setShortcut(QKeySequence("Ctrl+Shift+I"))
        iv_viz_action.triggered.connect(self._on_show_interval_vector)
        analysis_menu.addAction(iv_viz_action)

        compare_sets_action = QAction("&Compare Two Sets...", self)
        compare_sets_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        compare_sets_action.triggered.connect(self._on_compare_sets)
        analysis_menu.addAction(compare_sets_action)

        # === TOOLS MENU ===
        tools_menu = menubar.addMenu("&Tools")

        forte_dir_action = QAction("&Forte Directory", self)
        forte_dir_action.setShortcut(QKeySequence("Ctrl+F"))
        forte_dir_action.triggered.connect(self._on_forte_directory)
        tools_menu.addAction(forte_dir_action)

        music_examples_action = QAction("&Music Examples", self)
        music_examples_action.setShortcut(QKeySequence("Ctrl+E"))
        music_examples_action.triggered.connect(self._on_music_examples)
        tools_menu.addAction(music_examples_action)

        find_similar_action = QAction("Find &Similar Sets...", self)
        find_similar_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        find_similar_action.triggered.connect(self._on_find_similar)
        tools_menu.addAction(find_similar_action)

        # === AUDIO MENU ===
        audio_menu = menubar.addMenu("A&udio")

        play_action = QAction("&Play", self)
        play_action.setShortcut(QKeySequence("Ctrl+P"))
        play_action.triggered.connect(lambda: self._on_play(False))
        audio_menu.addAction(play_action)

        play_arp_action = QAction("Play &Arpeggiated", self)
        play_arp_action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        play_arp_action.triggered.connect(lambda: self._on_play(True))
        audio_menu.addAction(play_arp_action)

        audio_menu.addSeparator()

        audio_settings_action = QAction("Audio &Settings...", self)
        audio_settings_action.triggered.connect(self._on_audio_settings)
        audio_menu.addAction(audio_settings_action)

        # === VIEW MENU ===
        view_menu = menubar.addMenu("&View")

        toggle_analysis_action = QAction("Show/Hide &Analysis Panel", self)
        toggle_analysis_action.triggered.connect(self._toggle_analysis_panel)
        view_menu.addAction(toggle_analysis_action)

        view_menu.addSeparator()

        clock_mode_action = QAction("&Clock Visualization", self)
        clock_mode_action.triggered.connect(lambda: self._set_viz_mode('clock'))
        view_menu.addAction(clock_mode_action)

        graph_mode_action = QAction("&Graph Visualization", self)
        graph_mode_action.triggered.connect(lambda: self._set_viz_mode('graph'))
        view_menu.addAction(graph_mode_action)

        # === HELP MENU ===
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """Create status bar with hover help"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Create hover help label (permanent widget on left)
        self.hover_help_label = QLabel("Hover over any feature for help")
        self.hover_help_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
        self.status_bar.addPermanentWidget(self.hover_help_label, 1)

        # Create stop button (hidden by default)
        self.stop_audio_button = QPushButton("Stop Playback")
        self.stop_audio_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 4px 12px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.stop_audio_button.clicked.connect(self._on_stop_audio)
        self.stop_audio_button.hide()
        self.status_bar.addPermanentWidget(self.stop_audio_button)

        # Create audio status label (permanent widget on right)
        self.audio_status_label = QLabel()
        if self.audio_manager.is_available():
            self.audio_status_label.setText("Audio: Initializing...")
        else:
            self.audio_status_label.setText("Audio: MIDI Export Only")
        self.audio_status_label.setStyleSheet("QLabel { color: #444; }")
        self.status_bar.addPermanentWidget(self.audio_status_label)

        # Install event filter on main window to catch all hover events
        self.installEventFilter(self)

    def _connect_signals(self):
        """Connect signals between components"""
        # Input panel -> update visualization and analysis
        self.input_panel.setChanged.connect(self._on_set_changed)
        self.input_panel.transformationRequested.connect(self._on_transformation_from_panel)
        self.input_panel.playRequested.connect(self._on_play)
        self.input_panel.visualizeRequested.connect(self._on_visualize)
        self.input_panel.analyzeRequested.connect(self._on_analyze)
        self.input_panel.forteDirectoryRequested.connect(self._on_forte_directory)

        # Analysis panel
        self.analysis_panel.fullAnalysisRequested.connect(self._on_full_analysis)
        self.analysis_panel.forteNumberClicked.connect(self._on_forte_number_clicked)

        # Transformation panel
        self.transformation_panel.transformationSelected.connect(self._on_transformation_clicked)
        self.transformation_panel.playAllRequested.connect(self._on_play_all_transformations)

        # Subset explorer
        self.subset_explorer.setSelected.connect(self._on_subset_selected)

        # Audio manager signals
        if self.audio_manager.engine:
            self.audio_manager.playback_started.connect(self._on_playback_started)
            self.audio_manager.playback_finished.connect(self._on_playback_finished)
            self.audio_manager.error_occurred.connect(
                lambda msg: self.status_bar.showMessage(f"Audio error: {msg}", 5000))

            # Listen for initialization completion
            if hasattr(self.audio_manager.engine, 'worker') and self.audio_manager.engine.worker:
                self.audio_manager.engine.worker.initialization_complete.connect(self._on_audio_init_complete)

    def _on_audio_init_complete(self, success: bool):
        """Handle audio initialization completion"""
        if success:
            engine_name = "FluidSynth" if self.audio_manager.engine.engine_type == 'fluidsynth' else "python-rtmidi"
            self.audio_status_label.setText(f"Audio: {engine_name} Ready")
            self.audio_status_label.setStyleSheet("QLabel { color: green; }")
        else:
            self.audio_status_label.setText("Audio: Initialization Failed")
            self.audio_status_label.setStyleSheet("QLabel { color: red; }")

    def _on_playback_started(self):
        """Handle playback started - show stop button"""
        self.stop_audio_button.show()
        self.status_bar.showMessage("Playing...", 2000)

    def _on_playback_finished(self):
        """Handle playback finished - hide stop button"""
        if not self.is_playing_queue:
            self.stop_audio_button.hide()
        self.status_bar.showMessage("Playback finished", 2000)

    @pyqtSlot(PitchClassSet)
    def _on_set_changed(self, pcs: PitchClassSet):
        """Handle set change from input panel"""
        self.current_set = pcs

        # Update visualization
        self.visualization_canvas.update_visualization(pcs)

        # Update analysis
        self.analysis_panel.update_analysis(pcs)

        # Update transformation previews
        self.transformation_panel.update_transformations(pcs)

        # Update subset explorer
        self.subset_explorer.update_set(pcs)

        # Add to recent
        self.input_panel.add_to_recent(pcs)
        self.settings_manager.add_recent_set(sorted(pcs.pitch_classes))

        # Update status bar
        forte_num = self.forte_classification.get_forte_number(pcs)
        self.status_bar.showMessage(f"Set: {sorted(pcs.pitch_classes)} | Forte: {forte_num}", 5000)

    @pyqtSlot(str, int)
    def _on_transformation_from_panel(self, trans_type: str, value: int):
        """Handle transformation request from panel"""
        if not self.current_set:
            return

        try:
            if trans_type == 'T':
                transformed = self.current_set.transposition(value)
                self.status_bar.showMessage(f"Applied T{value}", 3000)
            elif trans_type == 'I':
                transformed = self.current_set.inversion(value)
                self.status_bar.showMessage(f"Applied I{value}", 3000)
            elif trans_type == 'R':
                transformed = self.current_set.rotation(value)
                self.status_bar.showMessage(f"Applied R{value}", 3000)
            else:
                return

            self.input_panel.set_current_set(transformed)

        except Exception as e:
            QMessageBox.warning(self, "Transformation Error", str(e))

    def _on_transformation(self, trans_type: str):
        """Handle transformation from menu"""
        if trans_type == 'T':
            self.input_panel.t_button.click()
        elif trans_type == 'I':
            self.input_panel.i_button.click()
        elif trans_type == 'R':
            self.input_panel.r_button.click()

    def _on_play(self, arpeggiate: bool):
        """Handle play request"""
        if not self.current_set:
            QMessageBox.information(self, "No Set", "Please enter a pitch class set first.")
            return

        try:
            self.audio_manager.play_set(self.current_set, arpeggiate)
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", str(e))

    def _on_export_midi(self):
        """Export current set to MIDI file"""
        if not self.current_set:
            QMessageBox.information(self, "No Set", "Please enter a pitch class set first.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export to MIDI", "", "MIDI Files (*.mid)")

        if filename:
            try:
                success = self.audio_manager.export_to_midi(self.current_set, filename, arpeggiate=True)
                if success:
                    QMessageBox.information(self, "Export Successful",
                                          f"Exported to {filename}")
                else:
                    QMessageBox.warning(self, "Export Failed",
                                       "Could not export MIDI file.")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def _on_export_all_transformations(self, trans_type: str):
        """Export all transformations to a multi-track MIDI file"""
        if not self.current_set:
            QMessageBox.information(self, "No Set", "Please enter a pitch class set first.")
            return

        type_names = {'T': 'Transpositions', 'I': 'Inversions', 'R': 'Retrogrades', 'RI': 'Retrograde_Inversions'}
        default_name = f"set_{'-'.join(map(str, sorted(self.current_set.pitch_classes)))}_{type_names[trans_type]}.mid"

        filename, _ = QFileDialog.getSaveFileName(
            self, f"Export All {type_names[trans_type]}", default_name, "MIDI Files (*.mid)")

        if filename:
            try:
                audio_settings = self.settings_manager.get_audio_settings()
                exporter = MIDIExporter(
                    octave=audio_settings.octave,
                    bpm=audio_settings.tempo,
                    duration=audio_settings.duration
                )

                if trans_type == 'T':
                    success = exporter.export_all_transpositions(self.current_set, filename, arpeggiate=True)
                elif trans_type == 'I':
                    success = exporter.export_all_inversions(self.current_set, filename, arpeggiate=True)
                elif trans_type == 'R':
                    success = exporter.export_all_retrogrades(self.current_set, filename, arpeggiate=True)
                elif trans_type == 'RI':
                    success = exporter.export_all_retrograde_inversions(self.current_set, filename, arpeggiate=True)
                else:
                    success = False

                if success:
                    QMessageBox.information(self, "Export Successful",
                                          f"Exported all {type_names[trans_type]} to:\n{filename}\n\n"
                                          f"Each transformation is on a separate MIDI track.")
                else:
                    QMessageBox.warning(self, "Export Failed",
                                       "Could not export MIDI file.")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def _on_visualize(self):
        """Handle visualize request"""
        self.status_bar.showMessage("Visualization updated", 2000)

    def _on_analyze(self):
        """Handle analyze request"""
        self.status_bar.showMessage("See analysis panel below", 2000)

    def _on_full_analysis(self):
        """Show full analysis dialog"""
        if not self.current_set:
            QMessageBox.information(self, "No Set", "Please enter a pitch class set first.")
            return

        dialog = FullAnalysisDialog(self.current_set, self)
        dialog.exec()

    def _on_show_interval_vector(self):
        """Show interval vector chart dialog"""
        if not self.current_set:
            QMessageBox.information(self, "No Set", "Please enter a pitch class set first.")
            return

        dialog = IntervalVectorDialog(self.current_set, self)
        dialog.exec()

    def _on_compare_sets(self):
        """Show compare sets dialog"""
        dialog = CompareSetsDialog(self.current_set, self)
        dialog.exec()

    def _on_forte_directory(self):
        """Show Forte directory browser"""
        dialog = ForteSelector(self)
        dialog.setSelected.connect(self._on_forte_set_selected)
        dialog.exec()

    def _on_forte_set_selected(self, pcs: PitchClassSet, forte_num: str):
        """Handle set selected from Forte directory"""
        self.input_panel.set_current_set(pcs)
        self.status_bar.showMessage(f"Loaded Forte {forte_num}", 3000)

    def _on_music_examples(self):
        """Show music examples browser"""
        dialog = MusicExamplesDialog(self)
        dialog.exampleSelected.connect(self._on_example_selected)
        dialog.exec()

    def _on_example_selected(self, pcs: PitchClassSet, example_name: str):
        """Handle example selected from music examples browser"""
        self.input_panel.set_current_set(pcs)
        self.status_bar.showMessage(f"Loaded example: {example_name}", 3000)

    def _on_find_similar(self):
        """Find sets similar to the current set"""
        if not self.current_set:
            QMessageBox.information(self, "No Set", "Please enter a pitch class set first.")
            return

        dialog = FindSimilarDialog(self.current_set, self)
        dialog.setSelected.connect(self._on_forte_set_selected)
        dialog.exec()

    def _on_forte_number_clicked(self, forte_num: str):
        """Handle Forte number clicked in analysis panel"""
        self.status_bar.showMessage(f"Forte number: {forte_num} (click Forte Directory to browse)", 3000)

    def _on_audio_settings(self):
        """Show audio settings dialog"""
        current_settings = self.settings_manager.get_audio_settings()
        dialog = AudioSettingsDialog(current_settings, self)

        def on_settings_changed(new_settings):
            self.settings_manager.set_audio_settings(new_settings)
            self.audio_manager.update_settings(new_settings)
            self.status_bar.showMessage("Audio settings updated", 3000)

        dialog.settingsChanged.connect(on_settings_changed)
        dialog.exec()

    def _on_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", "Preferences dialog coming soon!")

    def _on_transformation_clicked(self, trans_type: str, value: int):
        """Handle transformation clicked from transformation preview panel"""
        if not self.current_set:
            return

        try:
            if trans_type == 'T':
                transformed = self.current_set.transposition(value)
                self.status_bar.showMessage(f"Applied T{value} from preview", 3000)
            elif trans_type == 'I':
                transformed = self.current_set.inversion(value)
                self.status_bar.showMessage(f"Applied I{value} from preview", 3000)
            elif trans_type == 'R':
                transformed = self.current_set.retrograde().transposition(value)
                self.status_bar.showMessage(f"Applied RT{value} from preview", 3000)
            elif trans_type == 'RI':
                transformed = self.current_set.retrograde_inversion(value)
                self.status_bar.showMessage(f"Applied RI{value} from preview", 3000)
            else:
                return

            self.current_set = transformed
            self.input_panel.set_current_set(transformed)
            self.visualization_canvas.update_visualization(transformed)
            self.analysis_panel.update_analysis(transformed)
            self.transformation_panel.update_transformations(transformed)
            self.subset_explorer.update_set(transformed)

        except Exception as e:
            QMessageBox.warning(self, "Transformation Error", str(e))

    def _on_play_all_transformations(self, trans_type: str):
        """Play all 12 transformations sequentially"""
        if not self.current_set:
            return

        try:
            sets_to_play = []
            for i in range(12):
                if trans_type == 'T':
                    transformed = self.current_set.transposition(i)
                    sets_to_play.append((f"T{i}", transformed))
                elif trans_type == 'I':
                    transformed = self.current_set.inversion(i)
                    sets_to_play.append((f"I{i}", transformed))
                elif trans_type == 'R':
                    transformed = self.current_set.retrograde().transposition(i)
                    sets_to_play.append((f"RT{i}", transformed))
                elif trans_type == 'RI':
                    transformed = self.current_set.retrograde_inversion(i)
                    sets_to_play.append((f"RI{i}", transformed))

            self.status_bar.showMessage(f"Playing all {trans_type} transformations...", 5000)

            self.play_queue = sets_to_play
            self.play_index = 0
            self.is_playing_queue = True
            self._play_next_in_queue()

        except Exception as e:
            QMessageBox.warning(self, "Play All Error", str(e))
            self.stop_audio_button.hide()

    def _play_next_in_queue(self):
        """Play next transformation in the queue"""
        if not hasattr(self, 'is_playing_queue') or not self.is_playing_queue:
            self.status_bar.showMessage("Playback stopped", 2000)
            self.stop_audio_button.hide()
            return

        if self.play_index >= len(self.play_queue):
            self.status_bar.showMessage("Playback complete", 2000)
            self.stop_audio_button.hide()
            self.is_playing_queue = False
            return

        label, pcs = self.play_queue[self.play_index]
        self.status_bar.showMessage(f"Playing {label}... ({self.play_index + 1}/{len(self.play_queue)})", 2000)

        self.audio_manager.play_set(pcs, arpeggiate=True)

        self.play_index += 1
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1200, self._play_next_in_queue)

    def _on_stop_audio(self):
        """Stop audio playback"""
        self.is_playing_queue = False
        self.audio_manager.stop()
        self.stop_audio_button.hide()
        self.status_bar.showMessage("Playback stopped", 2000)

    def _on_subset_selected(self, pcs: PitchClassSet):
        """Handle subset/superset selected from subset explorer"""
        self.input_panel.set_current_set(pcs)
        self.status_bar.showMessage(f"Loaded subset/superset: {sorted(pcs.pitch_classes)}", 3000)

    def _on_new_set(self):
        """Clear current set"""
        self.input_panel.input_field.clear()
        self.status_bar.showMessage("Cleared", 2000)

    def _toggle_analysis_panel(self):
        """Toggle analysis panel visibility"""
        self.analysis_panel.setVisible(not self.analysis_panel.isVisible())

    def _set_viz_mode(self, mode: str):
        """Set visualization mode"""
        self.visualization_canvas.set_mode(mode)
        self.status_bar.showMessage(f"Visualization mode: {mode}", 2000)

    def _on_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Set Theory Analysis",
                         "<h2>Allen Forte Set Theory</h2>"
                         "<p>Interactive GUI for pitch class set analysis</p>"
                         "<p>Analysis-Only Edition</p>"
                         "<p>Built with PyQt6, matplotlib, and FluidSynth</p>")

    def eventFilter(self, obj, event):
        """Event filter to show hover help"""
        if event.type() == QEvent.Type.Enter:
            help_text = self._get_hover_help(obj)
            if help_text:
                self.hover_help_label.setText(help_text)
                self.hover_help_label.setStyleSheet("QLabel { color: #000; font-style: normal; font-weight: bold; }")
        elif event.type() == QEvent.Type.Leave:
            self.hover_help_label.setText("Hover over any feature for help")
            self.hover_help_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")

        return super().eventFilter(obj, event)

    def _get_hover_help(self, widget):
        """Get hover help text for a widget"""
        tooltip = widget.toolTip()
        if tooltip:
            return tooltip

        class_name = widget.__class__.__name__

        help_texts = {
            'SetInputPanel': 'Input pitch class sets - Type numbers 0-11 or Forte numbers like "3-11"',
            'AnalysisPanel': 'Live analysis of the current pitch class set',
            'VisualizationCanvas': 'Visual representation - Clock or Graph modes',
            'TransformationPanel': 'Transformation previews - Click to apply',
            'SubsetExplorer': 'Browse subsets and supersets',
        }

        return help_texts.get(class_name, "")

    def _restore_settings(self):
        """Restore window settings from last session"""
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        if self.audio_manager:
            self.audio_manager.cleanup()
        event.accept()


def launch_analysis_gui():
    """Launch the analysis-only GUI application"""
    from PyQt6.QtWidgets import QApplication
    import sys
    import traceback

    def exception_hook(exc_type, exc_value, exc_traceback):
        print("\n" + "=" * 60)
        print("UNHANDLED EXCEPTION:")
        print("=" * 60)
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print("=" * 60 + "\n")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    app.setApplicationName("Set Theory Analysis")
    app.setOrganizationName("SetTheory")

    try:
        window = AnalysisMainWindow()
        window.show()
        app.main_window = window
        exit_code = app.exec()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\nERROR creating AnalysisMainWindow: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    launch_analysis_gui()
