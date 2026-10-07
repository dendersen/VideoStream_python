import cv2
import os
from urllib.parse import urlsplit
import threading
import time

class Frame:
  def __init__(self, image:cv2.Mat):
    self.image = image

class ImageStream:
  def getFrame(self, count:int, allowMix:bool = False) -> list[Frame] | None:
    pass
  def awaitFrame(self, count:int, allowMix:bool = False) -> list[Frame] | None:
    pass
  def connect(self) -> bool:
    pass
  def disconnect(self) -> bool:
    pass

class ImageStream_Network(ImageStream):
  def __init__(self, streamLink:str):
    self.currentVideoSource = None
    self.running = False
    self.shouldRun = False
    self.connected = False
    self.streamLink = streamLink
    self.url = urlsplit(streamLink)
    self.waitTime = 5
  
  def _preloadFrames(self):
    while self.shouldRun and self.running:
      if self.currentVideoSource is None or not self.currentVideoSource.isOpened():
        self.currentVideoSource.release() if self.currentVideoSource is not None else None
        self.connected = False
        self.currentVideoSource = cv2.VideoCapture(self.streamLink)
        startWait = time.time()
        while time.time() - startWait < self.waitTime:
          if self.currentVideoSource.isOpened():
            break
          time.sleep(0.1)
        else:
          self.currentVideoSource.release()
          self.currentVideoSource = None
          time.sleep(1)
          print(f"Failed to connect to stream {self.streamLink}, retrying...")
          continue
      
      ready, frame = self.currentVideoSource.read()
      if ready:
        self.connected = True
        self.frameBuffer.append(Frame(frame))
      else:
        time.sleep(0.01)
    
    if not self.shouldRun:
      self.currentVideoSource.release() if self.currentVideoSource is not None else None
  
  def connect(self) -> bool:
    self.frameBuffer = []


class ImageStream_File(ImageStream):
  def __init__(self, filePath:str):
    self.Wildcard = None if not filePath.endswith("*") else os.path.split(filePath)[1].removesuffix("*")
    self.filePath = filePath
    
    if self.Wildcard:
      self.filePath = os.path.split(filePath)[0]
    
    if not os.path.exists(self.filePath):
      raise Exception(f"File path {self.filePath} does not exist")
    
    if not os.path.isdir(self.filePath) and self.Wildcard:
      raise Exception(f"File path {self.filePath} is not a directory, but wildcard is set")
    
    self.filePath = os.path.split(filePath)[0]
    
    self.files = self._FindFiles(os.path.join(self.filePath, self.Wildcard))
    self.disconnect()
  
  def _FindFiles(self, filePath:str) -> list[str]:
    if self.Wildcard:
      valid = []
      files = os.listdir(os.join(filePath))
      foundFiles = [os.join(filePath, f) for f in files if f.startswith(self.filePath)]
      for f in foundFiles:
        if os.path.isdir(f):
          valid += self._FindFiles(f)
        else:
          valid.append(f)
      return valid
    return [filePath] if os.path.isfile(filePath) else []
  
  def getFrame(self, count:int, allowMix:bool = False) -> list[Frame] | None:
    if self.currentVideoSource is None or not self.currentVideoSource.isOpened():
      self.fileIndex += 1
      if self.fileIndex >= len(self.videoSource):
        return None
      self.currentVideoSource = cv2.videoCapture(self.videoSource[self.fileIndex])
      if not self.currentVideoSource.isOpened():
        self.currentVideoSource.release()
        return self.getFrame(count)
    frames = []
    for i in range(count):
      ready, frame = self.currentVideoSource.read()
      if not ready:
        ready, frame = self.currentVideoSource.read()
        if not ready:
          self.currentVideoSource.release()
          if allowMix:
            found = self.getFrame(count - i, allowMix)
            if found is not None:
              frames += found
          else:
            frames = self.getFrame(count, allowMix)
          return frames
      frames.append(Frame(frame))
    return frames
  
  def awaitFrame(self, count:int, allowMix:bool = False) -> list[Frame] | None:
    return self.getFrame(count, allowMix)
  
  def connect(self) -> bool:
    self.videoSource = self.files
    self.fileIndex = -1
    self.currentVideoSource = None
    self.running = len(self.videoSource) > 0
    return self.running
  
  def disconnect(self):
    self.videoSource = None
    self.fileIndex = None
    if self.currentVideoSource is not None:
      self.currentVideoSource.release()
      self.currentVideoSource = None
    self.running = False

class StreamReader:
  STREAM_TYPE_FILE = 0
  STREAM_TYPE_NETWORK = 1
  _streamDefault:dict[int, str] = {STREAM_TYPE_FILE: "./", STREAM_TYPE_NETWORK: "rtsp://127.0.0.1:8080/video"}
  def __init__(self, streamLink:str|None = None, streamType:int = STREAM_TYPE_FILE):
    if streamType == self.STREAM_TYPE_FILE:
      self.stream = ImageStream_File(streamLink)
    else:
      self.stream = ImageStream_Network(streamLink)
      raise Exception("Stream type not supported yet")
  
  def stop(self):
    self.stream.disconnect()
  
  def getFrames(self, frameCount:int, forceCount:bool = True) -> list[Frame] | None:
    if forceCount:
      frames = self.stream.awaitFrame(frameCount, allowMix=True)
    else:
      frames = self.stream.getFrame(frameCount, allowMix=True)
    if frames is None:
      return None
    if len(frames) != frameCount:
      return None
    return frames