#!/usr/bin/env python
#####################################################################
#
# Author: Wiley Winters (wwinters@regis.edu)
# 
# Title: MSDS 670 Final Project 
#
# Class: MSDS 670 - Data Visualization
#
# Instructor: John Koenig
#
# Date: 2024-MAR-10
#
#####################################################################

#
# Load required libraries and packages
#
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib import rcParams
from labellines import labelLine, labelLines
import numpy as np

# plotly
from plotly.offline import init_notebook_mode, iplot, plot
import plotly as py
import plotly.express as px
init_notebook_mode(connected=True)

# Suppress Warnings
import warnings
warnings.filterwarnings('ignore')

# Set seaborn autoconfig to True
rcParams.update({'figure.autolayout': True})

