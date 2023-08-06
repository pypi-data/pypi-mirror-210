"""
Mesh
====
"""

import numpy
from MPSPlots.Render2D import Scene2D, Axis, Mesh


x = numpy.arange(100)
y = numpy.arange(100)
scalar = numpy.random.rand(100, 100)

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

artist = Mesh(
    scalar=scalar, 
    x=x, 
    y=y,
    show_colorbar=True
)

ax.add_artist(artist)


figure.show()
