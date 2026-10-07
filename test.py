if __name__ == "__main__":
  from streamInterface import StreamReader
  from tkinter import Tk
  from tkinter.filedialog import askopenfilename
  
  from cv2 import imshow, waitKey
  
  Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
  filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
  print(f"Selected file: {filename}")
  stream = StreamReader(filename, StreamReader.STREAM_TYPE_FILE)
  print("Starting stream...")
  stream.start()
  for i in range(10):
    frames = stream.getFrames(1,True)
    print(f"Got {len(frames) if frames is not None else 0} frames")
    if frames is not None and len(frames) > 0:
      imshow("Frame", frames[0].image)
      waitKey(100)