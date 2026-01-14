# Musical Geometry - Part II: Lattices and Harmonic Space

A plain-text guide based on MAT 111MC coursework, with implementation instructions for the Set Theory Analysis online tool.

---

## 1. Harmonic Space

### Prime Factorization of Intervals

Any rational interval (fraction) can be expressed as a product of prime powers:

```
16/15 = 2^4 × 3^(-1) × 5^(-1)
      = 16 × (1/3) × (1/5)
      = 16/15

9/8 = 2^(-3) × 3^2
    = (1/8) × 9
    = 9/8

5/4 = 2^(-2) × 5^1
    = (1/4) × 5
    = 5/4
```

### Lattice Coordinates

A **harmonic space** is a coordinate system with an axis for each prime:
- Axis 1: Prime 2 (octaves - often omitted)
- Axis 2: Prime 3 (fifths)
- Axis 3: Prime 5 (major thirds)
- Axis 4: Prime 7 (septimal/blues intervals)
- etc.

The ratio 16/15 becomes the coordinate **(4, -1, -1)** in (2, 3, 5) space.

### Prime Limit

The **prime limit** is the largest prime in the system:
- **5-limit**: Uses primes 2, 3, 5 (traditional Western harmony)
- **7-limit**: Adds prime 7 (blues, barbershop)
- **11-limit**: Adds prime 11 (neutral intervals)
- **13-limit**: Adds prime 13 (complex just intonation)

### Implementation

```javascript
// Prime factorization
function primeFactors(n) {
    const factors = {};
    let d = 2;
    while (d * d <= Math.abs(n)) {
        while (n % d === 0) {
            factors[d] = (factors[d] || 0) + 1;
            n /= d;
        }
        d++;
    }
    if (Math.abs(n) > 1) {
        factors[Math.abs(n)] = (factors[Math.abs(n)] || 0) + 1;
    }
    return factors;
}

// Convert ratio to lattice vector
function ratioToLatticeVector(numerator, denominator, primes = [2, 3, 5, 7]) {
    const numFactors = primeFactors(numerator);
    const denFactors = primeFactors(denominator);

    return primes.map(p => {
        const numExp = numFactors[p] || 0;
        const denExp = denFactors[p] || 0;
        return numExp - denExp;
    });
}

// Examples:
// ratioToLatticeVector(3, 2) => [−1, 1, 0, 0] (perfect fifth)
// ratioToLatticeVector(5, 4) => [−2, 0, 1, 0] (major third)
// ratioToLatticeVector(7, 4) => [−2, 0, 0, 1] (septimal seventh)

// Octave reduce (keep within one octave)
function octaveReduce(ratio) {
    while (ratio >= 2) ratio /= 2;
    while (ratio < 1) ratio *= 2;
    return ratio;
}

// Convert lattice vector back to ratio
function latticeVectorToRatio(vector, primes = [2, 3, 5, 7]) {
    let num = 1, den = 1;
    for (let i = 0; i < vector.length; i++) {
        const exp = vector[i];
        if (exp > 0) num *= Math.pow(primes[i], exp);
        else if (exp < 0) den *= Math.pow(primes[i], -exp);
    }
    return { num, den, decimal: num / den };
}
```

---

## 2. 2D Lattice (5-Limit)

### The Tonnetz

A 2D lattice with:
- **X-axis**: Powers of 3 (fifths)
- **Y-axis**: Powers of 5 (major thirds)

```
          5/3----5/4----15/8
         / \    / \    / \
        /   \  /   \  /   \
      4/3----1----3/2----9/8
         \  / \  / \  /
          \/   \/   \/
         8/5----6/5----9/5
```

All ratios are **octave-reduced** (divided by 2 until between 1 and 2).

### Implementation - 2D Lattice Visualization

