"""
Copyright, 23 March 2023, Henry Joseph Sheehy. All rights reserved.
"""

from myoband.simulation.a_band import A_Band
from myoband.simulation.utils import get_compressed_slide
from myoband.simulation.slide import Slide
from myoband.plotting import imshow
import matplotlib.pyplot as plt
import numpy as np

from myoband.analysis.analysis import contour, skeleton

from myoband.analysis.gaussian import add_noise, remove_noise

import skimage

from myoband.plotting import imshow

def test(n_bands):
    print("Running test...")

    fig, axes = plt.subplots(2,sharex=True)

    slide=Slide(30,15,0.1,0.1)

    A_bands = [A_Band(origin=[5+5*i,0],radius=0.5,length=20,σr=0.05,σθ=0.1,r0=2) for i in range(n_bands)]
    slide.add_A_bands(A_bands)
    img_original = slide.imshow_A_bands(axes[0])
    compressed_slide = get_compressed_slide(slide.slide)
    img_compressed = axes[1].imshow(compressed_slide)

    for i in range(2):
        axes[i].set_xlabel("")
        axes[i].set_ylabel("")
        axes[i].set_xticks([])
        axes[i].set_yticks([])
    
    axes[0].title.set_text("Simulated A Bands")
    axes[1].title.set_text("Compressed A bands (labelling removed)")

    print("Saving image as PDF:")
    print(FIG)
    plt.tight_layout()
    plt.savefig(FIG,dpi=DPI)
    print("Saving image as PNG:")
    print(PNG)
    plt.savefig(PNG,dpi=DPI, transparent=True)
    print("Image saved with high DPI (required to see skeleton)")
    plt.close()

    print("Compressed data saved at:")
    print(DATA)
    np.savez(DATA,data=compressed_slide)

# Plotting and data:
FILE=__file__.split(".py")[0]
PTS=FILE+"_pts"
MASK=FILE+"_mask"
FIG=FILE+".pdf"
PNG=FILE+'.png'
DATA=FILE+".npz"
DPI=800

test(n_bands=5)
