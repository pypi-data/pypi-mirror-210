from myoband.simulation.a_band import A_Band
import matplotlib.pyplot as plt

print("Running test...")

p = A_Band(origin=[0,0],radius=0.5,length=20,σr=0.05,σθ=0.1,r0=2)
fig,ax=plt.subplots()
p.plot_A_band(ax)
plt.show()

print("Test passed.")
