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

#
# Read datasets into Pandas DataFrames. The main dataset is the one from the
# NCHS with the 10 leading causes of death in the United States. The 
# states1999 and states2011 contain population data for each state plus the
# total for the United States. In order to have the option to create a 
# choropleth map of the United States, an abbreviation dataset was created.
#
causes_df = pd.read_csv('../data/NCHS_-_Leading_Causes_of_Death__United_States.csv')
states2000_df = pd.read_csv('../data/states2000-2010.csv')
states2010_df = pd.read_csv('../data/states2011-2019.csv')
abbrev_df = pd.read_csv('../data/stateAbb.csv')

# Take a quick look at each data set
print(causes_df.head())
print(states2000_df.head())
print(states2010_df.head())
print(abbrev_df.head())

#
# The column names in the causes_df DataFrame are not in a user friendly
# format.  I will name them.
#
causes_df.rename({'Year':'year', '113 Cause Name': '113_cause_name',
                 'Cause Name':'cause_name', 'State': 'state', 'Deaths':'deaths',
                 'Age-adjusted Death Rate':'age_adjusted'}, axis=1, inplace=True)
causes_df.columns

#
# Combine all DataFrames into one
#

# Concatenate states1999_df and states2011_df
states = pd.concat([states2000_df, states2010_df], ignore_index=True)

# Merge DataFrames and add abbreviations
all_df = pd.merge(causes_df, states, on=['year', 'state'], how='inner')
all_df = all_df.merge(abbrev_df, on='state', how='left')

#
# Check that all_df data frame is sane enough to use
#
print(all_df.info())
print('\\nNaN Values:\\n', all_df.isna().sum())
print('\\nDuplicates: ', all_df.duplicated().sum())
print('\\nSize: ', all_df.size)
print('\\nDistribution:\\n', all_df.describe().T)

# One last look
print(all_df.head())

#
# The 113_cause_name column is just a more complicated copy of the 
# cause_name one.  I will drop it.
#
all_df.drop('113_cause_name', axis=1, inplace=True)

#
# Calculate the crude death rate per 100,000 for each state
#
all_df['crude_deaths'] = round((all_df['deaths'] / all_df['population']) * 100000)

#
# Some of the cause_name records are not that clear or hard to read.
# I will rename them
#
all_df.cause_name = all_df.cause_name.apply(lambda x: 'Accidents'
                                            if x == 'Unintentional injuries'
                                            else x)

all_df.cause_name = all_df.cause_name.apply(lambda x: 'Respiratory disease'
                                            if x == 'CLRD' else x)

#
# Look at some groupings
#

# filter on all causes and break into crude death and age adjusted rates
all = all_df[(all_df.cause_name == 'All causes') & \
             (all_df.state != 'United States')]
crude = all.groupby(['year', 'state', 'cause_name']).agg({'crude_deaths': 'max'}). \
            reset_index()
age = all.groupby(['year', 'state', 'cause_name']).agg({'age_adjusted': 'max'}). \
          reset_index()

# plot crude and age adjusted death rates
fig, ax = plt.subplots(figsize=(10, 6))
ax.set(xlabel='Year', ylabel='Death Rate per 100,000',
       title='United States All Causes of Death from 2000 to 2017')
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
text1 = '\n'.join(('As illustrated in this graphic,',
                   'the values between Age Adjusted and Crude Death',
                   'rates are different. When comparing populations',
                   'in different locations, the Age Adjusted Rate',
                   'is preferred.'))
