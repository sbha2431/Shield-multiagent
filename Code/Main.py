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


regionkeys = {'pavement','gravel','grass','sand','deterministic'}
regions = dict.fromkeys(regionkeys,{-1})
regions['deterministic']= range(nrows*ncols)

gwg = Gridworld(initial, nrows, ncols,nagents, targets, obstacles, moveobstacles,regions)
gwg.colorstates = [set(),set()]
gwg.render()

gwg.draw_state_labels()
infile = 'LocalController_{}x{}'.format(gwg.nrows,gwg.ncols)
outfile = 'LocalController_{}x{}.json'.format(gwg.nrows,gwg.ncols)
# Salty_input.write_to_slugs_fullyCentralized(infile,gwg,initial,targets)
# os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
# print('Computing controller...')
# sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# sp.wait()
# for n in range(nagents):
#     outfile = 'LocalController{}x{}_{}.json'.format(gwg.nrows,gwg.ncols,n)
#     infile = 'LocalController{}x{}_{}'.format(gwg.nrows,gwg.ncols,n)
#     print 'output file: ', outfile
#     print 'input file name:', infile
#
#     print 'Writing input file...'
#     Salty_input.write_to_slugs_resilient(infile,gwg,initial[n],targets[n],7,7)
#     print 'Converting input file...'
#     os.system('python compiler.py ' + infile + '.structuredslugs > ' + infile + '.slugsin')
#     print('Computing controller...')
#     sp = subprocess.Popen(slugs + ' --explicitStrategy --jsonOutput ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
#     sp.wait()
#
# infile = 'shieldtest_4x4_2'
# outfile = 'shieldtest_4x4_2.json'
# Salty_input.write_to_slugs_central_shield2(infile,gwg,initial,[7,7],[7,7])
# print 'Converting input file...'

# sp.wait()
local_filenames = ['LocalController4x5_0.json','LocalController4x5_1.json']
shield_filename = 'shieldtest_4x4_2.json'
simulateController.centralizedShield_Local(local_filenames,shield_filename,gwg)
# simulateController.centralizedShield(outfile,gwg)

# simulateController.centralizedPermissiveShield(outfile,gwg)
# sp = subprocess.Popen(slugs + ' --extractExplicitPermissiveStrategy ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# #     # sp = subprocess.Popen(slugs + ' --analyzeInitialPositions ' + infile + '.slugsin > '+ outfile,shell=True, stdout=subprocess.PIPE)
# #     # # sp = subprocess.Popen(slugs + ' --counterStrategy ' + infile+'.slugsin > ' + outfile,shell=True, stdout=subprocess.PIPE)