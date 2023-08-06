# OpenCV Images (NumPy Arrays) to OBS Virtual Cam

### Tested against Windows 10 / Python 3.10 / Anaconda

### pip install cv2obs

## Example 

```python
from adbblitz import AdbShotTCP
from kthread_sleep import sleep
import numpy as np
from cv2obs.cv2obscam import start_cv2obs, get_index_of_working_cameras
	
	

cameras = get_index_of_working_cameras()
px = start_cv2obs(
    height=540,
    width=960,
    fps=29.97,
    camera=cameras[-1],
    killkeys="ctrl+alt+l",
)

with AdbShotTCP(
    device_serial="localhost:5555",
    adb_path=r"C:\ProgramData\chocolatey\lib\scrcpy\tools\scrcpy-win64-v2.0\adb.exe",
    ip="127.0.0.1",
    port=5555,
    max_frame_rate=60,
    max_video_width=960,
    scrcpy_server_version="2.0",
    forward_port=None,
    frame_buffer=24,
    byte_package_size=131072,
    sleep_after_exception=0.01,
    log_level="info",
    lock_video_orientation=0,
) as shosho:
    for bi in shosho:
        if bi.dtype == np.uint16:
            continue
        px.write_image(
            bi
        )  # Writes images to the camera, image will be resized automatically
        # (according to width/height in start_cv2obs)
        sleep(0.001)





get_index_of_working_cameras():
    """
    Get the indices of the working cameras.

    Returns:
        List[int]: A list containing the indices of the cameras that are working.

    Note:
        - This function internally calls the `list_ports` function to test the camera ports.
        - The `list_ports` function returns a tuple with available ports, working ports, and non-working ports.
        - Only the working ports are extracted and returned by this function.
    """
	
	
start_cv2obs(
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
	
```





