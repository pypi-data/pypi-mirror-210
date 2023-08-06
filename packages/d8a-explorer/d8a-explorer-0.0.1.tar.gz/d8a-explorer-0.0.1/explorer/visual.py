#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.11                                                                             #
# Filename   : /cadx/analyzer/visual.py                                                            #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Wednesday May 24th 2023 04:11:27 pm                                                 #
# Modified   : Friday May 26th 2023 06:43:31 pm                                                    #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from dataclasses import dataclass, field
from typing import List

import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------------------------ #
#                                            PALETTE                                               #
# ------------------------------------------------------------------------------------------------ #


@dataclass
class Palette:
    blues: str = "Blues"
    blues_r: str = "Blues_r"
    dark_blue: str = "dark:b"
    dark_blue_reversed: str = "dark:b_r"
    mako: str = "mako"
    bluegreen: str = "crest"
    link: str = "https://colorhunt.co/palette/002b5b2b4865256d858fe3cf"


# ------------------------------------------------------------------------------------------------ #
#                                           COLORS                                                 #
# ------------------------------------------------------------------------------------------------ #
@dataclass
class Colors:
    blue: str = "#69d"


# ------------------------------------------------------------------------------------------------ #
#                                            CANVAS                                                #
# ------------------------------------------------------------------------------------------------ #


@dataclass
class Canvas:
    style = "whitegrid"
    figsize: tuple = (12, 3)
    nrows: int = 1
    ncols: int = 1
    color: str = None
    palette: str = Palette.blues_r
    fig: plt.figure = None
    ax: plt.axes = None
    axs: List = field(default_factory=lambda: [plt.axes])

    def __post_init__(self) -> None:
        if self.nrows > 1 or self.ncols > 1:
            figsize = []
            figsize.append(self.figsize[0] * self.ncols)
            figsize.append(self.figsize[1] * self.nrows)
            self.fig, self.axs = plt.subplots(nrows=self.nrows, ncols=self.ncols, figsize=figsize)
        else:
            self.fig, self.ax = plt.subplots(
                nrows=self.nrows, ncols=self.ncols, figsize=self.figsize
            )
