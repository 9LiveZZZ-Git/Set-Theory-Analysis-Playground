"""
Pitch Class Set Theory Implementation
Based on Allen Forte's Structure of Atonal Music

This module provides comprehensive tools for analyzing pitch class sets,
including transposition, inversion, rotation, subset analysis, and similarity relations.
"""

from typing import List, Set, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from itertools import combinations, permutations
import math


@dataclass
class PitchClassSet:
    """
    Represents a pitch class set with various analytical methods.
    
    Pitch classes are represented as integers 0-11:
    0=C, 1=C#, 2=D, 3=D#, 4=E, 5=F, 6=F#, 7=G, 8=G#, 9=A, 10=A#, 11=B
    """
    pitch_classes: List[int]
    
    def __post_init__(self):
        # Normalize pitch classes to 0-11 range and remove duplicates
        self.pitch_classes = sorted(list(set([pc % 12 for pc in self.pitch_classes])))
        self.cardinality = len(self.pitch_classes)
    
    def __str__(self):
        return f"PCS({self.pitch_classes})"
    
    def __repr__(self):
        return f"PitchClassSet({self.pitch_classes})"
    
    def __eq__(self, other):
        if not isinstance(other, PitchClassSet):
            return False
        return self.pitch_classes == other.pitch_classes
    
    def __hash__(self):
        return hash(tuple(self.pitch_classes))
    
    def __len__(self):
        return self.cardinality
    
    def contains(self, pitch_class: int) -> bool:
        """Check if a pitch class is in the set."""
        return (pitch_class % 12) in self.pitch_classes
    
    def add_pitch_class(self, pitch_class: int) -> 'PitchClassSet':
        """Add a pitch class to the set."""
        new_pcs = self.pitch_classes + [pitch_class % 12]
        return PitchClassSet(new_pcs)
    
    def remove_pitch_class(self, pitch_class: int) -> 'PitchClassSet':
        """Remove a pitch class from the set."""
        new_pcs = [pc for pc in self.pitch_classes if pc != (pitch_class % 12)]
        return PitchClassSet(new_pcs)
    
    def transposition(self, n: int) -> 'PitchClassSet':
        """
        Transpose the set by n semitones (T-n operation).
        
        Args:
            n: Number of semitones to transpose (can be negative)
        
        Returns:
            New PitchClassSet transposed by n semitones
        """
        transposed_pcs = [(pc + n) % 12 for pc in self.pitch_classes]
        return PitchClassSet(transposed_pcs)
    
    def inversion(self, n: int = 0) -> 'PitchClassSet':
        """
        Invert the set around pitch class n (I-n operation).
        
        Args:
            n: Pitch class around which to invert (default: 0)
        
        Returns:
            New PitchClassSet inverted around n
        """
        inverted_pcs = [(n - pc) % 12 for pc in self.pitch_classes]
        return PitchClassSet(inverted_pcs)
    
    def rotation(self, n: int) -> 'PitchClassSet':
        """
        Rotate the set by n positions (cyclic permutation).
        
        Args:
            n: Number of positions to rotate (can be negative)
        
        Returns:
            New PitchClassSet rotated by n positions
        """
        if not self.pitch_classes:
            return PitchClassSet([])
        
        n = n % len(self.pitch_classes)
        rotated_pcs = self.pitch_classes[n:] + self.pitch_classes[:n]
        return PitchClassSet(rotated_pcs)
    
    def retrograde(self) -> 'PitchClassSet':
        """
        Retrograde (R) operation: reverse the order of pitch classes.
        
        Note: As a set, this is equivalent to the original set, but the order
        is reversed for sequential playback purposes.
        
        Returns:
            New PitchClassSet (same set, but order reversed for playback)
        """
        if not self.pitch_classes:
            return PitchClassSet([])
        
        # Reverse the order - create new set which will sort, but store original order
        retrograde_pcs = list(reversed(self.pitch_classes))
        result = PitchClassSet(retrograde_pcs)
        # Store the retrograde order for playback (override sorted order)
        result.pitch_classes = retrograde_pcs
        return result
    
    def retrograde_inversion(self, n: int = 0) -> 'PitchClassSet':
        """
        Retrograde Inversion (RI) operation: invert then retrograde.
        
        Args:
            n: Pitch class around which to invert (default: 0)
        
        Returns:
            New PitchClassSet that is the retrograde of the inversion
        """
        # First invert, then retrograde
        inverted = self.inversion(n)
        return inverted.retrograde()
    
    def get_playback_order(self) -> List[int]:
        """
        Get pitch classes in playback order (for sequential playback).
        For retrograde operations, this returns the reversed order.
        
        Returns:
            List of pitch classes in playback order
        """
        return self.pitch_classes
    
    def prime_form(self) -> List[int]:
        """
        Find the prime form of the set (Forte's normal form).
        
        Returns:
            List representing the prime form
        """
        if not self.pitch_classes:
            return []
        
        # Try all rotations and inversions to find the lexicographically smallest
        candidates = []
        
        # Add all rotations of the original set
        for i in range(len(self.pitch_classes)):
            rotated = self.rotation(i)
            candidates.append(rotated.pitch_classes)
        
        # Add all rotations of the inverted set
        inverted = self.inversion()
        for i in range(len(inverted.pitch_classes)):
            rotated_inv = inverted.rotation(i)
            candidates.append(rotated_inv.pitch_classes)
        
        # Find the lexicographically smallest
        return min(candidates)
    
    def interval_vector(self) -> List[int]:
        """
        Calculate the interval vector (ic1, ic2, ic3, ic4, ic5, ic6).
        
        Returns:
            List of 6 integers representing interval class counts
        """
        if len(self.pitch_classes) < 2:
            return [0, 0, 0, 0, 0, 0]
        
        interval_counts = [0] * 6
        
        # Calculate all intervals between pairs
        for i in range(len(self.pitch_classes)):
            for j in range(i + 1, len(self.pitch_classes)):
                interval = abs(self.pitch_classes[i] - self.pitch_classes[j])
                interval_class = min(interval, 12 - interval)
                interval_counts[interval_class - 1] += 1
        
        return interval_counts
    
    def is_subset_of(self, other: 'PitchClassSet') -> bool:
        """Check if this set is a subset of another set."""
        return all(pc in other.pitch_classes for pc in self.pitch_classes)
    
    def is_superset_of(self, other: 'PitchClassSet') -> bool:
        """Check if this set is a superset of another set."""
        return other.is_subset_of(self)
    
    def intersection(self, other: 'PitchClassSet') -> 'PitchClassSet':
        """Find the intersection of two sets."""
        common_pcs = [pc for pc in self.pitch_classes if pc in other.pitch_classes]
        return PitchClassSet(common_pcs)
    
    def union(self, other: 'PitchClassSet') -> 'PitchClassSet':
        """Find the union of two sets."""
        all_pcs = self.pitch_classes + other.pitch_classes
        return PitchClassSet(all_pcs)
    
    def complement(self) -> 'PitchClassSet':
        """Find the complement of the set (all pitch classes not in the set)."""
        all_pcs = list(range(12))
        complement_pcs = [pc for pc in all_pcs if pc not in self.pitch_classes]
        return PitchClassSet(complement_pcs)
    
    def similarity_relation(self, other: 'PitchClassSet') -> Dict[str, bool]:
        """
        Calculate similarity relations R, R0, R1, R2 between two sets.
        
        Returns:
            Dictionary with similarity relation results
        """
        # R: Sets have the same interval vector
        same_interval_vector = self.interval_vector() == other.interval_vector()
        
        # R0: Sets have the same interval vector and same cardinality
        same_cardinality = self.cardinality == other.cardinality
        r0 = same_interval_vector and same_cardinality
        
        # R1: Sets have the same interval vector and complementary cardinalities
        complementary_cardinality = self.cardinality + other.cardinality == 12
        r1 = same_interval_vector and complementary_cardinality
        
        # R2: Sets have the same interval vector and cardinalities differ by 1
        cardinality_diff_1 = abs(self.cardinality - other.cardinality) == 1
        r2 = same_interval_vector and cardinality_diff_1
        
        return {
            'R': same_interval_vector,
            'R0': r0,
            'R1': r1,
            'R2': r2
        }
    
    def find_subsets(self, subset_size: int) -> List['PitchClassSet']:
        """
        Find all subsets of a given size.
        
        Args:
            subset_size: Size of subsets to find
        
        Returns:
            List of PitchClassSet objects representing all subsets
        """
        if subset_size > len(self.pitch_classes) or subset_size < 0:
            return []
        
        subsets = []
        for combo in combinations(self.pitch_classes, subset_size):
            subsets.append(PitchClassSet(list(combo)))
        
        return subsets
    
    def find_supersets(self, superset_size: int) -> List['PitchClassSet']:
        """
        Find all supersets of a given size.
        
        Args:
            superset_size: Size of supersets to find
        
        Returns:
            List of PitchClassSet objects representing all supersets
        """
        if superset_size < len(self.pitch_classes) or superset_size > 12:
            return []
        
        # Find all pitch classes not in the current set
        remaining_pcs = [pc for pc in range(12) if pc not in self.pitch_classes]
        
        supersets = []
        # Generate all combinations of additional pitch classes
        for combo in combinations(remaining_pcs, superset_size - len(self.pitch_classes)):
            superset_pcs = self.pitch_classes + list(combo)
            supersets.append(PitchClassSet(superset_pcs))
        
        return supersets
    
    def forte_number(self) -> Optional[str]:
        """
        Find the Forte number for this set (if it exists).
        This is a simplified implementation - a complete Forte table would be needed.
        
        Returns:
            Forte number as string (e.g., "3-1") or None if not found
        """
        # This is a placeholder - a complete implementation would require
        # the full Forte classification table
        prime = self.prime_form()
        
        # Some well-known Forte numbers for demonstration
        forte_map = {
            (0, 1, 2): "3-1",      # Trichord 1
            (0, 1, 3): "3-2",      # Trichord 2
            (0, 1, 4): "3-3",      # Trichord 3
            (0, 1, 5): "3-4",      # Trichord 4
            (0, 1, 6): "3-5",      # Trichord 5
            (0, 2, 4): "3-6",      # Trichord 6
            (0, 2, 5): "3-7",      # Trichord 7
            (0, 2, 6): "3-8",      # Trichord 8
            (0, 2, 7): "3-9",      # Trichord 9
            (0, 3, 6): "3-10",     # Trichord 10
            (0, 3, 7): "3-11",     # Trichord 11
            (0, 4, 8): "3-12",     # Trichord 12
        }
        
        return forte_map.get(tuple(prime))


