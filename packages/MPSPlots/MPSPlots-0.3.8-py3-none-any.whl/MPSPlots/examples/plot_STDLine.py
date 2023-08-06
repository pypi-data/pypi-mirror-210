"""
STD line
========
"""

import numpy
from MPSPlots.Render2D import Scene2D, Axis, STDLine


x = numpy.arange(100)
y = numpy.random.rand(10, 100)
y_mean = numpy.mean(y, axis=0)
y_std = numpy.std(y, axis=0)

figure = Scene2D(
    unit_size=(8, 4), 
    title='random data simple lines'
)

ax = Axis(
    row=0, 
    col=0, 
    x_label='x data', 
    y_label='y data', 
    show_legend=True
)

figure.add_axes(ax)

artist_0 = STDLine(
    x=x, 
    y_mean=y_mean, 
    y_std=y_std, 
    label='Fill between lines',
)

ax.add_artist(artist_0)

figure.show()
