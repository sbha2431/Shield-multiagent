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
ncols = 4
nagents = 2
initial = [12,15]
targets = [[0],[3]]
# obstacles = [153,154,155,173,174,175,193,194,195,213,214,215,233,234,235,68,69,88,89,108,109,128,129,183,184,185,186,187,203,204,205,206,207,223,224,225,226,227]
obstacles = []
moveobstacles = []
slugs = '/home/sudab/Applications/slugs/src/slugs'


regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()

# for n in range(nagents):
#     outfile = 'test{}'.format(n)
#     infile = 'test{}'.format(n)
#     print 'output file: ', outfile
#     print 'input file name:', infile
#
#     print 'Writing input file...'
#     Salty_input.write_to_slugs_resilient(infile,gwg,initial[n],targets[n],4,4)
infile = 'shieldtest'
outfile = 'shieldtest'
Salty_input.write_to_slugs_central_shield(infile,gwg,initial,[2,2],[0,0])
print 'Converting input file...'
os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
print('Computing controller...')
# sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
sp = subprocess.Popen(slugs + ' --extractExplicitPermissiveStrategy ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# #     # sp = subprocess.Popen(slugs + ' --analyzeInitialPositions ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# #     # # sp = subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + outfile,shell=True, stdout=subprocess.PIPE)
sp.wait()
# simulateController.centralizedShield(outfile,gwg)