def generate_all_sets(cardinality: int) -> List[PitchClassSet]:
    """
    Generate all possible pitch class sets of a given cardinality.
    
    Args:
        cardinality: Size of sets to generate (1-12)
    
    Returns:
        List of all PitchClassSet objects of the given cardinality
    """
    if cardinality < 1 or cardinality > 12:
        return []
    
    all_sets = []
    for combo in combinations(range(12), cardinality):
        all_sets.append(PitchClassSet(list(combo)))
    
    return all_sets


def analyze_set_relations(set1: PitchClassSet, set2: PitchClassSet) -> Dict[str, Union[bool, List[PitchClassSet]]]:
    """
    Comprehensive analysis of relations between two sets.
    
    Args:
        set1: First pitch class set
        set2: Second pitch class set
    
    Returns:
        Dictionary with various relation analyses
    """
    return {
        'set1_prime_form': set1.prime_form(),
        'set2_prime_form': set2.prime_form(),
        'same_prime_form': set1.prime_form() == set2.prime_form(),
        'interval_vector_1': set1.interval_vector(),
        'interval_vector_2': set2.interval_vector(),
        'same_interval_vector': set1.interval_vector() == set2.interval_vector(),
        'similarity_relations': set1.similarity_relation(set2),
        'set1_subset_of_set2': set1.is_subset_of(set2),
        'set2_subset_of_set1': set2.is_subset_of(set1),
        'intersection': set1.intersection(set2),
        'union': set1.union(set2),
        'set1_complement': set1.complement(),
        'set2_complement': set2.complement(),
        'forte_number_1': set1.forte_number(),
        'forte_number_2': set2.forte_number(),
    }


# Example usage and testing
if __name__ == "__main__":
    # Create some example sets
    trichord = PitchClassSet([0, 1, 2])  # C, C#, D
    tetrachord = PitchClassSet([0, 1, 3, 6])  # C, C#, D#, F#
    
    print("=== Pitch Class Set Analysis ===")
    print(f"Trichord: {trichord}")
    print(f"Prime form: {trichord.prime_form()}")
    print(f"Interval vector: {trichord.interval_vector()}")
    print(f"Forte number: {trichord.forte_number()}")
    
    print(f"\nTetrachord: {tetrachord}")
    print(f"Prime form: {tetrachord.prime_form()}")
    print(f"Interval vector: {tetrachord.interval_vector()}")
    
    print(f"\nTransposition T3: {trichord.transposition(3)}")
    print(f"Inversion I0: {trichord.inversion(0)}")
    print(f"Rotation by 1: {trichord.rotation(1)}")
    
    # Find subsets
    print(f"\nSubsets of size 2: {trichord.find_subsets(2)}")
    
    # Similarity relations
    other_trichord = PitchClassSet([0, 1, 3])
    relations = trichord.similarity_relation(other_trichord)
    print(f"\nSimilarity relations with {other_trichord}: {relations}")
