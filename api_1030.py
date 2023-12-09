import json
import requests
import io
import base64
import os
import webbrowser
from PIL import Image, PngImagePlugin
from datetime import datetime
import time
from http.server import SimpleHTTPRequestHandler
import socketserver
import threading
import shutil

# Define the URL of the API server
url = "http://127.0.0.1:7860"
output_folder = 'C:\\Users\\harry\\OneDrive\\Desktop\\Code\\API_IMG\\'
prompt_path = 'C:\\Users\\harry\\OneDrive\\Desktop\\Code\\prompt.txt'
PORT = 5500

def get_encoded_image(output_folder):
    """Return the encoded content of the latest image."""
    # Read the latest image's filename
    with open(os.path.join(output_folder, 'latest-image.txt'), 'r') as file:
        latest_image_filename = file.read().strip()

    # Encode the image
    with open(os.path.join(output_folder, latest_image_filename), 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string   

def get_payload(prompt_value, sum_value, threshold, encoded_image=None):
    """Generate the payload based on the given conditions."""
    payload = {
        "prompt": prompt_value,
        "negative_prompt": "EasyNegativeV2",
        "steps": 5,
        "checkpoint": "revAnimated_v122.safetensors",
    }
    
    return payload

# Prepare the control image
with open("C:\\Users\\harry\\OneDrive\\Desktop\\Code\\control_human_openpose.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# Get the payload
# You would have to define values for prompt_value, sum_value, and threshold before calling this function
# For now, I am using placeholders
prompt_value = "YOUR_PROMPT_VALUE"
sum_value = 0  # Just a placeholder
threshold = 100  # Just a placeholder
payload_data = get_payload(prompt_value, sum_value, threshold, encoded_image)

payload = json.dumps(payload_data)

headers = {
    'Content-Type': 'application/json'
}

# Send the API request
response = requests.request("POST", url, headers=headers, data=payload)

# Decode the response and save as an image
if response.status_code == 200:
    response_data = response.json()
    image_data_str = response_data['images'][0]

    if "," in image_data_str:
        generated_image_data = base64.b64decode(image_data_str.split(",", 1)[1])
    else:
        generated_image_data = base64.b64decode(image_data_str)

    with open("C:\\Users\\harry\\OneDrive\\Desktop\\Code\\generated_image.png", "wb") as out_file:
        out_file.write(generated_image_data)
else:
    print(f"Error: {response.status_code} - {response.text}")
        
def delete_excess_images(folder, max_files):
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.endswith('.png')]
    if len(files) > max_files:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
        for i in range(len(files) - max_files):
            os.remove(os.path.join(folder, files[i]))

def serve():
    os.chdir(output_folder)
    Handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# Start the server in a separate thread
threading.Thread(target=serve, daemon=True).start()
time.sleep(2)  # Give the server a few seconds to initialize
webbrowser.open(f'http://localhost:{PORT}')

last_copied_prompt = ""

while True:
    with open(prompt_path, 'r') as file:
        prompt_value = file.read().strip()

    if prompt_value != last_copied_prompt:
        shutil.copy(prompt_path, output_folder)
        last_copied_prompt = prompt_value

    print("Prompt content:", prompt_value)

    # Logic to get the sum_value from the EEG stream should be inserted here
    sum_value = 2  # This is a placeholder. Replace with actual logic.

    encoded_image = get_encoded_image(output_folder)
    payload = get_payload(prompt_value, sum_value, threshold=2.5, encoded_image=encoded_image)
    
    try:
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        response.raise_for_status()
        r = response.json()
    except requests.RequestException as e:
        print(f"Error: API request failed due to: {e}")
        continue

    for index, i in enumerate(r['images']):
        encoded_data = i.split(",", 1)[1] if "," in i else i
        image = Image.open(io.BytesIO(base64.b64decode(encoded_data)))

        png_payload = {
            "image": "data:image/png;base64," + i
        }

        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        # Generate a filename with the current timestamp
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y%m%d%H%M%S%f')
        image_filename = f"output_{formatted_time}.png"
        
        image.save(os.path.join(output_folder, image_filename), pnginfo=pnginfo)
        print("Image saved as:", image_filename)

        # Save the name of the latest image to a file
        with open(os.path.join(output_folder, 'latest-image.txt'), 'w') as file:
            file.write(image_filename)

        # Save the latest prompt to a file
        with open(os.path.join(output_folder, 'latest-prompt.txt'), 'w') as file:
            file.write(prompt_value)

    delete_excess_images(output_folder, 300)
    time.sleep(2)
