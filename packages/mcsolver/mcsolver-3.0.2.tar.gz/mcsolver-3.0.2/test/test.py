import matplotlib.pyplot as plt
import numpy as np

x=np.linspace(-np.pi,np.pi,100)
y1=np.sin(x)
y2=10*np.cos(x)

fig, ax = plt.subplots(2,1,figsize=(8,6),sharex=True) # define two subplots
fig.subplots_adjust(hspace=0) # adjacent two subplots
ax[0].scatter(x,y1,color='blue') # add data to the first axis
ax[0].set_ylabel('y1')           # set ylabel for 1st axis
ax[1].scatter(x,y2,color='red')  
ax[1].set_xlabel('x')
ax[1].set_ylabel('y2')
ax[1].set_xticks([])             # anihilate numbers on horizontal axis
ax[1].set_xlim(-np.pi,np.pi)     # set axis range

plt.show()                       # save, show etc should done by plt obj.
