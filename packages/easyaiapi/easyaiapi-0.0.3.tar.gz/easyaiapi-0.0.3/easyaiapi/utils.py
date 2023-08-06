# https://alpha2phi.medium.com/yolo-using-fastapi-websocket-and-react-2b2d28e9f7ed

import asyncio
from threading import Thread
from typing import Callable
import numpy as np
import cv2
import base64
from opencv_stream import Option

@Option.wrap
def read_base64_image(uri, shape=(600,600)):
   
   split_uri = uri.split(',') 
   encoded_data = split_uri[0] if len(split_uri) == 0 else split_uri[0]
   nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

   if not shape is None:
     img = cv2.resize(img, shape, interpolation=cv2.INTER_AREA)

   return img


def handle_receive(stream):
    
    img =  read_base64_image(stream)
    if img is None: return
    cv2.imshow("img", img)

        

def image_to_base64(img: np.ndarray) -> bytes:
    """ Given a numpy 2D array, returns a JPEG image in base64 format """

    # using opencv 2, there are others ways
    img_buffer = cv2.imencode('.jpg', img)[1]
    return base64.b64encode(img_buffer).decode('utf-8')
    
def get_image(volume, index: int):
    image = volume[:, :, index]
    return image_to_base64(image)

def create_thread(fn):

    thread = Thread(target=fn)
    thread.daemon = True
    thread.start()

def background_thread(fn:Callable):
    def wrapper():
        create_thread(fn)

    return wrapper    
