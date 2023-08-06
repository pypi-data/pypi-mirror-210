#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Matplotlib imports
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# Other imports
import numpy
from dataclasses import dataclass
import MPSPlots
from MPSPlots.render2D.artist import ColorBar
from MPSPlots.render2D.scene import Scene2D

MPSPlots.use_ggplot_style()


@dataclass
class Axis:
    row: int
    col: int
    x_label: str = None
    y_label: str = None
    title: str = ''
    show_grid: bool = True
    show_legend: bool = False
    x_scale: str = 'linear'
    y_scale: str = 'linear'
    x_limits: list = None
    y_limits: list = None
    equal_limits: bool = False
    equal: bool = False
    colorbar: ColorBar = None
    water_mark: str = ''
    Figure: Scene2D = None
    projection: str = None
    font_size: int = 10
    tick_size: int = 10
    show_ticks: bool = True
    show_colorbar: bool = True
    legend_font_size: bool = 12
    line_width: float = 1
    """ Line width of the contained artists. """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """

    def __post_init__(self):
        self._ax = None
        self.Artist = []

    def __add__(self, other):
        self.Artist += other.Artist
        return self

    @property
    def style(self):
        return {
            'x_label': self.x_label,
            'y_label': self.y_label,
            'title': self.title,
            'show_grid': self.show_grid,
            'show_legend': self.show_legend,
            'x_scale': self.x_scale,
            'y_scale': self.y_scale,
            'x_limits': self.x_limits,
            'y_limits': self.y_limits,
            'equal_limits': self.equal_limits,
            'equal': self.equal,
            'colorbar': self.colorbar,
            'water_mark': self.water_mark,
            'projection': self.projection,
            'font_size': self.font_size,
            'legend_font_size': self.legend_font_size,
            'tick_size': self.tick_size
        }

    def copy_style(self, other) -> None:
        assert isinstance(other, self), f"Cannot copy style from other class {other.__class__}"
        for element, value in other.style.items():
            setattr(self, element, value)

    def add_artist(self, *Artist) -> None:
        for art in Artist:
            self.Artist.append(art)

    def set_style(self, **style_dict):
        for element, value in style_dict.items():
            setattr(self, element, value)

        return self

    def _render_(self) -> None:
        for artist in self.Artist:
            artist.x_scale_factor = self.x_scale_factor
            artist.y_scale_factor = self.y_scale_factor

            artist.show_colorbar = self.show_colorbar
            artist.line_width = self.line_width

            artist._render_(self)

        if self.x_limits is not None:
            self._ax.set_xlim(self.x_limits)

        if self.y_limits is not None:
            self._ax.set_ylim(self.y_limits)

        if self.equal_limits:
            self.set_equal_limits()

        self._decorate_ax_()

    def set_equal_limits(self) -> None:
        min_limit = numpy.min([*self._ax.get_xlim(), *self._ax.get_ylim()])
        max_limit = numpy.max([*self._ax.get_xlim(), *self._ax.get_ylim()])

        self._ax.set_xlim([min_limit, max_limit])
        self._ax.set_ylim([min_limit, max_limit])

    def _decorate_ax_(self):
        if self.show_legend:
            self._ax.legend(
                fancybox=True,
                facecolor='white',
                edgecolor='k',
                fontsize=self.legend_font_size - 4
            )
            handles, labels = self._ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self._ax.legend(by_label.values(), by_label.keys())

        if self.x_label is not None:
            self._ax.set_xlabel(self.x_label, fontsize=self.font_size)

        if self.y_label is not None:
            self._ax.set_ylabel(self.y_label, fontsize=self.font_size)

        if self.title is not None:
            self._ax.set_title(self.title, fontsize=self.font_size)

        if self.x_scale is not None:
            self._ax.set_xscale(self.x_scale)

        if self.y_scale is not None:
            self._ax.set_yscale(self.y_scale)

        if self.tick_size is not None:
            self._ax.tick_params(labelsize=self.tick_size)

        if self.equal:
            self._ax.set_aspect("equal")

        if self.show_grid:
            self._ax.grid(self.show_grid)

        self._ax.axes.get_xaxis().set_visible(self.show_ticks)
        self._ax.axes.get_yaxis().set_visible(self.show_ticks)

        if self.water_mark is not None:
            self._ax.text(0.5, 0.1, self.water_mark, transform=self._ax.transAxes,
                    fontsize=30, color='white', alpha=0.2,
                    ha='center', va='baseline')


def Multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)

    for fig in figs:
        fig._mpl_figure.savefig(pp, format='pdf')

    pp.close()


# -
