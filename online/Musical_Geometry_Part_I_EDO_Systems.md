# Musical Geometry - Part I: EDO Systems

A plain-text guide based on MAT 111MC coursework, with implementation instructions for the Set Theory Analysis online tool.

---

## 1. Equal Octave Divisions (EDO)

### Concept

Scales are patterns of intervals that repeat at the **octave**. An octave is a doubling of frequency:

- A3 = 220 Hz
- A4 = 440 Hz
- A5 = 880 Hz

The conventional piano uses **12-tone Equal Temperament (12-TET)**, dividing each octave into 12 equal slices of 100 cents each.

### The Chromatic Circle

In any **n-EDO** system, you take n equal steps to reach the next octave. The 12-TET chromatic scale:

```
C -> C# -> D -> D# -> E -> F -> F# -> G -> G# -> A -> A# -> B -> C (octave)
```

Each step = 100 cents (1200 cents / 12 steps)

### Implementation in Online Tool

The current online tool already implements 12-TET visualization:
- Clock diagram with 12 nodes (0-11)
- Each node = one pitch class
- Intervals measured in semitones (100 cents each)

**To extend for general n-EDO:**

```javascript
// Add to index.html
class EDOSystem {
    constructor(divisions, equave = 1200) {
        this.n = divisions;
        this.equave = equave;  // 1200 cents = octave
        this.stepSize = equave / divisions;
    }

    getCents(step) {
        return (step * this.stepSize) % this.equave;
    }

    getFrequency(step, baseFreq = 261.63) {
        return baseFreq * Math.pow(2, this.getCents(step) / 1200);
    }
}

// 12-TET (standard)
const edo12 = new EDOSystem(12);

// 24-TET (quarter-tones)
const edo24 = new EDOSystem(24);

// 31-TET (meantone approximation)
const edo31 = new EDOSystem(31);
```

---

## 2. Shapes and Transformations

### Shape = Quality

In the circular pitch space, geometric **shapes** correspond to chord **qualities**:

| Shape | Pitch Classes | Chord Type |
|-------|---------------|------------|
| [0,4,7] | Oblong triangle | Major triad |
| [0,3,7] | Different triangle | Minor triad |
| [0,3,6] | Symmetric triangle | Diminished triad |
| [0,4,8] | Equilateral triangle | Augmented triad |

### Rotation = Transposition

**Rotating** a shape around the circle = **transposing** the chord.
The shape (internal proportions) stays the same, only the position changes.

Example: Major triad [0,4,7] rotated by 5 semitones = [5,9,0] = F major

### Current Implementation

The online tool already does this! The transformation grid shows:
- All 12 transpositions (T0-T11)
- All 12 inversions (I0-I11)

**Enhancement idea - add rotation animation:**

```javascript
function animateRotation(pitchClasses, steps, duration = 1000) {
    const startTime = performance.now();
    const startPCs = [...pitchClasses];

    function animate(currentTime) {
        const progress = (currentTime - startTime) / duration;
        if (progress >= 1) {
            return pitchClasses.map(pc => (pc + steps) % 12);
        }

        const currentAngle = progress * (steps * 30); // 30 degrees per step
        // Animate rotation visually
        drawRotatedClock(startPCs, currentAngle);
        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}
```

---

## 3. Just Intonation vs Equal Temperament

### The Tuning Problem

12-TET intervals are **irrational ratios** (powers of 12th root of 2).

A "pure" major third is 5/4 = 386.31 cents.
A 12-TET major third is 400 cents.

**Difference: ~14 cents sharp** (audible as "beating")

### Just Intonation (JI) Ratios

Common JI intervals:
| Interval | Ratio | Cents | 12-TET Cents | Difference |
|----------|-------|-------|--------------|------------|
| Unison | 1/1 | 0 | 0 | 0 |
| Minor 2nd | 16/15 | 111.7 | 100 | +11.7 |
| Major 2nd | 9/8 | 203.9 | 200 | +3.9 |
| Minor 3rd | 6/5 | 315.6 | 300 | +15.6 |
| Major 3rd | 5/4 | 386.3 | 400 | -13.7 |
| Perfect 4th | 4/3 | 498.0 | 500 | -2.0 |
| Tritone | 7/5 | 582.5 | 600 | -17.5 |
| Perfect 5th | 3/2 | 702.0 | 700 | +2.0 |
| Minor 6th | 8/5 | 813.7 | 800 | +13.7 |
| Major 6th | 5/3 | 884.4 | 900 | -15.6 |
| Minor 7th | 7/4 | 968.8 | 1000 | -31.2 |
| Major 7th | 15/8 | 1088.3 | 1100 | -11.7 |
| Octave | 2/1 | 1200 | 1200 | 0 |