```javascript
class ToneLattice2D {
    constructor(resolution = 3) {
        this.resolution = resolution;
        this.nodes = [];
        this.generateNodes();
    }

    generateNodes() {
        for (let x = -this.resolution; x <= this.resolution; x++) {
            for (let y = -this.resolution; y <= this.resolution; y++) {
                // Compute ratio: 3^x × 5^y (ignoring prime 2 for octave reduction)
                let ratio = Math.pow(3, x) * Math.pow(5, y);
                ratio = this.octaveReduce(ratio);

                this.nodes.push({
                    coords: [x, y],
                    ratio: ratio,
                    fraction: this.toFraction(ratio)
                });
            }
        }
    }

    octaveReduce(ratio) {
        while (ratio >= 2) ratio /= 2;
        while (ratio < 1) ratio *= 2;
        return ratio;
    }

    toFraction(decimal, tolerance = 0.0001) {
        // Convert decimal to fraction using continued fractions
        let h1 = 1, h2 = 0, k1 = 0, k2 = 1;
        let b = decimal;
        do {
            let a = Math.floor(b);
            let aux = h1; h1 = a * h1 + h2; h2 = aux;
            aux = k1; k1 = a * k1 + k2; k2 = aux;
            b = 1 / (b - a);
        } while (Math.abs(decimal - h1/k1) > tolerance);
        return `${h1}/${k1}`;
    }
}

// Visualization
function drawLattice2D(lattice, canvas, activeRatios = []) {
    const ctx = canvas.getContext('2d');
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const scale = 40;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges (connections between adjacent nodes)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    lattice.nodes.forEach(node => {
        const [x, y] = node.coords;
        const px = cx + x * scale;
        const py = cy - y * scale;

        // Draw lines to adjacent nodes
        [[1, 0], [0, 1], [1, 1], [1, -1]].forEach(([dx, dy]) => {
            const neighbor = lattice.nodes.find(n =>
                n.coords[0] === x + dx && n.coords[1] === y + dy
            );
            if (neighbor) {
                const nx = cx + neighbor.coords[0] * scale;
                const ny = cy - neighbor.coords[1] * scale;
                ctx.beginPath();
                ctx.moveTo(px, py);
                ctx.lineTo(nx, ny);
                ctx.stroke();
            }
        });
    });

    // Draw nodes
    lattice.nodes.forEach(node => {
        const [x, y] = node.coords;
        const px = cx + x * scale;
        const py = cy - y * scale;

        const isActive = activeRatios.includes(node.fraction);
        const isOrigin = x === 0 && y === 0;

        ctx.beginPath();
        ctx.arc(px, py, isActive ? 12 : 8, 0, Math.PI * 2);
        ctx.fillStyle = isActive ? '#7c9fff' : (isOrigin ? '#ff7c9f' : '#333');
        ctx.fill();

        if (isActive || isOrigin) {
            ctx.fillStyle = '#fff';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(node.fraction, px, py + 20);
        }
    });
}
```

---

## 3. 3D Lattice (7-Limit)

### Adding the Septimal Dimension

- **X-axis**: Powers of 3 (fifths)
- **Y-axis**: Powers of 5 (major thirds)
- **Z-axis**: Powers of 7 (septimal/blues intervals)

The 7th harmonic (7/4 = 968.8 cents) is the "blue note" or "barbershop seventh" - 31 cents flatter than the 12-TET minor seventh.

### Implementation - 3D Lattice

