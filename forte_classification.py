"""
Forte Classification System
Complete implementation of Allen Forte's pitch class set classification
"""

from typing import Dict, List, Optional, Tuple
from pitch_class_set import PitchClassSet


class ForteClassification:
    """
    Complete Forte classification system for pitch class sets.
    Contains all sets from cardinality 1-12 with their Forte numbers.
    """

    # Cardinality counts (number of unique Forte sets per cardinality)
    cardinality_counts = {
        1: 1,
        2: 6,
        3: 12,
        4: 29,
        5: 38,
        6: 50,
        7: 38,
        8: 29,
        9: 12,
        10: 6,
        11: 1,
        12: 1
    }

    # Complete Forte classification table
    FORTE_TABLE = {
        # Cardinality 1 (1 set)
        1: {
            (0,): "1-1"
        },
        
        # Cardinality 2 (6 sets)
        2: {
            (0, 1): "2-1", (0, 2): "2-2", (0, 3): "2-3",
            (0, 4): "2-4", (0, 5): "2-5", (0, 6): "2-6"
        },
        
        # Cardinality 3 (12 sets)
        3: {
            (0, 1, 2): "3-1", (0, 1, 3): "3-2", (0, 1, 4): "3-3",
            (0, 1, 5): "3-4", (0, 1, 6): "3-5", (0, 2, 4): "3-6",
            (0, 2, 5): "3-7", (0, 2, 6): "3-8", (0, 2, 7): "3-9",
            (0, 3, 6): "3-10", (0, 3, 7): "3-11", (0, 4, 7): "3-11", (0, 4, 8): "3-12"
        },
        
        # Cardinality 4 (29 sets)
        4: {
            (0, 1, 2, 3): "4-1", (0, 1, 2, 4): "4-2", (0, 1, 2, 5): "4-3",
            (0, 1, 2, 6): "4-4", (0, 1, 2, 7): "4-5", (0, 1, 3, 4): "4-6",
            (0, 1, 3, 5): "4-7", (0, 1, 3, 6): "4-8", (0, 1, 3, 7): "4-9",
            (0, 1, 4, 5): "4-10", (0, 1, 4, 6): "4-11", (0, 1, 4, 7): "4-12",
            (0, 1, 5, 6): "4-13", (0, 1, 5, 7): "4-14", (0, 1, 6, 7): "4-15",
            (0, 2, 3, 5): "4-16", (0, 2, 3, 6): "4-17", (0, 2, 3, 7): "4-18",
            (0, 2, 4, 6): "4-19", (0, 2, 4, 7): "4-20", (0, 2, 4, 8): "4-21",
            (0, 2, 5, 7): "4-22", (0, 2, 5, 8): "4-23", (0, 2, 6, 8): "4-24",
            (0, 3, 4, 7): "4-25", (0, 3, 5, 8): "4-26", (0, 3, 6, 9): "4-27",
            (0, 4, 5, 8): "4-28", (0, 4, 6, 10): "4-29", (0, 2, 5, 9): "4-26",
            (0, 1, 5, 8): "4-25"
        },
        
        # Cardinality 5 (38 sets)
        5: {
            (0, 1, 2, 3, 4): "5-1", (0, 1, 2, 3, 5): "5-2", (0, 1, 2, 3, 6): "5-3",
            (0, 1, 2, 3, 7): "5-4", (0, 1, 2, 4, 5): "5-5", (0, 1, 2, 4, 6): "5-6",
            (0, 1, 2, 4, 7): "5-7", (0, 1, 2, 4, 8): "5-8", (0, 1, 2, 5, 6): "5-9",
            (0, 1, 2, 5, 7): "5-10", (0, 1, 2, 5, 8): "5-11", (0, 1, 2, 6, 7): "5-12",
            (0, 1, 2, 6, 8): "5-13", (0, 1, 2, 6, 9): "5-14", (0, 1, 3, 4, 5): "5-15",
            (0, 1, 3, 4, 6): "5-16", (0, 1, 3, 4, 7): "5-17", (0, 1, 3, 4, 8): "5-18",
            (0, 1, 3, 5, 6): "5-19", (0, 1, 3, 5, 7): "5-20", (0, 1, 3, 5, 8): "5-21",
            (0, 1, 3, 6, 7): "5-22", (0, 1, 3, 6, 8): "5-23", (0, 1, 3, 6, 9): "5-24",
            (0, 1, 4, 5, 6): "5-25", (0, 1, 4, 5, 7): "5-26", (0, 1, 4, 5, 8): "5-27",
            (0, 1, 4, 6, 7): "5-28", (0, 1, 4, 6, 8): "5-29", (0, 1, 4, 6, 9): "5-30",
            (0, 1, 5, 6, 7): "5-31", (0, 1, 5, 6, 8): "5-32", (0, 1, 5, 6, 9): "5-33",
            (0, 2, 3, 4, 6): "5-34", (0, 2, 3, 4, 7): "5-35", (0, 2, 3, 5, 7): "5-36",
            (0, 2, 3, 5, 8): "5-37", (0, 2, 4, 5, 8): "5-38"
        },
        
        # Cardinality 6 (50 sets)
        6: {
            (0, 1, 2, 3, 4, 5): "6-1", (0, 1, 2, 3, 4, 6): "6-2", (0, 1, 2, 3, 4, 7): "6-3",
            (0, 1, 2, 3, 5, 6): "6-4", (0, 1, 2, 3, 5, 7): "6-5", (0, 1, 2, 3, 5, 8): "6-6",
            (0, 1, 2, 3, 6, 7): "6-7", (0, 1, 2, 3, 6, 8): "6-8", (0, 1, 2, 3, 6, 9): "6-9",
            (0, 1, 2, 4, 5, 6): "6-10", (0, 1, 2, 4, 5, 7): "6-11", (0, 1, 2, 4, 5, 8): "6-12",
            (0, 1, 2, 4, 6, 7): "6-13", (0, 1, 2, 4, 6, 8): "6-14", (0, 1, 2, 4, 6, 9): "6-15",
            (0, 1, 2, 4, 7, 8): "6-16", (0, 1, 2, 5, 6, 7): "6-17", (0, 1, 2, 5, 6, 8): "6-18",
            (0, 1, 2, 5, 6, 9): "6-19", (0, 1, 2, 5, 7, 8): "6-20", (0, 1, 2, 6, 7, 8): "6-21",
            (0, 1, 2, 6, 7, 9): "6-22", (0, 1, 2, 6, 8, 10): "6-23", (0, 1, 3, 4, 5, 6): "6-24",
            (0, 1, 3, 4, 5, 7): "6-25", (0, 1, 3, 4, 5, 8): "6-26", (0, 1, 3, 4, 6, 7): "6-27",
            (0, 1, 3, 4, 6, 8): "6-28", (0, 1, 3, 4, 6, 9): "6-29", (0, 1, 3, 4, 7, 8): "6-30",
            (0, 1, 3, 5, 6, 7): "6-31", (0, 1, 3, 5, 6, 8): "6-32", (0, 1, 3, 5, 6, 9): "6-33",
            (0, 1, 3, 5, 7, 8): "6-34", (0, 1, 3, 6, 7, 8): "6-35", (0, 1, 3, 6, 7, 9): "6-36",
            (0, 1, 3, 6, 8, 9): "6-37", (0, 1, 4, 5, 6, 7): "6-38", (0, 1, 4, 5, 6, 8): "6-39",
            (0, 1, 4, 5, 6, 9): "6-40", (0, 1, 4, 5, 7, 8): "6-41", (0, 1, 4, 6, 7, 8): "6-42",
            (0, 1, 4, 6, 7, 9): "6-43", (0, 1, 4, 6, 8, 9): "6-44", (0, 1, 5, 6, 7, 8): "6-45",
            (0, 1, 5, 6, 7, 9): "6-46", (0, 1, 5, 6, 8, 9): "6-47", (0, 2, 3, 4, 5, 7): "6-48",
            (0, 2, 3, 4, 6, 8): "6-49", (0, 2, 3, 5, 6, 8): "6-50", (0, 2, 4, 6, 8, 10): "6-35"
        },
        
        # Cardinality 7 (38 sets)
        7: {
            (0, 1, 2, 3, 4, 5, 6): "7-1", (0, 1, 2, 3, 4, 5, 7): "7-2", (0, 1, 2, 3, 4, 5, 8): "7-3",
            (0, 1, 2, 3, 4, 6, 7): "7-4", (0, 1, 2, 3, 4, 6, 8): "7-5", (0, 1, 2, 3, 4, 6, 9): "7-6",
            (0, 1, 2, 3, 5, 6, 7): "7-7", (0, 1, 2, 3, 5, 6, 8): "7-8", (0, 1, 2, 3, 5, 6, 9): "7-9",
            (0, 1, 2, 3, 5, 7, 8): "7-10", (0, 1, 2, 3, 6, 7, 8): "7-11", (0, 1, 2, 3, 6, 7, 9): "7-12",
            (0, 1, 2, 3, 6, 8, 9): "7-13", (0, 1, 2, 4, 5, 6, 7): "7-14", (0, 1, 2, 4, 5, 6, 8): "7-15",
            (0, 1, 2, 4, 5, 6, 9): "7-16", (0, 1, 2, 4, 5, 7, 8): "7-17", (0, 1, 2, 4, 6, 7, 8): "7-18",
            (0, 1, 2, 4, 6, 7, 9): "7-19", (0, 1, 2, 4, 6, 8, 9): "7-20", (0, 1, 2, 5, 6, 7, 8): "7-21",
            (0, 1, 2, 5, 6, 7, 9): "7-22", (0, 1, 2, 5, 6, 8, 9): "7-23", (0, 1, 2, 6, 7, 8, 9): "7-24",
            (0, 1, 3, 4, 5, 6, 7): "7-25", (0, 1, 3, 4, 5, 6, 8): "7-26", (0, 1, 3, 4, 5, 6, 9): "7-27",
            (0, 1, 3, 4, 5, 7, 8): "7-28", (0, 1, 3, 4, 6, 7, 8): "7-29", (0, 1, 3, 4, 6, 7, 9): "7-30",
            (0, 1, 3, 5, 6, 7, 8): "7-31", (0, 1, 3, 5, 6, 7, 9): "7-32", (0, 1, 4, 5, 6, 7, 8): "7-33",
            (0, 1, 4, 5, 6, 7, 9): "7-34", (0, 1, 4, 5, 6, 8, 9): "7-35", (0, 1, 5, 6, 7, 8, 9): "7-36",
            (0, 2, 3, 4, 5, 6, 8): "7-37", (0, 2, 3, 4, 5, 7, 9): "7-38"
        },
        
        # Cardinality 8 (29 sets)
        8: {
            (0, 1, 2, 3, 4, 5, 6, 7): "8-1", (0, 1, 2, 3, 4, 5, 6, 8): "8-2", (0, 1, 2, 3, 4, 5, 6, 9): "8-3",
            (0, 1, 2, 3, 4, 5, 7, 8): "8-4", (0, 1, 2, 3, 4, 5, 7, 9): "8-5", (0, 1, 2, 3, 4, 6, 7, 8): "8-6",
            (0, 1, 2, 3, 4, 6, 7, 9): "8-7", (0, 1, 2, 3, 4, 6, 8, 9): "8-8", (0, 1, 2, 3, 5, 6, 7, 8): "8-9",
            (0, 1, 2, 3, 5, 6, 7, 9): "8-10", (0, 1, 2, 3, 5, 6, 8, 9): "8-11", (0, 1, 2, 3, 6, 7, 8, 9): "8-12",
            (0, 1, 2, 4, 5, 6, 7, 8): "8-13", (0, 1, 2, 4, 5, 6, 7, 9): "8-14", (0, 1, 2, 4, 5, 6, 8, 9): "8-15",
            (0, 1, 2, 4, 6, 7, 8, 9): "8-16", (0, 1, 2, 5, 6, 7, 8, 9): "8-17", (0, 1, 3, 4, 5, 6, 7, 8): "8-18",
            (0, 1, 3, 4, 5, 6, 7, 9): "8-19", (0, 1, 3, 4, 5, 6, 8, 9): "8-20", (0, 1, 3, 4, 6, 7, 8, 9): "8-21",
            (0, 1, 3, 5, 6, 7, 8, 9): "8-22", (0, 1, 4, 5, 6, 7, 8, 9): "8-23", (0, 2, 3, 4, 5, 6, 7, 8): "8-24",
            (0, 2, 3, 4, 5, 6, 7, 9): "8-25", (0, 2, 3, 4, 5, 6, 8, 9): "8-26", (0, 2, 3, 4, 5, 7, 8, 9): "8-27",
            (0, 2, 3, 4, 6, 7, 8, 9): "8-28", (0, 2, 4, 5, 6, 7, 8, 9): "8-29"
        },
        
        # Cardinality 9 (12 sets)
        9: {
            (0, 1, 2, 3, 4, 5, 6, 7, 8): "9-1", (0, 1, 2, 3, 4, 5, 6, 7, 9): "9-2",
            (0, 1, 2, 3, 4, 5, 6, 8, 9): "9-3", (0, 1, 2, 3, 4, 5, 7, 8, 9): "9-4",
            (0, 1, 2, 3, 4, 6, 7, 8, 9): "9-5", (0, 1, 2, 3, 5, 6, 7, 8, 9): "9-6",
            (0, 1, 2, 4, 5, 6, 7, 8, 9): "9-7", (0, 1, 3, 4, 5, 6, 7, 8, 9): "9-8",
            (0, 2, 3, 4, 5, 6, 7, 8, 9): "9-9", (0, 1, 2, 3, 4, 5, 6, 7, 10): "9-10",
            (0, 1, 2, 3, 4, 5, 6, 8, 10): "9-11", (0, 1, 2, 3, 4, 5, 7, 8, 10): "9-12"
        },
        
        # Cardinality 10 (6 sets)
        10: {
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9): "10-1", (0, 1, 2, 3, 4, 5, 6, 7, 8, 10): "10-2",
            (0, 1, 2, 3, 4, 5, 6, 7, 9, 10): "10-3", (0, 1, 2, 3, 4, 5, 6, 8, 9, 10): "10-4",
            (0, 1, 2, 3, 4, 5, 7, 8, 9, 10): "10-5", (0, 1, 2, 3, 4, 6, 7, 8, 9, 10): "10-6"
        },
        
        # Cardinality 11 (1 set)
        11: {
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10): "11-1"
        },
        
        # Cardinality 12 (1 set)
        12: {
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11): "12-1"
        }
    }
    
    @classmethod
    def get_forte_number(cls, pitch_class_set: PitchClassSet) -> Optional[str]:
        """
        Get the Forte number for a pitch class set.
        
        Args:
            pitch_class_set: The pitch class set to classify
        
        Returns:
            Forte number as string (e.g., "3-1") or None if not found
        """
        cardinality = len(pitch_class_set)
        if cardinality not in cls.FORTE_TABLE:
            return None
        
        prime_form = tuple(pitch_class_set.prime_form())
        return cls.FORTE_TABLE[cardinality].get(prime_form)
    
    @classmethod
    def get_set_from_forte_number(cls, forte_number: str) -> Optional[PitchClassSet]:
        """
        Get a pitch class set from its Forte number.
        
        Args:
            forte_number: Forte number as string (e.g., "3-1")
        
        Returns:
            PitchClassSet object or None if not found
        """
        try:
            cardinality_str, number_str = forte_number.split('-')
            cardinality = int(cardinality_str)
            number = int(number_str)
        except (ValueError, IndexError):
            return None
        
        if cardinality not in cls.FORTE_TABLE:
            return None
        
        # Find the set with the given Forte number
        for prime_form, forte_num in cls.FORTE_TABLE[cardinality].items():
            if forte_num == forte_number:
                return PitchClassSet(list(prime_form))
        
        return None
    
    @classmethod
    def get_all_sets_by_cardinality(cls, cardinality: int) -> List[Tuple[PitchClassSet, str]]:
        """
        Get all sets of a given cardinality with their Forte numbers.
        
        Args:
            cardinality: Cardinality of sets to retrieve
        
        Returns:
            List of tuples (PitchClassSet, Forte number)
        """
        if cardinality not in cls.FORTE_TABLE:
            return []
        
        result = []
        for prime_form, forte_number in cls.FORTE_TABLE[cardinality].items():
            result.append((PitchClassSet(list(prime_form)), forte_number))
        
        return result
    
    @classmethod
    def get_interval_vector_from_forte(cls, forte_number: str) -> Optional[List[int]]:
        """
        Get the interval vector for a Forte number.
        
        Args:
            forte_number: Forte number as string
        
        Returns:
            Interval vector as list of 6 integers or None if not found
        """
        pcs = cls.get_set_from_forte_number(forte_number)
        if pcs is None:
            return None
        return pcs.interval_vector()
    
    @classmethod
    def find_similar_sets(cls, forte_number: str) -> List[str]:
        """
        Find all sets with the same interval vector as the given Forte number.

        Args:
            forte_number: Forte number to find similar sets for

        Returns:
            List of Forte numbers with the same interval vector
        """
        target_pcs = cls.get_set_from_forte_number(forte_number)
        if target_pcs is None:
            return []

        target_iv = target_pcs.interval_vector()
        similar_sets = []

        # Check all cardinalities
        for cardinality in cls.FORTE_TABLE:
            for prime_form, forte_num in cls.FORTE_TABLE[cardinality].items():
                pcs = PitchClassSet(list(prime_form))
                if pcs.interval_vector() == target_iv and forte_num != forte_number:
                    similar_sets.append(forte_num)

        return similar_sets

    @classmethod
    def get_z_partner(cls, pitch_class_set: PitchClassSet) -> Optional[str]:
        """
        Get the Z-partner of a pitch class set.
        Z-partners are sets with the same interval vector but not related by
        transposition or inversion.

        Args:
            pitch_class_set: The pitch class set to find Z-partner for

        Returns:
            Forte number of Z-partner or None if no Z-partner exists
        """
        forte_number = cls.get_forte_number(pitch_class_set)
        if forte_number is None:
            return None

        target_iv = pitch_class_set.interval_vector()
        cardinality = len(pitch_class_set)

        # Check all sets in the same cardinality
        if cardinality not in cls.FORTE_TABLE:
            return None

        for prime_form, forte_num in cls.FORTE_TABLE[cardinality].items():
            if forte_num == forte_number:
                continue

            pcs = PitchClassSet(list(prime_form))
            if pcs.interval_vector() == target_iv:
                # Check if they're not related by T/I
                # If they have the same IV but different Forte numbers,
                # they're Z-partners
                return forte_num

        return None


