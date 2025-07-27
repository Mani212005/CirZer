import streamlit as st
from PIL import Image
import pandas as pd
from utils.image_processing import recognize_gates
from utils.canvas_utils import predictions_to_canvas_objects, get_image_b64
from utils.logic_simulation import build_graph, simulate_circuit, calculate_gate_output
from streamlit_drawable_canvas import st_canvas
import os
import networkx as nx
from io import BytesIO
import base64

# --- MONKEY-PATCH FOR STREAMLIT COMPATIBILITY ---
def image_to_url(image, width, clamp, channel, output_format, image_id):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

st.elements.image.image_to_url = image_to_url
# --- END OF PATCH ---

st.set_page_config(page_title="Interactive Circuit Builder", layout="wide")
st.title("Interactive Circuit Builder")

# --- SESSION STATE INITIALIZATION ---
if 'roboflow_predictions' not in st.session_state:
    st.session_state.roboflow_predictions = []
if 'canvas_objects' not in st.session_state:
    st.session_state.canvas_objects = []
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'circuit_graph' not in st.session_state:
    st.session_state.circuit_graph = None
if 'selected_gate_to_add' not in st.session_state:
    st.session_state.selected_gate_to_add = None

# --- SIDEBAR FOR IMAGE UPLOAD AND API KEY ---
st.sidebar.header("Configuration")
api_key = st.secrets.get("ROBOFLOW_API_KEY", "") # Get API key from secrets

uploaded_file = st.sidebar.file_uploader("Upload Circuit Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.session_state.uploaded_image = Image.open(uploaded_file)
    # Reset predictions and canvas when a new image is uploaded
    st.session_state.roboflow_predictions = []
    st.session_state.canvas_objects = []

if st.sidebar.button("1. Detect Gates from Image"):
    if st.session_state.uploaded_image and api_key:
        with st.spinner('Detecting gates...'):
            temp_path = "temp_image.jpg"
            st.session_state.uploaded_image.save(temp_path)
            try:
                results = recognize_gates(temp_path, api_key)
                st.session_state.roboflow_predictions = results.get('predictions', [])
                print(f"DEBUG: Roboflow predictions received: {st.session_state.roboflow_predictions}")
                # Generate canvas objects once and store them in session state
                st.session_state.canvas_objects.extend(predictions_to_canvas_objects(st.session_state.roboflow_predictions))
                st.sidebar.success(f"Detected {len(st.session_state.roboflow_predictions)} gates!")
            except Exception as e:
                st.sidebar.error(f"Error during detection: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    else:
        st.sidebar.warning("Please upload an image and ensure API key is set in secrets.")

# --- SIDEBAR FOR GATE PALETTE ---
st.sidebar.header("Add Gates Manually")
gate_types = ["AND", "OR", "NOT", "XOR", "NAND", "NOR", "XNOR"]

for gate_type in gate_types:
    if st.sidebar.button(f"Add {gate_type} Gate"):
        st.session_state.selected_gate_to_add = gate_type
        st.sidebar.info(f"Click on the canvas to place the {gate_type} gate.")

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["Circuit Builder", "Simulation", "Export"])

with tab1:
    st.header("Design Your Circuit")
    st.write("Use the sidebar to upload an image for gate detection or add gates manually. Draw lines to connect them.")

    canvas_height = 600
    canvas_width = 800
    if st.session_state.uploaded_image:
        canvas_height = st.session_state.uploaded_image.height
        canvas_width = st.session_state.uploaded_image.width

    # Handle placing a new gate
    if st.session_state.selected_gate_to_add:
        st.write(f"Placing {st.session_state.selected_gate_to_add} gate. Click on the canvas.")
        # This part needs a custom component or more advanced handling to get click coordinates
        # For now, we'll just add it at a default position.
        if st.button("Place Gate at (100, 100)"):
            gate_type = st.session_state.selected_gate_to_add
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", f"{gate_type.lower()}_gate.jpg")
            new_gate_obj = {
                "type": "image",
                "left": 100,
                "top": 100,
                "width": 50, # Default size, adjust as needed
                "height": 50, # Default size, adjust as needed
                "src": get_image_b64(image_path),
                "label": gate_type,
                "gate_id": f"{gate_type}_{len(st.session_state.canvas_objects)}",
                "lockMovementX": False,
                "lockMovementY": False,
            }
            st.session_state.canvas_objects.append(new_gate_obj)
            st.session_state.selected_gate_to_add = None # Reset
            st.experimental_rerun()

    # --- HARDCODED TEST OBJECT ---
    # This is for debugging purposes to see if any image renders
    test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "and_gate.jpg")
    test_b64_string = get_image_b64(test_image_path)
    if test_b64_string:
        test_object = {
            "type": "image",
            "left": 50,
            "top": 50,
            "width": 70,
            "height": 70,
            "src": test_b64_string,
            "label": "TEST_AND",
            "gate_id": "test_and_0",
            "lockMovementX": False,
            "lockMovementY": False,
        }
        # Add the test object if it's not already there
        if not any(obj.get("gate_id") == "test_and_0" for obj in st.session_state.canvas_objects):
            st.session_state.canvas_objects.append(test_object)
            print("DEBUG: Added hardcoded test AND gate to canvas_objects.")

    print(f"DEBUG: canvas_objects before st_canvas: {st.session_state.canvas_objects}")

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#FF0000",
        background_image=st.session_state.uploaded_image,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="transform", # Changed to transform to allow moving objects
        initial_drawing={"objects": st.session_state.canvas_objects},
        key="circuit_builder_canvas",
    )

    if canvas_result and canvas_result.json_data:
        # Update canvas objects with user's drawings (lines) and movements
        st.session_state.canvas_objects = canvas_result.json_data.get("objects", [])
        st.session_state.circuit_graph, _, _ = build_graph(canvas_result.json_data)

    if st.button("Clear All"):
        st.session_state.roboflow_predictions = []
        st.session_state.canvas_objects = []
        st.session_state.uploaded_image = None
        st.session_state.circuit_graph = None
        st.experimental_rerun()

    if st.button("Clear Connections Only"):
        st.session_state.canvas_objects = [obj for obj in st.session_state.canvas_objects if obj.get('type') == 'image']
        st.experimental_rerun()

