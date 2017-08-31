#!/usr/bin/env python
import os
import cv2
import numpy as np
import platform
import requests


LOG_FILE_DIRECTORY = "log/log_file.log"
# Required image size of Facenet, resize before sending to Facenet as network optimization.
image_size = 160

# Check OS environment variable PK_ENABLE_WS to run with Flask web service.
pk_enable_ws = False
if os.getenv("PK_ENABLE_WS"):
    pk_enable_ws = True


def setup():
    # If web services not enabled, then import/run required facenet services locally.
    if not pk_enable_ws:
        global pfs
        import pk_facenet_service as pfs
        pfs.setup_face_parser()
        pfs.setup_facenet()
        pfs.setup_reference_table()

def facenet_classify_image_bbs(cv2_image):
    facenet_result = None
    cv2_image_resized = cv2.resize(cv2_image, (image_size, image_size))
    cv2_image_string = cv2.imencode('.png', cv2_image_resized)[1].tostring()
    response = requests.post('http://localhost:5000/get-image-facenet', files={'image_data': cv2_image_string})
    facenet_result = np.asarray(response.json())
    return facenet_result

def facenet_classify_image_data(cv2_image):
    facenet_result = None
    if pk_enable_ws:
        cv2_image_string = cv2.imencode('.png', cv2_image)[1].tostring()
        response = requests.post('http://localhost:5000/get-image-with-bbs', files={'image_data': cv2_image_string})
        file_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
        facenet_result = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    else:
        facenet_result = pfs.get_image_with_bbs(cv2_image)
    return facenet_result

def facenet_get_classified_image(cv2_image):
    facenet_result = None
    #cv2_image_resized = cv2_image
    #cv2_image_resized = cv2.resize(cv2_image, (image_size, image_size))
    cv2_image_resized = cv2.resize(cv2_image, (640, 360))
    #cv2_image_resized = cv2.resize(cv2_image, (320, 180))
    #cv2_image_resized = cv2.resize(cv2_image, (160, 90))
    facenet_result = facenet_classify_image_data(cv2_image_resized)
    return facenet_result


def read_cam():
    base_facenet = None
    #DBG print("cv2 version:", cv2.__version__)
    #DBG print("cv2 path:", cv2.__file__)
    # Try base camera (e.g. for osx), otherwise try nvidia onboard camera (jetson).
    # Detect platform to determine camera device capture spec as calling VideoCapture on the wrong device seems to hang.
    uname = platform.uname()
    print("platform.uname:", uname)
    video_spec = 0
    if any("Darwin" in name for name in uname):
        print("Darwin detected")
        video_spec = 0
    elif any("tegra" in name for name in uname):
        print("tegra detected")
        video_spec = "nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720,format=(string)I420, framerate=(fraction)24/1 ! nvvidconv flip-method=2 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
    else:
        print("Unknown")

    print("Opening camera:", video_spec)
    cap = cv2.VideoCapture(video_spec)
    print("Opened camera:", cap)
    if cap.isOpened():
        print("Open window")
        cv2.namedWindow("demo", cv2.WINDOW_AUTOSIZE)
        print("Opened window")
        while True:
            #DBG print("Read camera")
            ret_val, img = cap.read();
            #DBG print("Got image", img)

            img = facenet_get_classified_image(img)

            cv2.imshow('demo',img)
            # waitKey on jetson returns 255 instead of -1 when no key pressed.
            # esc key is 27.
            pressed_key = cv2.waitKey(1)
            if pressed_key >= 0 and pressed_key < 255:
                break
    else:
     print "camera open failed"

    cv2.destroyAllWindows()


if __name__ == '__main__':
    setup()
    read_cam()
