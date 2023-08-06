#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Matplotlib imports
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# Other imports
import numpy
from dataclasses import dataclass
import MPSPlots

MPSPlots.use_ggplot_style()


@dataclass
class Scene2D:
    unit_size: tuple = (10, 3)
    tight_layout: bool = True
    transparent_background: bool = False
    title: str = ""

    def __post_init__(self):
        self.axis_generated = False
        self._axis = []
        self.nCols = None
        self.nRows = None

    def set_axis_row(self, value) -> None:
        for ax in self._axis:
            ax.row = value

    def set_axis_col(self, value) -> None:
        for ax in self._axis:
            ax.col = value

    def set_style(self, **style_dict):
        for ax in self:
            ax.set_style(**style_dict)

        return self

    @property
    def axis_matrix(self):
        ax_matrix = numpy.full(shape=(self.max_row + 1, self.max_col + 1), fill_value=None)
        for ax in self._axis:
            ax_matrix[ax.row, ax.col] = ax

        return ax_matrix

    @property
    def max_row(self) -> int:
        max_row = 0
        for ax in self._axis:
            max_row = ax.row if ax.row > max_row else max_row

        return max_row

    @property
    def max_col(self) -> int:
        max_col = 0
        for ax in self._axis:
            max_col = ax.col if ax.col > max_col else max_col

        return max_col

    def __getitem__(self, idx: int):
        return self._axis[idx]

    def __setitem__(self, idx: int, value) -> None:
        assert isinstance(value, Axis), f"Cannot assign type: {value.__class__} to Scene2D axis"
        self._axis[idx] = value

    def __add__(self, other):
        assert isinstance(other, Scene2D), f"Cannot add two different classes {self.__class__} and {other.__class__}"
        for ax in other._axis:
            self.append_axis(ax)

        return self

    def append_axis(self, ax):
        ax.row = self.max_row + 1 if self.max_row != 0 else 0
        ax.col = self.max_col + 1 if self.max_col != 0 else 0
        self._axis.append(ax)

    def ax_inherit(function):
        def wrapper(self, value):
            for ax in self:
                setattr(ax, function.__name__, value)

        return wrapper

    @ax_inherit
    def x_scale_factor(self, value: int):
        pass

    @ax_inherit
    def y_scale_factor(self, value: int):
        pass

    @ax_inherit
    def font_size(self, value: int):
        pass

    @ax_inherit
    def line_width(self, value: int):
        pass

    @ax_inherit
    def legend_font_size(self, value: int):
        pass

    @ax_inherit
    def tick_size(self, value: int):
        pass

    @ax_inherit
    def x_limits(self, value: list):
        pass

    @ax_inherit
    def y_limits(self, value: list):
        pass

    @ax_inherit
    def x_label(self, value: list):
        pass

    @ax_inherit
    def y_label(self, value: list):
        pass

    @ax_inherit
    def water_mark(self, value: str):
        pass

    @ax_inherit
    def equal(self, value: bool):
        pass

    @ax_inherit
    def equal_limits(self, value: bool):
        pass

    @ax_inherit
    def show_legend(self, value: bool):
        pass

    @ax_inherit
    def show_grid(self, value: bool):
        pass

    @ax_inherit
    def show_ticks(self, value: bool):
        pass

    @ax_inherit
    def show_colorbar(self, value: int):
        pass

    def colorbar_n_ticks(self, value: int):
        for ax in self:
            ax.colorbar.n_ticks = value

    def colorbar_label_size(self, value: int):
        for ax in self:
            ax.colorbar.label_size = value

    font_size = property(None, font_size)
    line_width = property(None, line_width)
    legend_font_size = property(None, legend_font_size)
    tick_size = property(None, tick_size)
    x_limits = property(None, x_limits)
    y_limits = property(None, y_limits)
    x_scale_factor = property(None, x_scale_factor)
    y_scale_factor = property(None, y_scale_factor)
    x_label = property(None, x_label)
    y_label = property(None, y_label)
    water_mark = property(None, water_mark)
    equal = property(None, equal)
    equal_limits = property(None, equal_limits)
    show_legend = property(None, show_legend)
    show_grid = property(None, show_grid)
    show_ticks = property(None, show_ticks)
    show_colorbar = property(None, show_colorbar)
    colorbar_n_ticks = property(None, colorbar_n_ticks)
    colorbar_label_size = property(None, colorbar_label_size)

    def add_axes(self, *axis):
        for ax in axis:
            self._axis.append(ax)

        return self

    def _generate_axis_(self):
        figure_size = [
            self.unit_size[0] * (self.max_col + 1),
            self.unit_size[1] * (self.max_row + 1)
        ]

        self._mpl_figure = plt.figure(figsize=figure_size)
        self._mpl_figure.suptitle(self.title)

        grid = gridspec.GridSpec(
            ncols=self.max_col + 1,
            nrows=self.max_row + 1,
            figure=self._mpl_figure
        )

        ax_matrix = numpy.full(
            shape=(self.max_row + 1, self.max_col + 1),
            fill_value=None
        )

        for axis in self._axis:
            subplot = self._mpl_figure.add_subplot(grid[axis.row, axis.col], projection=axis.projection)
            ax_matrix[axis.row, axis.col] = subplot
            axis._ax = subplot

        self.axis_generated = True

        return self

    def auto_arrange_axis(self, type='row') -> None:
        if type == 'row':
            for n, ax in enumerate(self._axis):
                ax.row = n
                ax.col = 0
        else:
            for n, ax in enumerate(self._axis):
                ax.row = 0
                ax.col = n

    def _render_(self):
        if not self.axis_generated:
            self._generate_axis_()

        for ax in self._axis:
            ax._render_()

        if self.tight_layout:
            plt.tight_layout()

        return self

    def close(self) -> None:
        plt.close(self._mpl_figure)

    def save_figure(self, save_directory: str, **kwargs):
        plt.savefig(
            fname=save_directory,
            transparent=self.transparent_background,
            **kwargs
        )

    def show(self, save_directory: str = None, **kwargs):
        self._render_()
        if save_directory is not None:
            self.save_figure(save_directory=save_directory, **kwargs)

        plt.show()

        return self


def Multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)

    for fig in figs:
        fig._mpl_figure.savefig(pp, format='pdf')

    pp.close()


# -
