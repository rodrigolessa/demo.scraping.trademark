# The main goal is to find the logo in the image

# Import the necessary packages
from skimage import exposure
# http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
from sklearn.cluster import KMeans
from functions import image_utils as iutils
from functions import helpers
import matplotlib.pyplot as plt
import numpy as np
import argparse
import cv2
 
# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-q", "--query", required = True, help = "Path to the query image")
# args = vars(ap.parse_args())
imagePath = "dataset\\leaf\\0001.jpg"
clusters = 3

# Load the image, 
image = cv2.imread(imagePath)

original = image.copy()

# Convert it from BGR to RGB so that
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# show our image
plt.figure()
plt.axis("off")
plt.imshow(image)

# Blur the image slightly by using the cv2.bilateralFilter function
# Bilateral filtering has the nice property of removing noise in the image
#gray = cv2.bilateralFilter(gray, 11, 17, 17)

#cv2.imshow('Blur', gray)
cv2.waitKey(0)

# Reshape the image to be a list of pixels
image = image.reshape((image.shape[0] * image.shape[1], 3))

# Using k-means to find the most dominant colors in an image
# Cluster the pixel intensities
clt = KMeans(n_clusters = clusters)
clt.fit(image)

# build a histogram of clusters and then create a figure
# representing the number of pixels labeled to each color
hist = helpers.centroid_histogram(clt)
bar = helpers.plot_colors(hist, clt.cluster_centers_)
 
# show our color bart
plt.figure()
plt.axis("off")
plt.imshow(bar)
plt.show()