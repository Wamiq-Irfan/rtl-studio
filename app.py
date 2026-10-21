from collections import Counter
from pathlib import Path
import hashlib
import base64
import json
import os

import streamlit as st
from engine import explain, lint, module_names, schematic, synthesize
from viewer import viewer_html

ROOT = Path(__file__).parent
st.set_page_config(page_title='RTL Studio · Write. Inspect. Debug.', page_icon='◈', layout='wide')
st.markdown('''<style>
.stApp {background:#0b1220;color:#e2e8f0}
h1 {letter-spacing:-1.8px} [data-testid="stSidebar"] {background:#111c2c}
textarea {font-family:Consolas,monospace!important;font-size:14px!important;line-height:1.6!important}
.eyebrow {color:#2dd4bf;letter-spacing:3px;font-size:12px;font-weight:700}
.intro {color:#94a3b8;font-size:17px;margin-bottom:24px}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">RTL STUDIO / LOCAL WORKSPACE</div>', unsafe_allow_html=True)
st.title('From RTL to a clearer picture.')
st.markdown('<div class="intro">Write SystemVerilog, inspect the hardware, and work through diagnostics.</div>', unsafe_allow_html=True)

if 'code' not in st.session_state:
    st.session_state.code = (ROOT / 'examples/counter.sv').read_text()
if 'analysis' not in st.session_state:
    st.session_state.analysis = None

with st.sidebar:
    st.subheader('◈ RTL Studio')
    st.caption('Python + Yosys + slang')
    example = st.selectbox('Example design', ['counter', 'mux', 'broken'])
    if st.button('Load example', use_container_width=True):
        st.session_state.code = (ROOT / f'examples/{example}.sv').read_text()
        st.session_state.analysis = None
        st.session_state.pop('ai_answer', None)
        st.rerun()
    st.divider()
    st.subheader('AI connection · optional')
    st.caption('Local synthesis needs no API key. Clicking “Ask AI” sends the current RTL and diagnostics to your configured provider.')
    endpoint = st.text_input('Chat Completions endpoint', value=os.getenv('RTL_AI_ENDPOINT', ''), placeholder='https://your-provider/…/chat/completions')
    model = st.text_input('Model ID', value=os.getenv('RTL_AI_MODEL', ''))
    key = st.text_input('API key', type='password', value=os.getenv('RTL_AI_KEY', ''))
    st.caption('Credentials stay in this running session; they are not written to project files.')
    st.divider()
    st.caption('Version 0.1 · Synthesizable RTL only for diagrams. UVM classes and testbenches are not circuits.')

wide_view = st.toggle('Full-width workspace', value=True, help='Show the editor and circuit vertically so the circuit can use the full page width.')
left, right = (st.container(), st.container()) if wide_view else st.columns([1.05, 1], gap='large')
with left:
    st.subheader('01 / Source')
    mode = st.radio('Input method', ['Write / paste RTL', 'Upload files'], horizontal=True)
    if mode == 'Upload files':
        files = st.file_uploader('Select .sv or .v files', type=['sv', 'v'], accept_multiple_files=True)
        st.caption('Files are combined in the selected order. Put packages before modules that import them. Include-file resolution is not supported in v0.1.')
        if files:
            signature = hashlib.sha256(b''.join(f.name.encode() + f.getvalue() for f in files)).hexdigest()
            if st.button('Open uploads in editor', use_container_width=True):
                try:
                    st.session_state.code = '\n\n'.join(f'// File: {Path(f.name).name}\n' + f.getvalue().decode('utf-8-sig') for f in files)
                    st.session_state.analysis = None
                    st.rerun()
                except UnicodeDecodeError:
                    st.error('Please upload UTF-8 text files.')
    source = st.text_area('Editable SystemVerilog source', key='code', height=460)
    names = module_names(source)
    top = st.selectbox('Top module', names) if names else ''
    gates = st.toggle('Generic gate view', value=False, help='Technology-independent logic mapping; not a foundry standard-cell netlist.')
    run_col, lint_col = st.columns(2)
    run = run_col.button('Generate circuit →', type='primary', use_container_width=True, disabled=not bool(top))
    check = lint_col.button('Check SV', use_container_width=True, disabled=not source.strip())
    st.download_button('Download source', source, file_name=f'{top or "design"}.sv', mime='text/plain')

fingerprint = hashlib.sha256((source + '\0' + top + str(gates)).encode()).hexdigest()
if run or check:
    record = {'fingerprint': fingerprint, 'diagnostics': '', 'result': None, 'top': top}
    with st.spinner('Checking SystemVerilog…'):
        try:
            record['diagnostics'] = lint(source)
        except Exception as error:
            record['diagnostics'] = f'SV checker failed: {error}'
    if run:
        with st.spinner('Synthesizing the actual RTL… first launch may take a minute.'):
            try:
                record['result'] = synthesize(source, top, gates)
            except Exception as error:
                record['result'] = {'ok': False, 'log': str(error), 'netlist': None}
    st.session_state.analysis = record
    st.session_state.pop('ai_answer', None)

with right:
    st.subheader('02 / Inspect')
    diagram_tab, diagnostics_tab, netlist_tab = st.tabs(['Circuit', 'Diagnostics', 'Netlist'])
    record = st.session_state.analysis
    fresh = bool(record and record['fingerprint'] == fingerprint)
    if record and not fresh:
        st.warning('Source or settings changed. Run again to refresh the results.')
    with diagram_tab:
        if not fresh or not record.get('result'):
            st.info('Write or upload RTL, choose its top module, then generate the circuit.')
        elif not record['result']['ok']:
            st.error('Synthesis did not complete. Open Diagnostics for the actual tool output.')
        else:
            netlist = record['result']['netlist']
            cells = netlist['modules'][top].get('cells', {})
            a, b = st.columns(2)
            a.metric('Synthesized cells', len(cells))
            b.metric('Module ports', len(netlist['modules'][top].get('ports', {})))
            try:
                show_symbols = st.toggle('Gate symbols', value=True, help='Draw supported logic cells using gate symbols. Other cells remain labeled blocks. Exact Yosys types and port names are preserved.')
                svg = schematic(netlist, top, symbols=show_symbols)
                page = viewer_html(svg)
                st.iframe('data:text/html;base64,' + base64.b64encode(page.encode()).decode(), height=680 if wide_view else 560)
                st.caption('Fit circuit shows all blocks. Use + / − or Ctrl+wheel to zoom; scroll to explore. Hover for source and connection details. Crossings are not junctions.')
                st.caption('Symbols can represent multi-bit operations in RTL view. Enable Generic gate view for technology-independent bit-level mapping. Sequential blocks retain their exact cell type; clock/reset polarity and behavior are defined by the netlist parameters.')
                st.download_button('Export SVG', svg, f'{top}.svg', 'image/svg+xml')
                st.download_button('Download full-browser circuit viewer', page, f'{top}_viewer.html', 'text/html', help='Open this HTML file in your browser for a standalone interactive circuit view.')
            except Exception as error:
                st.warning(f'Diagram unavailable: {error}. The synthesized JSON is still available.')
            if cells:
                with st.expander('Cell types'):
                    st.json(dict(Counter(c['type'] for c in cells.values())))
    with diagnostics_tab:
        if fresh:
            st.markdown('**SystemVerilog compiler diagnostics**')
            st.code(record['diagnostics'] or 'No compiler diagnostics reported. This does not prove functional correctness.', language='text')
            if record.get('result'):
                st.markdown('**Synthesis output**')
                st.code(record['result']['log'], language='text')
        else:
            st.caption('Run Check SV or Generate circuit to see tool diagnostics.')
    with netlist_tab:
        if fresh and record.get('result') and record['result']['ok']:
            data = json.dumps(record['result']['netlist'], indent=2)
            st.download_button('Export netlist JSON', data, f'{top}.json', 'application/json')
            with st.expander('Inspect JSON'):
                st.json(record['result']['netlist'])
        else:
            st.caption('A successful synthesis produces the netlist shown here.')

st.divider()
st.subheader('03 / Debug with context')
question = st.text_area('What should this design do, and what is going wrong?', height=85,
    placeholder='Example: count should increment only when enable is high. Explain any reset or width issues.')
ask = st.button('Ask AI', disabled=not (endpoint and model and key and source.strip() and question.strip() and fresh))
if not fresh:
    st.caption('Run a check on the current source before asking AI.')
elif not (endpoint and model and key):
    st.caption('Configure your AI provider in the sidebar to enable explanations.')
if ask:
    with st.spinner('Reviewing source and tool diagnostics…'):
        try:
            logs = record['diagnostics'] + '\n' + ((record.get('result') or {}).get('log', ''))
            st.session_state.ai_answer = {'fingerprint': fingerprint, 'text': explain(source, logs, question, key, endpoint, model)}
        except Exception:
            st.error('AI request failed. Check your endpoint, model ID, key, provider quota, and network connection.')
answer = st.session_state.get('ai_answer')
if answer and answer['fingerprint'] == fingerprint:
    st.markdown(answer['text'])
    st.caption('AI suggestions are unverified. Review changes and rerun checking, synthesis, and your testbench.')
