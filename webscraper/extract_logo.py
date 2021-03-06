# The main goal is to find the logo in the image

# Import the necessary packages
import image_utils as iutils
import numpy as np
import argparse
import cv2
from skimage import exposure
 
# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-q", "--query", required = True, help = "Path to the query image")
# args = vars(ap.parse_args())
imagePath = "..\\tests\\leaf\\0001.jpg"

# Load the image, 
image = cv2.imread(imagePath)

# clone it
original = image.copy()

# Only for the test image we have
#image = iutils.rotate(image, 90, center = None, scale = 1.0)
# compute the ratio of the old height
# to the new height, clone it, and resize it
#ratio = image.shape[0] / 300.0

# TODO: Remove the background

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

cv2.imshow('Gray', gray)
cv2.waitKey(0)

# Blur the image slightly by using the cv2.bilateralFilter function
# Bilateral filtering has the nice property of removing noise in the image
gray = cv2.bilateralFilter(gray, 11, 17, 17)

cv2.imshow('Blur', gray)
cv2.waitKey(0)

# Canny edge detector finds edge like regions in the image
edged = cv2.Canny(gray, 30, 200)

cv2.imshow('Canny', edged)
cv2.waitKey(0)

# New image segmentation with Watershed Algorithm
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# noise removal
kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

# sure background area
sure_bg = cv2.dilate(opening,kernel,iterations=3)

# Finding sure foreground area
dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)

# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg,sure_fg)



# Find contours in the edged image, keep only the largest ones, 
# and initialize our screen contour:
# The cv2.findContours function gives us a list of contours that it has found.
# The second parameter cv2.RETR_TREE tells OpenCV to compute the hierarchy 
# (relationship) between contours,
# We could have also used the cv2.RETR_LIST option as well;
# To compress the contours to save space using cv2.CV_CHAIN_APPROX_SIMPLE.
image2, cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# Return only the 10 largest contours
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
# Initialize screenCnt, the contour that corresponds to our object to find
screenCnt = None

# Loop over contours
for c in cnts:
    # cv2.arcLength and cv2.approxPolyDP. 
    # These methods are used to approximate the polygonal curves of a contour.
	peri = cv2.arcLength(c, True)
    # Level of approximation precision. 
    # In this case, we use 2% of the perimeter of the contour.
	approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    # we know that a Object screen is a rectangle,
    # and we know that a rectangle has four sides, thus has four vertices.
	# If our approximated contour has four points, then
	# we can assume that we have found our screen.
	if len(approx) == 4:
		screenCnt = approx
		break

# Drawing our screen contours, we can clearly see that we have found the Object screen
cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 3)
cv2.imshow("Object Screen", image)
cv2.waitKey(0)

###############################################################
# OpenCV Perspective Transform Example

# Now that we have our screen contour, we need to determine
# the top-left, top-right, bottom-right, and bottom-left
# points so that we can later warp the image -- we'll start
# by reshaping our contour to be our finals and initializing
# our output rectangle in top-left, top-right, bottom-right,
# and bottom-left order
pts = screenCnt.reshape(4, 2)
rect = np.zeros((4, 2), dtype = "float32")

# The top-left point has the smallest sum whereas the
# bottom-right has the largest sum
s = pts.sum(axis = 1)
rect[0] = pts[np.argmin(s)]
rect[2] = pts[np.argmax(s)]
 
# Compute the difference between the points -- the top-right
# will have the minumum difference and the bottom-left will
# have the maximum difference
diff = np.diff(pts, axis = 1)
rect[1] = pts[np.argmin(diff)]
rect[3] = pts[np.argmax(diff)]
 
# Multiply the rectangle by the original ratio
rect *= ratio

# Now that we have our rectangle of points, let's compute
# the width of our new image
(tl, tr, br, bl) = rect
widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
 
# ...and now for the height of our new image
heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
 
# Take the maximum of the width and height values to reach
# our final dimensions
maxWidth = max(int(widthA), int(widthB))
maxHeight = max(int(heightA), int(heightB))
 
# Construct our destination points which will be used to
# map the screen to a top-down, "birds eye" view
dst = np.array([
	[0, 0],
	[maxWidth - 1, 0],
	[maxWidth - 1, maxHeight - 1],
	[0, maxHeight - 1]], dtype = "float32")
 
# Calculate the perspective transform matrix and warp
# the perspective to grab the screen
M = cv2.getPerspectiveTransform(rect, dst)
warp = cv2.warpPerspective(orig, M, (maxWidth, maxHeight))

# Convert the warped image to grayscale and then adjust
# the intensity of the pixels to have minimum and maximum
# values of 0 and 255, respectively
warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
warp = exposure.rescale_intensity(warp, out_range = (0, 255))
 
# The object we want to identify will be in the top-right
# corner of the warped image -- let's crop this region out
(h, w) = warp.shape
(dX, dY) = (int(w * 0.4), int(h * 0.45))
crop = warp[10:dY, w - dX:w - 10]
 
# save the cropped image to file
cv2.imwrite("object.png", crop)
 
# show our images
cv2.imshow("warp", iutils.resize(warp, height = 300))
cv2.waitKey(0)
cv2.imshow("crop", iutils.resize(crop, height = 300))
cv2.waitKey(0)


# resize it - The smaller the image is, the faster it is to process
image = iutils.resize(image, height = 300)

cv2.destroyAllWindows()