```javascript
class ToneLattice3D {
    constructor(resolution = 2) {
        this.resolution = resolution;
        this.nodes = [];
        this.generateNodes();
    }

    generateNodes() {
        for (let x = -this.resolution; x <= this.resolution; x++) {
            for (let y = -this.resolution; y <= this.resolution; y++) {
                for (let z = -this.resolution; z <= this.resolution; z++) {
                    let ratio = Math.pow(3, x) * Math.pow(5, y) * Math.pow(7, z);
                    ratio = this.octaveReduce(ratio);

                    this.nodes.push({
                        coords: [x, y, z],
                        ratio: ratio,
                        cents: 1200 * Math.log2(ratio)
                    });
                }
            }
        }
    }

    octaveReduce(ratio) {
        while (ratio >= 2) ratio /= 2;
        while (ratio < 1) ratio *= 2;
        return ratio;
    }
}

// 3D visualization using isometric projection
function drawLattice3D(lattice, canvas, rotation = { x: 0.5, y: 0.3 }) {
    const ctx = canvas.getContext('2d');
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const scale = 30;

    // Isometric projection
    function project(x, y, z) {
        const cos_x = Math.cos(rotation.x);
        const sin_x = Math.sin(rotation.x);
        const cos_y = Math.cos(rotation.y);
        const sin_y = Math.sin(rotation.y);

        // Rotate around Y axis then X axis
        const x1 = x * cos_y - z * sin_y;
        const z1 = x * sin_y + z * cos_y;
        const y1 = y * cos_x - z1 * sin_x;

        return {
            x: cx + x1 * scale,
            y: cy - y1 * scale,
            depth: z1
        };
    }

    // Sort nodes by depth for proper rendering
    const sortedNodes = [...lattice.nodes].sort((a, b) => {
        const pa = project(...a.coords);
        const pb = project(...b.coords);
        return pa.depth - pb.depth;
    });

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    sortedNodes.forEach(node => {
        const p = project(...node.coords);
        const brightness = Math.max(0.3, 1 - Math.abs(p.depth) * 0.1);

        ctx.beginPath();
        ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(124, 159, 255, ${brightness})`;
        ctx.fill();
    });
}
```

---

## 4. Random Walks (Traversals)

### Adjacent Step Rule

From any node, move only to **immediately adjacent** nodes. This creates melodic motion that is:
- Locally consonant (each step is a simple ratio)
- Globally exploratory (can reach distant harmonies)

### Implementation

```javascript
function randomWalk(lattice, startCoords, numSteps, maxRepeats = 0) {
    const path = [startCoords];
    let current = startCoords;
    let repeatCount = 0;
    let lastNode = null;

    for (let i = 0; i < numSteps; i++) {
        const neighbors = getNeighbors(current, lattice);

        // Filter to avoid immediate repetition
        let validNeighbors = neighbors;
        if (maxRepeats === 0 && lastNode) {
            validNeighbors = neighbors.filter(n =>
                !coordsEqual(n, lastNode)
            );
        }

        if (validNeighbors.length === 0) validNeighbors = neighbors;

        // Random selection
        const next = validNeighbors[Math.floor(Math.random() * validNeighbors.length)];
        path.push(next);
        lastNode = current;
        current = next;
    }

    return path;
}

function getNeighbors(coords, lattice) {
    const dim = coords.length;
    const neighbors = [];

    // Generate all adjacent coordinates (±1 in each dimension)
    for (let d = 0; d < dim; d++) {
        for (const delta of [-1, 1]) {
            const newCoords = [...coords];
            newCoords[d] += delta;

            // Check if node exists in lattice
            if (lattice.nodes.find(n => coordsEqual(n.coords, newCoords))) {
                neighbors.push(newCoords);
            }
        }
    }

    return neighbors;
}

function coordsEqual(a, b) {
    return a.length === b.length && a.every((v, i) => v === b[i]);
}

// Convert path to playable sequence
function pathToMelody(path, lattice, baseFreq = 261.63) {
    return path.map(coords => {
        const node = lattice.nodes.find(n => coordsEqual(n.coords, coords));
        return baseFreq * node.ratio;
    });
}
```

---

## 5. Scales Embedded in Lattices

### Major Scale in 5-Limit Lattice

```
Scale degrees as ratios:
1 = 1/1   [0, 0]
2 = 9/8   [2, 0]
3 = 5/4   [0, 1]
4 = 4/3   [-1, 0]
5 = 3/2   [1, 0]
6 = 5/3   [-1, 1]
7 = 15/8  [1, 1]
```

### Visualization

```javascript
const SCALE_RATIOS = {
    major: ['1/1', '9/8', '5/4', '4/3', '3/2', '5/3', '15/8'],
    minor: ['1/1', '9/8', '6/5', '4/3', '3/2', '8/5', '9/5'],
    dorian: ['1/1', '9/8', '6/5', '4/3', '3/2', '5/3', '9/5'],
    bagpipes: ['1/1', '9/8', '5/4', '4/3', '27/20', '3/2', '5/3', '7/4', '16/9', '9/5']
};

