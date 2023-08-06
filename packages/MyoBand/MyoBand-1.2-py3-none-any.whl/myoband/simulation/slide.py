"""
Copyright, 23 March 2023, Henry Joseph Sheehy. All rights reserved.
"""

import numpy as np

# A_Band
from .a_band import A_Band

# Plotting:
from matplotlib import pyplot as plt
from matplotlib.pyplot import cm
from ..plotting import imshow

# Polygons: fast detection of points within polygon
from matplotlib.patches import Rectangle,Circle
from matplotlib.path import Path
## Better polygons: dilates random walk path into polygon
from shapely.geometry import LineString
from shapely.plotting import plot_polygon, plot_line
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

class Slide():
    """
    The area on which to place the A_Bands.
    Area=width x height
    Spacing: dwidth, dheight

    Labels the A_Bands.

    Attribute:
        get_plot(): imshow() of the slide.

    """
    def __init__(self,width,height,dwidth,dheight):

        self.width=width
        self.height=height
        self.dwidth=dwidth
        self.dheight=dheight

        self.A_bands={}

        xx=np.arange(0,width+dwidth,dwidth)
        yy=np.arange(0,height+dheight,dheight)

        self.pts=np.array([[[x,y] for x in xx] for y in yy])
        self.nx,self.ny,_=np.shape(self.pts)
    
    def flatten_pts(self):

        self.pts=np.reshape(self.pts,[self.nx*self.ny,2])

        return self.pts

    def reshape_pts(self):

        self.pts=np.reshape(self.pts,[self.nx,self.ny,2])

        return self.pts

    def add_A_bands(self,A_band:A_Band):
        """
        Add a A_band or a list of A_bands
        """
        if hasattr(A_band,'__len__'):
            for _A_band in A_band:
                self.add_A_bands(_A_band)
        else:
            index=len(self.A_bands)
            A_band.index=index
            self.A_bands[index]=A_band

    @property
    def n_bands(self):
        return len(self.A_bands)

    def get_slide(self):
        
        if hasattr(self,"slide"):
            return self.slide

        self.slide=np.ones([self.n_bands,self.nx,self.ny],dtype=bool)
        
        for index,A_band in self.A_bands.items():
            polygon=A_band.get_A_band()
            x,y = polygon.exterior.xy
            coords=np.vstack((x,y)).T
            point=Point(0.,4)
            p = Path(coords) # make a polygon
            points=self.flatten_pts()
            grid = p.contains_points(points)
            self.slide[index] = grid.reshape(self.nx,self.ny) # now you have a mask with points inside a polygon

        return self.slide

    def imshow_A_bands(self,ax,indices='all'):

        if indices=='all':
            indices=np.arange(self.n_bands)

        return imshow(ax,self.get_slide())
