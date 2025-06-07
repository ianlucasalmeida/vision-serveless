import moviepy.editor as mp
import os
import random
TEMP_DIR = "/tmp"
def create_slideshow(image_paths, interval, is_random, output_name="slideshow"):
    output_path = os.path.join(TEMP_DIR, f"{output_name}.mp4")
    if is_random:
        random.shuffle(image_paths)
    clips = [mp.ImageClip(path).set_duration(interval) for path in image_paths]
    video_clip = mp.concatenate_videoclips(clips, method="compose")
    video_clip.write_videofile(output_path, fps=24)
    return output_path