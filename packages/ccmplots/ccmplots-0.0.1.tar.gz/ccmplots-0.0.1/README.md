# CCMPlots



## Purpose

CCM plots includes .mplstyle files suitable for plotting scientific data. It uses the same approach as the package SciencePlots.

## Installation

```python
pip install ccmplots
```

## Usage

The package has to be imported. The style can be selected. The base style is called "ccm". 

```python
import ccmplots

plt.style.use("ccm")

x = np.linspace(0,10,100)
y = np.sin(x)

plt.plot(x,y)
plt.xlabel("my xlabel")
plt.ylabel("my ylabel")
plt.title("my title")
# save figure
filepath = Path(__file__).parent.resolve()
plt.savefig(filepath/"simple.png")
```

The code above produces the following figure which has the default aspect ratio of 6/5
![alt text](examples/simple.png "Simple figure"){width=75%}


The base style "ccm" can be combined with other styles such as "square" or "sans".


The examples folder contains the python code to create the following figure:

![alt text](examples/plot_3square.png "Panel with 3 diagrams"){width=75%}
