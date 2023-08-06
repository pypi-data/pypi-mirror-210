"""
Copyright, 23 March 2023, Henry Joseph Sheehy. All rights reserved.
"""

import numpy as np
from myoband.analysis.gaussian import remove_noise
from myoband.analysis.analysis import contour, skeleton
import skimage
import matplotlib.pyplot as plt

from myoband.plotting import imshow
def main(IMPORT_DATA):

    FILE=__file__.split(".py")[0]
    FILENAME=FILE.split("/")[-1]
    FIG=FILE+".pdf"
    PNG=FILE+".png"
    if IMPORT_DATA==None:
        IMPORT_DATA=FILE.split(FILENAME)[0]+"simulation.npz"
    DATA=FILE+".npz"

    print("Load data...")
    npz_mask=np.load(IMPORT_DATA)
    print("Files contained in data directory:")
    print(npz_mask.files)
    data=npz_mask["data"]

    nx,ny=np.shape(data)

    # Apply Gaussian twice:
    data=remove_noise(data)
    data=remove_noise(data)

    tmp=contour(data)

    mask=[]
    pts=np.indices((nx,ny))
    pts=np.reshape(pts,[2,nx*ny]).T
    for i in range(len(tmp)):
        arr1=np.array(pts)
        # tmp[i]=np.rint(tmp[i]).astype(int)
        arr2=tmp[i]
        mask.append(skimage.measure.points_in_poly(arr1, arr2))
    mask=np.array(mask)
    mask=np.reshape(mask,[len(mask),nx,ny])
    fig,axes=plt.subplots(2)
    axes[0].imshow(data,origin='lower')
    imshow(axes[1],mask)

    for i in range(2):
        axes[i].set_xlabel("")
        axes[i].set_ylabel("")
        axes[i].set_xticks([])
        axes[i].set_yticks([])
    
    axes[0].title.set_text("Original A bands")
    axes[1].title.set_text("Extracted A bands")

    print("Saving image as PDF:")
    print(FIG)
    plt.tight_layout()
    plt.savefig(FIG,dpi=DPI)
    print("Saving image as PNG:")
    print(PNG)
    plt.tight_layout()
    plt.savefig(PNG,dpi=DPI, transparent=True)
    print("Image saved with high DPI (required to see skeleton)")
    plt.close()

# Plotting and data:
IMPORT_DATA=None
DPI=800

main(IMPORT_DATA)
