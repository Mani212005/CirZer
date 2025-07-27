import numpy as np
import cv2
import os
from inference_sdk import InferenceHTTPClient

def recognize_gates(image_path, api_key):
    """
    Recognizes gates in an image using the Roboflow API.
    """
    CLIENT = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=api_key
    )

    result = CLIENT.infer(image_path, model_id="my-first-project-yz9wf/1")
    return result
