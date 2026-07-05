import dxcam 
import time
import cv2
import numpy as np
from PIL import Image
import json
from pathlib import Path
import pandas as pd
import questionary
from dualsense_logger import DualSenseLogger

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


def stop_recording(camera):
    camera.stop()

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
    ROOT=Path(__file__).resolve().parents[1]

    id_to_resolution={
        0: (1920,1080),
        1: (2560,1440),
        2: (3840,2160)
    }

    resolution, fps, session_name=read_data(ROOT)

    session_dir=ROOT/f"data/{session_name}"
    frame_dir=session_dir/f"frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    
    camera=dxcam.create(
        backend="dxgi",
        processor_backend="cv2" 
    )
    dualsense=DualSenseLogger()

    start_recording(
        camera,
        left=0,
        top=0,
        right=id_to_resolution[resolution["id"]][0],
        bottom=id_to_resolution[resolution["id"]][1],
        fps=int(fps)
    )
    dualsense.start()

    id=0
    image_row=[]
    dualsense_row=[]

    try:
        while True:
            frame,frame_timestamp=camera.get_latest_frame(with_timestamp=True)
            if frame is not None:
                now=time.time()

                img=Image.fromarray(frame)
                img_path=frame_dir/f"frame_{id}.png"
                img.save(img_path,quality=90,optimize=True)
                image_row.append({
                    "frame_id": id,
                    "timestamp": frame_timestamp,
                    "image_path": str(img_path)
                })

                ds=dualsense.get_data()
                dualsense_row.append({
                    "frame_id": id,
                    "dualsense_timestamp": ds["dualsense_timestamp"],
                    "acc_x": ds["acc_x"],
                    "acc_y": ds["acc_y"],
                    "acc_z": ds["acc_z"],
                    "gyro_x": ds["gyro_x"],
                    "gyro_y": ds["gyro_y"],
                    "gyro_z": ds["gyro_z"],
                    "acc_mag": ds["acc_mag"],
                    "gyro_mag": ds["gyro_mag"],
                    "vibration_mag": ds["vibration_mag"]
                })

                id+=1
                time.sleep(1/int(fps))

    except KeyboardInterrupt:
        stop_recording(camera)
        dualsense.stop()

        df_image_timestamps=pd.DataFrame(image_row)
        df_image_timestamps.to_csv(session_dir/f"image_timestamps.csv",index=False)  

        df_dualsense_data=pd.DataFrame(dualsense_row)
        df_dualsense_data.to_csv(session_dir/f"dualsense_data.csv",index=False)

    
if __name__ == "__main__":
    main()