function embedScaleInLattice(scaleRatios, lattice) {
    const embeddedNodes = [];

    scaleRatios.forEach(ratioStr => {
        const [num, den] = ratioStr.split('/').map(Number);
        const vector = ratioToLatticeVector(num, den);

        // Find corresponding node in lattice
        const node = lattice.nodes.find(n =>
            coordsEqual(n.coords, vector.slice(1)) // Skip prime 2
        );

        if (node) embeddedNodes.push(node);
    });

    return embeddedNodes;
}

// Key observation: All scale notes are CONNECTED in the lattice
// There are no isolated "islands" - each note is adjacent to at least one other
```

---

## 6. Combination Product Sets (CPS)

### The Hexany

The simplest CPS structure. Take 4 elements {A, B, C, D} and form all **2-wise products**:

```
AB, AC, AD, BC, BD, CD
```

That's 6 products (hence "Hexany" = 6).

Using harmonics {1, 3, 5, 7}:

```
1×3 = 3
1×5 = 5
1×7 = 7
3×5 = 15
3×7 = 21
5×7 = 35
```

Octave-reduced:
```
3/2, 5/4, 7/4, 15/8, 21/16, 35/32
```

### CPS Geometry

The Hexany forms an **octahedron** in harmonic space - a perfectly symmetric structure with no tonal center.

### Implementation

```javascript
class CombinationProductSet {
    constructor(factors, k) {
        this.factors = factors;  // e.g., [1, 3, 5, 7]
        this.k = k;              // k-wise combinations (2 for Hexany)
        this.products = this.generateProducts();
    }

    generateProducts() {
        const combos = this.combinations(this.factors, this.k);
        return combos.map(combo => ({
            factors: combo,
            product: combo.reduce((a, b) => a * b, 1),
            reduced: this.octaveReduce(combo.reduce((a, b) => a * b, 1))
        }));
    }

    combinations(arr, k) {
        if (k === 0) return [[]];
        if (arr.length === 0) return [];

        const [first, ...rest] = arr;
        const withFirst = this.combinations(rest, k - 1).map(c => [first, ...c]);
        const withoutFirst = this.combinations(rest, k);
        return [...withFirst, ...withoutFirst];
    }

    octaveReduce(ratio) {
        while (ratio >= 2) ratio /= 2;
        while (ratio < 1) ratio *= 2;
        return ratio;
    }

    // Get all ratios as playable frequencies
    toFrequencies(baseFreq = 261.63) {
        return this.products.map(p => baseFreq * p.reduced);
    }
}

// Hexany: 4 factors, 2-wise combinations
const hexany = new CombinationProductSet([1, 3, 5, 7], 2);
// Products: 3, 5, 7, 15, 21, 35

// Eikosany: 6 factors, 3-wise combinations
const eikosany = new CombinationProductSet([1, 3, 5, 7, 9, 11], 3);
// Products: 20 combinations = "Eikosany" (Greek for 20)
```

### CPS Shape Finding

Find all instances of a particular shape within a CPS:

```javascript
function findShapeInCPS(cps, shape) {
    // shape is array of intervals, e.g., [0, 4, 7] for major triad
    // Find all transpositions of this shape that exist in the CPS

    const matches = [];
    const products = cps.products.map(p => p.reduced);

    products.forEach((root, i) => {
        const shapeRatios = shape.map(interval => {
            // Convert interval to ratio and multiply by root
            const ratio = Math.pow(2, interval / 12) * root;
            return cps.octaveReduce(ratio);
        });

        // Check if all shape ratios exist in CPS
        const allExist = shapeRatios.every(r =>
            products.some(p => Math.abs(p - r) < 0.001)
        );

        if (allExist) {
            matches.push({
                root: root,
                ratios: shapeRatios
            });
        }
    });

    return matches;
}
```

---

## 7. Dimensionality Reduction

### The Problem

Higher prime limits (11-limit, 13-limit) require 4D, 5D, or more dimensions - impossible to visualize directly.

### Solution: MDS (Multi-Dimensional Scaling)

Project high-dimensional points to 2D/3D while preserving distances as much as possible.

```javascript
// Simplified MDS implementation
function mds(distances, targetDim = 2) {
    const n = distances.length;

    // Double centering
    const B = doubleCenter(distances);

    // Eigendecomposition (simplified - use a library in practice)
    const { eigenvalues, eigenvectors } = eigenDecompose(B);

    // Take top k eigenvectors
    const coords = [];
    for (let i = 0; i < n; i++) {
        const point = [];
        for (let d = 0; d < targetDim; d++) {
            point.push(eigenvectors[d][i] * Math.sqrt(Math.max(0, eigenvalues[d])));
        }
        coords.push(point);
    }

    return coords;
}

