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

def write_to_slugs_part(infile,gw,init,initmovetarget,targets,k,b,vel=1,partitionGrid =[], belief_safety = 0, belief_liveness = 0, target_reachability = False):

    nonbeliefstates = gw.states
    beliefcombs = powerset(partitionGrid.keys())

    allstates = copy.deepcopy(nonbeliefstates)
    for i in range(gw.nstates,gw.nstates + len(beliefcombs)):
        allstates.append(i)

    invisibilityset = [dict.fromkeys(set(gw.states),frozenset({gw.nrows*gw.ncols+1}))]
    for s in set(gw.states) - set(gw.edges):
        invisibilityset[s] = visibility.invis(gw,s)
        if s in gw.obstacles:
            invisibilityset[s] = {-1}

    filename = infile+'.structuredslugs'
    file = open(filename,'w')
    file.write('[INPUT]\n')
    file.write('s:0...{}\n'.format(gw.ncols-1))
    file.write('st:0...{}\n'.format(gw.nrows-1))
    file.write('k:0...{}\n'.format(k))
    file.write('b:0...{}\n'.format(b))

    file.write('[OUTPUT]\n')
    for v in range(vel):
        file.write('u{}:0...{}\n'.format(v,gw.nactions-1))

    file.write('[ENV_INIT]\n')
    file.write('s = {}\n'.format(gw.coords(init)[1]))
    file.write('st = {}\n'.format(gw.coords(initmovetarget)[1]))
    file.write('k = {}\n'.format(0))
    file.write('b = {}\n'.format(0))


    # writing env_trans
    file.write('\n[ENV_TRANS]\n')
    for st in allstates:
        if st in nonbeliefstates:
            for s in nonbeliefstates:
                stri = " (s = {} /\\ st = {}) -> ".format(s,st)
                beliefset = set()
                for a in range(gw.nactions):
                    for t in np.nonzero(gw.prob[gw.actlist[a]][st])[0]:
                        if not t in invisibilityset[s]:
                            stri += 'st\' = {} \\/'.format(t)
                        else:
                            if not t == s and t not in targets: # not allowed to move on agent's position
                                t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                beliefset.add(t2)
                if len(beliefset) > 0:
                    b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                    stri += ' st\' = {} \\/'.format(b2)
                stri = stri[:-3]
                stri += '\n'
                file.write(stri)
                for n in range(gw.nagents):
                    file.write("s = {} -> !st' = {}\n".format(s,s))

        else:
            for s in nonbeliefstates:
                invisstates = invisibilityset[0][s]
                visstates = set(nonbeliefstates) - invisstates

                beliefcombstate = beliefcombs[st - len(nonbeliefstates)]
                beliefstates = set()
                for currbeliefstate in beliefcombstate:
                    beliefstates = beliefstates.union(partitionGrid[currbeliefstate])
                beliefstates = beliefstates - set(targets) # remove taret positions (no transitions from target positions)
                beliefstates_vis = beliefstates.intersection(visstates)
                beliefstates_invis = beliefstates - beliefstates_vis

                if belief_safety > 0 and len(beliefstates_invis) > belief_safety:
                    continue # no transitions from error states

                if len(beliefstates) > 0:
                    stri = " (s = {} /\\ st = {}) -> ".format(s,st)

                    beliefset = set()
                    for b in beliefstates:
                        for a in range(gw.nactions):
                            for t in np.nonzero(gw.prob[gw.actlist[a]][b])[0]:
                                if not t in invisibilityset[s]:
                                    stri += ' st\' = {} \\/'.format(t)
                                else:
                                    if t in gw.targets[0]:
                                        continue
                                    t2 = partitionGrid.keys()[[inv for inv in range(len(partitionGrid.values())) if t in partitionGrid.values()[inv]][0]]
                                    beliefset.add(t2)
                    if len(beliefset) > 0:
                        b2 = allstates[len(nonbeliefstates) + beliefcombs.index(beliefset)]
                        stri += ' st\' = {} \\/'.format(b2)


                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)


    # Writing env_safety
    for obs in gw.obstacles:
        file.write('!y = {}\n'.format(obs))

    if target_reachability:
        for t in targets:
            file.write('!st = {}\n'.format(t))

    # writing sys_trans
    file.write('\n[SYS_TRANS]\n')
    for s in nonbeliefstates:
        uset = list(itertools.product(range(len(gw.actlist)),repeat=vel))
        for k1 in range(k):
            for b1 in range(b):
                stri = "s = {} /\\ k = {} /\\ b = {} /\\ ".format(s,k1,b1)
        for u in uset:
            for v in range(vel):
                stri += "u{} = {} /\\ ".format(v,u[v])
            stri = stri[:-3]
            stri += ' -> '
            for ushield in uset:
                snext = copy.deepcopy(s)
                for v in range(vel):
                    snext = np.nonzero(gw.prob[ushield[v]][snext])[0]
                if snext not in gw.obstacles:
                    if ushield == u:
                        if b1 < b:
                            stri += '(s\' = {} /\\ k\' = {} /\\ b\' = {}) \\/ '.format(snext,0,b1+1)
                        else:
                            stri += '(s\' = {} /\\ k\' = {} /\\ b\' = {}) \\/ '.format(snext,0,b1)
                    else:
                        counter = 0
                        for n in range(len(ushield)):
                            if ushield[n] != u[n]:
                                counter += 1


                        if k1 < k:
                            stri += '(s\' = {} /\\ k\' = {} /\\ b\' = {}) \\/ '.format(snext,k1+1,0)
                        else:
                            stri += '(s\' = {} /\\ k\' = {} /\\ b\' = {}) \\/ '.format(snext,k1,0)
                    stri = stri[:-3]
                    stri += '\n'
                    file.write(stri)
