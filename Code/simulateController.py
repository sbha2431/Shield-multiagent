__author__ = 'sudab'
import random
import simplejson as json
import time
import copy
import visibility
import grid_partition
import itertools
import numpy as np

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
    file = open(filename)
    data = json.load(file)
    file.close()
    automata_state = 0
    "Split up the variables in the json file"
    vars = data['variables']
    varletters = ['x','y','k','b','u']
    xlen = 0
    ylen = 0
    klen = 0
    blen = 0
    ulen = 0
    for v in vars:
        if v[0] == varletters[0]:
            xlen += 1
        if v[0] == varletters[1]:
            ylen += 1
        if v[0] == varletters[2]:
            klen += 1
        if v[0] == varletters[3]:
            blen += 1
        if v[0] == varletters[4]:
            ulen += 1

    xlen = xlen/gwg.nagents
    ylen = ylen/gwg.nagents
    klen = klen/gwg.nagents
    blen = blen/gwg.nagents
    ulen = ulen/(2*gwg.nagents)

    totlen = xlen+ylen+klen+blen+ulen
    totstate = data['nodes'][str(automata_state)]['state']
    shieldstart = totlen*gwg.nagents
    shield_action = [None]*gwg.nagents
    k = [None]*gwg.nagents
    b = [None]*gwg.nagents
    control_action = [None]*gwg.nagents
    control_action_dirn = [None]*gwg.nagents
    agentpos = [(None,None)]*gwg.nagents
    nextgridstate = [None]*gwg.nagents
    for n in range(gwg.nagents):
        ubin = totstate[n*totlen+(xlen+ylen+klen+blen):n*totlen+(xlen+ylen+klen+blen+ulen)]
        ushieldbin = totstate[shieldstart+(n*ulen):(shieldstart+ulen*n)+ulen]
        kbin = totstate[n*totlen+xlen+ylen:n*totlen+xlen+ylen+klen]
        bbin = totstate[n*totlen+xlen+ylen+klen:n*totlen+xlen+ylen+klen+blen]
        k[n] = int(''.join(str(e) for e in kbin)[::-1], 2)
        # b[n] = int(''.join(str(e) for e in bbin)[::-1], 2)
        shield_action[n] = int(''.join(str(e) for e in ushieldbin)[::-1], 2)
        control_action[n] = int(''.join(str(e) for e in ubin)[::-1], 2)
        xbin = totstate[n*totlen:(n*totlen)+xlen]
        ybin = totstate[n*totlen+xlen:(n*totlen)+xlen+ylen]
        agentpos[n] = (int(''.join(str(e) for e in xbin)[::-1], 2),int(''.join(str(e) for e in ybin)[::-1], 2))
        nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
    check_int(gwg,shield_action,control_action)
    print '{} steps interfered with'.format(k)
    gwg.current = copy.deepcopy(nextgridstate)
    gwg.render()

    while True:
        nextstates = data['nodes'][str(automata_state)]['trans']
        combarrow = [None]*gwg.nagents
        for n in range(gwg.nagents):
            while True:
                combarrow[n] = gwg.getkeyinput()
                if combarrow[n] != None:
                    combarrow[n] = gwg.actlist.index(combarrow[n])
                    break
        for ns in nextstates:
            ntotstate = data['nodes'][str(ns)]['state']
            for n in range(gwg.nagents):
                ubin = ntotstate[n*totlen+(xlen+ylen+klen+blen):n*totlen+(xlen+ylen+klen+blen+ulen)]
                control_action[n] = int(''.join(str(e) for e in ubin)[::-1], 2)
                control_action_dirn[n] = gwg.actlist[control_action[n]]
            if control_action == combarrow:
                for n in range(gwg.nagents):
                    xbin = ntotstate[n*totlen:(n*totlen)+xlen]
                    ybin = ntotstate[n*totlen+xlen:(n*totlen)+xlen+ylen]
                    ushieldbin = ntotstate[shieldstart+(n*ulen):(shieldstart+ulen*n)+ulen]
                    kbin = ntotstate[n*totlen+xlen+ylen:n*totlen+xlen+ylen+klen] # Note that we use the k and b values from the previous time step.
                    bbin = ntotstate[n*totlen+xlen+ylen+klen:n*totlen+xlen+ylen+klen+blen]
                    k[n] = int(''.join(str(e) for e in kbin)[::-1], 2)
                    # b[n] = int(''.join(str(e) for e in bbin)[::-1], 2)
                    shield_action[n] = int(''.join(str(e) for e in ushieldbin)[::-1], 2)
                    agentpos[n] = (int(''.join(str(e) for e in xbin)[::-1], 2),int(''.join(str(e) for e in ybin)[::-1], 2))
                    nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
                    automata_state = copy.deepcopy(ns)
                break
        check_int(gwg,shield_action,control_action)
        print '{} steps interfered with'.format(k)
        gwg.current = copy.deepcopy(nextgridstate)
        gwg.render()


