import dxcam 
import time
import cv2
import numpy as np
from PIL import Image
import json
from pathlib import Path
import pandas as pd

def start_recording(camera,left=0,top=0,right=1920,bottom=1080):
    camera.start(region=(left,top,right,bottom), target_fps=60)
    print("Recording started...")


def stop_recording(camera):
    camera.stop()
    print("Recording stopped.")

def read_data(ROOT):
    resolution=int(input("Press 1 for 1080p and 2 for 1440p and 3 for 4K:"))
    game=input("Enter the game name:")
    session_name=input("Enter the session name:")
    meta={
        "game": game,
        "resolution": 1080 if resolution==1 else 1440 if resolution==2 else 2160,
    }
    path=Path(ROOT/f"data/{session_name}/meta.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,"w") as f:
        json.dump(meta,f,indent=4)
    return resolution, session_name


def main():
    ROOT=Path(__file__).resolve().parents[1]
    resolution, session_name=read_data(ROOT)

    camera=dxcam.create(
        backend="dxgi",
        processor_backend="cv2" 
    )
    if resolution==1:
        start_recording(camera,right=1920,bottom=1080)
    elif resolution==2:
        start_recording(camera,right=2560,bottom=1440)
    else:
        start_recording(camera,right=3840,bottom=2160)
    id=0
    df_image_timestamps=pd.DataFrame(columns=["frame_id","timestamp"])

    while True:
        frame,frame_timestamp=camera.get_latest_frame(with_timestamp=True)
        if frame is not None:
            img=Image.fromarray(frame)
            img_path=ROOT/f"data/{session_name}/frames/frame_{id}.png"
            img_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(img_path)
            df_image_timestamps.loc[id]=[id,frame_timestamp]
            df_image_timestamps.to_csv(ROOT/f"data/{session_name}/image_timestamps.csv",index=False)  
            id+=1
            time.sleep(0.5)
   
if __name__ == "__main__":
    main()
