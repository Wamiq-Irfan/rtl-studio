"""Vector gate artwork and named pin geometry for synthesized Yosys cells."""
import html


def gate_kind(cell_type):
    basic = cell_type.strip('$').strip('_').upper()
    if basic in {'AND', 'OR', 'XOR', 'XNOR', 'NAND', 'NOR', 'NOT', 'BUF', 'MUX'}:
        return basic
    reductions = {'$reduce_and': 'AND', '$reduce_or': 'OR', '$reduce_xor': 'XOR',
                  '$reduce_xnor': 'XNOR', '$reduce_bool': 'OR', '$logic_not': 'NOT',
                  '$logic_and': 'AND', '$logic_or': 'OR'}
    if cell_type in reductions:
        return reductions[cell_type]
    # Preserve the exact Yosys type below the symbol: reset/enable/polarity
    # variants remain identifiable and all actual ports remain visible.
    if 'dff' in cell_type.lower():
        return 'DFF'
    return None


def port_y(node, port, direction):
    ports = [p for p, d in node.get('directions', {}).items() if d == direction]
    if port not in ports:
        return 49
    return 49 + (ports.index(port) - (len(ports)-1)/2) * min(22, 60/max(1, len(ports)-1))


def cell_art(node, enabled=True):
    """Local coordinates span x=0..175; port terminals match edge anchors."""
    esc = lambda text: html.escape(str(text), quote=True)
    kind = gate_kind(node['label']) if enabled else None
    color = '#2dd4bf'
    parts = [f'<g data-symbol="{kind or "BLOCK"}">',
             f'<title>{esc(node["label"])}\n{esc(node["detail"])}\n{esc(node.get("src", ""))}</title>']
    style = f'fill="#19283b" stroke="{color}" stroke-width="2"'
    if kind in {'AND', 'NAND'}:
        parts.append(f'<path d="M45,18 H92 C149,18 149,80 92,80 H45 Z" {style}/>')
    elif kind in {'OR', 'NOR', 'XOR', 'XNOR'}:
        parts.append(f'<path d="M40,18 Q100,18 135,49 Q100,80 40,80 Q66,49 40,18 Z" {style}/>')
        if kind in {'XOR', 'XNOR'}:
            parts.append(f'<path d="M32,18 Q58,49 32,80" fill="none" stroke="{color}" stroke-width="2"/>')
    elif kind in {'NOT', 'BUF'}:
        parts.append(f'<path d="M45,18 L135,49 L45,80 Z" {style}/>')
    elif kind == 'MUX':
        parts.append(f'<path d="M45,12 L135,27 V71 L45,86 Z" {style}/><text x="80" y="53" fill="#e2e8f0" font-family="monospace" font-size="13">MUX</text>')
    else:
        parts.append(f'<rect x="40" y="10" width="100" height="78" rx="{0 if kind == "DFF" else 8}" {style}/><text x="90" y="53" text-anchor="middle" fill="#e2e8f0" font-family="monospace" font-size="12">{esc(kind or node["label"][:12])}</text>')
    inverted = kind in {'NOT', 'NAND', 'NOR', 'XNOR'}
    for port, direction in node.get('directions', {}).items():
        y = port_y(node, port, direction)
        if direction == 'input':
            # Curved OR/XOR input outline is a quadratic; end at its real boundary.
            end = 45
            if kind in {'OR', 'NOR', 'XOR', 'XNOR'}:
                t = max(0, min(1, (y-18)/62))
                end = 40 + 52*t*(1-t)
            if kind is None or kind == 'DFF':
                end = 40
            parts.append(f'<path d="M0,{y} H{end}" fill="none" stroke="{color}" stroke-width="1.5"/>')
            if kind == 'DFF' and port.upper() in {'CLK', 'C'}:
                parts.append(f'<path d="M40,{y-5} L48,{y} L40,{y+5}" fill="none" stroke="{color}"/>')
            tx = 2
        elif direction == 'output':
            start = 147 if inverted else (140 if kind in {None, 'DFF'} else 135)
            parts.append(f'<path d="M{start},{y} H175" fill="none" stroke="{color}" stroke-width="1.5"/>')
            if inverted:
                parts.append(f'<circle cx="141" cy="{y}" r="6" {style}/>')
            tx = 153
        else:
            continue
        bits = len(node.get('connections', {}).get(port, []))
        title = esc(f'{port}: {bits} bit(s), {direction}')
        parts.append(f'<text x="{tx}" y="{y-4}" fill="#b9cbe0" font-family="monospace" font-size="9"><title>{title}</title>{esc(port)}</text>')
    parts.append(f'<text x="87" y="107" text-anchor="middle" fill="#a3b9d0" font-family="monospace" font-size="10">{esc(node["label"][:27])}</text></g>')
    return ''.join(parts)
