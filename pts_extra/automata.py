import os
import requests

from graphviz import Digraph
from pts_extra.lr1 import LR1Builder


def construir_automata_lr1(builder: LR1Builder):
    """
    Construye y devuelve un grafo Graphviz que representa el autómata LR(1)
    a partir de los estados y transiciones del builder.
    """
    dot = Digraph(comment="Autómata LR(1)")

    # 🔹 Forzar tamaño grande y escala más legible
    dot.attr(rankdir='LR')
    dot.attr(size='100,40!', dpi='300')  # aumenta el área de dibujo
    dot.attr(nodesep='0.8', ranksep='1.0')  # separa más los nodos
    dot.attr('node', fontname='Consolas', fontsize='12')

    # 🔹 Crear nodos: cada estado I0, I1, ...
    for i, items in enumerate(builder.states):
        label = f"I{i}\\n"  # encabezado del estado
        label += "\\n".join([str(it) for it in sorted(items, key=lambda x: (x.head, x.body, x.dot, x.lookahead))])
        shape = "doublecircle" if any(
            it.head == builder.aug.start_symbol and it.lookahead == builder.grammar.END_MARKER and it.at_end()
            for it in items
        ) else "circle"
        dot.node(f"I{i}", label=label, shape=shape)

    # 🔹 Crear transiciones: ACTION y GOTO combinadas
    for (i, symbol), j in builder.transitions.items():
        dot.edge(f"I{i}", f"I{j}", label=symbol)

    # 🔹 Flecha de inicio
    dot.attr('node', shape='none')
    dot.edge('', 'I0', label='inicio')

    return dot



def render_automata_svg_interactivo(builder):
    """
    Genera y muestra el autómata LR(1) en formato SVG interactivo
    sin requerir Graphviz instalado (usa kroki.io para renderizado).
    """
    dot = construir_automata_lr1(builder)
    dot_source = dot.source.encode("utf-8")

    # 🔹 Llamada al servicio remoto de Graphviz (kroki.io)
    response = requests.post("https://kroki.io/graphviz/svg", data=dot_source, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Error al generar SVG remoto: {response.status_code}")

    svg = response.text  # SVG devuelto por el servicio

    html = f"""
    <div id="graph-container"
         style="
            width: 100%;
            height: 90vh;
            overflow: hidden;
            background-color: #111;
            display: flex;
            align-items: center;
            justify-content: center;
         ">
        <div id="zoom-wrapper" style="width:100%; height:100%; transform-origin:center center;">
            {svg}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <script>
        const svgElement = document.querySelector('#graph-container svg');
        if (svgElement) {{
            // Limpia restricciones de tamaño del SVG
            svgElement.removeAttribute('width');
            svgElement.removeAttribute('height');
            svgElement.style.width = '100%';
            svgElement.style.height = '100%';
            svgElement.style.maxWidth = '100%';
            svgElement.style.maxHeight = '100%';
            svgElement.style.display = 'block';
            svgElement.style.margin = 'auto';

            // Inicializa pan y zoom
            const panZoom = svgPanZoom(svgElement, {{
                zoomEnabled: true,
                controlIconsEnabled: false,
                fit: true,          // 🔹 Ajusta automáticamente al contenedor
                center: true,
                contain: true,      // 🔹 Fuerza a ocupar todo el espacio visible
                minZoom: 0.2,
                maxZoom: 10,
                zoomScaleSensitivity: 0.3
            }});

            // 🔹 Ajusta tamaño inicial para que ocupe bien el área
            function ajustarVista() {{
                panZoom.resize();
                panZoom.fit();
                panZoom.center();
                panZoom.zoomBy(1.8); // valor cómodo de zoom inicial
            }}

            ajustarVista();
            window.addEventListener('resize', ajustarVista);
        }}
    </script>
    """

    return html
