import numpy as np

def get_compressed_slide(slide):
    """
    Returns self.slide with labelling information removed.
    """
    return np.sum(slide,axis=0)