def centralizedPermissiveShield(filename,gwg):
    file = open(filename)
    data = json.load(file)
    file.close()
    automata_state = 0
    "Split up the variables in the json file"
    vars = data['variables']
    varletters = ['x','y','k','b','u']
    xlen = 0
    ylen = 0
    klen = 0
    blen = 0
    ulen = 0
    for v in vars:
        if v[0] == varletters[0]:
            xlen += 1
        if v[0] == varletters[1]:
            ylen += 1
        if v[0] == varletters[2]:
            klen += 1
        if v[0] == varletters[3]:
            blen += 1
        if v[0] == varletters[4]:
            ulen += 1

    xlen = xlen/gwg.nagents
    ylen = ylen/gwg.nagents
    klen = klen/gwg.nagents
    blen = blen/gwg.nagents
    ulen = ulen/(2*gwg.nagents)

    totlen = xlen+ylen+klen+blen+ulen
    totstate = data['nodes'][str(automata_state)]['state']
    shieldstart = totlen*gwg.nagents
    shield_action = [None]*gwg.nagents
    k = [None]*gwg.nagents
    b = [None]*gwg.nagents
    control_action = [None]*gwg.nagents
    control_action_dirn = [None]*gwg.nagents
    agentpos = [(None,None)]*gwg.nagents
    nextgridstate = [None]*gwg.nagents
    for n in range(gwg.nagents):
        ubin = totstate[n*totlen+(xlen+ylen+klen+blen):n*totlen+(xlen+ylen+klen+blen+ulen)]
        ushieldbin = totstate[shieldstart+(n*ulen):(shieldstart+ulen*n)+ulen]
        kbin = totstate[n*totlen+xlen+ylen:n*totlen+xlen+ylen+klen]
        bbin = totstate[n*totlen+xlen+ylen+klen:n*totlen+xlen+ylen+klen+blen]
        k[n] = int(''.join(str(e) for e in kbin)[::-1], 2)
        # b[n] = int(''.join(str(e) for e in bbin)[::-1], 2)
        shield_action[n] = int(''.join(str(e) for e in ushieldbin)[::-1], 2)
        control_action[n] = int(''.join(str(e) for e in ubin)[::-1], 2)
        xbin = totstate[n*totlen:(n*totlen)+xlen]
        ybin = totstate[n*totlen+xlen:(n*totlen)+xlen+ylen]
        agentpos[n] = (int(''.join(str(e) for e in xbin)[::-1], 2),int(''.join(str(e) for e in ybin)[::-1], 2))
        nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
    check_int(gwg,shield_action,control_action)
    print '{} steps interfered with'.format(k)
    gwg.current = copy.deepcopy(nextgridstate)
    gwg.render()

    while True:
        nextstates = data['nodes'][str(automata_state)]['trans']
        combarrow = [None]*gwg.nagents
        for n in range(gwg.nagents):
            while True:
                combarrow[n] = gwg.getkeyinput()
                if combarrow[n] != None:
                    combarrow[n] = gwg.actlist.index(combarrow[n])
                    break
        for ns in nextstates:
            ntotstate = data['nodes'][str(ns)]['state']
            for n in range(gwg.nagents):
                ubin = ntotstate[n*totlen+(xlen+ylen+klen+blen):n*totlen+(xlen+ylen+klen+blen+ulen)]
                control_action[n] = int(''.join(str(e) for e in ubin)[::-1], 2)
                control_action_dirn[n] = gwg.actlist[control_action[n]]
            if control_action == combarrow:
                for n in range(gwg.nagents):
                    xbin = ntotstate[n*totlen:(n*totlen)+xlen]
                    ybin = ntotstate[n*totlen+xlen:(n*totlen)+xlen+ylen]
                    ushieldbin = ntotstate[shieldstart+(n*ulen):(shieldstart+ulen*n)+ulen]
                    kbin = ntotstate[n*totlen+xlen+ylen:n*totlen+xlen+ylen+klen] # Note that we use the k and b values from the previous time step.
                    bbin = ntotstate[n*totlen+xlen+ylen+klen:n*totlen+xlen+ylen+klen+blen]
                    k[n] = int(''.join(str(e) for e in kbin)[::-1], 2)
                    # b[n] = int(''.join(str(e) for e in bbin)[::-1], 2)
                    shield_action[n] = int(''.join(str(e) for e in ushieldbin)[::-1], 2)
                    agentpos[n] = (int(''.join(str(e) for e in xbin)[::-1], 2),int(''.join(str(e) for e in ybin)[::-1], 2))
                    nextgridstate[n] = move_agent(gwg,agentpos[n],shield_action[n])
                    automata_state = copy.deepcopy(ns)
                break
        check_int(gwg,shield_action,control_action)
        print '{} steps interfered with'.format(k)
        gwg.current = copy.deepcopy(nextgridstate)
        gwg.render()


def gazeboOutput(gwg,timestep):
    filename = 'statehistory15x20.txt'
    with open(filename,'a') as file:
        if timestep == 0:
            file.write('t,e,a\n')
        file.write('{},{},{}\n'.format(timestep,gwg.moveobstacles[0],gwg.current[0]))
        file.close()
