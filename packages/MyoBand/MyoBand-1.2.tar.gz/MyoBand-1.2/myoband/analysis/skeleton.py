import numpy as np
# Plotting:
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm
from matplotlib.colors import colorConverter
import matplotlib as mpl
from ..plotting import imshow

## Better cmaps
from mycolorpy import colorlist as mcp

# Polygons: fast detection of points within polygon
from matplotlib.patches import Rectangle,Circle
from matplotlib.path import Path
## Better polygons: dilates random walk path into polygon
from shapely.geometry import LineString
from shapely.plotting import plot_polygon, plot_line
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Image analysis: find contour of image and skeleton of polygon
import skimage

def contour(slide):
    if len(np.shape(slide))==3:
        slide=np.sum(slide,axis=0)
    return skimage.measure.find_contours(slide, 0.9)

def skeleton(slide):
    """
    Returns an array of dimensions of the slide. The array is zeros, with ones only where the skeleton is located.
    """
    return skimage.morphology.skeletonize(slide, method='lee') # 'lee' avoid bifurications

def get_pts(skeletons):

    pts={}
    for i in range(len(skeletons)):
        pts[i]=np.nonzero(skeletons[i].T)
    return pts
