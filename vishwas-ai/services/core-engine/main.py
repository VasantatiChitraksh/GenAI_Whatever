import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

# --- Initialize the Flask App ---
app = Flask(__name__)
CORS(app)

# --- Vertex AI Configuration ---
PROJECT_ID = "vishwas-ai-471305"
LOCATION = "us-central1"
# We must use a model that explicitly supports multimodal inputs
MODEL_NAME = "gemini-2.5-flash" 

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL_NAME)
# -------------------

def load_image_from_url(image_url: str) -> Image:
    """Loads an image from a URL and returns it as a Vertex AI Image object."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status() # Raise an exception for bad status codes
        return Image.from_bytes(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL: {e}")
        return None

@app.route("/verify", methods=["POST"])
def verify_content():
    """
    API endpoint to verify content, now supporting both text and an optional image_url.
    e.g., {"text": "...", "image_url": "http://..."}
    """
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Invalid request. JSON payload must include a 'text' key."}), 400

    text_to_analyze = data["text"]
    image_url = data.get("image_url") # Safely get the image_url if it exists

    # --- Multimodal Prompting ---
    prompt_parts = []

    # 1. Add the text part of the prompt
    prompt_text = f"""
    You are a misinformation analysis expert for an Indian audience.
    Analyze the provided content (text and potentially an image).
    Look for signs of misinformation, scams, or fake news. Specifically check if the image supports the text or if it is being used out of context.

    Provide your analysis as a valid JSON object with two keys:
    1. "verdict": (e.g., "Likely Misinformation", "Deceptive Content", "Seems Credible").
    2. "summary": A one-paragraph explanation of your reasoning in simple terms.

    Text to analyze: "{text_to_analyze}"
    """
    prompt_parts.append(Part.from_text(prompt_text))

    # 2. If an image URL is provided, load the image and add it to the prompt
    if image_url:
        print(f"Fetching image from: {image_url}")
        image = load_image_from_url(image_url)
        if image:
            prompt_parts.append(image)
        else:
            return jsonify({"error": f"Failed to load image from URL: {image_url}"}), 400

    try:
        print(f"Generating multimodal analysis for: '{text_to_analyze[:50]}...'")
        response = model.generate_content(prompt_parts)

        raw_output = response.candidates[0].content.parts[0].text
        print(f"Model generated response: {raw_output}")

        # --- Robust JSON parsing ---
        cleaned_output = raw_output.strip().lstrip("```json").rstrip("```")
        json_response = json.loads(cleaned_output)

        return jsonify(json_response), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Failed to process the request due to an internal error."}), 500

# --- Main execution for local testing ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))