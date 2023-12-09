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
blink_path = 'C:\\Users\\harry\\OneDrive\\Desktop\\Code\\blink.txt'
image_path = 'C:\\Users\\harry\\OneDrive\\Desktop\\Code\\control_human_openpose.png'
PORT = 5500

def get_encoded_image(output_folder):
    """Return the encoded content of the latest image."""
    with open(os.path.join(output_folder, 'latest-image.txt'), 'r') as file:
        latest_image_filename = file.read().strip()

    with open(os.path.join(output_folder, latest_image_filename), 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    return encoded_string   

def get_payload(prompt_value, blink_value, threshold, encoded_image=None):
    """Generate the payload based on the given conditions."""
    payload = {
        "prompt": prompt_value,
        "negative_prompt": "EASYNEGATIVEV2, text",
        "steps": 5,
        "checkpoint": "sd_xl_turbo_1.0_fp16.safetensors",

    }
    
    add_values = "\"prompt\":  \"dreamcore,blue_sky,scenery,blurry foreground, building\","
    string_dict = eval("{" + add_values + "}")
    merged_payload = {**payload, **string_dict}
    
    # if blink_value > threshold and encoded_image:
    #     payload["alwayson_scripts"] = {
    #         "controlnet": {
    #             "args": [
    #                 {
    #                     "input_image": encoded_image,
    #                     "module": "canny",
    #                     "model": "control_v11p_sd15_canny [d14c016b]", 
    #                 }
    #             ]
    #         }
    #     }
    #     print(f"CN added! (blink_value: {blink_value}, threshold: {threshold})")
    return payload

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

threading.Thread(target=serve, daemon=True).start()
time.sleep(1)  # Give the server a few seconds to initialize
webbrowser.open(f'http://localhost:{PORT}')

last_copied_prompt = ""

while True:
    with open(prompt_path, 'r') as file:
        prompt_value = file.read().strip()

    if prompt_value != last_copied_prompt:
        shutil.copy(prompt_path, output_folder)
        last_copied_prompt = prompt_value

    with open(blink_path, 'r') as blink_file:
        blink_value = float(blink_file.read().strip())  # Assuming the value in the file is a float.

    encoded_image = get_encoded_image(output_folder)
    payload = get_payload(prompt_value, blink_value, threshold=0.5, encoded_image=encoded_image)

    try:
        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
        response.raise_for_status()
        r = response.json()
    except requests.RequestException as e:
        print(f"Error: API request failed due to: {e}")
        time.sleep(1)
        continue

    for index, i in enumerate(r['images']):
        if index == 1:  # Skip saving the second image
            continue

        encoded_data = i.split(",", 1)[1] if "," in i else i
        image = Image.open(io.BytesIO(base64.b64decode(encoded_data)))

        png_payload = {
            "image": "data:image/png;base64," + i
        }

        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y%m%d%H%M%S%f')
        image_filename = f"output_{formatted_time}.png"
        
        image.save(os.path.join(output_folder, image_filename), pnginfo=pnginfo)
        print("Image saved as:", image_filename)

        with open(os.path.join(output_folder, 'latest-image.txt'), 'w') as file:
            file.write(image_filename)

        actual_add_value = "dreamcore, scenery, blurry foreground, building"
        combined_prompt = f"{prompt_value}\n{actual_add_value}"
        
        with open(os.path.join(output_folder, 'latest-prompt.txt'), 'w') as file:
            file.write(combined_prompt)

        with open(os.path.join(output_folder, 'latest-prompt.txt'), 'r') as file:
            content = file.read()

        print(content)

    delete_excess_images(output_folder, 200)
    time.sleep(1)
