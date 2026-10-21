# Validation

Original version validated in Python 3.11 with the versions pinned in requirements.txt. The circuit-view update was also checked with Python 3.12.

- Counter synthesized to real sequential and arithmetic cells.
- Mux synthesized to a real mux, with connected ports and valid exported SVG.
- Generic gate mapping produced generic mux cells.
- Malformed SV produced compiler diagnostics.
- The intentional always_comb latch example failed synthesis with a latch diagnostic.
- Invalid top-module identifiers were rejected.
- Module discovery ignored commented-out declarations.
- Streamlit AppTest exercised initial render, direct source editing, compilation, synthesis, stale-result warnings, and upload mode selection.
- Viewer JavaScript fit, zoom-in, 100% scale, and reset calculations were exercised using a simulated DOM in Node.js. Real browser rendering remains unverified.
- Gate symbol artwork was rasterized with Inkscape and visually inspected. A synthesized full-adder test checks for AND/OR/XOR symbols, valid SVG, and the fallback block view. Generic inverter and sequential-cell classification are checked separately.

Live AI calls were not exercised because no provider credentials were supplied. Full browser visual QA, Windows installation, and end-to-end file picker upload were not exercised in this environment. No functional equivalence or timing claim is made.
