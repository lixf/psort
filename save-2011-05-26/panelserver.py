#!/usr/bin/python

import panel
import getopt
import sys
import socket

# This code runs an RPC server that allows remote display
# of a panel

def usage(name):
    print 'Usage: %s [-h] -r R -c C [-p P] [-W width] [-H height] [-LOlf]' % name
    print '   -h    Print this message'
    print '   -r R  Display R rows'
    print '   -c C  Display C columns'
    print '   -p P  Run server on port P'
    print '   -W width  Set rectangle width (in pixels)'
    print '   -H height Set rectangle height (in pixels)'
    print '   -L    Serve on localhost'
    print '   -O    Optimize socket performance'
    print '   -f    Disable nogetfqdn'
    print '   -l    Enable logging'


def run(name, args):
    rows = 2
    cols = 40
    port = 8000
    rwidth = 0
    rheight = 0
    logging = False
    optimize = False
    nogetfqdn = False
    localhost = False
    optlist, args = getopt.getopt(args, 'hr:c:p:W:H:LOlf')
    for (opt,val) in optlist:
        if opt == '-h':
            usage(name)
            return
        elif opt == '-r':
            rows = int(val)
        elif opt == '-c':
            cols = int(val)
        elif opt == '-p':
            port = int(val)
        elif opt == '-W':
            rwidth = int(val)
        elif opt == '-H':
            rheight = int(val)
        elif opt == '-O':
            optimize = True
        elif opt == '-L':
            localhost = True
        elif opt == '-l':
            logging = True
        elif opt == '-f':
            nogetfqdn = True

    print 'Creating panel with rows = %d, cols = %d, rwidth = %d, rheight =  %d' \
          % (rows, cols, rwidth, rheight)
    if optimize:
        print 'Enabling socket optimization'
    if logging:
        print 'Enabling event logging'
    if nogetfqdn:
        print 'Disabling getfqdn'
    p = panel.Panel(rows, cols, rwidth, rheight)
    host = 'localhost' if localhost else socket.gethostname()
    print 'Running server on host %s, port %d' % (host, port)
    p.runserver(host, port, logging=logging, nodelay = optimize, nogetfqdn = nogetfqdn)

run(sys.argv[0], sys.argv[1:])


    
