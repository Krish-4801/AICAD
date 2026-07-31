# AICAD — Workspace Guidelines

Welcome to the **AICAD** workspace. This project enables parametric 3D CAD model generation from natural language descriptions.

## Workspace Conventions

- **Language**: Python 3.13+
- **Package Manager**: `uv`
- **Core Library**: `build123d` (high-level parametric CAD wrapper around OpenCascade/OCP)
- **Primary Files**: STEP files (`.step`, `.stp`) are the primary source of truth for CAD models.
- **Secondary Exports**: STL, 3MF, and DXF are exported from STEP models.

## CAD Skill Integration

A dedicated agent skill for CAD generation is located at `.gemini/skills/cad/`. Gemini CLI automatically discovers this skill at session start.

When processing user requests to build or modify 3D parts:
1. **Design first**: Translate requirements into an internal brief following the guidelines in `.gemini/skills/cad/references/natural-language-specs.md`.
2. **Write build123d code**: Follow the precise API patterns documented in `.gemini/skills/cad/references/build123d-modeling.md`.
3. **Generate STEP**: Generate the 3D model using the step script:
   ```bash
   uv run python .gemini/skills/cad/scripts/step path/to/source.py
   ```
4. **Inspect STEP details**: Inspect generated or existing STEP files with:
   ```bash
   uv run python .gemini/skills/cad/scripts/inspect path/to/source.py
   ```
5. **Verify Visually**: Take snapshots of the model to ensure it is correct:
   ```bash
   uv run python .gemini/skills/cad/scripts/snapshot path/to/source.py
   ```
6. **Convert formats**: Export secondary files (STL, 3MF, DXF) using step sidecars or the dxf script:
   ```bash
   uv run python .gemini/skills/cad/scripts/step path/to/source.py --stl path/to/model.stl --3mf path/to/model.3mf
   uv run python .gemini/skills/cad/scripts/dxf path/to/source.py
   ```

7. **Conversational Memory & Editing**: When processing a request inside a `requests/req_xxx` folder, inspect `requests/req_xxx/request.json`. If a `parent_id` is specified, there should be a `model.py` already present in the folder (pre-copied from the parent request). Read this code, and instead of generating a new script from scratch, modify the existing parent code to implement the requested changes. Retain parameters, dimensions, and logic that are not targeted by the edit to maintain continuity.

Always use `uv run python` to ensure commands execute within the configured virtual environment.
