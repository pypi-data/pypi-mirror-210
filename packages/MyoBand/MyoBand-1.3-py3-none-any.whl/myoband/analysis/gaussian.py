import numpy as np
import scipy as sp

def add_noise(slide):
    """
    Add Gaussian noise
    """
    noise = np.random.randint(2,size=np.shape(slide))
    return np.logical_and(slide,noise)
    
def remove_noise(slide,sigma=[0.2,0.2]):
    """
    Remove Gaussian noise with a Gaussian filter
    """
    _2d=False
    if len(np.shape(slide))==2:
        _2d=True
        slide=np.array([slide])
    slide=np.logical_not(slide)
    slide = np.array([sp.ndimage.filters.gaussian_filter(slide[i], sigma, mode='constant') for i in range(len(slide))], dtype=bool)
    slide=np.logical_not(slide)
    # Remove Gaussian around edges:
    slide[:,:,0]=slide[:,:,-1]=0
    slide[:,0,:]=slide[:,-1,:]=0
    if _2d:
        slide=slide[0]
    return slide