ax.xaxis.set_ticks(np.arange(2000, 2018, 1))
p = sns.lineplot(data=crude, x='year', y='crude_deaths', ci=None, label='Crude')
p = sns.lineplot(data=age, x='year', y='age_adjusted', ci=None, label='Age Adjusted')
ax.text(0.55, 0.4, text1, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', bbox=props)
ax.get_legend().remove()
labelLines(plt.gca().get_lines())
fig.savefig('../images/compareCDR-AADR.png', bbox_inches='tight', dpi=300)

#
# Plot the 10 leading causes of death in the United States
#

# filter data
not_all = all_df[(all_df.cause_name != 'All causes') & \
                 (all_df.state == 'United States')] 
p_usa = not_all.groupby('cause_name').agg({'age_adjusted':'max'}). \
                sort_values('age_adjusted', ascending=False).reset_index()

# Create bar plot
fig, ax = plt.subplots(figsize=(10,6))
cols = ['grey' if (x < max(p_usa.age_adjusted)) else 'steelblue' \
               for x in p_usa.age_adjusted]
sns.barplot(data=p_usa, y='cause_name', x='age_adjusted', ci=None, palette=cols)
ax.set(xlabel='Age Adjusted Death Rate per 100,000', ylabel='Cause of Death',
       title='Leading Causes of Death in United States (2000-2017)')
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
text1 = '\n'.join(('Heart disease is the leading cause',
                   'of death in the United States from',
                   '2000 to 2017.'))
ax.annotate(text1, xy=(210,0.3), xytext=(178,3), bbox=props,
            fontsize=10, arrowprops=dict(facecolor='black', shrink=0.05))
fig.savefig('../images/allLeadingCauses.png', bbox_inches='tight', dpi=300)

#
# Create a line plot to show how time relates to the death rates
#

# Create filters
usa = all_df[all_df.state == 'United States']
causes = ['Heart disease', 'Cancer', 'Stroke', 'Accidents', 'Respiratory disease',
          'Alzheimer\'s disease', 'Diabetes', 'Influenza and pneumonia',
          'Kidney disease', 'Suicide']

# Configure plot
fig, ax = plt.subplots(figsize=(15,15))
ax.set(xlabel='Year', ylabel='Crude Death Rate per 100,000',
       title='United States Leading Causes of Death (2000-2017)')
ax.xaxis.set_ticks(np.arange(2000, 2018, 1))
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
text1 = '\n'.join(('Heart disease and cancer have remained the two',
                   'leading causes of death in the U.S. from',
                   '2000 to 2017'))

# Loop through the causes and create group to be plotted
for cause in causes:
    name = usa[usa.cause_name == cause].groupby('year').agg({'crude_deaths': 'max'}). \
           reset_index()
    p = sns.lineplot(data=name, x='year', y='crude_deaths', ci=None, label=cause)
ax.text(0.04, 0.8, text1, transform=ax.transAxes, fontsize=13,
        verticalalignment='top', bbox=props)
ax.get_legend().remove()
labelLines(ax.get_lines())
fig.savefig('../images/usLeadingCauseLine.png', bbox_inches='tight', dpi=300)

#
# Plot top ten states with highest death rates
#

# filter information to heart disease and top 10 states
states = all_df[(all_df.cause_name == 'All causes') & \
                 (all_df.state != 'United States')]
plot = states.groupby('state').agg({'age_adjusted':'mean'}). \
              sort_values('age_adjusted', ascending=False).head(10).reset_index()

# Plot results
fig, ax = plt.subplots(figsize=(10,6))
ax.set(xlabel='Age Adjusted Death Rate per 100,000', ylabel='State',
       title='U.S. States with Highest Death Rates - All Causes (2000-2017)')
sns.barplot(data=plot, y='state', x='age_adjusted', ci=None)
fig.savefig('../images/statesMaxDeath.png', bbox_inches='tight', dpi=300)

#
# Create some groupings and lists to be used in the rest of the plots
#
top10States = states.groupby('state').agg({'age_adjusted':'mean'}). \
              sort_values('age_adjusted', ascending=False).head(10).reset_index()
p_states = top10States.state.head(10).tolist()
top5 = p_states[:5]
bottom5 = p_states[:-5]

#
# Plot the top 5 states death rates as a time series
#

# Create filters
all_causes = all_df[all_df.cause_name == 'All causes']

# Plot chart
fig, ax = plt.subplots(figsize=(15,15))
ax.set(xlabel='Year', ylabel='Age Adjusted Death Rate per 100,000',
       title='Top Five States with the Highest Death Rates - All causes (2000 - 2017)')
ax.xaxis.set_ticks(np.arange(2000, 2018, 1))
text1 = '\n'.join(('All of the states with high death rates',
                   'show that rates are dropping with the',
                   'District of Columbia having the most',
                   'improvement.'))
# looping saves a lot of time
for state in top5:
    name = all_causes[all_causes.state == state].groupby('year'). \
           agg({'age_adjusted': 'mean'}).reset_index()
    p = sns.lineplot(data=name, x='year', y='age_adjusted', ci=None, label=state)
ax.text(0.2, 0.3, text1, transform=ax.transAxes, fontsize=15,
        verticalalignment='top', bbox=props)
ax.get_legend().remove()
labelLines(ax.get_lines())
fig.savefig('../images/top5DeathRateLine.png', bbox_inches='tight', dpi=300)

#
# Plot the next 5 top death rate states
#
all_causes = all_df[all_df.cause_name == 'All causes']
fig, ax = plt.subplots(figsize=(10,6))
ax.set(xlabel='Year', ylabel='Age Adjusted Death Rate per 100,000',
       title='Next Five States with the Highest Death Rates - '\
              'All Causes (2000-2017)')
ax.xaxis.set_ticks(np.arange(2000, 2018, 1))
text1 = '\n'.join(('The next top 5 states with high death rates',
                   'show that rates are dropping with the',
                   'District of Columbia showing the most improvement.'))

# Loop through top 5 states
for state in bottom5:
    name = all_causes[all_causes.state == state].groupby('year'). \
           agg({'age_adjusted': 'mean'}).reset_index()
    p = sns.lineplot(data=name, x='year', y='age_adjusted', ci=None, label=state)
ax.text(0.4, 0.9, text1, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)
ax.get_legend().remove()
labelLines(ax.get_lines())
fig.savefig('../images/next5DeathRateLine.png', bbox_inches='tight', dpi=300)

#
# Plot the top 10 states death rates and causes as a time series
#

# Create lists
causes = ['Heart disease', 'Cancer', 'Stroke', 'Accidents', 'Respiratory disease',
          'Alzheimer\'s disease', 'Diabetes', 'Influenza and pneumonia',
          'Kidney disease', 'Suicide']
states = ['Mississippi', 'Oklahoma', 'District of Columbia', 'West Virginia',
          'Kentucky', 'Alabama', 'New York', 'Tennessee', 'Louisiana', 'Missouri']

# Create plots
for state in p_states:
    fig, ax = plt.subplots(figsize=(10, 6))
    for cause in causes:
        name = all_df[(all_df.state == state) & (all_df.cause_name ==cause)]. \
               groupby('year').agg({'crude_deaths': 'mean'}).reset_index()
        p = sns.lineplot(data=name, x='year', y='crude_deaths', ci=None,
                         label=cause)
        ax.xaxis.set_ticks(np.arange(2000, 2018, 1))
        ax.set(xlabel='Year', ylabel='Crude Death Rates per 100,000',
               title=state+': Leading Causes of Death (2000-2017)')
        ax.get_legend().remove()
    labelLines(ax.get_lines())
    fig.savefig('../images/'+state+'CausesLine.png', bbox_inches='tight', dpi=300)

#
# Create a choropleth of the Age-Adjusted death rates
#

# Filter data
all_causes = all_df[(all_df.cause_name == 'All causes') & \
                    (all_df.state != 'United States')]
plot = all_causes.groupby('abbreviation').agg({'age_adjusted':'mean'}).reset_index()

# Create plot
fig = px.choropleth(plot, locations='abbreviation', locationmode='USA-states',
                    color='age_adjusted', scope='usa',
                    title='United States Age Adjusted Death Rates (2000-2017)',
                    hover_data='age_adjusted')
fig.update_layout(hoverlabel=dict(bgcolor='wheat', font_size=15))
fig.write_html('../images/mapUSA.html')
fig.write_image('../images/mapUSA.png')