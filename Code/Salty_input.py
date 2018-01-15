__author__ = 'sudab'

import numpy as np
import visibility
import grid_partition
import copy
import itertools

def reach_states(gw,states):
    t =set()
    for state in states:
        for action in gw.actlist:
            t.update(set(np.nonzero(gw.prob[action][state])[0]))
    return t

def powerset(s):
    x = len(s)
    a = []
    for i in range(1,1<<x):
        a.append({s[j] for j in range(x) if (i &(1<<j))})
    return a

def cartesian (lists):
    if lists == []: return [()]
    return [x + (y,) for x in cartesian(lists[:-1]) for y in lists[-1]]

def write_to_slugs_resilient(infile,gw,init,targets,k,b):
    states = gw.states

    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('x:0...{}\n'.format(gw.ncols-1))
    file.write('y:0...{}\n'.format(gw.nrows-1))
    file.write('k:0...{}\n'.format(k))
    file.write('b:0...{}\n'.format(b))

    file.write('[OUTPUT]\n')
    file.write('u:0...{}\n'.format(gw.nactions-1))

    file.write('[ENV_INIT]\n')
    file.write('x = {}\n'.format(gw.coords(init)[1]))
    file.write('y = {}\n'.format(gw.coords(init)[0]))
    file.write('k = {}\n'.format(0))
    file.write('b = {}\n'.format(0))

    file.write('[SYS_INIT]\n')
    file.write('u = {}\n'.format(4))


    file.write('\n[ENV_TRANS]\n')
    for s in states:
        y,x = gw.coords(s)
        for u in range(gw.nactions):
            for k1 in range(k+1):
                for b1 in range(b+1):
                    stri = "(x = {} /\\ y = {} /\\ u = {} /\\ k = {} /\\ b = {}) -> ".format(x,y,u,k1,b1)
                    for u2 in range(gw.nactions):
                        ns = np.nonzero(gw.prob[gw.actlist[u2]][s])[0][0]
                        ny,nx = gw.coords(ns)
                        if u2 == u:
                            if b1 < b:
                                stri += "(x' = {} /\\ y' = {} /\\ k' = 0 /\\ b' = {}) \\/".format(nx,ny,b1+1)
                            else:
                                stri += "(x' = {} /\\ y' = {} /\\ k' = 0 /\\ b' = {}) \\/".format(nx,ny,b1)
                        else:
                            if k1 <  k:
                                stri += "(x' = {} /\\ y' = {} /\\ k' = {} /\\ b' = 0) \\/".format(nx,ny,k1+1)
                            else:
                                stri += "(x' = {} /\\ y' = {} /\\ k' = {} /\\ b' = 0) \\/".format(nx,ny,k1)
                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)
    file.write('!(k = {})\n'.format(k))

    # writing env_trans
    file.write('\n[ENV_LIVENESS]\n')
    file.write('b = {}\n'.format(b))

    file.write('\n[SYS_TRANS]\n')
    for obs in gw.obstacles:
        xobs = gw.coords(obs)[1]
        yobs = gw.coords(obs)[0]
        file.write('!(x = {} /\\ y = {})\n'.format(xobs,yobs))


    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    for targ in targets:
        xtarg = gw.coords(targ)[1]
        ytarg = gw.coords(targ)[0]
        file.write('(x = {} /\\ y = {})\n'.format(xtarg,ytarg))

    # Writing env_liveness
    file.close()

