__author__ = 'sudab'
import random
import simplejson as json
import time
import copy
import visibility
import grid_partition
import itertools
import numpy as np

def parsePermissiveStrategy(filename):
    automaton = dict()
    file = open(filename)
    varflag = 0
    transflag = 0
    for line in file:
        l = line.split()
        if len(l) > 0:
            if l[0] == 'State':
                transflag = 0
                automaton_state = int(l[1])
                automaton[automaton_state] = dict.fromkeys(['State','Successors'])
                automaton[automaton_state]['State'] = dict()
                automaton[automaton_state]['Successors'] = []
                varflag = 1
            elif varflag == 1:
                for var in l:
                    v = var[0:var.index('@')]
                    if v not in automaton[automaton_state]['State'].keys():
                        automaton[automaton_state]['State'][v] = []
                        automaton[automaton_state]['State'][v].append(int(var[var.index(':')+1]))
                    else:
                        automaton[automaton_state]['State'][v].append(int(var[var.index(':')+1]))
                varflag = 0
                transflag = 1
                for var in automaton[automaton_state]['State'].keys():
                    automaton[automaton_state]['State'][var] = int(''.join(str(e) for e in automaton[automaton_state]['State'][var])[::-1], 2)
            elif transflag == 1:
                automaton[automaton_state]['Successors'].append(int(l[0]))
    return automaton


def parseJson(filename):
    automaton = dict()
    file = open(filename)
    data = json.load(file)
    file.close()
    variables = dict()
    for var in data['variables']:
        if '@' in var:
            v = var[0:var.index('@')]
            Flag = True
        else:
            v = copy.deepcopy(var)
            Flag = False
        if v not in variables.keys():
            if Flag:
                variables[v] = [data['variables'].index(var), max(loc for loc, val in enumerate(data['variables']) if val[0:val.index('@')] == v)+1]
            else:
                variables[v] = [data['variables'].index(var), data['variables'].index(var)+1]

    for s in data['nodes'].keys():
        automaton[int(s)] = dict.fromkeys(['State','Successors'])
        automaton[int(s)]['State'] = dict()
        automaton[int(s)]['Successors'] = []
        for v in variables.keys():
            bin = data['nodes'][s]['state'][variables[v][0]:variables[v][1]]
            automaton[int(s)]['State'][v] = int(''.join(str(e) for e in bin)[::-1], 2)
            automaton[int(s)]['Successors'] = data['nodes'][s]['trans']
    return automaton


def computeInitialState(automaton,initial):
    for state in automaton.keys():
        check = 0
        for var in initial.keys():
            if automaton[state]['State'][var] == initial[var]:
                check+=1
            else:
                break
        if check == len(initial.keys()):
            break
    return state



def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

def coord2state(gwg,coords):
    s = coords[1] * gwg.ncols + coords[0]
    return s

def move_agent(gwg,coords,u):
    s = coord2state(gwg,coords)
    ns = np.nonzero(gwg.prob[gwg.actlist[u]][s])[0][0]
    return ns

def check_int(gwg,ushield,u):
    if ushield != u:
        actlist = []
        shield_actlist = []
        for n in range(gwg.nagents):
            actlist.append(gwg.actlist[u[n]])
            shield_actlist.append(gwg.actlist[ushield[n]])
        print 'Shield interference occurred'
        print 'Agents intended to take action {}, but shield forced {}'.format(actlist,shield_actlist)
        return  1
    else: return 0


def centralizedShield(filename,gwg):
    automaton = parseJson(filename)
    automaton_state = 0
    shield_action = [None]*gwg.nagents
    k = [None]*gwg.nagents
    control_action = [None]*gwg.nagents
    control_action_dirn = [None]*gwg.nagents
    agentpos = [(None,None)]*gwg.nagents
    nextgridstate = [None]*gwg.nagents
    for n in range(gwg.nagents):
        k[n] = automaton[automaton_state]['State']['k'+str(n)]
        shield_action[n] = automaton[automaton_state]['State']['ushield'+str(n)]
        control_action[n] = automaton[automaton_state]['State']['uloc'+str(n)]
        agentpos[n] = (automaton[automaton_state]['State']['x'+str(n)],automaton[automaton_state]['State']['y'+str(n)])
        nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
    check_int(gwg,shield_action,control_action)
    print '{} steps interfered with'.format(k)
    gwg.current = copy.deepcopy(nextgridstate)
    gwg.render()

    while True:
        nextstates = automaton[automaton_state]['Successors']
        combarrow = [None]*gwg.nagents
        for n in range(gwg.nagents):
            while True:
                combarrow[n] = gwg.getkeyinput()
                if combarrow[n] != None:
                    combarrow[n] = gwg.actlist.index(combarrow[n])
                    break
        for ns in nextstates:
            for n in range(gwg.nagents):
                control_action[n] = automaton[ns]['State']['uloc'+str(n)]
                control_action_dirn[n] = gwg.actlist[control_action[n]]
            if control_action == combarrow:
                for n in range(gwg.nagents):
                    k[n] = automaton[ns]['State']['k'+str(n)]
                    shield_action[n] = automaton[ns]['State']['ushield'+str(n)]
                    agentpos[n] = (automaton[ns]['State']['x'+str(n)],automaton[ns]['State']['y'+str(n)])
                    nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
                    automaton_state = copy.deepcopy(ns)
                break
        check_int(gwg,shield_action,control_action)
        print '{} steps interfered with'.format(k)
        gwg.current = copy.deepcopy(nextgridstate)
        gwg.render()
        # print automaton[automaton_state]['State']['sane']