with tab2:
    st.header("Circuit Simulation")

    if not st.session_state.circuit_graph or not st.session_state.canvas_objects:
        st.info("Build and wire your circuit in the 'Circuit Builder' tab first.")
    else:
        graph = st.session_state.circuit_graph
        input_nodes = [node for node, in_degree in graph.in_degree() if in_degree == 0]
        
        st.write("### Set Primary Input Values")
        input_values = {}
        for node in input_nodes:
            input_values[node] = st.slider(f"Input for {graph.nodes[node]['label']}", 0, 1, 0, key=f"input_{node}")

        if st.button("Run Full Simulation"):
            with st.spinner("Simulating..."):
                simulated_graph = simulate_circuit(graph.copy(), input_values)
                st.session_state.simulated_graph = simulated_graph
                st.success("Simulation complete!")

        if 'simulated_graph' in st.session_state:
            st.write("### Simulation Results")
            results_data = []
            for node, data in st.session_state.simulated_graph.nodes(data=True):
                results_data.append({
                    "Gate": data.get('label', node),
                    "Type": data.get('type', 'N/A'),
                    "Output": data.get('output', 'Not computed')
                })
            st.dataframe(pd.DataFrame(results_data))

with tab3:
    st.header("Export Options")
    st.write("Export functionality will be implemented here.")

    # Placeholder data for demonstration
    truth_table_data = {
        "Input A": [0, 0, 1, 1],
        "Input B": [0, 1, 0, 1],
        "Output": [0, 0, 0, 1]  # Example for AND gate
    }
    truth_table_df = pd.DataFrame(truth_table_data)

    st.write("### Truth Table")
    st.dataframe(truth_table_df)

    boolean_expression = "Output = A AND B"
    st.write("### Boolean Expression")
    st.code(boolean_expression, language="plaintext")

    st.download_button(
        label="Download Truth Table (CSV)",
        data=truth_table_df.to_csv(index=False),
        file_name="truth_table.csv",
        mime="text/csv",
    )

    st.download_button(
        label="Download Boolean Expression (.txt)",
        data=boolean_expression,
        file_name="boolean_expression.txt",
        mime="text/plain",
    )
