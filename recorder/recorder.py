import dxcam 
import time
import cv2
import numpy as np
from PIL import Image
import json
from pathlib import Path
import pandas as pd
import questionary

def choose_resolution():
    resolution_map={
        "1080p":0,
        "1440p":1,
        "4K":2,
    }
    selected=questionary.select(
        "Choose resolution:",
        choices=list(resolution_map.keys())
    ).ask()
    return {
        "name": selected,
        "id": resolution_map[selected]
    }

def start_recording(camera,left=0,top=0,right=1920,bottom=1080,fps=60):
    camera.start(region=(left,top,right,bottom), target_fps=fps)
    print("Recording started...")


def stop_recording(camera):
    camera.stop()
    print("Recording stopped.")

def read_data(ROOT):
    resolution=choose_resolution()
    fps=questionary.select(
        "Choose FPS:",
        choices=["30","60","120"]
    ).ask()
    game=input("Enter the game name:")
    session_name=input("Enter the session name:")
    meta={
        "game": game,
        "resolution": resolution["name"],
        "fps": (int(fps)),
        "session_name": session_name
    }
    path=Path(ROOT/f"data/{session_name}/meta.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path,"w") as f:
        json.dump(meta,f,indent=4)
    return resolution, fps, session_name


def main():
    id_to_resolution={
        0: (1920,1080),
        1: (2560,1440),
        2: (3840,2160)
    }
    ROOT=Path(__file__).resolve().parents[1]
    resolution, fps, session_name=read_data(ROOT)

    camera=dxcam.create(
        backend="dxgi",
        processor_backend="cv2" 
    )
    start_recording(camera,left=0,top=0,right=id_to_resolution[resolution["id"]][0],bottom=id_to_resolution[resolution["id"]][1],fps=int(fps))
    df_image_timestamps=pd.DataFrame(columns=["frame_id","timestamp"])
    id=0

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
