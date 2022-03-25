# import the opencv library
import cv2
import os
import numpy as np
  
"""
This is to aid in camera callibration
First, set two webcams up - ideally two identical cams with the same picture quality / resolution
Next, make sure they are at the same height - callibration will work when the y is the same
Hit "s" to capture a series of images - using a checkerboard is a good way to get corners
"""
CAM1 = cv2.VideoCapture(0)
CAM2 = cv2.VideoCapture(1)
if not CAM1.isOpened():
    raise IOError("Cannot open webcam 1")
if not CAM2.isOpened():
    raise IOError("Cannot open webcam 2")
stereoL_path = 'data/stereoL'
stereoR_path = 'data/stereoR'
  
frame_count = 0
while(True):
      
    # Capture the video frame
    # by frame
    ret1, frame1 = CAM1.read()
    ret2, frame2 = CAM2.read()


    scale_percent = 40 # percent of original size
    width = int(frame1.shape[1] * scale_percent / 100)
    height = int(frame1.shape[0] * scale_percent / 100)
    dim = (width, height)

    # let's try b&w images
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    # resize image
    resized1 = cv2.resize(frame1, dim, interpolation = cv2.INTER_AREA)
    resized2 = cv2.resize(frame2, dim, interpolation = cv2.INTER_AREA)

    corners1 = cv2.goodFeaturesToTrack(frame1,25,0.01,10)
    corners2 = cv2.goodFeaturesToTrack(frame2,25,0.01,10)
    corners1 = np.int0(corners1)
    corners2 = np.int0(corners2)

    frame1_copy = np.copy(frame1)
    frame2_copy = np.copy(frame2)

    for i in corners1:
        x,y = i.ravel()
        cv2.circle(frame1_copy,(x,y),3,(0,0,255),-1)
    for i in corners2:
        x,y = i.ravel()
        cv2.circle(frame2_copy,(x,y),3,(0,0,255),-1)
    frame1_copy = cv2.resize(frame1_copy, dim, interpolation = cv2.INTER_AREA)
    frame2_copy = cv2.resize(frame2_copy, dim, interpolation = cv2.INTER_AREA)

    cv2.imshow('Corners 1',frame1_copy)
    cv2.imshow('Corners 2',frame2_copy)

    # Display the resulting frame
    cv2.imshow('Cam 1', resized1)
    cv2.imshow('Cam 2', resized2)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    key = cv2.waitKey(1)
    if key == ord("s"):
        if frame_count < 25:
            save_path_L = os.path.join(stereoL_path , f"img{frame_count}.png")
            save_path_R = os.path.join(stereoR_path , f"img{frame_count}.png")
            print(f"Capturing Frame {frame_count}")
            print(save_path_L)
            print(save_path_R)
            try:
                cv2.imwrite(save_path_L, frame1)
                cv2.imwrite(save_path_R, frame2)
                frame_count += 1 
            except Exception as e:
                print(e)

    # if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        break
  
# After the loop release the cap object
CAM1.release()
CAM2.release()
# Destroy all the windows
cv2.destroyAllWindows()