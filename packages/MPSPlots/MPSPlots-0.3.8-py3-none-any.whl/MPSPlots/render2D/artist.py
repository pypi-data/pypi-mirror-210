#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Matplotlib imports
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib import colors
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

# Other imports
import numpy
import shapely.geometry as geo
from itertools import cycle
from dataclasses import dataclass
import MPSPlots
from MPSPlots import colormaps

MPSPlots.use_ggplot_style()

linecycler = cycle(["-", "--", "-.", ":"])


@dataclass
class ColorBar:
    color: str = 'viridis'
    """ colormap for the colorbar """
    discreet: bool = False
    position: str = 'left'
    orientation: str = "vertical"
    symmetric: bool = False
    log_norm: bool = False
    numeric_format: str = '%.3f'
    n_ticks: int = None
    label_size: int = None
    show: bool = True

    def _render_(self, ax, scalar, image) -> None:
        if self.discreet:
            unique_values = numpy.unique(scalar)
            Norm = colors.BoundaryNorm(unique_values, unique_values.size + 1, extend='both')
            image.set_norm(Norm)

        elif self.log_norm and self.symmetric:
            Norm = matplotlib.colors.SymLogNorm(linthresh=1e-10)
            Norm.autoscale(scalar)
            image.set_norm(Norm)

        elif self.log_norm and not self.symmetric:
            Norm = matplotlib.colors.LogNorm()
            Norm.autoscale(scalar)
            image.set_norm(Norm)

        elif not self.log_norm and self.symmetric:
            Norm = matplotlib.colors.TwoSlopeNorm(
                vcenter=0,
                vmax=numpy.abs(scalar).max(),
                vmin=-numpy.abs(scalar).max()
            )

            image.set_norm(Norm)

        if ax.show_colorbar:
            self.construct_ax(ax=ax, image=image)

    def construct_ax(self, ax, image) -> None:
        divider = make_axes_locatable(ax._ax)

        colorbar_ax = divider.append_axes(self.position, size="10%", pad=0.15)

        cbar = plt.colorbar(
            mappable=image,
            norm=None,
            cax=colorbar_ax,
            orientation=self.orientation,
            format=self.numeric_format
        )

        if self.n_ticks is not None:
            cbar.ax.locator_params(nbins=self.n_ticks)
        if self.n_ticks is not None:
            cbar.ax.tick_params(labelsize=self.label_size)


@dataclass
class Contour:
    x: numpy.ndarray
    y: numpy.ndarray
    scalar: numpy.ndarray
    colormap: str = colormaps.blue_black_red
    iso_values: list = None
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def _render_(self, ax) -> None:
        ax.contour(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            level=self.iso_values,
            colors="black",
            linewidth=.5
        )

        ax.contourf(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            level=self.iso_values,
            cmap=self.colormap,
            norm=colors.LogNorm()
        )


@dataclass
class Mesh:
    scalar: numpy.ndarray
    """ 2 dimensional numpy array representing the mesh to be plotted """
    colormap: str = colormaps.blue_black_red
    """ Colormap to be used for the plot """
    x: numpy.ndarray = None
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    y: numpy.ndarray = None
    """ Array representing the y axis, if not defined a numpy arrange is used instead """
    show_colorbar: bool = True
    """ Boolean option to show or not the colorbar of the mesh """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(self.scalar.shape[1])

        if self.y is None:
            self.y = numpy.arange(self.scalar.shape[0])

    def _render_(self, ax):
        image = ax._ax.pcolormesh(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            cmap=self.colormap,
            shading='auto',
            zorder=1
        )

        image.set_edgecolor('face')

        if ax.colorbar is not None:
            ax.colorbar.show = ax.show_colorbar

            ax.colorbar._render_(
                ax=ax,
                scalar=self.scalar,
                image=image
            )

        return image


@dataclass
class Polygon:
    instance: object
    """ Shapely geo instance representing the polygone to be plotted """
    name: str = ''
    """ Name to be added to the plot next to the polygon """
    alpha: float = 0.4
    """ Opacity of the polygon to be plotted """
    facecolor: str = 'lightblue'
    """ Color for the interior of the polygon """
    edgecolor: str = 'black'
    """ Color for the border of the polygon """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def _render_(self, ax):

        if isinstance(self.instance, geo.MultiPolygon):
            for polygon in self.instance.geoms:
                self.add_polygon_to_ax(polygon, ax)

        else:
            self.add_polygon_to_ax(self.instance, ax)

    def add_polygon_to_ax(self, polygon, ax, add_name: str = None):
        collection = self.get_polygon_path(polygon)
        ax._ax.add_collection(collection, autolim=True)
        ax._ax.autoscale_view()

        if add_name:
            ax._ax.scatter(polygon.centroid.x, polygon.centroid.y)
            ax._ax.text(polygon.centroid.x, polygon.centroid.y, self.name)

    def get_polygon_path(self, polygon):
        exterior_coordinate = numpy.asarray(polygon.exterior.coords)

        exterior_coordinate[:, 0] *= self.x_scale_factor
        exterior_coordinate[:, 1] *= self.y_scale_factor

        path_exterior = Path(exterior_coordinate)

        path_interior = []
        for ring in polygon.interiors:
            interior_coordinate = numpy.asarray(ring.coords)
            path_interior.append(Path(interior_coordinate))

        path = Path.make_compound_path(
            path_exterior,
            *path_interior
        )

        patch = PathPatch(path)

        collection = PatchCollection(
            [patch],
            alpha=self.alpha,
            facecolor=self.facecolor,
            edgecolor=self.edgecolor
        )

        return collection


