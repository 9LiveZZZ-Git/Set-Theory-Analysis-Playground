"""
Set Analysis and Generation Tools
Advanced tools for analyzing and generating pitch class sets
"""

from typing import List, Dict, Tuple, Optional, Set as TypingSet
from itertools import combinations, permutations, product
import random
from pitch_class_set import PitchClassSet
from forte_classification import ForteClassification


class SetAnalyzer:
    """
    Advanced set analysis tools for pitch class sets.
    """
    
    def __init__(self):
        self.forte_classification = ForteClassification()
    
    def analyze_set_comprehensive(self, pcs: PitchClassSet) -> Dict:
        """
        Comprehensive analysis of a pitch class set.
        
        Args:
            pcs: Pitch class set to analyze
        
        Returns:
            Dictionary with comprehensive analysis results
        """
        analysis = {
            'pitch_classes': pcs.pitch_classes,
            'cardinality': len(pcs),
            'prime_form': pcs.prime_form(),
            'interval_vector': pcs.interval_vector(),
            'forte_number': self.forte_classification.get_forte_number(pcs),
            'complement': pcs.complement(),
            'complement_forte': self.forte_classification.get_forte_number(pcs.complement()),
            'transpositions': {},
            'inversions': {},
            'rotations': {},
            'subsets': {},
            'supersets': {},
            'similar_sets': []
        }
        
        # Generate transpositions
        for n in range(12):
            transposed = pcs.transposition(n)
            analysis['transpositions'][f'T{n}'] = transposed.pitch_classes
        
        # Generate inversions
        for n in range(12):
            inverted = pcs.inversion(n)
            analysis['inversions'][f'I{n}'] = inverted.pitch_classes
        
        # Generate rotations
        for n in range(len(pcs)):
            rotated = pcs.rotation(n)
            analysis['rotations'][f'R{n}'] = rotated.pitch_classes
        
        # Find subsets
        for size in range(1, len(pcs)):
            subsets = pcs.find_subsets(size)
            analysis['subsets'][size] = [(subset.pitch_classes, 
                                        self.forte_classification.get_forte_number(subset)) 
                                       for subset in subsets]
        
        # Find supersets
        for size in range(len(pcs) + 1, 13):
            supersets = pcs.find_supersets(size)
            analysis['supersets'][size] = [(superset.pitch_classes,
                                          self.forte_classification.get_forte_number(superset))
                                         for superset in supersets]
        
        # Find similar sets
        if analysis['forte_number']:
            analysis['similar_sets'] = self.forte_classification.find_similar_sets(
                analysis['forte_number'])
        
        return analysis
    
    def compare_sets(self, set1: PitchClassSet, set2: PitchClassSet) -> Dict:
        """
        Compare two pitch class sets comprehensively.
        
        Args:
            set1: First pitch class set
            set2: Second pitch class set
        
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            'set1': {
                'pitch_classes': set1.pitch_classes,
                'prime_form': set1.prime_form(),
                'interval_vector': set1.interval_vector(),
                'forte_number': self.forte_classification.get_forte_number(set1)
            },
            'set2': {
                'pitch_classes': set2.pitch_classes,
                'prime_form': set2.prime_form(),
                'interval_vector': set2.interval_vector(),
                'forte_number': self.forte_classification.get_forte_number(set2)
            },
            'relations': {
                'same_prime_form': set1.prime_form() == set2.prime_form(),
                'same_interval_vector': set1.interval_vector() == set2.interval_vector(),
                'same_forte_number': self.forte_classification.get_forte_number(set1) == 
                                   self.forte_classification.get_forte_number(set2),
                'set1_subset_of_set2': set1.is_subset_of(set2),
                'set2_subset_of_set1': set2.is_subset_of(set1),
                'intersection': set1.intersection(set2).pitch_classes,
                'union': set1.union(set2).pitch_classes
            },
            'similarity_relations': set1.similarity_relation(set2)
        }
        
        return comparison
    
    def find_common_subsets(self, sets: List[PitchClassSet], subset_size: int) -> List[PitchClassSet]:
        """
        Find subsets that are common to all given sets.
        
        Args:
            sets: List of pitch class sets
            subset_size: Size of subsets to find
        
        Returns:
            List of common subsets
        """
        if not sets:
            return []
        
        # Get all subsets of the first set
        all_subsets = sets[0].find_subsets(subset_size)
        
        # Filter to only those that are subsets of all other sets
        common_subsets = []
        for subset in all_subsets:
            if all(subset.is_subset_of(s) for s in sets[1:]):
                common_subsets.append(subset)
        
        return common_subsets
    
    def find_common_supersets(self, sets: List[PitchClassSet], superset_size: int) -> List[PitchClassSet]:
        """
        Find supersets that contain all given sets.
        
        Args:
            sets: List of pitch class sets
            superset_size: Size of supersets to find
        
        Returns:
            List of common supersets
        """
        if not sets:
            return []
        
        # Get all supersets of the first set
        all_supersets = sets[0].find_supersets(superset_size)
        
        # Filter to only those that are supersets of all other sets
        common_supersets = []
        for superset in all_supersets:
            if all(s.is_subset_of(superset) for s in sets[1:]):
                common_supersets.append(superset)
        
        return common_supersets


class SetGenerator:
    """
    Tools for generating pitch class sets with various constraints.
    """
    
    def __init__(self):
        self.forte_classification = ForteClassification()
    
    def generate_random_set(self, cardinality: int, seed: Optional[int] = None) -> PitchClassSet:
        """
        Generate a random pitch class set of given cardinality.
        
        Args:
            cardinality: Size of the set to generate
            seed: Random seed for reproducibility
        
        Returns:
            Random pitch class set
        """
        if seed is not None:
            random.seed(seed)
        
        if cardinality < 1 or cardinality > 12:
            raise ValueError("Cardinality must be between 1 and 12")
        
        pitch_classes = random.sample(range(12), cardinality)
        return PitchClassSet(pitch_classes)
    
    def generate_sets_by_interval_vector(self, target_iv: List[int]) -> List[PitchClassSet]:
        """
        Generate all sets with a given interval vector.
        
        Args:
            target_iv: Target interval vector (6 integers)
        
        Returns:
            List of pitch class sets with the given interval vector
        """
        matching_sets = []
        
        # Check all cardinalities
        for cardinality in range(1, 13):
            sets_with_cardinality = self.forte_classification.get_all_sets_by_cardinality(cardinality)
            for pcs, forte_num in sets_with_cardinality:
                if pcs.interval_vector() == target_iv:
                    matching_sets.append(pcs)
        
        return matching_sets
    
    def generate_sets_by_forte_number(self, forte_number: str) -> List[PitchClassSet]:
        """
        Generate all transpositions and inversions of a set with given Forte number.
        
        Args:
            forte_number: Forte number (e.g., "3-1")
        
        Returns:
            List of all related pitch class sets
        """
        base_set = self.forte_classification.get_set_from_forte_number(forte_number)
        if base_set is None:
            return []
        
        related_sets = []
        
        # Add all transpositions
        for n in range(12):
            related_sets.append(base_set.transposition(n))
        
        # Add all inversions
        for n in range(12):
            related_sets.append(base_set.inversion(n))
        
        # Remove duplicates
        unique_sets = []
        seen = set()
        for pcs in related_sets:
            pcs_tuple = tuple(pcs.pitch_classes)
            if pcs_tuple not in seen:
                seen.add(pcs_tuple)
                unique_sets.append(pcs)
        
        return unique_sets
    
    def generate_sets_with_constraints(self, 
                                     cardinality: int,
                                     required_intervals: Optional[List[int]] = None,
                                     forbidden_intervals: Optional[List[int]] = None,
                                     required_pcs: Optional[List[int]] = None,
                                     forbidden_pcs: Optional[List[int]] = None) -> List[PitchClassSet]:
        """
        Generate sets with specific constraints.
        
        Args:
            cardinality: Size of sets to generate
            required_intervals: Interval classes that must be present
            forbidden_intervals: Interval classes that must not be present
            required_pcs: Pitch classes that must be present
            forbidden_pcs: Pitch classes that must not be present
        
        Returns:
            List of sets meeting the constraints
        """
        if cardinality < 1 or cardinality > 12:
            return []
        
        valid_sets = []
        
        # Generate all possible sets of the given cardinality
        for combo in combinations(range(12), cardinality):
            pcs = PitchClassSet(list(combo))
            
            # Check constraints
            valid = True
            
            # Check required pitch classes
            if required_pcs:
                if not all(pc in pcs.pitch_classes for pc in required_pcs):
                    valid = False
            
            # Check forbidden pitch classes
            if forbidden_pcs:
                if any(pc in pcs.pitch_classes for pc in forbidden_pcs):
                    valid = False
            
            # Check interval constraints
            if required_intervals or forbidden_intervals:
                iv = pcs.interval_vector()
                
                # Check required intervals
                if required_intervals:
                    for interval_class in required_intervals:
                        if interval_class < 1 or interval_class > 6:
                            continue
                        if iv[interval_class - 1] == 0:
                            valid = False
                            break
                
                # Check forbidden intervals
                if forbidden_intervals and valid:
                    for interval_class in forbidden_intervals:
                        if interval_class < 1 or interval_class > 6:
                            continue
                        if iv[interval_class - 1] > 0:
                            valid = False
                            break
            
            if valid:
                valid_sets.append(pcs)
        
        return valid_sets
    
    def generate_hexachordal_combinatorial_sets(self) -> List[Tuple[PitchClassSet, PitchClassSet]]:
        """
        Generate all hexachordal combinatorial pairs.
        
        Returns:
            List of tuples (set1, set2) where set1 and set2 are hexachordal combinatorial
        """
        hexachords = self.forte_classification.get_all_sets_by_cardinality(6)
        combinatorial_pairs = []
        
        for i, (hex1, forte1) in enumerate(hexachords):
            for j, (hex2, forte2) in enumerate(hexachords[i+1:], i+1):
                # Check if they are combinatorial (union is chromatic scale)
                union = hex1.union(hex2)
                if len(union) == 12:  # Full chromatic scale
                    combinatorial_pairs.append((hex1, hex2))
        
        return combinatorial_pairs
    
    def generate_alltonic_sets(self) -> List[PitchClassSet]:
        """
        Generate all alltonic sets (sets that contain all 12 pitch classes).
        
        Returns:
            List containing the single alltonic set
        """
        return [PitchClassSet(list(range(12)))]
    
    def generate_aggregate_sets(self, cardinality: int) -> List[PitchClassSet]:
        """
        Generate sets that can form aggregates with their complements.
        
        Args:
            cardinality: Cardinality of the sets
        
        Returns:
            List of sets that form aggregates with their complements
        """
        if cardinality < 1 or cardinality > 11:
            return []
        
        aggregate_sets = []
        sets_of_cardinality = self.forte_classification.get_all_sets_by_cardinality(cardinality)
        
        for pcs, forte_num in sets_of_cardinality:
            complement = pcs.complement()
            union = pcs.union(complement)
            
            # Check if union is the full chromatic scale
            if len(union) == 12:
                aggregate_sets.append(pcs)
        
        return aggregate_sets


class SetVisualizer:
    """
    Tools for visualizing pitch class sets and their relationships.
    """
    
    @staticmethod
    def print_set_analysis(analysis: Dict) -> None:
        """
        Print a formatted analysis of a pitch class set.
        
        Args:
            analysis: Analysis dictionary from SetAnalyzer.analyze_set_comprehensive
        """
        print(f"=== Pitch Class Set Analysis ===")
        print(f"Pitch Classes: {analysis['pitch_classes']}")
        print(f"Cardinality: {analysis['cardinality']}")
        print(f"Prime Form: {analysis['prime_form']}")
        print(f"Interval Vector: {analysis['interval_vector']}")
        print(f"Forte Number: {analysis['forte_number']}")
        print(f"Complement: {analysis['complement'].pitch_classes}")
        print(f"Complement Forte: {analysis['complement_forte']}")
        
        if analysis['similar_sets']:
            print(f"Similar Sets: {analysis['similar_sets']}")
        
        print(f"\nTranspositions:")
        for trans_name, trans_pcs in analysis['transpositions'].items():
            print(f"  {trans_name}: {trans_pcs}")
        
        print(f"\nInversions:")
        for inv_name, inv_pcs in analysis['inversions'].items():
            print(f"  {inv_name}: {inv_pcs}")
        
        print(f"\nRotations:")
        for rot_name, rot_pcs in analysis['rotations'].items():
            print(f"  {rot_name}: {rot_pcs}")
        
        print(f"\nSubsets:")
        for size, subsets in analysis['subsets'].items():
            print(f"  Size {size}:")
            for subset_pcs, subset_forte in subsets:
                print(f"    {subset_pcs} ({subset_forte})")
        
        print(f"\nSupersets:")
        for size, supersets in analysis['supersets'].items():
            print(f"  Size {size}:")
            for superset_pcs, superset_forte in supersets:
                print(f"    {superset_pcs} ({superset_forte})")
    
    @staticmethod
    def print_comparison(comparison: Dict) -> None:
        """
        Print a formatted comparison of two pitch class sets.
        
        Args:
            comparison: Comparison dictionary from SetAnalyzer.compare_sets
        """
        print(f"=== Set Comparison ===")
        print(f"Set 1: {comparison['set1']['pitch_classes']} ({comparison['set1']['forte_number']})")
        print(f"Set 2: {comparison['set2']['pitch_classes']} ({comparison['set2']['forte_number']})")
        
        print(f"\nRelations:")
        relations = comparison['relations']
        print(f"  Same Prime Form: {relations['same_prime_form']}")
        print(f"  Same Interval Vector: {relations['same_interval_vector']}")
        print(f"  Same Forte Number: {relations['same_forte_number']}")
        print(f"  Set 1 ⊆ Set 2: {relations['set1_subset_of_set2']}")
        print(f"  Set 2 ⊆ Set 1: {relations['set2_subset_of_set1']}")
        print(f"  Intersection: {relations['intersection']}")
        print(f"  Union: {relations['union']}")
        
        print(f"\nSimilarity Relations:")
        sim_rel = comparison['similarity_relations']
        for rel_name, rel_value in sim_rel.items():
            print(f"  {rel_name}: {rel_value}")


# Example usage
if __name__ == "__main__":
    # Create analyzer and generator
    analyzer = SetAnalyzer()
    generator = SetGenerator()
    visualizer = SetVisualizer()
    
    # Analyze a trichord
    trichord = PitchClassSet([0, 1, 2])
    analysis = analyzer.analyze_set_comprehensive(trichord)
    visualizer.print_set_analysis(analysis)
    
    print("\n" + "="*50 + "\n")
    
    # Compare two sets
    set1 = PitchClassSet([0, 1, 2])
    set2 = PitchClassSet([0, 1, 3])
    comparison = analyzer.compare_sets(set1, set2)
    visualizer.print_comparison(comparison)
    
    print("\n" + "="*50 + "\n")
    
    # Generate sets with constraints
    constrained_sets = generator.generate_sets_with_constraints(
        cardinality=4,
        required_intervals=[1],  # Must contain semitone
        forbidden_intervals=[6]  # Must not contain tritone
    )
    
    print(f"Sets with semitone but no tritone (cardinality 4):")
    for pcs in constrained_sets[:10]:  # Show first 10
        forte_num = ForteClassification.get_forte_number(pcs)
        print(f"  {pcs.pitch_classes} ({forte_num})")
    
    print(f"\nTotal: {len(constrained_sets)} sets")
