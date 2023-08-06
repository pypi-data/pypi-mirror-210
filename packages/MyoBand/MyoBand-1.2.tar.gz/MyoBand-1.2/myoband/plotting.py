import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter
import matplotlib as mpl
## Better cmaps
from mycolorpy import colorlist as mcp

def imshow(ax,slide):
    """
    Class for plotting
    """
    N=len(slide)
    colours=mcp.gen_color(cmap="Set1",n=N)
    background='black'

    cmaps = [mpl.colors.LinearSegmentedColormap.from_list('cmap',[background,colours[i]],256) for i in range(N)]

    for i in range(1,N):
        cmaps[i]._init()

        alphas = np.linspace(0, 0.8, cmaps[i].N+3)
        cmaps[i]._lut[:,-1] = alphas
    
    img=[]
    for i in range(N):
        img.append(ax.imshow(slide[i], interpolation='nearest', cmap=cmaps[i]))
    plt.gca().invert_yaxis()

    return img
        