### Implementation - JI Mode

```javascript
// Add Just Intonation support
const JI_RATIOS = {
    0: 1,           // Unison
    1: 16/15,       // Minor 2nd
    2: 9/8,         // Major 2nd
    3: 6/5,         // Minor 3rd
    4: 5/4,         // Major 3rd
    5: 4/3,         // Perfect 4th
    6: 7/5,         // Tritone (septimal)
    7: 3/2,         // Perfect 5th
    8: 8/5,         // Minor 6th
    9: 5/3,         // Major 6th
    10: 7/4,        // Minor 7th (septimal)
    11: 15/8        // Major 7th
};

function ratioToCents(ratio) {
    return 1200 * Math.log2(ratio);
}

function playJIChord(pitchClasses, baseFreq = 261.63) {
    pitchClasses.forEach(pc => {
        const ratio = JI_RATIOS[pc];
        const freq = baseFreq * ratio;
        playFrequency(freq);
    });
}

// Compare 12-TET vs JI
function compareTemperaments(pitchClasses) {
    console.log("12-TET vs Just Intonation:");
    pitchClasses.forEach(pc => {
        const tetCents = pc * 100;
        const jiCents = ratioToCents(JI_RATIOS[pc]);
        const diff = jiCents - tetCents;
        console.log(`PC ${pc}: 12-TET=${tetCents}c, JI=${jiCents.toFixed(1)}c, diff=${diff.toFixed(1)}c`);
    });
}
```

---

## 4. Microtonality and Other EDOs

### Quarter-Tones (24-EDO)

Step size = 50 cents (half of 12-TET semitone)

```javascript
const edo24 = new EDOSystem(24);
// Now we have "neutral" intervals between major and minor

// Neutral triad (halfway between major and minor)
const neutralTriad = [0, 7, 14];  // Steps in 24-EDO
// 0 = root, 7 = 350 cents (neutral 3rd), 14 = 700 cents (5th)
```

### Third-Tones (36-EDO)

Step size = 33.33 cents

```javascript
const edo36 = new EDOSystem(36);
// Asymmetric division - some find this more pleasing than quarter-tones
```

### 31-EDO (Meantone)

Very good approximation of JI intervals:
- Fifth: 696.8 cents (JI = 702)
- Major third: 387.1 cents (JI = 386.3) - almost perfect!

### Implementation - EDO Selector

```javascript
// Add EDO system selector to UI
function createEDOSelector() {
    const container = document.createElement('div');
    container.innerHTML = `
        <label>EDO System:</label>
        <select id="edo-select">
            <option value="12">12-TET (Standard)</option>
            <option value="19">19-TET</option>
            <option value="24">24-TET (Quarter-tones)</option>
            <option value="31">31-TET (Meantone)</option>
            <option value="36">36-TET (Third-tones)</option>
            <option value="53">53-TET (Mercator)</option>
            <option value="custom">Custom...</option>
        </select>
    `;

    container.querySelector('#edo-select').addEventListener('change', (e) => {
        const n = parseInt(e.target.value);
        currentEDO = new EDOSystem(n);
        updateVisualization();
    });

    return container;
}

// Update clock visualization for n-EDO
function drawNEDOClock(edo, cx, cy, radius) {
    for (let i = 0; i < edo.n; i++) {
        const angle = (i * (360 / edo.n) - 90) * Math.PI / 180;
        const x = cx + Math.cos(angle) * radius;
        const y = cy + Math.sin(angle) * radius;

        // Draw node
        const cents = edo.getCents(i);
        drawNode(x, y, i, cents);
    }
}
```

---

## 5. Non-Octave Divisions

### Bohlen-Pierce Scale

Divides the **tritave** (octave + fifth = 1902 cents) into 13 equal steps.

```javascript
// Bohlen-Pierce: 13 divisions of the tritave
const bohlenPierce = new EDOSystem(13, 1902);
// Step size = 146.3 cents

// BP "triad" equivalent
const bpTriad = [0, 2, 5];  // Steps in BP scale
```

### Wendy Carlos Scales

- **Alpha**: 78 cents/step (15.385 steps/octave)
- **Beta**: 63.8 cents/step (18.8 steps/octave)
- **Gamma**: 35.1 cents/step (34.19 steps/octave)

```javascript
// Carlos Alpha (approximates JI well)
const carlosAlpha = new EDOSystem(15.385, 1200);

// Carlos Beta
const carlosBeta = new EDOSystem(18.8, 1200);
```

