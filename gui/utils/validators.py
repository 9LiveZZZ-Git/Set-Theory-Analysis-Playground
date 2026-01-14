"""
Input Validators for Set Theory Application
Validates pitch class input and provides parsing utilities
"""

import re
from typing import List, Optional, Tuple

try:
    from PyQt6.QtGui import QValidator
    from PyQt6.QtCore import QObject
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


def parse_pitch_classes(text: str) -> Optional[List[int]]:
    """
    Parse pitch class input from various formats

    Accepts:
    - Space-separated: "0 1 3 6"
    - Comma-separated: "0,1,3,6"
    - Bracketed: "[0,1,3,6]" or "[0 1 3 6]"
    - Forte number: "3-11" (requires forte_classification module)

    Args:
        text: Input text

    Returns:
        List of pitch classes (0-11) or None if invalid
    """
    text = text.strip()

    if not text:
        return None

    # Check if it's a Forte number (e.g., "3-11")
    if re.match(r'^\d+-\d+[AB]?$', text):
        try:
            from pathlib import Path
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from forte_classification import ForteClassification
            from pitch_class_set import PitchClassSet

            fc = ForteClassification()
            pcs = fc.get_set_from_forte_number(text)
            if pcs:
                return sorted(pcs.pitch_classes)
        except Exception:
            return None

    # Remove brackets if present
    text = re.sub(r'[\[\]{}()]', '', text)

    # Split by comma, space, or both
    parts = re.split(r'[,\s]+', text)

    # Parse integers
    pitch_classes = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        try:
            pc = int(part)
            if 0 <= pc <= 11:
                pitch_classes.append(pc)
            else:
                return None  # Out of range
        except ValueError:
            return None  # Not an integer

    if not pitch_classes:
        return None

    # Remove duplicates while preserving order
    seen = set()
    unique_pcs = []
    for pc in pitch_classes:
        if pc not in seen:
            seen.add(pc)
            unique_pcs.append(pc)

    return unique_pcs


def validate_pitch_classes(text: str) -> Tuple[bool, str]:
    """
    Validate pitch class input

    Args:
        text: Input text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text.strip():
        return False, "Input is empty"

    pcs = parse_pitch_classes(text)

    if pcs is None:
        return False, "Invalid format. Use 0-11 separated by spaces or commas, or Forte number (e.g., 3-11)"

    if len(pcs) == 0:
        return False, "No valid pitch classes found"

    if len(pcs) > 12:
        return False, "Too many pitch classes (max 12)"

    return True, ""


if PYQT_AVAILABLE:
    class PitchClassValidator(QValidator):
        """
        Qt Validator for pitch class input.
        Provides real-time validation feedback.
        """

        def validate(self, input_str: str, pos: int) -> Tuple[QValidator.State, str, int]:
            """
            Validate input

            Args:
                input_str: Current input string
                pos: Cursor position

            Returns:
                Tuple of (State, string, position)
                States: Invalid, Intermediate, Acceptable
            """
            # Empty input is intermediate (waiting for input)
            if not input_str.strip():
                return (QValidator.State.Intermediate, input_str, pos)

            # Check if it's a Forte number in progress
            if re.match(r'^\d+$', input_str.strip()):
                # Just a number - might be typing Forte number
                return (QValidator.State.Intermediate, input_str, pos)

            if re.match(r'^\d+-$', input_str.strip()):
                # Number followed by dash - definitely typing Forte number
                return (QValidator.State.Intermediate, input_str, pos)

            # Try to parse
            pcs = parse_pitch_classes(input_str)

            if pcs is not None:
                # Valid pitch classes
                return (QValidator.State.Acceptable, input_str, pos)

            # Check if input is partially valid (intermediate)
            # Allow digits, spaces, commas, brackets while typing
            if re.match(r'^[\d,\s\[\]{}()-]*$', input_str):
                # Contains only valid characters - might be incomplete
                return (QValidator.State.Intermediate, input_str, pos)

            # Invalid characters
            return (QValidator.State.Invalid, input_str, pos)

        def fixup(self, input_str: str) -> str:
            """
            Fix up invalid input (called when user presses Enter on invalid input)

            Args:
                input_str: Input string to fix

            Returns:
                Fixed string
            """
            # Remove invalid characters
            fixed = re.sub(r'[^0-9,\s\[\]{}()-]', '', input_str)

            # Try to parse and reformat
            pcs = parse_pitch_classes(fixed)
            if pcs:
                # Reformat as space-separated
                return ' '.join(map(str, pcs))

            return fixed


def test_validators():
    """Test validation functions"""
    print("Testing Pitch Class Validators\n")

    test_cases = [
        "0 1 3 6",
        "0,1,3,6",
        "[0,1,3,6]",
        "0 4 7",
        "3-11",
        "4-9",
        "0 1 2 3 4 5 6 7 8 9 10 11",
        "0 13",  # Invalid: out of range
        "abc",  # Invalid: not numbers
        "",  # Empty
        "5",  # Single note
    ]

    for test in test_cases:
        pcs = parse_pitch_classes(test)
        is_valid, error = validate_pitch_classes(test)
        print(f"Input: '{test}'")
        print(f"  Parsed: {pcs}")
        print(f"  Valid: {is_valid}")
        if not is_valid:
            print(f"  Error: {error}")
        print()


if __name__ == "__main__":
    test_validators()
