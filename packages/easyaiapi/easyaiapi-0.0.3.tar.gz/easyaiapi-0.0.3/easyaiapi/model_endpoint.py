from pprint import pprint
from typing import Callable, Optional
from .server import WssServer
from opencv_stream import FpsDrawer, ModelOutput, Option, Model
import numpy as np
import cv2


server = WssServer()

def create_model_enpoint(endpoint, model: Model, window_name=None, draw=True, resize_shape:Optional[tuple[int, int]]=None):
    
    window_name = endpoint if window_name is None else window_name
    utils = {"prev_draw": lambda img: None}
    fps = FpsDrawer()

    def _draw_fn(image, result: Option=None):
        if result.is_ok():
            result.unwrap().draw(image)  
            utils['prev_draw'] = result.unwrap().draw
        else:    
            utils['prev_draw'](image)

    def _no_draw(*args, **kwargs):...

    draw_fn = _draw_fn if draw else _no_draw
    
    @server.videostream(endpoint, resize_shape)
    def index(image: np.ndarray, client_address):
        
        result: Option = model.predict(image)

        if not result.is_ok():
            output =  {"success": False, "message": str(result.exception)}
            draw_fn(image, result)
        
        else:
            output: ModelOutput = result.unwrap()
            draw_fn(image, output.to_dict())
        
        cv2.imshow(f"{window_name} @ {client_address}", image)
        cv2.waitKey(1)

        return output

def create_model_enpoint_multi_client(endpoint, get_model_fn: Callable[[], Model], window_name=None, draw=True, resize_shape:Optional[tuple[int, int]]=None):
    
    window_name = endpoint if window_name is None else window_name
    models: dict[str, Model] = {}

    def on_connect(client_address:str):
        models[client_address] = get_model_fn()

    def on_disconnect(client_address:str):
        del models[client_address]

    @server.videostream(endpoint, resize_shape, on_connect=on_connect, on_disconnect=on_disconnect)
    def index(image: np.ndarray, client_address):

        result: Option = models[client_address].predict(image)

        if not result.is_ok():
            output =  {"success": False, "message": result.msg}
        else:
            data: ModelOutput = result.unwrap()
            output = data.to_dict()


        # cv2.waitKey(10)
        return output