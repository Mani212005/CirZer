
import streamlit as st
from utils.visual_circuit import (
    initialize_circuit,
    add_gate,
    add_input,
    add_wire,
    get_circuit_graph,
    draw_circuit,
    generate_boolean_from_graph,
)
from utils.logic_simulation import generate_truth_table
from utils.logic_simulation import generate_logic_transformation_table

def main_interactive():
    st.set_page_config(page_title="Interactive Circuit Builder", page_icon="️", layout="wide")
    st.title("Interactive Circuit Builder")

    # Initialize the circuit
    initialize_circuit()

    # --- Sidebar for Circuit Editing ---
    st.sidebar.header("Circuit Editor")

    # Add Gates
    gate_type = st.sidebar.selectbox("Add Gate", ["AND", "OR", "NOT", "XOR"])
    if st.sidebar.button("Add Gate"):
        add_gate(gate_type)

    # Add Inputs
    input_name = st.sidebar.text_input("Add Input Node (e.g., A, B)", "A").strip().upper()
    if st.sidebar.button("Add Input") and input_name:
        add_input(input_name)

    # Add Wires
    graph = get_circuit_graph()
    nodes = {f"{data['label']} (ID: {node})": node for node, data in graph.nodes(data=True)}
    
    if len(nodes) > 1:
        st.sidebar.subheader("Add Wire")
        source_node_label = st.sidebar.selectbox("From Node", list(nodes.keys()), key="source_node")
        target_node_label = st.sidebar.selectbox("To Node", list(nodes.keys()), key="target_node")

        if st.sidebar.button("Add Wire"):
            source_node = nodes[source_node_label]
            target_node = nodes[target_node_label]
            if source_node != target_node:
                add_wire(source_node, target_node)
            else:
                st.sidebar.warning("Cannot connect a node to itself.")

    # --- Main Panel for Visualization and Analysis ---
    st.header("Circuit Diagram")
    circuit_graph = get_circuit_graph()
    draw_circuit(circuit_graph)

    if circuit_graph.nodes:
        st.header("Circuit Analysis")
        
        # Generate and display Boolean expression
        boolean_expression = generate_boolean_from_graph(circuit_graph)
        st.subheader("Boolean Expression")
        st.code(boolean_expression, language="plaintext")

        # Generate and display truth table
        if boolean_expression and "No output" not in boolean_expression:
            try:
                truth_table = generate_truth_table(boolean_expression)
                st.subheader("Truth Table")
                st.table(truth_table)

                # Display logic transformations
                transformation_table = generate_logic_transformation_table(boolean_expression)
                st.subheader("Logical Transformation Table")
                st.table(transformation_table)
            except Exception as e:
                st.error(f"Could not generate tables: {e}")

if __name__ == "__main__":
    main_interactive()
