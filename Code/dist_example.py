__author__ = 'sudab'

from gridworld import *
import grid_partition
import Slugs_input
import Salty_input
import random
import os
import subprocess
import visibility
import simplejson as json
import time
import simulateController
# Define gridworld parameters
nrows = 4
ncols = 5
nagents = 2
initial = [15,19]
targets = [[9,10,5,14],[5,9,10,14]]
# obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
obstacles = []
moveobstacles =  []
slugs = '/home/sudab/Applications/slugs/src/slugs'


