import networkx as nx

def get_gate_at_point(x, y, gates, tolerance=15):
    """Finds which gate contains the given (x, y) point, with a tolerance."""
    for gate_id, gate in gates.items():
        # Check if the point is within the bounding box of the gate, with tolerance
        if (
            (gate['left'] - tolerance <= x <= gate['left'] + gate['width'] + tolerance) and
            (gate['top'] - tolerance <= y <= gate['top'] + gate['height'] + tolerance)
        ):
            return gate_id
    return None

def build_graph(canvas_data):
    """Builds a directed graph from the canvas data."""
    G = nx.DiGraph()
    gates = {}
    wires = []

    print(f"DEBUG: build_graph received canvas_data: {canvas_data}")

    if not canvas_data or "objects" not in canvas_data:
        print("DEBUG: No canvas_data or objects found.")
        return G, gates, wires

    # First, populate the gates dictionary from image objects
    for obj in canvas_data["objects"]:
        if obj["type"] == "image":
            # Use a persistent ID if available, otherwise create one
            gate_id = obj.get("gate_id", f"gate_{len(gates)}")
            gates[gate_id] = {
                "type": obj.get("label", "unknown"),
                "left": obj["left"],
                "top": obj["top"],
                "width": obj["width"],
                "height": obj["height"],
                "inputs": [],
                "output": None, # Will be calculated during simulation
                "label": obj.get("label", "unknown")
            }
            G.add_node(gate_id, **gates[gate_id])
            print(f"DEBUG: Added gate node: {gate_id} with data {gates[gate_id]}")
        elif obj["type"] == "line":
            wires.append(obj)
            print(f"DEBUG: Found line object: {obj}")

    # Now, process the wires to connect the gates
    for wire in wires:
        # 'path' is a list of lists, e.g., [['M', x1, y1], ['L', x2, y2]]
        path = wire.get("path", [])
        if len(path) < 2:
            print(f"DEBUG: Skipping invalid line path: {path}")
            continue

        # Extract start and end points from the path
        start_x, start_y = path[0][1], path[0][2]
        end_x, end_y = path[-1][1], path[-1][2]

        print(f"DEBUG: Line from ({start_x}, {start_y}) to ({end_x}, {end_y})")

        from_gate_id = get_gate_at_point(start_x, start_y, gates)
        to_gate_id = get_gate_at_point(end_x, end_y, gates)

        print(f"DEBUG: Identified from_gate_id: {from_gate_id}, to_gate_id: {to_gate_id}")

        if from_gate_id and to_gate_id and from_gate_id != to_gate_id:
            G.add_edge(from_gate_id, to_gate_id)
            # Record the connection in the 'to' gate's input list
            if 'inputs' not in G.nodes[to_gate_id]:
                 G.nodes[to_gate_id]['inputs'] = []
            G.nodes[to_gate_id]['inputs'].append(from_gate_id)
            print(f"DEBUG: Added edge from {from_gate_id} to {to_gate_id}")
        else:
            print(f"DEBUG: Could not add edge for line. from_gate_id: {from_gate_id}, to_gate_id: {to_gate_id}")

    print(f"DEBUG: Final graph nodes: {G.nodes(data=True)}")
    print(f"DEBUG: Final graph edges: {G.edges()}")

    return G, gates, wires

def calculate_gate_output(gate_type, inputs):
    """Calculates the output of a single logic gate."""
    if not inputs:
        return 0

    if gate_type == "AND":
        return 1 if all(inputs) else 0
    elif gate_type == "OR":
        return 1 if any(inputs) else 0
    elif gate_type == "NOT":
        return 1 - inputs[0]
    elif gate_type == "XOR":
        # Assumes two inputs for XOR
        return inputs[0] ^ inputs[1] if len(inputs) == 2 else 0
    elif gate_type == "NAND":
        return 0 if all(inputs) else 1
    elif gate_type == "NOR":
        return 0 if any(inputs) else 1
    elif gate_type == "XNOR":
        return 1 if (inputs[0] == inputs[1]) else 0
    return 0

def simulate_circuit(graph, input_values):
    """Simulates the entire logic circuit represented by the graph."""
    for node in graph.nodes:
        if graph.in_degree(node) == 0: # It's a primary input
            graph.nodes[node]['output'] = input_values.get(node, 0) # Default to 0 if not specified

    # Process nodes in topological order to ensure inputs are ready
    for node in nx.topological_sort(graph):
        gate = graph.nodes[node]
        
        # Skip primary inputs, their values are already set
        if graph.in_degree(node) == 0:
            continue

        # Gather input values from predecessor nodes
        input_signals = [graph.nodes[pred]['output'] for pred in graph.predecessors(node)]
        
        # Ensure all inputs are available (not None)
        if any(val is None for val in input_signals):
            gate['output'] = None # Cannot compute if an input is missing
            continue

        # Perform logic based on gate type
        gate_type = gate.get("type")
        output = 0
        if gate_type == "AND":
            output = 1 if all(input_signals) else 0
        elif gate_type == "OR":
            output = 1 if any(input_signals) else 0
        elif gate_type == "NOT":
            output = 1 - input_signals[0] if input_signals else 0
        elif gate_type == "XOR":
            # Assumes two inputs for XOR
            if len(input_signals) == 2:
                output = input_signals[0] ^ input_signals[1]
        elif gate_type == "NAND":
            output = 0 if all(input_signals) else 1
        elif gate_type == "NOR":
            output = 0 if any(input_signals) else 1
        elif gate_type == "XNOR":
            output = 1 if (input_signals[0] == input_signals[1]) else 0
        
        gate['output'] = output

    return graph