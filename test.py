

if __name__ == "__main__":
  from streamInterface import StreamReader
  import os.path as path
  from cv2 import imshow, waitKey
  import time
  def displayTest(target:str):
    import os.path as path
    stream = StreamReader(path.join(source,target), StreamReader.STREAM_TYPE_FILE)
    stream.start()
    noFrame = 0
    while True:
      frames = stream.getFrames(1,True)
      if frames is not None and len(frames) > 0:
        imshow("Frame", frames[0].image)
        waitKey(100)
      else:
        time.sleep(.1)
        noFrame += 1
        if noFrame > 10:
          break
  source = path.abspath(__file__)
  source = path.split(source)[0]
  displayTest("placeholder_0.png")
  displayTest("placeholder_2.mp4")
  displayTest("placeholder*")
