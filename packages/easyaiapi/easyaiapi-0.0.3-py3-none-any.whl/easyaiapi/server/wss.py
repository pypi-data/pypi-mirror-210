from cgitb import reset
from typing import Any, Callable, Optional
from fastapi import WebSocket, FastAPI
from easyaiapi.utils import read_base64_image
from opencv_stream import FpsDrawer, ModelOutput, Option, Model
import cv2
import uuid
import numpy as np
import uvicorn

       
                        
class WssServer(FastAPI):
    
    def __init__(self, **options):
        super().__init__(**options)
 
    def run(self, port=8080, host="0.0.0.0"):
        uvicorn.run(self, host=host, port=port)

    def stream(self, endpoint: str, on_received:Callable[[str], Any]=lambda x: Option(x), on_connect:Callable[[str], None]=None, on_disconnect:Callable[[str], None]=None):
        
        on_connect = on_connect if callable(on_connect) else lambda _ : None
        on_disconnect = on_disconnect if callable(on_disconnect) else lambda _ : None
        def wrapper(func:Callable[[Any, str], None]):
            
            @self.websocket(f"{endpoint}")
            async def websocket_index(websocket: WebSocket):

                client_address = websocket.client or f"id: {uuid.uuid4()}"
                print(f"{client_address} HAS ARRIVED")
                
                await websocket.accept()
                on_connect(client_address)
                # print(f"{client_address} HAS CONNECTED")
                
                try:
                    while True:
                        # print("TRYING TO RECEIVE DATA")
                        data = await websocket.receive_text()
                        # print("received ", data)
                        result: Option = on_received(data)
                        if not result.is_ok():
                           await websocket.send_json({
                               "success": False,
                               "message": str(result.exception)
                           })
                        else:    
                        
                            await websocket.send_json(
                                func(result.unwrap(), client_address)
                            )
                
                except Exception as e:
                    raise (e)
                finally:
                    await websocket.close()
                    on_disconnect(client_address)

                    cv2.destroyAllWindows()
        
        return  lambda f: wrapper(f)   

    def videostream(self, endpoint: str, resize_shape:Optional[tuple[int,int]]=None, on_connect:Callable[[str], None]=None, on_disconnect:Callable[[str], None]=None):

        on_received = lambda x: read_base64_image(x, resize_shape) if resize_shape else lambda x: x
        return self.stream(endpoint, on_received, on_connect, on_disconnect) 


    def create_model_enpoint(self, endpoint, model: Model, window_name=None, draw=True, resize_shape:Optional[tuple[int, int]]=None):
    
        window_name = endpoint if window_name is None else window_name
        utils = {"prev_draw": lambda img: None}
        fps = FpsDrawer()

        def _draw_fn(image, client_address:str, result: Option=None):
            if result.is_ok():
                result.unwrap().draw(image)  
                utils['prev_draw'] = result.unwrap().draw
            else:    
                utils['prev_draw'](image)
            
            fps.draw(image) 
            cv2.imshow(f"{window_name} @ {client_address}", image)
            cv2.waitKey(1)  
        
        def _no_draw(*args, **kwargs):...

        draw_fn = _draw_fn if draw else _no_draw
        
        @self.videostream(endpoint, resize_shape)
        def index(image: np.ndarray, client_address):
            
            result = model(image)

            if not result.is_ok():
                output =  {"success": False, "message": str(result.exception)}            
            else:
                output = result.unwrap().to_dict()

            draw_fn(image, client_address, result)
                      
            return output

    def create_model_enpoint_multi_client(self, endpoint, get_model_fn: Callable[[], Model], window_name=None, resize_shape:Optional[tuple[int, int]]=None):
        
        window_name = endpoint if window_name is None else window_name
        models: dict[str, Model] = {}

        def on_connect(client_address:str):
            models[client_address] = get_model_fn()

        def on_disconnect(client_address:str):
            del models[client_address]

        @self.videostream(endpoint, resize_shape, on_connect=on_connect, on_disconnect=on_disconnect)
        def index(image: np.ndarray, client_address):

            result: Option = models[client_address].predict(image)

            if not result.is_ok():
                output =  {"success": False, "message": result.msg}
            else:
                data: ModelOutput = result.unwrap()
                output = data.to_dict()

            return output       

