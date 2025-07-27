import base64
from PIL import Image
import io
import os

_this_file = os.path.abspath(__file__)
_this_dir = os.path.dirname(_this_file)
_project_root = os.path.dirname(_this_dir)

def get_image_b64(image_path):
    """Converts an image file to a base64 string for embedding in the canvas."""
    try:
        with open(image_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read()).decode('utf-8')
            print(f"DEBUG: Successfully encoded {image_path}. Length of base64 string: {len(b64_string)}")
            return "data:image/png;base64," + b64_string
    except Exception as e:
        print(f"DEBUG: Error encoding image {image_path}: {e}")
        return None

def predictions_to_canvas_objects(predictions):
    """
    Converts Roboflow prediction JSON to a list of objects for Streamlit Drawable Canvas.
    """
    objects = []
    gate_image_map = {
        "and": os.path.join(_project_root, "templates", "and_gate.jpg"),
        "or": os.path.join(_project_root, "templates", "or_gate.jpg"),
        "not": os.path.join(_project_root, "templates", "not_gate.jpg"),
        "xor": os.path.join(_project_root, "templates", "xor_gate.jpg"),
        "nand": os.path.join(_project_root, "templates", "nand_gate.jpg"), # Assuming you'll add these templates
        "nor": os.path.join(_project_root, "templates", "nor_gate.jpg"),   # Assuming you'll add these templates
        "xnor": os.path.join(_project_root, "templates", "xnor_gate.jpg"), # Assuming you'll add these templates
    }

    for pred in predictions:
        gate_type = pred['class'].lower() # Normalize to lowercase
        image_path = gate_image_map.get(gate_type)

        if not image_path:
            print(f"DEBUG: Warning: No image mapping for gate type: {gate_type}")
            continue

        print(f"DEBUG: Attempting to load image from: {image_path}")

        # Center coordinates from Roboflow
        center_x = pred['x']
        center_y = pred['y']
        width = pred['width']
        height = pred['height']

        # Convert center coords to top-left coords for canvas
        left = center_x - (width / 2)
        top = center_y - (height / 2)

        print(f"DEBUG: Gate {gate_type} calculated position: left={left}, top={top}, width={width}, height={height}")

        # Create a unique ID for each gate for future reference
        gate_id = f"{gate_type}_{len(objects)}"

        objects.append({
            "type": "image",
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "src": get_image_b64(image_path),
            "label": gate_type, # Custom attribute
            "gate_id": gate_id, # Custom attribute
            "lockMovementX": False, # Allow movement for user interaction
            "lockMovementY": False,
        })
    return objects