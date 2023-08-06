import cv2

from easyaiapi.utils import image_to_base64


class Video:
    
    def __init__(self, path:str, shape=None, show_video=True, window_name=None) -> None:
        self.path = path
        self.shape = shape
        self.show_video = show_video
        self.window_name = window_name or "webcam"
        self.pre_process = lambda img: img if self.shape is None else cv2.resize(img, self.shape, interpolation=cv2.INTER_AREA)
        self.__load_video()

    def __load_video(self):    
        self.vid = cv2.VideoCapture(self.path)

    def read(self):
        ret, img = self.vid.read()
        if ret:
            if self.show_video:
                cv2.imshow(f"image", img)
                cv2.waitKey(1)  
            return image_to_base64(self.pre_process(img))
        self.__load_video()