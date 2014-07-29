"""Camera module.

This module handles various backends (different for every OS) for streaming the video from a (web)camera.
"""

import os

    
import Image
import cv

class Camera:
    """Implement basic camera capabilities
    
    This class has different implementations for different OS. On posix
    systems it calls to opencv, on Windows to VideoCapture."""
    # TODO what about win 64?
    # TODO why not openCV on win?
    # TODO document VideoCapture as a dependency
    def __init__(self, vid=0, res=None):
        self._cam = cv.CreateCameraCapture(vid)
        if res:
            cv.SetCaptureProperty(self._cam, cv.CV_CAP_PROP_FRAME_WIDTH, res[0])
            cv.SetCaptureProperty(self._cam, cv.CV_CAP_PROP_FRAME_HEIGHT,
                                  res[1])

    def get_image(self):
        """Get a new image from the camera."""
        for _ in range(5): #HACK TODO document this
            im = cv.QueryFrame(self._cam)
        return Image.fromstring("RGB", cv.GetSize(im), im.tostring(), "raw",
                                "BGR", 0, 1) 
    
    def __del__(self):
        del self._cam 
