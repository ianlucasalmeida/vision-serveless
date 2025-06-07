from PIL import Image
import os
TEMP_DIR = "/tmp"
def change_format(input_path, new_format):
    base_name = os.path.basename(input_path).rsplit('.', 1)[0]
    output_path = os.path.join(TEMP_DIR, f"{base_name}.{new_format.lower()}")
    with Image.open(input_path) as img:
        img.convert("RGB").save(output_path, format=new_format.upper())
    return output_path
def convert_to_bw(input_path):
    base_name = os.path.basename(input_path).rsplit('.', 1)[0]
    output_path = os.path.join(TEMP_DIR, f"{base_name}_bw.jpg")
    with Image.open(input_path) as img:
        img.convert("L").save(output_path)
    return output_path