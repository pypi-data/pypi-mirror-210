import numpy as np
# Random walk and polynomial:
from .randomwalk import Polynomial
# Plotting:
## Better polygons: dilates random walk path into polygon
from shapely.plotting import plot_polygon

class A_Band(Polynomial):
    """
    A_Band is a dilated Polynomial.

    Attributes:
        origin: [x0,y0]
        length: total length
        radius: gives thickness to the polynomial
        index: labelling of the A_Band
        σr: standard deviation of length of each edge
        σθ: standard deviation of angle of edge relatives to the previous
        r0: mean length of each edge (default r0=1)
    """
    def __init__(self,origin=[0,0],radius=0.4,length=20,σr=0.1,σθ=0.01,r0=1,θ0=np.pi/2):
        
        self.radius=radius

        super().__init__(origin,radius,length,σr,σθ,r0,θ0)
        
    def get_A_band(self):
        """
        Returns a dilated polynomial.
        """

        if not hasattr(self,"A_band"):
            self.A_band = self.get_polynomial().buffer(self.radius, cap_style=3)

        return self.A_band

    def plot_A_band(self,ax,A_band=None):
        if type(A_band)==type(None):
            A_band=self.get_A_band()
        plot_polygon(A_band, ax=ax, add_points=False, alpha=0.5)
