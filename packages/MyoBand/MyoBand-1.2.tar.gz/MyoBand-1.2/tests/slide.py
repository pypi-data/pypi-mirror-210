from myoband.simulation.a_band import A_Band
from myoband.simulation.slide import Slide
from myoband.plotting import imshow
import matplotlib.pyplot as plt

def test(n_bands):
    print("Running test...")

    fig, ax = plt.subplots()

    slide=Slide(30,15,0.1,0.1)

    A_bands = [A_Band(origin=[5+5*i,0],radius=0.5,length=20,σr=0.05,σθ=0.1,r0=2) for i in range(n_bands)]
    slide.add_A_bands(A_bands)
    img_original = slide.imshow_A_bands(ax)

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])
    
    ax.title.set_text("Simulated A Bands")

    plt.show()

    print("Test passed.")

n_bands=5
test(n_bands)