@dataclass
class FillLine:
    x: numpy.ndarray
    """ Array representing the x axis """
    y0: numpy.ndarray
    """ Array representing the inferior y axis to be filled with color """
    y1: numpy.ndarray
    """ Array representing the superior y axis to be filled with color """
    label: str = ""
    color: str = None
    """ Color for the fill """
    line_style: str = None
    """ Line style for the unique line default is next in cycle """
    line_width: float = 1
    """ Line width of the artists """
    show_outline: bool = True
    """ Show the outline of the filling """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def _render_(self, ax) -> None:
        if self.line_style is None:
            self.line_style = next(linecycler)

        ax._ax.fill_between(
            self.x * self.x_scale_factor,
            self.y0 * self.y_scale_factor,
            self.y1 * self.y_scale_factor,
            color=self.color,
            linestyle=self.line_style,
            alpha=0.7,
            label=self.label
        )

        if self.show_outline:
            ax._ax.plot(
                self.x * self.x_scale_factor,
                self.y1 * self.y_scale_factor,
                color='k',
                linestyle='-',
                linewidth=self.line_width
            )

            ax._ax.plot(
                self.x * self.x_scale_factor,
                self.y0 * self.y_scale_factor,
                color='k',
                linestyle='-',
                linewidth=self.line_width
            )


@dataclass
class STDLine:
    x: numpy.ndarray
    """ Array representing the x axis """
    y_mean: numpy.ndarray
    """ Array representing the mean value of y axis """
    y_std: numpy.ndarray
    """ Array representing the standard deviation value of y axis """
    label: str = ""
    """ Label to be added to the plot """
    color: str = None
    """ Color for the artist to be ploted """
    line_style: str = None
    """ Line style for the y_mean line default is straight lines '-' """
    line_width: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def _render_(self, ax):
        if self.line_style is None:
            self.line_style = '-'

        y0 = self.y_mean - self.y_std / 2
        y1 = self.y_mean + self.y_std / 2

        line = ax._ax.plot(
            self.x * self.x_scale_factor,
            self.y_mean * self.y_scale_factor,
            color=self.color,
            linestyle=self.line_style,
            linewidth=self.line_width
        )

        ax._ax.fill_between(
            self.x * self.x_scale_factor,
            y0 * self.y_scale_factor,
            y1 * self.y_scale_factor,
            color=line[-1].get_color(),
            linestyle='-',
            alpha=0.3,
            label=self.label
        )


@dataclass
class Line:
    y: numpy.ndarray
    """ Array representing the y axis """
    x: numpy.ndarray = None
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    label: str = None
    """ Label to be added to the plot """
    color: str = None
    """ Color for the artist to be ploted """
    line_style: str = None
    """ Line style for the unique line default is next in cycle """
    line_width: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(self.y.size)

        self.y = numpy.asarray(self.y)
        self.x = numpy.asarray(self.x)

    def _render_(self, ax):
        if self.line_style is None:
            self.line_style = next(linecycler)

        if numpy.iscomplexobj(self.y):
            ax._ax.plot(
                self.x * self.x_scale_factor,
                self.y.real * self.y_scale_factor,
                label=self.label + "[real]",
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width
            )

            ax._ax.plot(
                self.x * self.x_scale_factor,
                self.y.imag * self.y_scale_factor,
                label=self.label + "[imag]",
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width
            )

        else:
            ax._ax.plot(
                self.x * self.x_scale_factor,
                self.y * self.y_scale_factor,
                label=self.label,
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width
            )


@dataclass
class Scatter:
    y: numpy.ndarray
    """ Array representing the y axis """
    x: numpy.ndarray = None
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    label: str = None
    """ Label to be added to the plot """
    color: str = None
    """ Color for the artist to be ploted """
    marker: str = None
    """ Line style for the unique line default is next in cycle """
    marker_size: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(self.y.size)

        self.y = numpy.asarray(self.y)
        self.x = numpy.asarray(self.x)

    def _render_(self, ax):
        ax._ax.plot(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            label=self.label,
            color=self.color,
            marker=self.marker,
            markersize=self.marker_size
        )


@dataclass
class Text:
    position: tuple = (0.9, 0.9)
    font_size: int = 8
    text: str = ''
    add_box: bool = False

    def _render_(self, ax):
        art = AnchoredText(
            self.text,
            loc='lower center',
            prop=dict(size=self.font_size),
            frameon=self.add_box,
            bbox_to_anchor=self.position,
            bbox_transform=ax._ax.transAxes
        )

        ax._ax.get_figure().add_artist(art)


# -
