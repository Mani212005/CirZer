import streamlit as st
from PIL import Image

def sidebar():
    st.sidebar.header("Logic Gates")

    gate_images = {
        "AND": "templates/and_gate.jpg",
        "OR": "templates/or_gate.jpg",
        "NOT": "templates/not_gate.jpg",
        "XOR": "templates/xor_gate.jpg",
    }

    for gate_name, image_path in gate_images.items():
        try:
            image = Image.open(image_path)
            st.sidebar.image(image, caption=f"{gate_name} Gate", width=100)
            if st.sidebar.button(f"Add {gate_name} Gate"):
                st.session_state.selected_gate = {
                    "type": gate_name,
                    "image": image_path
                }
        except FileNotFoundError:
            st.sidebar.error(f"Image not found for {gate_name} gate.")