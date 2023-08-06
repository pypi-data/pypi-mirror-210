import asyncio
from typing import Callable, Optional
import websockets
from easyaiapi.utils import image_to_base64, read_base64_image
import cv2
from .source import Video

class NoDataException(Exception):
    pass

class WssClient:

    def get_data(self):
        raise NotImplementedError("Must implement 'get_data'") 

    def on_data_received(self):
        raise NotImplementedError("Must implement 'on_data_received'")     

    def start(self, uri:str):

        async def wrapper():

            async with websockets.connect(uri) as websocket:
                while True:  
                    try:
                        data = self.get_data()
                        if not data:
                            break
                        await websocket.send( data )
                        message = await websocket.recv()
                        self.on_data_received(message)

                    except NoDataException:
                        break    

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(wrapper())

    def from_source(uri:str, get_data: Callable):

        ws = WssClient()
        ws.get_data = get_data

        def wrapper(on_data_received: Callable):
            ws.on_data_received = on_data_received
            ws.start(uri)

        return wrapper    
    
    @classmethod
    def from_video_source(cls, uri:str, path:str, shape:Optional[tuple[int, int]]=None, show_video=True, restart_on_video_end:bool=False) -> None:
        video = Video(path, shape, show_video)
        return cls.from_source(uri, video.read)