def write_to_slugs_fullyCentralized(infile,gw,init,targets):
    states = gw.states

    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    for n in range(gw.nagents):
        file.write('x{}:0...{}\n'.format(n,gw.ncols-1))
        file.write('y{}:0...{}\n'.format(n,gw.nrows-1))
    file.write('[OUTPUT]\n')
    for n in range(gw.nagents):
        file.write('u{}:0...{}\n'.format(n,gw.nactions-1))

    file.write('[ENV_INIT]\n')
    for n in range(gw.nagents):
        file.write('x{} = {}\n'.format(n,gw.coords(init[n])[1]))
        file.write('y{} = {}\n'.format(n,gw.coords(init[n])[0]))


    file.write('\n[ENV_TRANS]\n')
    for n in range(gw.nagents):
        for s in states:
            y,x = gw.coords(s)
            for u in range(gw.nactions):
                stri = "(x{} = {} /\\ y{} = {} /\\ u{} = {}) -> ".format(n,x,n,y,n,u)
                ns = np.nonzero(gw.prob[gw.actlist[u]][s])[0][0]
                ny,nx = gw.coords(ns)
                stri += "(x{}' = {} /\\ y{}' = {})\n".format(n,nx,n,ny)
                file.write(stri)


    file.write('\n[SYS_TRANS]\n')
    for obs in gw.obstacles:
        xobs = gw.coords(obs)[1]
        yobs = gw.coords(obs)[0]
        file.write('!(x = {} /\\ y = {})\n'.format(xobs,yobs))
    for n in range(gw.nagents):
        for m in range(gw.nagents):
            if m != n:
                file.write('!(x{} = x{} /\\ y{} = y{})\n'.format(n,m,n,m))

    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    for n in range(gw.nagents):
        for targ in gw.targets[n]:
            xtarg = gw.coords(targ)[1]
            ytarg = gw.coords(targ)[0]
            file.write('(x{} = {} /\\ y{} = {})\n'.format(n,xtarg,n,ytarg))


    # Writing env_liveness
    file.close()

def write_to_slugs_central_shield2(infile,gw,init,k,b):
    states = gw.states
    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    for n in range(gw.nagents):
        file.write('x{}:0...{}\n'.format(n,gw.ncols-1))
        file.write('y{}:0...{}\n'.format(n,gw.nrows-1))
        file.write('uloc{}:0...{}\n'.format(n,gw.nactions-1))


    file.write('[OUTPUT]\n')
    file.write('sane:0...1\n')
    for n in range(gw.nagents):
        file.write('ushield{}:0...{}\n'.format(n,gw.nactions-1))
        file.write('k{}:0...{}\n'.format(n,k[n]))
        file.write('b{}:0...{}\n'.format(n,b[n]))

    file.write('[ENV_INIT]\n')
    for n in range(gw.nagents):
        file.write('x{} = {}\n'.format(n,gw.coords(init[n])[1]))
        file.write('y{} = {}\n'.format(n,gw.coords(init[n])[0]))
        file.write('uloc{} = {}\n'.format(n,4))


    file.write('[SYS_INIT]\n')
    file.write('sane = 0\n')
    for n in range(gw.nagents):
        file.write('ushield{} = {}\n'.format(n,4))
        file.write('k{} = {}\n'.format(n,0))
        file.write('b{} = {}\n'.format(n,0))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for n in range(gw.nagents):
        for s in states:
            y,x = gw.coords(s)
            for ushield in range(gw.nactions):
                stri = "(x{} = {} /\\ y{} = {} /\\ ushield{} = {}) -> ".format(n,x,n,y,n,ushield)
                ns = np.nonzero(gw.prob[gw.actlist[ushield]][s])[0][0]
                ny,nx = gw.coords(ns)
                stri += "(x{}' = {} /\\ y{}' = {})\n".format(n,nx,n,ny)
                file.write(stri)

    #Writing sys liveness
    file.write('\n[SYS_LIVENESS]\n')
    stri = ''
    for n in range(gw.nagents):
        stri += 'b{}\' >= {}\n'.format(n,b[n])
    stri += '\n'
    file.write(stri)

    file.write('\n[SYS_TRANS]\n')
    for n in range(gw.nagents):
        file.write('!(k{} = {})\n'.format(n,k[n]))
        for m in range(gw.nagents):
            if m != n:
                file.write('!(x{} = x{} /\\ y{} = y{})\n'.format(n,m,n,m))
    for n in range(gw.nagents):
        stri = "(uloc{}' = ushield{}' /\\ b{} < {}) -> k{}' = 0 /\\ b{}' = b{}+1\n".format(n,n,n,b[n]-1,n,n,n,n)
        stri += "(uloc{}' = ushield{}' /\\ b{} >= {}) -> k{}' = 0 /\\ b{}' = {}\n".format(n,n,n,b[n]-1,n,n,b[n])
        stri += "!(uloc{}' = ushield{}') -> (k{}' = k{}+1) /\\ b{}' = 0\n".format(n,n,n,n,n)
        file.write(stri)
    stri = 'sane\' = 1 <-> ('
    for n in range(gw.nagents):
        stri += 'b{}\' = {} \\/ '.format(n,0)
    stri = stri[:-3]
    stri += ')'
    stri += '\n'
    file.write(stri)
    file.close()

