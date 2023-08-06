#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Enter Project Name in Workspace Settings                                            #
# Version    : 0.1.19                                                                              #
# Python     : 3.10.10                                                                             #
# Filename   : /cadx/analyzer/univariate.py                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : Enter URL in Workspace Settings                                                     #
# ------------------------------------------------------------------------------------------------ #
# Created    : Friday May 26th 2023 06:22:28 pm                                                    #
# Modified   : Friday May 26th 2023 08:47:26 pm                                                    #
# ------------------------------------------------------------------------------------------------ #
# License    : MIT License                                                                         #
# Copyright  : (c) 2023 John James                                                                 #
# ================================================================================================ #
"""Univariate Analysis Module"""
from typing import Union

from scipy.stats import chisquare
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from cadx.analyzer.base import Analyzer, StatTestResult


# ------------------------------------------------------------------------------------------------ #
class CategoricalOne(Analyzer):
    """Univariate Analysis class for categorical variables.

    Args:
        data (pd.DataFrame): A DataFrame containing one or more categorical variables.
    """

    def describe(self, X: pd.Series) -> pd.DataFrame:
        """Returns descriptive statistics for a categorical variable.

        This method assumes nominal variables, unless indicated as ordinal.

        Args:
            X (pd.Series): The data to be described
        """
        description = X.describe()
        counts = X.value_counts()

    def test_distribution(
        self, f_obs: Union[list, np.ndarray], f_exp: Union[list, np.ndarray] = None
    ) -> StatTestResult:
        """Tests frequency distribution of a categorical variable against an expected frequency distribution.

        Args:
            f_obs (Union[list,np.ndarray]): Observed frequencies for each level of a categorical variable.
            f_exp (Union[list,np.ndarray]): Expected frequencies for each level of a categorical variable. If None,
                a uniform frequency distribution is the default.
        """
        chisq, p = chisquare(f_exp=f_exp, f_obs=f_obs)
        return StatTestResult(statistic=chisq, pvalue=p)

    def plot(self, ax: plt.Axes = None) -> plt.Axes:
        """Renders a Count Plot of Frequencies by Categorical Level

        Args:
            ax (plt.Axes): An axes object. If no object is provided, one will be provided.
        """
