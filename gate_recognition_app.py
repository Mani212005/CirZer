import streamlit as st
import cv2
import numpy as np
from PIL import Image
from utils.image_processing import recognize_gates
import os

def main():
    st.set_page_config(page_title="Gate Recognition with Roboflow", layout="wide")
    st.title("Gate Recognition with Roboflow")

    api_key = st.secrets["ROBOFLOW_API_KEY"]

    uploaded_file = st.file_uploader("Choose a circuit image...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Recognize Gates"):
            if not api_key:
                st.error("Roboflow API key not found in secrets.")
                return

            # Save the uploaded file temporarily to pass its path to the API
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Call the recognize_gates function
                results = recognize_gates("temp_image.jpg", api_key)
                
                # Process and display the results
                if results and 'predictions' in results:
                    st.success(f"Detected {len(results['predictions'])} components!")
                    
                    image_np = np.array(image)
                    img_with_boxes = image_np.copy()

                    # Ensure the image is in BGR format for OpenCV
                    if img_with_boxes.shape[2] == 4: # RGBA
                        img_with_boxes = cv2.cvtColor(img_with_boxes, cv2.COLOR_RGBA2BGR)
                    elif img_with_boxes.shape[2] == 3: # RGB
                        img_with_boxes = cv2.cvtColor(img_with_boxes, cv2.COLOR_RGB2BGR)

                    gate_counts = {}
                    for prediction in results['predictions']:
                        x = int(prediction['x'] - prediction['width'] / 2)
                        y = int(prediction['y'] - prediction['height'] / 2)
                        w = int(prediction['width'])
                        h = int(prediction['height'])
                        label = prediction['class']
                        
                        cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(img_with_boxes, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                        if label in gate_counts:
                            gate_counts[label] += 1
                        else:
                            gate_counts[label] = 1
                    
                    st.image(img_with_boxes, caption="Image with Detected Gates", use_column_width=True, channels="BGR")

                    st.subheader("Detected Gates Summary")
                    for gate_type, count in gate_counts.items():
                        st.write(f"- {gate_type}: {count}")
                else:
                    st.error("No components were detected or there was an error in the API response.")

            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Clean up the temporary file
                if os.path.exists("temp_image.jpg"):
                    os.remove("temp_image.jpg")

if __name__ == "__main__":
    main()
