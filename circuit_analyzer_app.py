
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import base64
from io import BytesIO
from components.sidebar import sidebar as image_sidebar
from utils.image_processing import process_image
from utils.logic_simulation import generate_truth_table
from utils.logic_simulation import generate_logic_transformation_table
from utils.visual_circuit import (
    initialize_circuit,
    add_gate,
    add_input,
    add_wire,
    get_circuit_graph,
    draw_circuit,
    generate_boolean_from_graph,
    build_graph_from_image_components,
)

def image_to_base64(img):
    """Convert a PIL image to a base64 string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def interactive_editor_sidebar(graph):
    st.sidebar.header("Circuit Editor")

    if graph.nodes:
        st.sidebar.subheader("Edit Components")
        for node_id, data in list(graph.nodes(data=True)):
            st.sidebar.text(f"{data['label']} (ID: {node_id})")
            if st.sidebar.button(f"Delete {data['label']}", key=f"del_{node_id}"):
                graph.remove_node(node_id)
                st.rerun()

    st.sidebar.subheader("Add New Components")
    gate_type = st.sidebar.selectbox("Gate Type", ["AND", "OR", "NOT", "XOR"])
    if st.sidebar.button("Add Gate"):
        add_gate(gate_type)
        st.rerun()

    input_name = st.sidebar.text_input("Input Name", "C").strip().upper()
    if st.sidebar.button("Add Input") and input_name:
        add_input(input_name)
        st.rerun()

    nodes = {f"{data['label']} (ID: {node})": node for node, data in graph.nodes(data=True)}
    if len(nodes) > 1:
        st.sidebar.subheader("Add Wire")
        source_label = st.sidebar.selectbox("From", list(nodes.keys()), key="src_wire")
        target_label = st.sidebar.selectbox("To", list(nodes.keys()), key="tgt_wire")
        if st.sidebar.button("Add Wire"):
            source_node = nodes[source_label]
            target_node = nodes[target_label]
            if source_node != target_node:
                add_wire(source_node, target_node)
                st.rerun()
            else:
                st.sidebar.warning("Cannot connect a node to itself.")

def main():
    st.set_page_config(page_title="Circuit Analyzer", page_icon="⚡", layout="wide")
    st.title("Interactive Circuit Analyzer")

    initialize_circuit()

    st.header("1. Upload Circuit Image")
    uploaded_file, captured_image = image_sidebar()
    
    if 'image' not in st.session_state:
        st.session_state.image = None

    if uploaded_file:
        st.session_state.image = Image.open(uploaded_file)
    elif captured_image is not None:
        st.session_state.image = Image.fromarray(captured_image)

    if st.session_state.image:
        if st.button("Analyze and Create Interactive Overlay"):
            image_np = np.array(st.session_state.image)
            components, connections, _, _, _ = process_image(image_np)
            if components:
                st.success(f"Detected {len(components)} components!")
                build_graph_from_image_components(components, connections)
                st.session_state.mode = 'interactive'
                st.session_state.bg_image = image_to_base64(st.session_state.image)
                st.rerun()
            else:
                st.error("No components detected.")

    if st.session_state.get('mode') == 'interactive':
        st.header("2. Interactive Circuit Overlay")
        circuit_graph = get_circuit_graph()
        interactive_editor_sidebar(circuit_graph)

        bg_image = st.session_state.get('bg_image')
        draw_circuit(circuit_graph, bg_image_base64=bg_image, layout='none')

        if circuit_graph.nodes:
            st.header("3. Circuit Analysis")
            boolean_expression = generate_boolean_from_graph(circuit_graph)
            st.subheader("Boolean Expression")
            st.code(boolean_expression, language="plaintext")

            if boolean_expression and "No output" not in boolean_expression and "GATE" not in boolean_expression:
                try:
                    truth_table = generate_truth_table(boolean_expression)
                    st.subheader("Truth Table")
                    st.table(truth_table)

                    transformation_table = generate_logic_transformation_table(boolean_expression)
                    st.subheader("Logical Transformation Table")
                    st.table(transformation_table)
                except Exception as e:
                    st.warning(f"Could not generate tables. Error: {e}")
            else:
                st.info("Expression not ready for analysis.")
    elif st.session_state.image:
        st.image(st.session_state.image, caption="Your Circuit", use_column_width=True)

if __name__ == "__main__":
    main()
