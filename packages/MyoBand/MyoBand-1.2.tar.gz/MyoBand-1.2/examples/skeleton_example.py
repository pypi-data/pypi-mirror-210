"""
Copyright, 23 March 2023, Henry Joseph Sheehy. All rights reserved.
"""

import numpy as np

from myoband.simulation.a_band import A_Band
from myoband.simulation.slide import Slide

from myoband.analysis.gaussian import add_noise, remove_noise
from myoband.analysis.analysis import contour, skeleton, get_pts

import matplotlib.pyplot as plt
from myoband.plotting import imshow

def main(n_bands):
    print("Running simulation...")

    fig, axes = plt.subplots(4,2,sharex=True,sharey=True)

    slide=Slide(30,15,0.1,0.1)

    A_bands = [A_Band(origin=[5+5*i,0],radius=0.5,length=20,σr=0.05,σθ=0.1,r0=2) for i in range(n_bands)]
    slide.add_A_bands(A_bands)
    img_original = slide.imshow_A_bands(axes[0,0])

    skeleton_original=skeleton(slide.slide)
    img_skeleton_original = imshow(axes[0,1],skeleton_original)

    noisy_slide=add_noise(slide.slide)
    img_noisy = imshow(axes[1,0],noisy_slide)

    skeleton_noisy=skeleton(noisy_slide)
    img_skeleton_noisy = imshow(axes[1,1],skeleton_noisy)
    
    clean_slide=remove_noise(noisy_slide,sigma=[.2,.2])
    img_clean = imshow(axes[2,0],clean_slide)

    skeleton_clean=skeleton(clean_slide)
    img_skeleton_clean = imshow(axes[2,1],skeleton_clean)

    double_gaussian=remove_noise(clean_slide,sigma=[.2,.2])
    img_double = imshow(axes[3,0],double_gaussian)

    double_skeleton=skeleton(double_gaussian)
    img_skeleton_double = imshow(axes[3,1],double_skeleton)

    # Remove ticks and axis labels:
    for i in range(3):
        for j in range(2):
            axes[i,j].set_xlabel("")
            axes[i,j].set_ylabel("")
            axes[i,j].set_xticks([])
            axes[i,j].set_yticks([])
    
    axes[0,0].title.set_text("A Bands")
    axes[0,1].title.set_text("Extracted skeleton")
    axes[0,0].set_xlabel("(1a) Simulated image")
    axes[1,0].set_xlabel("(2a) Added Gaussian noise")
    axes[2,0].set_xlabel("(3a) Gaussian convolution")
    axes[3,0].set_xlabel("(4a) Gaussian convolution\nreapplied")

    axes[0,1].set_xlabel("(1b) Missing length")
    axes[1,1].set_xlabel("(2b) Fails in presence\nof large noise")
    axes[2,1].set_xlabel("(3b) Loop bug in presence\nof small noise")
    axes[3,1].set_xlabel("(4b) Success")
    
    print("Saving image as PDF:")
    print(FIG)
    plt.tight_layout()
    plt.savefig(FIG,dpi=DPI)
    print("Saving image as PNG:")
    plt.savefig(PNG,dpi=DPI, transparent=True)
    print("Image saved with high DPI (required to see skeleton)")
    plt.close()

    # double_skeleton_points=[np.nonzero(double_skeleton[i]) for i in range(len(double_skeleton))]
    # print((double_skeleton_points[0]))
    double_skeleton_pts=get_pts(double_skeleton)
    
    print("Skeleton mask and points saved at:")
    print(DATA)
    np.savez(DATA,double_skeleton=double_skeleton,double_skeleton_pts=double_skeleton_pts)

    print("Skeleton mask re-loaded:")
    npz_mask=np.load(DATA)
    print("Files contained in DATA directory:")
    print(npz_mask.files)
    double_skeleton=npz_mask["double_skeleton"]
    double_skeleton=np.load(DATA)["double_skeleton"]

    fig,ax=plt.subplots()
    imshow(ax,double_skeleton)
    ax.set_xlabel("Arbitrary length scale")
    ax.set_ylabel("Arbitrary length scale")
    print("Saving image as PDF:")
    print(FIG_MASK)
    # plt.tight_layout()
    plt.savefig(FIG_MASK,dpi=DPI)
    print("Saving image as PNG:")
    plt.savefig(PNG_MASK,dpi=DPI, transparent=True)
    print("Image saved with high DPI (required to see skeleton)")
    plt.close()

    fig,ax=plt.subplots()
    for i in range(len(double_skeleton_pts)):
        ax.scatter(*double_skeleton_pts[i])
    ax.set_xlabel("Arbitrary length scale")
    ax.set_ylabel("Arbitrary length scale")

    print("Saving image as PDF:")
    print(FIG_PTS)
    plt.tight_layout()
    plt.savefig(FIG_PTS,dpi=DPI)
    print("Saving image as PNG:")
    plt.savefig(PNG_PTS,dpi=DPI, transparent=True)
    print("Image saved with high DPI (required to see skeleton)")
    plt.close()

# Plotting and data:
FILE=__file__.split(".py")[0]
PTS=FILE+"_pts"
MASK=FILE+"_mask"
FIG=FILE+".pdf"
FIG_PTS=PTS+".pdf"
FIG_MASK=MASK+".pdf"
PNG=FILE+".png"
PNG_PTS=PTS+".png"
PNG_MASK=MASK+".png"
DATA=FILE+".npz"
DPI=800

main(n_bands=5)
