"""
Copyright, 23 March 2023, Henry Joseph Sheehy. All rights reserved.
"""

import argparse 

import numpy as np
from myoband.analysis.gaussian import remove_noise
from myoband.analysis.analysis import contour, skeleton, get_pts
import skimage
import matplotlib.pyplot as plt

from myoband.plotting import imshow

parser = argparse.ArgumentParser(
                    prog='MyoBand skeleton extraction',
                    description="""Extract the skeleton of a given array in the following way: 
'python3 get_skeleton.py -d IMPORT_DATA_LOCATION' -e EXPORT_DATA_LOCATION -s EXPORT_IMAGE_LOCATION'
If EXPORT_IMAGE_LOCATION not given, takes simulation.npz
""",
                    epilog="Hint: try 'python3 get_skeleton.py'")
parser.add_argument('-d', '--import_data_loc',required=False)
parser.add_argument('-e', '--export_data_loc',required=False)
parser.add_argument('-s', '--export_image_loc',required=False)
args = parser.parse_args()
IMPORT_DATA=args.import_data_loc
DATA=args.export_data_loc
FIG=args.export_image_loc
FILE=__file__.split(".py")[0]
FILENAME=FILE.split("/")[-1]
if FIG==None:
    FIG=FILE+".pdf"
    PNG=FILE+".png"
if IMPORT_DATA==None:
    IMPORT_DATA=FILE.split(FILENAME)[0]+"simulation.npz"
if DATA==None:
    DATA=FILE
DATA_MASK=DATA+"_mask"+".npz"
DATA_PTS=DATA+"_pts"+".npy"

def main(IMPORT_DATA):


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

    skeletons=skeleton(mask)
    skeleton_pts=get_pts(skeletons)

    print("Skeleton mask saved at:")
    print(DATA_MASK)
    np.savez(DATA_MASK,skeletons=skeletons)

    print("Skeleton points saved at:")
    print(DATA_PTS)
    np.save(DATA_PTS,skeleton_pts)

    print("Skeleton mask re-loaded:")
    npz_mask=np.load(DATA_MASK)
    print("Files contained in data directory:")
    print(npz_mask.files)
    skeletons=npz_mask["skeletons"]

    print("Skeleton pts re-loaded:")
    skeletons=np.load(DATA_PTS,allow_pickle=True).item()
    print("Files contained in skeleton_pts directory:")
    print(skeletons.keys())

    fig,ax=plt.subplots()
    ax.imshow(data)
    
    for i in range(len(skeleton_pts)):
        ax.scatter(*skeleton_pts[i])

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.title.set_text("Original A bands with skeletons superimposed")

    print("Saving image as PDF:")
    print(FIG)
    plt.tight_layout()
    plt.savefig(FIG,dpi=DPI)
    print("Saving image as PNG:")
    plt.savefig(PNG,dpi=DPI, transparent=True)
    print("Image saved with high DPI (required to see skeleton)")
    plt.close()

# Plotting and data:
DPI=800

main(IMPORT_DATA)