function doubleCenter(D) {
    const n = D.length;
    const D2 = D.map(row => row.map(d => d * d));

    // Row and column means
    const rowMeans = D2.map(row => row.reduce((a, b) => a + b, 0) / n);
    const colMeans = Array(n).fill(0).map((_, j) =>
        D2.reduce((sum, row) => sum + row[j], 0) / n
    );
    const grandMean = rowMeans.reduce((a, b) => a + b, 0) / n;

    // Double centered matrix
    const B = [];
    for (let i = 0; i < n; i++) {
        B[i] = [];
        for (let j = 0; j < n; j++) {
            B[i][j] = -0.5 * (D2[i][j] - rowMeans[i] - colMeans[j] + grandMean);
        }
    }

    return B;
}
```

---

## 8. UI Enhancement Suggestions

### Add Lattice View Tab

```html
<button class="viz-mode-btn" data-mode="lattice">Lattice</button>
```

### Lattice Controls

```html
<div id="lattice-controls" class="hidden">
    <label>Prime Limit:</label>
    <select id="prime-limit">
        <option value="5">5-limit (2D)</option>
        <option value="7">7-limit (3D)</option>
        <option value="11">11-limit (4D→MDS)</option>
    </select>

    <label>Resolution:</label>
    <input type="range" id="lattice-resolution" min="1" max="5" value="3">

    <button id="random-walk-btn">Random Walk</button>
    <button id="embed-scale-btn">Embed Scale</button>
</div>
```

### CPS Explorer

```html
<div id="cps-controls">
    <label>CPS Type:</label>
    <select id="cps-type">
        <option value="hexany">Hexany (4 factors, 2-wise)</option>
        <option value="dekany">Dekany (5 factors, 2-wise)</option>
        <option value="eikosany">Eikosany (6 factors, 3-wise)</option>
    </select>

    <label>Factors:</label>
    <input type="text" id="cps-factors" value="1, 3, 5, 7">

    <button id="generate-cps-btn">Generate</button>
    <button id="play-cps-btn">Play All</button>
</div>
```

---

## Summary

| Concept | Description | Implementation |
|---------|-------------|----------------|
| Prime Factorization | Express ratios as prime powers | `ratioToLatticeVector()` |
| 2D Lattice (5-limit) | Axes for primes 3 and 5 | `ToneLattice2D` class |
| 3D Lattice (7-limit) | Add prime 7 axis | `ToneLattice3D` class |
| Octave Reduction | Keep ratios between 1 and 2 | `octaveReduce()` |
| Random Walks | Adjacent-step traversals | `randomWalk()` |
| Scale Embedding | Map scale degrees to lattice | `embedScaleInLattice()` |
| CPS | Combination products, no center | `CombinationProductSet` class |
| Dimensionality Reduction | Project to 2D/3D | MDS algorithm |

### Key Insights

1. **All historical scales** from diverse cultures share a property: their lattice embeddings are **connected** (no isolated notes).

2. **CPS structures** have **no tonal center** - every note is equally important. This is fundamentally different from traditional scales.

3. **Random walks** in harmonic space create melodies that are locally consonant but globally exploratory - similar to how language models generate text that's syntactically correct but may lack semantic coherence.

4. The lattice representation reveals **hidden relationships** between intervals that aren't obvious in the standard pitch class representation.
