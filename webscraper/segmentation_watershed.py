# The main goal is to create segmentation objects

from skimage import exposure
from functions import image_utils as iutils
import numpy as np
import argparse
import cv2
 
# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-q", "--query", required = True, help = "Path to the query image")
# args = vars(ap.parse_args())
imagePath = "dataset\\leaf\\0027.jpg"

# Load the image, 
image = cv2.imread(imagePath)

# clone it
original = image.copy()

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

cv2.imshow('Gray', gray)
cv2.waitKey(0)

# New image segmentation with Watershed Algorithm
ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

cv2.imshow('Thresh', thresh)
cv2.waitKey(0)

# Problem: Lost image data
# noise removal
kernel = np.ones((3,3), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations = 2)

#cv2.imshow('opening', opening)
#cv2.waitKey(0)

# sure background area
sure_bg = cv2.dilate(opening, kernel, iterations = 3)

# Finding sure foreground area
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

# Finding unknown region
sure_fg = np.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)

cv2.imshow('unknown', unknown)
cv2.waitKey(0)



# Marker labelling
ret, markers = cv2.connectedComponents(sure_fg)

# Add one to all labels so that sure background is not 0, but 1
markers = markers+1

# Now, mark the region of unknown with zero
markers[unknown==255] = 0

cv2.imshow('markers', image)
cv2.waitKey(0)


markers = cv2.watershed(image, markers)

cv2.imshow('markers', image)
cv2.waitKey(0)

image[markers == -1] = [255,0,0]

cv2.imshow('image', image)
cv2.waitKey(0)


# save the cropped image to file
cv2.imwrite("segmentation.png", image)
 
cv2.destroyAllWindows()