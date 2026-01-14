"""
Music Examples Database
Collection of famous pitch class sets from classical and popular music (public domain)
"""

from typing import List, Tuple, Dict
from pitch_class_set import PitchClassSet


class MusicExample:
    """Represents a musical example with pitch class set"""

    def __init__(self, name: str, composer: str, piece: str,
                 pitch_classes: List[int], description: str = "",
                 year: str = ""):
        self.name = name
        self.composer = composer
        self.piece = piece
        self.pitch_classes = pitch_classes
        self.description = description
        self.year = year
        self.pitch_class_set = PitchClassSet(pitch_classes)

    def __str__(self):
        return f"{self.name} - {self.composer}: {self.piece}"


class MusicExamplesDatabase:
    """
    Database of famous pitch class sets from classical and popular music.
    All examples are from public domain works.
    """

    EXAMPLES = [
        # Classical Triads and Basic Harmonies
        MusicExample(
            name="C Major Triad",
            composer="Traditional",
            piece="Major Chord (Forte 3-11)",
            pitch_classes=[0, 4, 7],
            description="The most fundamental consonant triad in Western music. "
                       "Opening chord of countless pieces including Beethoven's Ode to Joy.",
            year="Traditional"
        ),

        MusicExample(
            name="A Minor Triad",
            composer="Traditional",
            piece="Minor Chord (Forte 3-11)",
            pitch_classes=[9, 0, 4],
            description="Natural minor triad. Used extensively in Bach's Toccata and Fugue in D minor, "
                       "Beethoven's Moonlight Sonata, and countless other works.",
            year="Traditional"
        ),

        MusicExample(
            name="Diminished Triad",
            composer="Traditional",
            piece="Diminished Chord (Forte 3-10)",
            pitch_classes=[0, 3, 6],
            description="Symmetrical diminished triad. Famous use in Bach's B Minor Mass, "
                       "and the opening of Chopin's Prelude in E minor.",
            year="Traditional"
        ),

        MusicExample(
            name="Augmented Triad",
            composer="Traditional",
            piece="Augmented Chord (Forte 3-12)",
            pitch_classes=[0, 4, 8],
            description="Whole-tone derived symmetrical triad. Featured in Liszt's compositions "
                       "and Debussy's impressionistic works.",
            year="Traditional"
        ),

        # Beethoven Examples
        MusicExample(
            name="Symphony No. 5 Opening",
            composer="Beethoven",
            piece="Symphony No. 5 in C minor",
            pitch_classes=[7, 11, 2, 3],  # G, B, D, Eb - the famous motif
            description="The iconic 'fate knocking at the door' motif. "
                       "One of the most recognizable melodic fragments in classical music.",
            year="1808"
        ),

        MusicExample(
            name="Ode to Joy Theme",
            composer="Beethoven",
            piece="Symphony No. 9 - Ode to Joy",
            pitch_classes=[2, 4, 5, 7, 9, 11],  # D major scale fragment
            description="The joyous theme from Beethoven's final symphony, "
                       "now the anthem of the European Union.",
            year="1824"
        ),

        # Bach Examples
        MusicExample(
            name="Well-Tempered Clavier Theme",
            composer="Bach",
            piece="Prelude No. 1 in C Major, BWV 846",
            pitch_classes=[0, 2, 4, 5, 7, 9, 11],  # C major scale
            description="The arpeggiated opening prelude from The Well-Tempered Clavier Book I. "
                       "A foundational work demonstrating equal temperament.",
            year="1722"
        ),

        MusicExample(
            name="Toccata and Fugue Opening",
            composer="Bach",
            piece="Toccata and Fugue in D minor, BWV 565",
            pitch_classes=[2, 5, 9, 0, 4],  # D, F, A, C, E
            description="The dramatic opening gesture of one of Bach's most famous organ works.",
            year="c. 1703-1707"
        ),

        # Mozart Examples
        MusicExample(
            name="Eine Kleine Nachtmusik Opening",
            composer="Mozart",
            piece="Serenade No. 13 in G Major, K. 525",
            pitch_classes=[7, 11, 2, 4],  # G, B, D, E
            description="The instantly recognizable opening motif of Mozart's famous serenade.",
            year="1787"
        ),

        MusicExample(
            name="Symphony No. 40 Theme",
            composer="Mozart",
            piece="Symphony No. 40 in G minor",
            pitch_classes=[7, 10, 2, 3, 5],  # G, Bb, D, Eb, F
            description="The melancholic main theme from one of Mozart's most famous symphonies.",
            year="1788"
        ),

        # Chopin Examples
        MusicExample(
            name="Funeral March",
            composer="Chopin",
            piece="Piano Sonata No. 2 - Funeral March",
            pitch_classes=[10, 0, 3, 5],  # Bb, C, Eb, F
            description="The solemn funeral march, one of Chopin's most recognized melodies.",
            year="1839"
        ),

        MusicExample(
            name="Prelude in E minor",
            composer="Chopin",
            piece="Prelude Op. 28 No. 4",
            pitch_classes=[4, 7, 11, 2],  # E, G, B, D
            description="The melancholic prelude played at Chopin's own funeral.",
            year="1838-1839"
        ),

        # Folk and Traditional
        MusicExample(
            name="Amazing Grace",
            composer="Traditional",
            piece="Amazing Grace",
            pitch_classes=[0, 2, 4, 7, 9],  # C pentatonic
            description="Famous hymn using pentatonic scale. Written by John Newton in 1772.",
            year="1772"
        ),

        MusicExample(
            name="Greensleeves",
            composer="Traditional English",
            piece="Greensleeves",
            pitch_classes=[9, 11, 0, 2, 4, 5],  # A natural minor
            description="Traditional English folk song, possibly from the 16th century. "
                       "Often attributed to Henry VIII (incorrectly).",
            year="16th century"
        ),

        MusicExample(
            name="Swing Low, Sweet Chariot",
            composer="Traditional Spiritual",
            piece="Swing Low, Sweet Chariot",
            pitch_classes=[0, 2, 4, 5, 7, 9],  # C major pentatonic
            description="African American spiritual, composed before 1862. "
                       "Wallis Willis is often credited as composer.",
            year="Before 1862"
        ),

        # Romantic Era
        MusicExample(
            name="Ride of the Valkyries",
            composer="Wagner",
            piece="Die Walküre",
            pitch_classes=[7, 10, 2, 5],  # Bb major 7th chord
            description="The famous galloping theme from Wagner's Ring Cycle opera.",
            year="1856"
        ),

        MusicExample(
            name="1812 Overture Theme",
            composer="Tchaikovsky",
            piece="1812 Overture",
            pitch_classes=[4, 7, 11, 2, 4],  # E major triad
            description="The triumphant Russian theme from Tchaikovsky's patriotic overture.",
            year="1880"
        ),

        # Early 20th Century
        MusicExample(
            name="Boléro Main Theme",
            composer="Ravel",
            piece="Boléro",
            pitch_classes=[0, 2, 3, 5, 7],  # C, D, Eb, F, G
            description="The hypnotic, repeating theme from Ravel's most famous orchestral work.",
            year="1928"
        ),

        # Whole Tone and Symmetrical Collections
        MusicExample(
            name="Whole Tone Scale",
            composer="Debussy",
            piece="Whole Tone Scale (Forte 6-35)",
            pitch_classes=[0, 2, 4, 6, 8, 10],
            description="Complete whole tone scale used extensively by Debussy in impressionistic works "
                       "like 'Voiles' and 'Prélude à l'après-midi d'un faune'.",
            year="Late 1800s"
        ),

        MusicExample(
            name="Octatonic Scale",
            composer="Various",
            piece="Diminished/Octatonic Scale (Forte 8-28)",
            pitch_classes=[0, 1, 3, 4, 6, 7, 9, 10],
            description="Symmetrical diminished scale alternating half and whole steps. "
                       "Used by Stravinsky, Bartók, and Rimsky-Korsakov.",
            year="20th century"
        ),

        # Christmas Carols (Public Domain)
        MusicExample(
            name="Silent Night",
            composer="Franz Xaver Gruber",
            piece="Silent Night (Stille Nacht)",
            pitch_classes=[0, 2, 4, 5, 7, 9],  # C major scale
            description="The beloved Christmas carol, originally composed in Austria.",
            year="1818"
        ),

        MusicExample(
            name="Joy to the World",
            composer="Lowell Mason / George Frideric Handel",
            piece="Joy to the World",
            pitch_classes=[0, 2, 4, 5, 7, 9, 11],  # C major scale
            description="Christmas carol based on Psalm 98, with music adapted from Handel.",
            year="1839"
        ),

        # Popular Children's Songs and Nursery Rhymes (Public Domain)
        MusicExample(
            name="Twinkle Twinkle Little Star",
            composer="Traditional / Mozart",
            piece="Twinkle Twinkle Little Star (Ah! vous dirai-je, maman)",
            pitch_classes=[0, 0, 7, 7, 9, 9, 7],  # C C G G A A G melody
            description="One of the most famous children's songs worldwide. "
                       "Uses the same melody as Mozart's 'Ah! vous dirai-je, maman' variations (K. 265) "
                       "and 'The Alphabet Song'. Poem by Jane Taylor (1806).",
            year="1761 (melody)"
        ),

        MusicExample(
            name="Mary Had a Little Lamb",
            composer="Traditional American",
            piece="Mary Had a Little Lamb",
            pitch_classes=[4, 2, 0, 2, 4, 4, 4],  # E D C D E E E melody
            description="Classic American nursery rhyme with words by Sarah Josepha Hale (1830). "
                       "One of the first songs recorded by Thomas Edison on his phonograph.",
            year="1830"
        ),

        MusicExample(
            name="London Bridge Is Falling Down",
            composer="Traditional English",
            piece="London Bridge Is Falling Down",
            pitch_classes=[7, 9, 7, 5, 4, 5, 7],  # G A G F E F G melody
            description="Traditional English nursery rhyme dating back to at least the 17th century. "
                       "References to the bridge appear in medieval literature.",
            year="17th century"
        ),

        MusicExample(
            name="Row, Row, Row Your Boat",
            composer="Traditional American",
            piece="Row, Row, Row Your Boat",
            pitch_classes=[0, 0, 0, 2, 4],  # C C C D E melody opening
            description="American children's song, popular as a round/canon. "
                       "First published in 1852 by Eliphalet Oram Lyte.",
            year="1852"
        ),

        MusicExample(
            name="Baa, Baa, Black Sheep",
            composer="Traditional English",
            piece="Baa, Baa, Black Sheep",
            pitch_classes=[0, 0, 7, 7, 9, 9, 7],  # Same melody as Twinkle Twinkle
            description="English nursery rhyme with the same melody as 'Twinkle Twinkle Little Star'. "
                       "First printed in 1731.",
            year="1731"
        ),

        MusicExample(
            name="Frère Jacques",
            composer="Traditional French",
            piece="Frère Jacques (Are You Sleeping)",
            pitch_classes=[0, 2, 4, 0],  # F G A F melody opening
            description="Traditional French children's song, popular as a round. "
                       "Known in English as 'Are You Sleeping' or 'Brother John'.",
            year="18th century"
        ),

        MusicExample(
            name="Old MacDonald Had a Farm",
            composer="Traditional American",
            piece="Old MacDonald Had a Farm",
            pitch_classes=[0, 0, 0, 7, 9, 9, 7],  # C C C G A A G melody
            description="American children's song about a farmer and animals. "
                       "Evolved from earlier songs dating to the 18th century.",
            year="1917 (published)"
        ),

        MusicExample(
            name="Happy Birthday to You",
            composer="Patty Hill / Mildred J. Hill",
            piece="Happy Birthday to You",
            pitch_classes=[0, 0, 2, 0, 5, 4],  # C C D C F E melody
            description="Originally 'Good Morning to All' (1893), now the most recognized song worldwide. "
                       "Copyright expired in 2016 - now public domain.",
            year="1893"
        ),

        MusicExample(
            name="Three Blind Mice",
            composer="Traditional English",
            piece="Three Blind Mice",
            pitch_classes=[4, 2, 0, 4, 2, 0],  # E D C E D C melody
            description="English nursery rhyme, possibly dating to the 16th century. "
                       "One of the oldest surviving English nursery rhymes.",
            year="16th century"
        ),

        MusicExample(
            name="Hickory Dickory Dock",
            composer="Traditional English",
            piece="Hickory Dickory Dock",
            pitch_classes=[0, 2, 4, 2, 0],  # C D E D C melody
            description="English nursery rhyme first published in 1744. "
                       "Features onomatopoeia and counting rhyme elements.",
            year="1744"
        ),

        MusicExample(
            name="Hot Cross Buns",
            composer="Traditional English",
            piece="Hot Cross Buns",
            pitch_classes=[4, 2, 0, 4, 2, 0],  # E D C (simple 3-note song)
            description="Very simple traditional English street cry, often the first song "
                       "taught to beginning musicians. Uses only three notes.",
            year="18th century"
        ),

        MusicExample(
            name="The Itsy Bitsy Spider",
            composer="Traditional American",
            piece="The Itsy Bitsy Spider (Incy Wincy Spider)",
            pitch_classes=[7, 0, 2, 4, 5, 4, 2, 0],  # G C D E F E D C
            description="American nursery rhyme and finger play for children. "
                       "First published in 1910 as 'The Spider Song'.",
            year="1910"
        ),

        MusicExample(
            name="Pop Goes the Weasel",
            composer="Traditional English/American",
            piece="Pop Goes the Weasel",
            pitch_classes=[0, 4, 5, 7, 9, 7, 5],  # C E F G A G F
            description="Traditional song with both English and American versions. "
                       "Used as music for country dances. First recorded in the 1850s.",
            year="1850s"
        ),

        MusicExample(
            name="Yankee Doodle",
            composer="Traditional American",
            piece="Yankee Doodle",
            pitch_classes=[0, 0, 2, 4, 0, 4, 2],  # C C D E C E D melody
            description="Patriotic American song, origins trace to Seven Years' War era. "
                       "Official state song of Connecticut.",
            year="1755-1767"
        ),

        MusicExample(
            name="When the Saints Go Marching In",
            composer="Traditional Gospel/Jazz",
            piece="When the Saints Go Marching In",
            pitch_classes=[0, 4, 5, 7],  # C E F G opening
            description="Gospel hymn and jazz standard, associated with New Orleans. "
                       "Popularized by Louis Armstrong. Published 1896.",
            year="1896"
        ),

        MusicExample(
            name="Auld Lang Syne",
            composer="Traditional Scottish / Robert Burns",
            piece="Auld Lang Syne",
            pitch_classes=[0, 4, 7, 9, 0, 11, 9, 7],  # Pentatonic melody
            description="Scottish poem by Robert Burns (1788), sung to traditional melody. "
                       "Traditionally sung at New Year's celebrations worldwide.",
            year="1788"
        ),

        # Pentatonic Collections
        MusicExample(
            name="Black Keys Pentatonic",
            composer="Traditional",
            piece="Pentatonic Scale (Forte 5-35)",
            pitch_classes=[1, 3, 6, 8, 10],  # Db, Eb, Gb, Ab, Bb
            description="The black keys on piano form a perfect pentatonic scale. "
                       "Fundamental to many folk traditions worldwide.",
            year="Traditional"
        ),

        # Chromatic Collections
        MusicExample(
            name="Chromatic Tetrachord",
            composer="Various",
            piece="Chromatic Tetrachord (Forte 4-1)",
            pitch_classes=[0, 1, 2, 3],
            description="Four consecutive semitones. Used in chromatic voice leading "
                       "by Bach, Wagner, and many 20th century composers.",
            year="Various"
        ),

        # Additional Historic Examples
        MusicExample(
            name="Dies Irae",
            composer="Gregorian Chant",
            piece="Dies Irae (Day of Wrath)",
            pitch_classes=[2, 4, 5, 7, 9],  # D, E, F, G, A
            description="Medieval plainchant melody used in Requiem Masses. "
                       "Quoted by many composers including Berlioz, Liszt, and Saint-Saëns.",
            year="13th century"
        ),

        MusicExample(
            name="La Marseillaise Opening",
            composer="Claude Joseph Rouget de Lisle",
            piece="La Marseillaise (French National Anthem)",
            pitch_classes=[0, 2, 4, 5, 7, 9],  # C major scale
            description="The French national anthem, composed during the French Revolution.",
            year="1792"
        ),
    ]

    @classmethod
    def get_all_examples(cls) -> List[MusicExample]:
        """Get all music examples"""
        return cls.EXAMPLES

    @classmethod
    def get_examples_by_composer(cls, composer: str) -> List[MusicExample]:
        """Get examples by composer"""
        return [ex for ex in cls.EXAMPLES if composer.lower() in ex.composer.lower()]

    @classmethod
    def get_examples_by_forte_number(cls, forte_number: str) -> List[MusicExample]:
        """Get examples by Forte number"""
        from forte_classification import ForteClassification
        fc = ForteClassification()

        results = []
        for example in cls.EXAMPLES:
            example_forte = fc.get_forte_number(example.pitch_class_set)
            if example_forte == forte_number:
                results.append(example)

        return results

    @classmethod
    def get_composers(cls) -> List[str]:
        """Get list of all composers"""
        composers = set(ex.composer for ex in cls.EXAMPLES)
        return sorted(composers)

    @classmethod
    def get_example_by_name(cls, name: str) -> MusicExample:
        """Get example by name"""
        for ex in cls.EXAMPLES:
            if ex.name.lower() == name.lower():
                return ex
        return None


# Convenience function for CLI/testing
def list_all_examples():
    """Print all examples"""
    from forte_classification import ForteClassification
    fc = ForteClassification()

    print("=== Music Examples Database ===\n")

    for i, example in enumerate(MusicExamplesDatabase.get_all_examples(), 1):
        forte = fc.get_forte_number(example.pitch_class_set)
        print(f"{i}. {example.name}")
        print(f"   Composer: {example.composer} ({example.year})")
        print(f"   Piece: {example.piece}")
        print(f"   Pitch Classes: {example.pitch_classes}")
        print(f"   Forte Number: {forte}")
        print(f"   Description: {example.description}")
        print()


if __name__ == "__main__":
    list_all_examples()
