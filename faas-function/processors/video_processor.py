import moviepy.editor as mp
import os
import random
TEMP_DIR = "/tmp"
def extract_frame(input_path, second=None):
    base_name = os.path.basename(input_path).rsplit('.', 1)[0]
    output_path = os.path.join(TEMP_DIR, f"{base_name}_frame.jpg")
    with mp.VideoFileClip(input_path) as video:
        duration = video.duration
        target_time = second if second is not None else random.uniform(0, duration)
        if target_time > duration: target_time = duration
        video.save_frame(output_path, t=target_time)
    return output_path