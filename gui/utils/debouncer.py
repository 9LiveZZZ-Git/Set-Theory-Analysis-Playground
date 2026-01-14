"""
Debouncer utility for Set Theory Application
QTimer-based debouncing to prevent excessive updates during user input
"""

try:
    from PyQt6.QtCore import QObject, QTimer, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class Debouncer(QObject if PYQT_AVAILABLE else object):
    """
    Debounces rapid events to prevent excessive processing.

    Usage:
        debouncer = Debouncer(delay_ms=300)
        debouncer.triggered.connect(some_expensive_function)

        # In your input handler:
        def on_text_changed(self, text):
            debouncer.trigger()  # Resets timer

        # some_expensive_function will be called 300ms after last trigger()
    """

    if PYQT_AVAILABLE:
        triggered = pyqtSignal()

    def __init__(self, delay_ms: int = 300):
        """
        Initialize debouncer

        Args:
            delay_ms: Delay in milliseconds before triggered signal is emitted
        """
        if PYQT_AVAILABLE:
            super().__init__()

        self.delay_ms = delay_ms
        self.timer = None

        if PYQT_AVAILABLE:
            self.timer = QTimer()
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.triggered)

    def trigger(self):
        """
        Trigger the debouncer.
        Resets the timer. The triggered signal will be emitted
        delay_ms milliseconds after the last call to trigger().
        """
        if self.timer:
            self.timer.stop()
            self.timer.start(self.delay_ms)

    def cancel(self):
        """Cancel pending trigger"""
        if self.timer:
            self.timer.stop()

    def set_delay(self, delay_ms: int):
        """
        Change the delay time

        Args:
            delay_ms: New delay in milliseconds
        """
        self.delay_ms = delay_ms
        if self.timer and self.timer.isActive():
            # Restart with new delay
            self.timer.stop()
            self.timer.start(self.delay_ms)


def test_debouncer():
    """Test debouncer functionality"""
    from PyQt6.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget, QLabel
    from PyQt6.QtCore import QDateTime
    import sys

    app = QApplication(sys.argv)

    # Create test window
    window = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Type rapidly in the field below.\nDebounced action will trigger 300ms after you stop typing.")
    layout.addWidget(label)

    input_field = QLineEdit()
    layout.addWidget(input_field)

    result_label = QLabel("Waiting for input...")
    layout.addWidget(result_label)

    window.setLayout(layout)

    # Create debouncer
    debouncer = Debouncer(delay_ms=300)

    # Connect to input field
    def on_text_changed(text):
        result_label.setText(f"Typing... ({text})")
        debouncer.trigger()

    def on_debounced():
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        text = input_field.text()
        result_label.setText(f"Debounced action triggered at {timestamp}\nFinal text: '{text}'")
        print(f"[{timestamp}] Debounced action with text: '{text}'")

    input_field.textChanged.connect(on_text_changed)
    debouncer.triggered.connect(on_debounced)

    window.setWindowTitle("Debouncer Test")
    window.resize(400, 150)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    test_debouncer()
