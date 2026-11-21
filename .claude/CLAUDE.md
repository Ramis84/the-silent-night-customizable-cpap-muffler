# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a parametric 3D CAD project that generates printable STL and STEP files for a CPAP sound muffler. The muffler attaches inline on a CPAP hose to reduce noise. It is compatible with standard 22mm rubber hose connectors.

The active version is **v2-build123d** (Python/build123d). The **v1-openscad** folder is a legacy version kept for spare-parts reference only.

## Running the Script

```bash
pip install build123d bd_warehouse
# Optional VSCode 3D preview:
pip install ocp_vscode

cd v2-build123d
python "The Silent Night Customizable CPAP Silencer-Muffler v2.py"
```

Running the script regenerates all ~66 output files (33 `.stl` + 33 `.step`) in the same directory. There is no separate build system, test suite, or lint configuration.

## Architecture of the Python Script

The single source file ([v2-build123d/The Silent Night Customizable CPAP Silencer-Muffler v2.py](v2-build123d/The%20Silent%20Night%20Customizable%20CPAP%20Silencer-Muffler%20v2.py)) is structured in four layers:

1. **Parameters** — All tunable constants and enums at the top of the file (dimensions, tolerances, thread pitch, grip geometry, O-ring sizes, mesh counts). Edit these to customize the design.
2. **Helper functions** — Parameterized geometry builders that return build123d `Part` or `Sketch` objects (profiles, bodies, end caps, threads, O-rings, inner mesh tube).
3. **Instance generation** — Calls helper functions to produce every size/length/configuration variant (e.g., `body_male_large_100`, `end_cap_female_small_2_0_extra_spacing`).
4. **Export loops** — Writes all instances to `.stl` and `.step` using build123d's `export_stl` / `export_step`.

### Key design patterns

- **2D → 3D via revolve:** Most parts are defined as a 2D `Sketch` on the XZ plane, then `revolve()`d around the Z-axis to produce rotationally symmetric solids.
- **Boolean composition:** Shapes are combined with `+` (union), `-` (difference), and `&` (intersection).
- **Size variants** are driven by the `MufflerORingInnerDiameter` enum (SMALL=44 mm, MEDIUM=47 mm, LARGE=50 mm) and `MufflerLength` enum (SHORT=70, REGULAR=85, LONG=100 mm).

### Printed parts per muffler
- **Body** — outer cylinder, male 22mm hose connector, internal thread for end cap, O-ring groove.
- **End cap** — male or female 22mm connector, external thread, grip cutouts. Female variant includes a slot for a 21 mm O-ring.
- **Inner mesh tube** — central air-flow tube with helical mesh strands; optional corkscrew interior variant for turbulence.
- **O-ring** (optional) — printable TPU version of the large body O-ring; real rubber is preferred for the female connector.

### VSCode 3D preview

Uncomment one `show()` call in the preview section near the bottom of the file to visualise a part interactively (requires `ocp_vscode`).
