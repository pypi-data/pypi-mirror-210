import os
import sys

import keyboard
import pyvirtualcam

import cv2
from time import sleep

from hackyargparser import add_sysargv
from pyvirtualcam import PixelFormat
from subprocess_multipipe.start_pipethread import stdincollection


camconfig = sys.modules[__name__]
camconfig.width = None
camconfig.height = None
camconfig.percentage_size = None
camconfig.interpolation = cv2.INTER_AREA
camconfig.camera = None
camconfig.fps = 29.97
camconfig.killkeys = "ctrl+alt+l"
camconfig.show = True


def on_off():
    camconfig.show = False


@add_sysargv
def kill_camera(killkeys: str = "ctrl+alt+l"):
    keyboard.add_hotkey(killkeys, on_off)


@add_sysargv
def get_cam_infos(
    fps: float | int | None = 29.97,
    camera: int | None = None,
    width: int | None = None,
    height: int | None = None,
    percentage_size: int | None = None,
    interpolation: int | None = cv2.INTER_AREA,
):
    camconfig.width = width
    camconfig.height = height
    camconfig.percentage_size = percentage_size
    camconfig.interpolation = interpolation
    camconfig.camera = camera
    camconfig.fps = fps
    print(camconfig)


get_cam_infos()
kill_camera()
if __name__ == "__main__":
    capture = cv2.VideoCapture(camconfig.camera)
    cam = pyvirtualcam.Camera(
        width=camconfig.width,
        height=camconfig.height,
        fps=camconfig.fps,
        fmt=PixelFormat.BGR,
    )
    while camconfig.show:
        if stdincollection.ran_out_of_input:
            break
        if not stdincollection.stdin_deque:
            sleep(0.01)
            continue
        try:
            cam.send(stdincollection.stdin_deque[-1].copy())

        except Exception:
            continue

    try:
        cam.close()

    except Exception:
        pass
    try:
        capture.release()

    except Exception:
        pass
    try:
        keyboard.remove_all_hotkeys()
    except Exception:
        pass
    try:
        sys.exit(0)
    finally:
        os._exit(0)
