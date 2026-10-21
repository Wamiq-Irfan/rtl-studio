# RTL Studio

**SystemVerilog → synthesized netlist → interactive logic-gate schematic.**

A Python EDA project for exploring RTL hardware structure and understanding compiler diagnostics, with optional AI-assisted debugging.

## Features

- Write or paste RTL, or upload editable Verilog/SystemVerilog files.
- Synthesize real hardware connectivity using Yosys.
- View gate symbols, named pins, and RTL-level or generic gate-level cells.
- Explore diagrams with fit/zoom controls and export SVG, JSON, or an interactive HTML viewer.
- Inspect SystemVerilog compiler diagnostics using slang/pyslang.
- Ask a configured AI provider to explain diagnostics and suggest changes.

## Overview

Write/paste SystemVerilog directly in an editable browser editor, or upload one or more `.v` / `.sv` files. Generate a real Yosys netlist and SVG connectivity diagram; inspect slang compiler diagnostics and synthesis logs. Optionally ask an AI provider to explain the source and actual diagnostics.

The workspace now defaults to full width. Circuit views automatically fit all blocks and include zoom controls, 100% scale, and Ctrl+wheel zoom. Turn off **Full-width workspace** for side-by-side editing. **Download full-browser circuit viewer** exports an interactive HTML file you can open in its own browser tab.

**Gate symbols** is on by default: AND, OR, XOR, NOT, NAND, NOR, XNOR, buffers and muxes use circuit shapes. Sequential cells use a labeled flip-flop block, with clock markers and the exact Yosys cell type. Input and output wires attach at individually named port terminals. Unsupported arithmetic and other cells stay as labeled blocks. In RTL view, one symbol may represent a multi-bit or reduction operation; use **Generic gate view** for bit-level generic mapping. This is not a transistor-level or foundry-library schematic. Reset values, enables and clock/reset polarity remain defined by the original netlist parameters; inspect the JSON for full sequential semantics.

## Start on Windows

Install Python 3.10 or newer. Extract this folder, open a terminal inside it, and run:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Open the local address printed by Streamlit, normally http://localhost:8501.
No separate FPGA tool installation is required: `yowasp-yosys` supplies a WebAssembly build of Yosys. First synthesis may take longer while the runtime initializes. Native `yosys`, if on PATH, is preferred.

## Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## First demo

1. Load `counter` from the sidebar, or type your RTL in the editor.
2. Select the top module and click **Generate circuit**.
3. Inspect the actual synthesized cells and their connectivity; export SVG or JSON.
4. Load `broken` and generate again. The intentional latch inside `always_comb` should trigger a synthesis error.
5. For AI help, supply a Chat Completions compatible endpoint, model ID, and API key in the sidebar. Run a check, describe the intended behavior, and click **Ask AI**.

API keys are not bundled. AI calls can incur provider charges. Only clicking Ask AI sends code and logs to the configured provider. Local synthesis and compiler checking do not need AI credentials. Settings can also be supplied as RTL_AI_ENDPOINT, RTL_AI_MODEL, RTL_AI_KEY environment variables.

## Implemented / boundaries

- Direct writing/pasting and file uploads both work; uploads remain editable.
- Compiler diagnostics use real pyslang; synthesis uses real Yosys. The tool does not invent circuits or use regex to synthesize RTL. A simple module-name scan only populates the top-module selector.
- Default view contains RTL-level cells after process lowering and optimization. Generic gate view adds technology-independent mapping; neither is a foundry-mapped or physical-layout view.
- Diagrams show grouped bit connectivity, not individual per-bit pin routing. Hover wires for pin and bit information. Hover cells for synthesis source attributes. Feedback edges are supported; large diagrams use a simple layout. There is no code-jump navigation or waveform viewer yet.
- Maximum rendered graph: 250 nodes. Larger synthesized designs can export JSON. Synthesis timeout: 120 seconds.
- Supported synthesis subset depends on your Yosys version/frontend. UVM classes, simulation delays, and testbench behavior are not synthesizable hardware. slang may accept code that the synthesis frontend cannot synthesize.
- Uploads are concatenated in selection order. Include directories, uploaded include files, macros configured outside source, arbitrary source-file ordering, and per-file diagnostic mapping are not yet supported. Diagnostic lines refer to the combined editor text.
- Diagnostics are compiler and synthesis checks, not a complete static-analysis suite or functional proof. Use simulation/assertions for design intent. AI patches are suggestions and are not automatically applied or verified.
- Run locally for trusted RTL. This is a development app, not an isolated multi-user synthesis service. Do not expose the Streamlit port publicly.

## Validation

Run `python -m unittest discover -s tests -v` after installing requirements.

## Structure

- `app.py`: Streamlit UI, editing/upload, results and AI configuration.
- `engine.py`: compilation, synthesis, SVG rendering, optional AI requests.
- `symbols.py`: vector gate artwork and pin geometry.
- `viewer.py`: standalone fit/zoom circuit viewer.
- `examples/`: counter, mux, and intentional latch failure.
- `tests/`: synthesis, malformed-source and connectivity checks.

Useful upstream references: https://yosyshq.readthedocs.io/ and https://sv-lang.com/user-manual.html