### Implementation - Custom Equave

```javascript
class GeneralEDO {
    constructor(divisions, equaveCents = 1200) {
        this.n = divisions;
        this.equave = equaveCents;
        this.stepSize = equaveCents / divisions;
    }

    // For Bohlen-Pierce: new GeneralEDO(13, 1902)
    // For stretched octave: new GeneralEDO(12, 1210)
}
```

---

## 6. Melodic Patterns

### Nested Pattern Structures

Patterns can be nested lists that unfold algorithmically:

```
Pattern(['A', ['B', 'C']]) => A B A C

Pattern(['A', ['B', ['C', 'D']], 'E', 'F']) =>
A B E F A C E F A B E F A D E F
```

The pattern cycles through, with nested items alternating.

### Implementation

```javascript
class MelodicPattern {
    constructor(structure) {
        this.structure = structure;
        this.indices = this._initIndices(structure);
    }

    _initIndices(arr) {
        return arr.map(item =>
            Array.isArray(item) ? { idx: 0, sub: this._initIndices(item) } : null
        );
    }

    _getNext(arr, indices) {
        const result = [];
        for (let i = 0; i < arr.length; i++) {
            const item = arr[i];
            if (Array.isArray(item)) {
                const subResult = this._getNextFromNested(item, indices[i]);
                result.push(subResult);
            } else {
                result.push(item);
            }
        }
        return result;
    }

    _getNextFromNested(arr, indexObj) {
        const item = arr[indexObj.idx];
        indexObj.idx = (indexObj.idx + 1) % arr.length;

        if (Array.isArray(item)) {
            return this._getNextFromNested(item, indexObj.sub[arr.indexOf(item)]);
        }
        return item;
    }

    // Generate full cycle
    *generate() {
        const totalLength = this._calculateCycleLength(this.structure);
        for (let i = 0; i < totalLength; i++) {
            yield this.next();
        }
    }

    _calculateCycleLength(arr) {
        let length = 1;
        for (const item of arr) {
            if (Array.isArray(item)) {
                length *= item.length * this._calculateCycleLength(item);
            }
        }
        return length;
    }
}

// Apply pattern to scale
function applyPatternToScale(pattern, scale, rootFreq) {
    const melody = [];
    for (const step of pattern.generate()) {
        const freq = scale.getFrequency(step, rootFreq);
        melody.push(freq);
    }
    return melody;
}
```

---

## 7. UI Enhancement Suggestions for Online Tool

### Add EDO Mode Switcher

```html
<div class="edo-controls">
    <label>Tuning System:</label>
    <select id="tuning-system">
        <option value="12-tet">12-TET (Standard)</option>
        <option value="ji">Just Intonation</option>
        <option value="24-tet">24-TET</option>
        <option value="31-tet">31-TET</option>
        <option value="custom">Custom EDO...</option>
    </select>

    <div id="custom-edo-input" class="hidden">
        <input type="number" id="edo-divisions" min="5" max="72" value="12">
        <label>divisions per</label>
        <input type="number" id="edo-equave" min="100" max="2400" value="1200">
        <label>cents</label>
    </div>
</div>
```

### Add Cents Display

Show actual cent values next to pitch classes:

```javascript
function updateAnalysisWithCents(pcs, edo) {
    const centsDisplay = pcs.pitchClasses.map(pc => {
        const cents = edo.getCents(pc);
        return `${pc} (${cents.toFixed(1)}c)`;
    }).join(', ');

    document.getElementById('cents-display').textContent = centsDisplay;
}
```

### Add Comparison Mode

Let users A/B test 12-TET vs JI for any chord:

```javascript
function playComparison(pitchClasses) {
    console.log("Playing 12-TET version...");
    playChord12TET(pitchClasses);

    setTimeout(() => {
        console.log("Playing Just Intonation version...");
        playChordJI(pitchClasses);
    }, 2000);
}
```

---

## Summary

| Concept | Mathematical Basis | Online Tool Feature |
|---------|-------------------|---------------------|
| 12-TET | 12th root of 2 | Current clock diagram |
| n-EDO | nth root of 2 | Add EDO selector |
| Just Intonation | Rational ratios | Add JI mode |
| Microtonality | Finer divisions | Extended EDO support |
| Non-octave | Custom equave | Generalized EDO class |
| Patterns | Nested recursion | Melodic pattern generator |

The key insight: **Shape = Quality, Rotation = Transposition**. This principle extends to any n-EDO system, not just 12-TET.
