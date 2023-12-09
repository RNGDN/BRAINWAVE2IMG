def get_payload(prompt_value, sum_value, threshold=2.5, encoded_image=None):
    payload = {
        "prompt": prompt_value,
        "steps": 5,
        "checkpoint": "revAnimated_v122.safetensors",
    }

    if sum_value > threshold:
        if encoded_image:
            controlnet_args = {
                "input_image": encoded_image,
                "module": "canny",
                "model": "control_v11p_sd15_canny [d14c016b]",
            }
            payload["alwayson_scripts"] = {
                "controlnet": {
                    "args": [controlnet_args]
                }
            }

    return payload
