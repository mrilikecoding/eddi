from email.charset import BASE64
import pickle
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np






pathL = "data/stereoL/"
pathR = "data/stereoR/"
img1 = cv.imread(pathL+"img0.png", cv.IMREAD_GRAYSCALE)
img2 = cv.imread(pathR+"img0.png", cv.IMREAD_GRAYSCALE)
disparity_SGBM = cv.imread(pathR+"img0.png", cv.IMREAD_GRAYSCALE)
h,w = img2.shape[:2]

# CAM PROPERTIES
# https://photo.stackexchange.com/questions/27218/how-do-i-find-a-cameras-focal-length-in-pixels
FOCAL_LENGTH = (2.8 * 1920)/8 # in pixels assuming 8mm sensor size
BASELINE = 50.8
# https://medium.com/@omar.ps16/stereo-3d-reconstruction-with-opencv-using-an-iphone-camera-part-iii-95460d3eddf0
Q = np.float32([[1,0,0,-w/2.0],
    [0,-1,0,h/2.0],
    [0,0,0,-FOCAL_LENGTH],
    [0,0,1,0]])
Q2 = np.float32([[1,0,0,0],
    [0,-1,0,0],
    [0,0,FOCAL_LENGTH*0.05,0], #Focal length multiplication obtained experimentally. 
    [0,0,0,1]])
def mouse_value(event,x,y,flags,param):
    frame = disparity_SGBM
    if event == cv.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        value = frame[y,x]
        z = (BASELINE * FOCAL_LENGTH) / value
        print("Coordinates of pixel: X: ",x,"Y: ",y)
        print("DEPTH (mm):", z)
cv.namedWindow('Disparity')
cv.setMouseCallback('Disparity',mouse_value)


with open('fundamental_matrix.pickle', 'rb') as f:
    FM = pickle.load(f)
pts1 = FM['pts1']
pts2 = FM['pts2']
fundamental_matrix = FM['F']

CAM1 = cv.VideoCapture(0)
CAM2 = cv.VideoCapture(1)
if not CAM1.isOpened():
    raise IOError("Cannot open webcam 1")
if not CAM2.isOpened():
    raise IOError("Cannot open webcam 2")

# StereoSGBM Parameter explanations:
# https://docs.opencv.org/4.5.0/d2/d85/classcv_1_1StereoSGBM.html

# Matched block size. It must be an odd number >=1 . Normally, it should be somewhere in the 3..11 range.
block_size = 5
min_disp = -128
max_disp = 128
# Maximum disparity minus minimum disparity. The value is always greater than zero.
# In the current implementation, this parameter must be divisible by 16.
num_disp = max_disp - min_disp
# Margin in percentage by which the best (minimum) computed cost function value should "win" the second best value to consider the found match correct.
# Normally, a value within the 5-15 range is good enough
uniquenessRatio = 5
# Maximum size of smooth disparity regions to consider their noise speckles and invalidate.
# Set it to 0 to disable speckle filtering. Otherwise, set it somewhere in the 50-200 range.
speckleWindowSize = 50
# Maximum disparity variation within each connected component.
# If you do speckle filtering, set the parameter to a positive value, it will be implicitly multiplied by 16.
# Normally, 1 or 2 is good enough.
speckleRange = 1
disp12MaxDiff = 0
stereo = cv.StereoSGBM_create(
    minDisparity=min_disp,
    numDisparities=num_disp,
    blockSize=block_size,
    uniquenessRatio=uniquenessRatio,
    speckleWindowSize=speckleWindowSize,
    speckleRange=speckleRange,
    disp12MaxDiff=disp12MaxDiff,
    P1=8 * 1 * block_size * block_size,
    P2=32 * 1 * block_size * block_size,
)
# Stereo rectification (uncalibrated variant)
# Adapted from: https://stackoverflow.com/a/62607343
h1, w1 = img1.shape
h2, w2 = img2.shape
_, H1, H2 = cv.stereoRectifyUncalibrated(
    np.float32(pts1), np.float32(pts2), fundamental_matrix, imgSize=(w1, h1)
)


while(True):
    key = cv.waitKey(1)
    if key == ord('q'):
        break
    # Capture the video frame
    # by frame
    ret1, img1 = CAM1.read()
    ret2, img2 = CAM2.read()
    img1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    img2 = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)

    # Rectify (undistort) the images and save them
    # Adapted from: https://stackoverflow.com/a/62607343
    img1_rectified = cv.warpPerspective(img1, H1, (w1, h1))
    img2_rectified = cv.warpPerspective(img2, H2, (w2, h2))

    # ------------------------------------------------------------
    # CALCULATE DISPARITY (DEPTH MAP)
    # Adapted from: https://github.com/opencv/opencv/blob/master/samples/python/stereo_match.py
    # and: https://docs.opencv.org/master/dd/d53/tutorial_py_depthmap.html
    disparity_SGBM = stereo.compute(img1_rectified, img2_rectified)

    # Normalize the values to a range from 0..255 for a grayscale image
    disparity_SGBM = cv.normalize(disparity_SGBM, disparity_SGBM, alpha=255,
                                beta=0, norm_type=cv.NORM_MINMAX)
    disparity_SGBM = np.uint8(disparity_SGBM)
    # resize image
    disparity_SGBM = cv.resize(disparity_SGBM, (400, 300), interpolation = cv.INTER_AREA)
    def mouse_callback(event, x, y, flags, params):
        if event == 2:
            print(f"coords {x, y}, value {disparity_SGBM[y, x]}")
    cv.namedWindow("Disparity")
    cv.setMouseCallback("Dispariy", mouse_callback)
    # img1_rectified = cv.resize(img1_rectified, (400, 300), interpolation = cv.INTER_AREA)
    # img2_rectified = cv.resize(img2_rectified, (400, 300), interpolation = cv.INTER_AREA)
    # cam = np.concatenate((img1_rectified, disparity_SGBM, img2_rectified), axis=1)
    # cv.imshow("Cam", cam)
    cv.imshow("Disparity", disparity_SGBM)

# After the loop release the cap object
CAM1.release()
CAM2.release()
# Destroy all the windows
cv.destroyAllWindows()