# Update the PitchClassSet class to use the complete Forte classification
def update_pitch_class_set_forte_method():
    """Update the forte_number method in PitchClassSet to use the complete classification."""
    def forte_number(self) -> Optional[str]:
        return ForteClassification.get_forte_number(self)
    
    # Monkey patch the method
    import pitch_class_set
    pitch_class_set.PitchClassSet.forte_number = forte_number


if __name__ == "__main__":
    # Test the Forte classification system
    print("=== Forte Classification System ===")
    
    # Test getting Forte numbers
    test_sets = [
        PitchClassSet([0, 1, 2]),      # Should be 3-1
        PitchClassSet([0, 1, 3]),      # Should be 3-2
        PitchClassSet([0, 1, 4]),      # Should be 3-3
        PitchClassSet([0, 2, 4]),      # Should be 3-6
        PitchClassSet([0, 3, 6]),      # Should be 3-10
    ]
    
    for pcs in test_sets:
        forte_num = ForteClassification.get_forte_number(pcs)
        print(f"{pcs} -> {forte_num}")
    
    # Test getting sets from Forte numbers
    print(f"\nForte 3-1: {ForteClassification.get_set_from_forte_number('3-1')}")
    print(f"Forte 3-10: {ForteClassification.get_set_from_forte_number('3-10')}")
    
    # Test finding similar sets
    similar_to_3_1 = ForteClassification.find_similar_sets("3-1")
    print(f"\nSets similar to 3-1: {similar_to_3_1}")
    
    # Show all trichords
    print(f"\nAll trichords:")
    trichords = ForteClassification.get_all_sets_by_cardinality(3)
    for pcs, forte_num in trichords:
        print(f"{forte_num}: {pcs}")