def centralizedShield_Local(local_filenames,shield_filename,gwg):
    automaton = []*gwg.nagents
    automaton_state = [0]*gwg.nagents
    for n in range(gwg.nagents):
        automaton[n] = parseJson(local_filenames[n])
    automaton_shield = parseJson(shield_filename)
    automaton_shield_state = 0
    shield_action = [None]*gwg.nagents
    k = [None]*gwg.nagents
    b = [None]*gwg.nagents
    control_action = [None]*gwg.nagents
    shieldcontrolaction = [None]*gwg.nagents
    control_action_dirn = [None]*gwg.nagents
    agentpos = [(None,None)]*gwg.nagents
    nextgridstate = [None]*gwg.nagents
    for n in range(gwg.nagents):
        k[n] = automaton_shield[automaton_shield_state]['State']['k'+str(n)]
        shield_action[n] = automaton_shield[automaton_shield_state]['State']['ushield'+str(n)]
        control_action[n] = automaton_shield[automaton_shield_state]['State']['uloc'+str(n)]
        agentpos[n] = (automaton_shield[automaton_shield_state]['State']['x'+str(n)],automaton_shield[automaton_shield_state]['State']['y'+str(n)])
        nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
    check_int(gwg,shield_action,control_action)
    print '{} steps interfered with'.format(k)
    gwg.current = copy.deepcopy(nextgridstate)
    gwg.render()

    while True:
        while True:
            keypress = gwg.getkeyinput()
            if keypress != None:
                break
        nextstates = automaton_shield[automaton_shield_state]['Successors']
        for n in range(gwg.nagents):
            control_action[n] = automaton[n][automaton_state]['State']['u']
            for ns in nextstates:
                for m in range(gwg.nagents):
                    shieldcontrolaction[m] = automaton_shield[ns]['State']['uloc'+str(n)]
                if control_action == shieldcontrolaction:
                    k[n] = automaton_shield[ns]['State']['k'+str(n)]
                    b[n] = automaton_shield[ns]['State']['b'+str(n)]
                    shield_action[n] = automaton_shield[ns]['State']['ushield'+str(n)]
                    agentpos[n] = (automaton_shield[ns]['State']['x'+str(n)],automaton_shield[ns]['State']['y'+str(n)])
                    nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
                    automaton_shield_state = copy.deepcopy(ns)
            a

        check_int(gwg,shield_action,control_action)
        print '{} steps interfered with'.format(k)
        gwg.current = copy.deepcopy(nextgridstate)
        gwg.render()


def centralizedPermissiveShield(filename,gwg):
    automaton = parsePermissiveStrategy(filename)
    init = {'x0':0,'y0':3,'k0':0, 'uloc0':4, 'x1':3, 'y1':3, 'k1':0,'uloc1':4,'ushield0':4,'ushield1':4}
    automatonstate = computeInitialState(automaton,init)
    agentpos = [(None,None)]*gwg.nagents
    shield_action = [None]*gwg.nagents
    k = [None]*gwg.nagents
    control_action = [None]*gwg.nagents
    nextgridstate = [None]*gwg.nagents
    for n in range(gwg.nagents):
        agentpos[n] = (automaton[automatonstate]['State']['x'+str(n)],automaton[automatonstate]['State']['y'+str(n)])
        shield_action[n] = automaton[automatonstate]['State']['ushield'+str(n)]
        control_action[n] = automaton[automatonstate]['State']['uloc'+str(n)]
        nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
    check_int(gwg,shield_action,control_action)
    # print '{} steps interfered with'.format(k)
    gwg.current = copy.deepcopy(nextgridstate)
    gwg.render()

    while True:
        nextstates = automaton[automatonstate]['Successors']
        combarrow = [None]*gwg.nagents
        for n in range(gwg.nagents):
            while True:
                combarrow[n] = gwg.getkeyinput()
                if combarrow[n] != None:
                    combarrow[n] = gwg.actlist.index(combarrow[n])
                    break
        nextmovestates = []
        for ns in nextstates: #Find states corresponding to the arrow key movement
            for n in range(gwg.nagents):
                control_action[n] = automaton[ns]['State']['uloc'+str(n)]
                shield_action[n] = automaton[ns]['State']['ushield'+str(n)]
            if (control_action == combarrow):
                nextmovestates.append(ns)
        for ns in nextmovestates: # Find states where the shield does not interfere if possible
            for n in range(gwg.nagents):
                control_action[n] = automaton[ns]['State']['uloc'+str(n)]
                shield_action[n] = automaton[ns]['State']['ushield'+str(n)]
            if control_action == shield_action or (nextmovestates.index(ns) == len(nextmovestates)-1):
                if (nextstates.index(ns) == len(nextstates)-1):
                    a = 1
                automatonstate = copy.deepcopy(ns)
                for n in range(gwg.nagents):
                    agentpos[n] = (automaton[automatonstate]['State']['x'+str(n)],automaton[automatonstate]['State']['y'+str(n)])
                    shield_action[n] = automaton[automatonstate]['State']['ushield'+str(n)]
                    control_action[n] = automaton[automatonstate]['State']['uloc'+str(n)]
                    nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
                break
        check_int(gwg,shield_action,control_action)
        # print '{} steps interfered with'.format(k)
        gwg.current = copy.deepcopy(nextgridstate)
        gwg.render()


def gazeboOutput(gwg,timestep):
    filename = 'statehistory15x20.txt'
    with open(filename,'a') as file:
        if timestep == 0:
            file.write('t,e,a\n')
        file.write('{},{},{}\n'.format(timestep,gwg.moveobstacles[0],gwg.current[0]))
        file.close()
