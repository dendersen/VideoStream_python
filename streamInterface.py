class Frame:
  selfimage:list[int]

class StreamReader:
  def __init__(self, streamLink:str):
    self.link = streamLink
    self.Thread = None
  def _start(self):
    pass
  def _run(self):
    pass
  def stop(self):
    pass
  def getFrames(self, frameCount:int) -> list[Frame]:
    pass