CC = gcc
CFLAGS = -O2 -Wall -g

ROOT = ~/Documents
SYNCHDIR = $(ROOT)/"My Dropbox"/Programs/pysort

SYNCHPROG = /cygdrive/c/src/synch/synch

PFILES = Makefile bridge.py hsv.py psort.py panel.py panelserver.py

drop: $(PFILES)
	cp -p $(PFILES) $(SYNCHDIR)

pickup:
	cp -p $(PFILES)/* .

afs:
	$(SYNCHPROG) bridge.syn

matrix.o: matrix.h matrix.c
	$(CC) $(CFLAGS) -c matrix.c

mtest: mtest.c matrix.h matrix.o
	$(CC) $(CFLAGS) -o mtest mtest.c matrix.o -lm

lsquare: lsquare.c matrix.h matrix.o
	$(CC) $(CFLAGS) -o lsquare lsquare.c matrix.o -lm