# Writing sys_safety
    for obs in gw.obstacles:
        file.write('!s = {}\n'.format(obs))

    for s in set(nonbeliefstates):
        stri = 'st = {} -> !s = {}\n'.format(s,s)
        file.write(stri)
        stri = 'st = {} -> !s\' = {}\n'.format(s,s)
        file.write(stri)

    if belief_safety > 0:
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            if len(beliefset) > belief_safety:
                stri = 'y = {} -> '.format(len(nonbeliefstates)+beliefcombs.index(b))
                counter = 0
                stri += '('
                for n in range(gw.nagents):
                    stri += '('
                    for x in nonbeliefstates:
                        invisstates = invisibilityset[n][x]
                        beliefset_invis = beliefset.intersection(invisstates)
                        if len(beliefset_invis) > belief_safety:
                            stri += '!{} = {} /\\ '.format(agentletters[n],nonbeliefstates.index(x))
                            counter += 1
                    stri = stri[:-3]
                    stri += ') \\/ '
                stri = stri[:-3]
                stri += ')'
                stri += '\n'
                if counter > 0:
                    file.write(stri)

    if gw.nagents > 1:
        for s in nonbeliefstates:
            for n in range(gw.nagents):
                stri = '{} = {} ->'.format(agentletters[n],nonbeliefstates.index(s))
                for m in range(gw.nagents):
                    if m!= n:
                        stri += ' !{} = {} /\\'.format(agentletters[m],nonbeliefstates.index(s))
                stri = stri[:-2]
                stri += '\n'
                file.write(stri)


    # Writing sys_liveness
    file.write('\n[SYS_LIVENESS]\n')
    if target_reachability:
        for n in range(gw.nagents):
            file.write('{} = {}\n'.format(agentletters[n],nonbeliefstates.index(gw.targets[n][0])))

    stri  = ''
    if belief_liveness >0:
        for y in range(len(nonbeliefstates)):
            stri+='y = {}'.format(y)
            if y < len(nonbeliefstates) - 1:
                stri+=' \\/ '
        for b in beliefcombs:
            beliefset = set()
            for beliefstate in b:
                beliefset = beliefset.union(partitionGrid[beliefstate])
            beliefset =  beliefset -set(gw.targets[0])
            stri1 = ' \\/ (y = {} /\\ ('.format(len(nonbeliefstates)+beliefcombs.index(b))
            count = 0
            for n in range(gw.nagents):
                for x in nonbeliefstates:
                    truebelief = beliefset.intersection(invisibilityset[n][x])
                    if len(truebelief) <= belief_liveness:
                        if count > 0:
                            stri1 += ' \\/ '
                        stri1 += ' {} = {} '.format(agentletters[n],nonbeliefstates.index(x))
                        count+=1
            stri1+='))'
            if count > 0 and count < len(nonbeliefstates):
                stri+=stri1
            if count == len(nonbeliefstates):
                stri+= ' \\/ y = {}'.format(len(nonbeliefstates)+beliefcombs.index(b))

        stri += '\n'
        file.write(stri)


    # Writing env_liveness
    file.write('\n[ENV_LIVENESS]\n')
    stri = 'y = {}'.format(gw.targets[0][0])
    file.write(stri)
    file.close()