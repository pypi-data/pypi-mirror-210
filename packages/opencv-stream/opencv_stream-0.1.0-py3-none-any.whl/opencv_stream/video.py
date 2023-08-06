from typing import Callable
import cv2
import numpy as np
from typing import Optional
from threading import Thread
from queue import Queue

from .fps_drawer import FpsDrawer

from .model_schema import Model, ModelOutput

class InvalidInputError(Exception): ...

def _assert_is_type(input, expected_type:type):

    if not isinstance(input, expected_type):
        raise InvalidInputError(f"Expected a '{expected_type}', received '{type(input)}'")


class VideoStreamer:
    """
    Use this class the read videos from path or from webcam
    Use the on_next_frame method as a decorator to wrap  

    """

    def __init__(self, cap, window_name="video", waitkey=1) -> None:
        
      self.__cap = cap
      self.__tasks = []
      self.__pre_tasks = []
      self.window_name = window_name
      self.waitkey = waitkey

      
    def from_webcam(cam_index:int=0,window_name:str="video", waitkey:int=1):

        _assert_is_type(cam_index, int)
       
        return VideoStreamer(
           cap = cv2.VideoCapture(cam_index),
           window_name=window_name, 
           waitkey=waitkey 
       )
       
    def on_next_frame(self, shape:Optional[tuple[int,int]]=None):
        """
        Use as a decorator to wrap your function\n
        The cam window is drawn automatically after the function has been called.\n
        Example: \n

        stream =  VideoStreamer.from_webcam()
        @stream.on_next_frame()
        def func(image):
             ...


        """
        if not shape is None:
           self.__pre_tasks.append(lambda img: cv2.resize(img, shape, interpolation=cv2.INTER_AREA))
           
        def inner(func:Callable[[np.ndarray], None]):
            self.__tasks.append(func)  

        return inner    


    def start_with_model(self, model: Model, fps_drawer:Optional[FpsDrawer]=FpsDrawer()):

        if fps_drawer:  
            @self.on_next_frame()
            def fn(image: np.ndarray):
                output = model.predict(image) 
                output.draw(image)
                fps_drawer.draw(image)
        else:
            @self.on_next_frame()
            def fn(image: np.ndarray):
                output = model.predict(image) 
                output.draw(image)

        self.start()

    def from_video_input(path, window_name="video", waitkey=1):

        _assert_is_type(path, str)

        return VideoStreamer(
            cap=cv2.VideoCapture(path),
           window_name=window_name, 
           waitkey=waitkey 
        ) 
    
    def __step(self, frame):
        
        for fn in self.__tasks: 
            
            fn(frame)
            
            cv2.imshow(self.window_name, frame)
            cv2.waitKey(self.waitkey)
        
    def start(self):
        """
        Using the method to start loading the next frames
        """
        
        queue = Queue()

        def update():
        
            while True:
                ret, frame = self.__cap.read()
                if ret:
                   queue.put(frame)
                else: 
                   queue.put(None)

        thread = Thread(target=update)
        thread.daemon = True
        thread.start()  

        while True:

            if  queue.empty(): continue
            
            frame = queue.get()
            if frame is None: return self.close()

            for task in self.__pre_tasks:
                frame = task(frame)

            self.__step(frame)  

    def close(self):
        self.__cap.release()
        cv2.destroyAllWindows()            
        
    
        