"""
Multi ax
========
"""

import numpy
from MPSPlots.Render2D import Scene2D, Axis, FillLine


x = numpy.arange(100)
y0 = numpy.random.rand(100) + x
y1 = numpy.random.rand(100) - x

figure = Scene2D(
    unit_size=(8, 4), 
    title='random data simple lines'
)

ax0 = Axis(
    row=0, 
    col=0, 
    x_label='x data', 
    y_label='y data', 
    show_legend=True
)

ax1 = Axis(
    row=0, 
    col=1, 
    x_label='x data', 
    y_label='y data', 
    show_legend=True
)

figure.add_axes(ax0, ax1)

artist = FillLine(
    x=x, 
    y0=y0, 
    y1=y1, 
    label='Fill between lines',
    show_outline=True
)

ax0.add_artist(artist)

ax1.add_artist(artist)

figure.show()
