#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.10                                                                             #
# Filename   : /cadx/analyzer/base.py                                                              #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday May 26th 2023 06:14:59 pm                                                    #
# Modified   : Friday May 26th 2023 08:28:51 pm                                                    #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from cadx.analyzer.visual import Canvas

# ------------------------------------------------------------------------------------------------ #
sns.set_style(Canvas.style)
sns.set_palette = sns.dark_palette(Canvas.palette.blue, reverse=True, as_cmap=True)


# ------------------------------------------------------------------------------------------------ #
@dataclass
class StatTestResult:
    statistic: float
    pvalue: float


# ------------------------------------------------------------------------------------------------ #
class Analysis(ABC):
    """Abstract class for classes that perform analyses on entire datasets."""

    @abstractmethod
    def quality(self, *args, **kwargs) -> Any:
        """Performs a quality analysis on a dataset."""

    @abstractmethod
    def distribution(self, *args, **kwargs) -> Any:
        """Analyzes the distribution of a variable."""


# ------------------------------------------------------------------------------------------------ #
class Analyzer(ABC):
    """Abstract base class for classes that perform analyses on one, two, or multiple variables simultaneously."""

    @abstractmethod
    def describe(self, *args, **kwargs) -> pd.DataFrame:
        """Returns descriptive statistics."""

    @abstractmethod
    def test_distribution(self, *args, **kwargs) -> StatTestResult:
        """Tests distribution of frequencies or continuous random variable."""

    @abstractmethod
    def plot_distribution(self, ax: plt.Axes = None, *args, **kwargs) -> plt.Axes:
        """Returns a matplotlib axis object with the plot"""
