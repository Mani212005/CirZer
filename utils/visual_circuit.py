import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Use session state to store the graph
if 'circuit_graph' not in st.session_state:
    st.session_state.circuit_graph = nx.DiGraph()
    st.session_state.node_counter = 0

def initialize_circuit():
    st.session_state.circuit_graph = nx.DiGraph()
    st.session_state.node_counter = 0

def get_circuit_graph():
    return st.session_state.circuit_graph

def add_gate(gate_type):
    st.session_state.node_counter += 1
    node_id = f"gate_{st.session_state.node_counter}"
    st.session_state.circuit_graph.add_node(node_id, label=gate_type, type='gate')
    st.success(f"Added {gate_type} gate with ID: {node_id}")

def add_input(input_name):
    st.session_state.node_counter += 1
    node_id = f"input_{st.session_state.node_counter}"
    st.session_state.circuit_graph.add_node(node_id, label=input_name, type='input')
    st.success(f"Added input {input_name} with ID: {node_id}")

def add_wire(source_node_id, target_node_id):
    if source_node_id in st.session_state.circuit_graph and target_node_id in st.session_state.circuit_graph:
        st.session_state.circuit_graph.add_edge(source_node_id, target_node_id)
        st.success(f"Added wire from {st.session_state.circuit_graph.nodes[source_node_id]['label']} to {st.session_state.circuit_graph.nodes[target_node_id]['label']}")
    else:
        st.error("Source or target node not found.")

def draw_circuit(graph, bg_image_base64=None, layout='dot'):
    """
    Draws the circuit graph using matplotlib and displays it in Streamlit.
    Can overlay on a background image.
    """
    if not graph.nodes:
        st.warning("Circuit is empty. Add some components!")
        return

    fig, ax = plt.subplots(figsize=(10, 7))

    if bg_image_base64:
        try:
            # Decode base64 image
            img_data = base64.b64decode(bg_image_base64)
            img = plt.imread(BytesIO(img_data), format='PNG')
            ax.imshow(img, extent=[0, 1, 0, 1], aspect='auto')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        except Exception as e:
            st.error(f"Error loading background image: {e}")
            bg_image_base64 = None # Don't use background if error

    pos = nx.spring_layout(graph) # You can choose different layouts

    # Draw nodes
    node_colors = ['skyblue' if graph.nodes[node].get('type') == 'gate' else 'lightgreen' for node in graph.nodes()]
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=3000, ax=ax)

    # Draw edges
    nx.draw_networkx_edges(graph, pos, ax=ax, arrowstyle='-|>', arrowsize=20)

    # Draw labels
    node_labels = {node: graph.nodes[node]['label'] for node in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=10, font_weight='bold', ax=ax)

    st.pyplot(fig)

def generate_boolean_from_graph(graph):
    """
    Generates a boolean expression from the circuit graph.
    This is a simplified placeholder. A real implementation would traverse the graph
    from inputs to outputs, applying gate logic.
    """
    if not graph.nodes:
        return ""

    # Find output nodes (nodes with no outgoing edges)
    output_nodes = [node for node in graph.nodes() if graph.out_degree(node) == 0]

    if not output_nodes:
        return "No output node found. Please connect components to an output."

    # For simplicity, let's assume a single output for now and just return its label
    # In a real scenario, you'd build the expression by traversing backwards from output
    # and combining expressions based on gate types.
    
    # This is a very basic placeholder. A proper implementation would involve:
    # 1. Topological sort to process nodes in order.
    # 2. Recursively building expressions from inputs to outputs.
    # 3. Handling multiple inputs to gates and correct operator precedence.

    # For now, just list all input and gate labels as a dummy expression
    expression_parts = []
    for node in nx.topological_sort(graph):
        node_type = graph.nodes[node].get('type')
        label = graph.nodes[node]['label']
        if node_type == 'input':
            expression_parts.append(label)
        elif node_type == 'gate':
            # This is where you'd combine inputs to the gate
            # For now, just add the gate label
            expression_parts.append(f"GATE_{label}")

    if expression_parts:
        return " & ".join(expression_parts) # Dummy ANDing of all parts
    else:
        return "No logical expression can be formed."

def build_graph_from_image_components(components, connections):
    """
    Builds the networkx graph from identified image components and connections.
    This is a placeholder and needs sophisticated logic to correctly map
    image-based components and connections to a logical circuit graph.
    """
    initialize_circuit() # Clear existing circuit

    # Add components as nodes
    for i, comp in enumerate(components):
        node_id = f"comp_{i}"
        st.session_state.circuit_graph.add_node(node_id, label=comp['label'], type=comp['type'], box=comp['box'])

    # Add connections as edges
    # This part is highly dependent on how `process_image` identifies connections.
    # For a simple placeholder, we'll just add some dummy connections.
    # In a real scenario, you'd analyze spatial relationships and wire paths.
    if len(components) > 1:
        for i in range(len(components) - 1):
            source_id = f"comp_{i}"
            target_id = f"comp_{i+1}"
            if source_id in st.session_state.circuit_graph and target_id in st.session_state.circuit_graph:
                st.session_state.circuit_graph.add_edge(source_id, target_id)

    st.success("Circuit graph built from image components (placeholder logic).")
