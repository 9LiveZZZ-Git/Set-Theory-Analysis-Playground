# Changelog - Set Theory Analysis Online

## Version 2.0.0 (2025-01-14)

### Major Features

#### Tone.js Audio Engine
Replaced basic Web Audio API with professional **Tone.js** synthesis library for high-quality audio playback.

**New Synth Types:**
| Synth | Description |
|-------|-------------|
| `triangle` | Classic soft triangle wave (default) |
| `sine` | Pure sine wave |
| `square` | Hollow square wave |
| `sawtooth` | Bright sawtooth wave |
| `fm` | FM synthesis with modulation index control |
| `am` | AM synthesis with harmonicity |
| `fat` | Layered "fat" oscillators with spread |
| `pulse` | Pulse wave with variable width |
| `duo` | Dual oscillator with vibrato |
| `metal` | Metallic/bell-like sounds |
| `pluck` | Plucked string simulation |
| `strings` | Orchestral string pad |
| `piano` | Piano-like FM synthesis |

#### Effects Chain
Full effects processing chain:
- **Filter** - Lowpass, highpass, bandpass with frequency control
- **Delay** - Feedback delay with time and wet controls
- **Reverb** - Convolution reverb with decay and wet mix
- **Chorus** - Chorus effect for width

#### SuperCollider Backend (Optional)
For professional sound design, connect to SuperCollider synthesis:

1. **SuperCollider Code** - Embedded SC3 code with custom synth definitions:
   - `\pcsSine` - Clean sine tones
   - `\pcsTri` - Triangle with warmth
   - `\pcsSaw` - Bright sawtooth
   - `\pcsSquare` - Classic square wave
   - `\pcsPad` - Evolving pad sounds
   - `\pcsBell` - FM bell tones
   - `\pcsFM` - General FM synthesis

2. **WebSocket-OSC Bridge** - Python bridge script included:
   ```bash
   pip install websockets python-osc
   python bridge.py
   ```

3. **OSC Commands**:
   - `/pcs/chord [pcs...] duration` - Play chord
   - `/pcs/arpeggio [pcs...] noteLength` - Play arpeggio
   - `/pcs/stop` - Stop all notes
   - `/pcs/synth name` - Change synth
   - `/pcs/octave n` - Set octave
   - `/pcs/velocity n` - Set velocity (0-1)

### Audio Settings
New configurable parameters:
- Base octave (default: 4)
- Velocity (0-1)
- A4 frequency (default: 440 Hz)
- Arpeggio speed (ms)
- Chord duration (ms)
- Envelope (ADSR)
- Filter frequency and type
- Effect wet/dry mix

---

## Version 1.0.0 (Initial Release)

### Core Features
- Pitch class set analysis (Allen Forte classification)
- Prime form and normal form calculation
- Interval vector computation
- Forte number lookup (complete 208 set classes)
- Z-relation detection

### Visualization
- Interactive clock diagram (p5.js)
- Graph view showing interval relationships
- Mini-clock transformation previews

### Transformations
- Transposition (T0-T11)
- Inversion (I0-I11)
- Retrograde
- Complement
- Prime form reduction

### Input Methods
- Text input (numbers, note names, Forte numbers)
- Interactive piano keyboard
- Click on clock nodes

### Additional Features
- Subset/superset finder
- Similar sets (by interval vector)
- Music examples library
- Recent sets history
- MIDI export
- Collapsible panels
- Dark theme

---

## Supplementary Documentation

### Musical Geometry Guides
Two educational documents based on MAT 111MC coursework:

1. **Musical_Geometry_Part_I_EDO_Systems.md**
   - Equal Octave Divisions (n-EDO)
   - Just Intonation vs Equal Temperament
   - Microtonality (24-TET, 31-TET, etc.)
   - Non-octave divisions (Bohlen-Pierce)
   - Melodic pattern generation

2. **Musical_Geometry_Part_II_Lattices.md**
   - Harmonic space / prime lattices
   - 2D and 3D lattice visualization
   - Random walk traversals
   - Scale embedding
   - Combination Product Sets (CPS)
   - Dimensionality reduction (MDS)

Both include JavaScript implementation code for extending the online tool.