def write_to_slugs_dist_shield(infile,gw,init,k,b):
    states = gw.states
    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    for n in range(gw.nagents):
        file.write('x{}:0...{}\n'.format(n,gw.ncols-1))
        file.write('y{}:0...{}\n'.format(n,gw.nrows-1))
        file.write('uloc{}:0...{}\n'.format(n,gw.nactions-1))


    file.write('[OUTPUT]\n')
    file.write('sane:0...1\n')
    for n in range(gw.nagents):
        file.write('ushield{}:0...{}\n'.format(n,gw.nactions-1))
        file.write('k{}:0...{}\n'.format(n,k[n]))
        file.write('b{}:0...{}\n'.format(n,b[n]))

    file.write('[ENV_INIT]\n')
    for n in range(gw.nagents):
        file.write('x{} = {}\n'.format(n,gw.coords(init[n])[1]))
        file.write('y{} = {}\n'.format(n,gw.coords(init[n])[0]))
        file.write('uloc{} = {}\n'.format(n,4))


    file.write('[SYS_INIT]\n')
    file.write('sane = 0\n')
    for n in range(gw.nagents):
        file.write('ushield{} = {}\n'.format(n,4))
        file.write('k{} = {}\n'.format(n,0))
        file.write('b{} = {}\n'.format(n,0))

    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for n in range(gw.nagents):
        for s in states:
            y,x = gw.coords(s)
            for ushield in range(gw.nactions):
                stri = "(x{} = {} /\\ y{} = {} /\\ ushield{} = {}) -> ".format(n,x,n,y,n,ushield)
                ns = np.nonzero(gw.prob[gw.actlist[ushield]][s])[0][0]
                ny,nx = gw.coords(ns)
                stri += "(x{}' = {} /\\ y{}' = {})\n".format(n,nx,n,ny)
                file.write(stri)

    #Writing sys liveness
    file.write('\n[SYS_LIVENESS]\n')
    stri = ''
    for n in range(gw.nagents):
        stri += 'b{}\' >= {}\n'.format(n,b[n])
    stri += '\n'
    file.write(stri)

    file.write('\n[SYS_TRANS]\n')
    for n in range(gw.nagents):
        file.write('!(k{} = {})\n'.format(n,k[n]))
        for m in range(gw.nagents):
            if m != n:
                file.write('!(x{} = x{} /\\ y{} = y{})\n'.format(n,m,n,m))
    for n in range(gw.nagents):
        stri = "(uloc{}' = ushield{}' /\\ b{} < {}) -> k{}' = 0 /\\ b{}' = b{}+1\n".format(n,n,n,b[n]-1,n,n,n,n)
        stri += "(uloc{}' = ushield{}' /\\ b{} >= {}) -> k{}' = 0 /\\ b{}' = {}\n".format(n,n,n,b[n]-1,n,n,b[n])
        stri += "!(uloc{}' = ushield{}') -> (k{}' = k{}+1) /\\ b{}' = 0\n".format(n,n,n,n,n)
        file.write(stri)
    stri = 'sane\' = 1 <-> ('
    for n in range(gw.nagents):
        stri += 'b{}\' = {} \\/ '.format(n,0)
    stri = stri[:-3]
    stri += ')'
    stri += '\n'
    file.write(stri)
    file.close()