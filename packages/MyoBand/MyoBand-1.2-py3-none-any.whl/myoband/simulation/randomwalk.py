"""
Copyright, 23 March 2023, Henry Joseph Sheehy. All rights reserved.
"""

# Used for random walk:
import numpy as np
import random
# Plotting
from matplotlib import pyplot as plt
# Polygons
from shapely.geometry import LineString
from shapely.plotting import plot_line

class PolarRandomWalk():
    """
    Random walk in polar coordinates

    n steps
    σθ standard deviation of the polar angle with mean 0
    σr standard devitation of the polar radius with mean r (default r0=1)
    """

    def __init__(self,n,σr,σθ,r0=1,θ0=np.pi/2):

        self.n=n
        self.σθ=σθ
        self.σr=σr
        self.r0=r0
        self.θ0=θ0

    def get_polar_distribution(self):

        if not hasattr(self,"polar_distribution"): 
            self.polar_distribution=np.random.normal(loc=[self.r0,self.θ0],scale=[self.σr,self.σθ],size=[self.n,2])
        return self.polar_distribution

    def get_cartesian_distribution(self):

        if not hasattr(self,"cartesian_distribution"): 
            argand=self.get_polar_distribution()[:,0]*np.exp(1j*self.polar_distribution[:,1])
            real=np.real(argand)
            imag=np.imag(argand)
            self.cartesian_distribution=np.stack((real,imag))
            self.cartesian_distribution=np.cumsum(self.cartesian_distribution,axis=1)

        return self.cartesian_distribution

        # plt.plot(*self.cartesian_distribution)
        # plt.show()

# prw = PolarRandomWalk(5,0.05,0.1)
# print(prw.polar_distribution)

class Polynomial(PolarRandomWalk):
    """
    Piecewise linear polynomial in two-dimensions given by a (2,n)-vector 
    with n vertices.

    Attributes:
        origin: [x0,y0]
        length: total length
        radius: gives thickness to the polynomial
        index: labelling 
        σr: standard deviation of length of each edge
        σθ: standard deviation of angle of edge relatives to the previous
        r0: mean length of each edge (default r0=1)
    """

    def __init__(self,origin=[0,0],radius=0.4,length=20,σr=0.1,σθ=0.01,r0=1,θ0=np.pi/2):
        
        self.n=int(length/(r0+2*radius)) # number of vertices
        self.origin=np.array(origin)
        self.radius=radius
        self.length=length
        self.σr=σr
        self.σθ=σθ
        self.r0=r0
        self.θ0=θ0
        self.index=None

    def get_polynomial(self):

        if not hasattr(self,"polynomial"):
            self.polynomial=LineString((self.get_cartesian_distribution() + self.origin[:,np.newaxis]).T)

        return self.polynomial

    def plot_polynomial(self,ax):

        plot_line(self.get_polynomial(), ax=ax, add_points=False)
