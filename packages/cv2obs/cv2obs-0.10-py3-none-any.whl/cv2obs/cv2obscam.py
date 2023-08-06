import os.path
from functools import partial
import cv2
from a_cv_imwrite_imread_plus import open_image_in_cv
import numpy as np
from subprocess_multipipe.run_multipipe_subproc import start_subprocess
from a_cv2_easy_resize import add_easy_resize_to_cv2

add_easy_resize_to_cv2()
from varpickler import encode_var

startp = os.path.normpath(os.path.join(os.path.dirname(__file__), "cv2obs.py"))


def list_ports():
    # https://stackoverflow.com/a/62639343/15096247
    """
    Test the ports and returns a tuple with the available ports and the ones that are working.
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []
    while (
        len(non_working_ports) < 6
    ):  # if there are more than 5 non working ports stop the testing.
        camera = cv2.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
            print("Port %s is not working." % dev_port)
        else:
            is_reading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if is_reading:
                print(
                    "Port %s is working and reads images (%s x %s)" % (dev_port, h, w)
                )
                working_ports.append(dev_port)
            else:
                print(
                    "Port %s for camera ( %s x %s) is present but does not read."
                    % (dev_port, h, w)
                )
                available_ports.append(dev_port)
        dev_port += 1
    return available_ports, working_ports, non_working_ports


def get_index_of_working_cameras():
    """
    Get the indices of the working cameras.

    Returns:
        List[int]: A list containing the indices of the cameras that are working.

    Note:
        - This function internally calls the `list_ports` function to test the camera ports.
        - The `list_ports` function returns a tuple with available ports, working ports, and non-working ports.
        - Only the working ports are extracted and returned by this function.
    """
    _, working, _ = list_ports()
    return working


def _write_image(px, height, width, interpolation, pic):
    pic1resize = cv2.easy_resize_image(
        img=open_image_in_cv(pic, channels_in_output=3),
        width=width,
        height=height,
        interpolation=interpolation,
    )
    px.write_function(pic1resize)


def start_cv2obs(
    height: int = 540,
    width: int = 960,
    fps: int | float = 29.97,
    camera: int = 2,
    killkeys: str = "ctrl+alt+l",
):
    """
    Start the cv2obs subprocess for capturing and processing camera images.

    Args:
        height (int): The desired height of the captured images. Defaults to 540.
        width (int): The desired width of the captured images. Defaults to 960.
        fps (int|float): The frames per second for capturing images. Defaults to 29.97.
        camera (int): The index of the camera to use. Defaults to 2.
        killkeys (str): The key combination to stop the cv2obs subprocess. Defaults to "ctrl+alt+l".


    Note:
        - The function internally creates a numpy array of shape (height, width, 3) with white pixels (255, 255, 255).
        - The numpy array is then encoded using `encode_var` function from the `varpickler` module.
        - The encoded array size is used for configuring the `bytesize` parameter of the `start_subprocess` function.
        - The cv2obs subprocess is started using the `start_subprocess` function with appropriate parameters.
        - The `px.write_image` attribute of the subprocess is set to a partial function `_write_image` for writing images.
    """
    rgbValues0 = np.zeros((height, width, 3), dtype=np.uint8)
    rgbValues0[:] = [255, 255, 255]
    numpybytes = encode_var(rgbValues0)
    imagesize = len(numpybytes)

    px = start_subprocess(
        pyfile=startp,
        bytesize=imagesize,
        pipename=None,
        block_or_unblock="unblock",
        deque_size=24,
        pickle_or_dill="dill",
        other_args=(
            "--fps",
            str(fps),
            "--camera",
            str(camera),
            "--width",
            str(width),
            "--height",
            str(height),
            "--killkeys",
            str(killkeys),
        ),
    )
    px.write_image = partial(_write_image, px, height, width, cv2.INTER_AREA)
    return px
