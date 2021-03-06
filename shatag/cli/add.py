#!/usr/bin/env python3
# Copyright 2010 Maxime Augier
# Distributed under the terms of the GNU General Public License

import argparse
import os
import re
import shatag
import subprocess
import sys

# fileLineIter, stolen from Douglas Alan


def fileLineIter(inputFile,
                 inputNewline="\n",
                 outputNewline=None,
                 readSize=8192):
    """Like the normal file iter but you can set what string indicates newline.

    The newline string can be arbitrarily long; it need not be restricted to a
    single character. You can also set the read size and control whether or not
    the newline string is left on the end of the iterated lines.  Setting
    newline to '\0' is particularly good for use with an input file created with
    something like "os.popen('find -print0')".
    """
    if outputNewline is None:
        outputNewline = inputNewline
    partialLine = ''
    while True:
        charsJustRead = inputFile.read(readSize)
        if not charsJustRead:
            break
        partialLine += charsJustRead
        lines = partialLine.split(inputNewline)
        partialLine = lines.pop()
        for line in lines:
            yield line + outputNewline
    if partialLine:
        yield partialLine
# End of stolen fragment


def main():
    parser = argparse.ArgumentParser(description='Receives output from "shatag -0" and records it in the local database ')
    parser.add_argument('-d', '--database', metavar='DB', help='path to sqlite database (defaults to $HOME/.shatagdb)')
    parser.add_argument('-v', '--verbose', action='store_true', help='report additions to the database')
    parser.add_argument('-b', '--base', metavar='PATH', help='base path getting processed (for deletion of older entries)', default='/')
    parser.add_argument('name', metavar='NAME', help='name of storage location')

    args = parser.parse_args()

    if args.base[-1] != '/':
        args.base += '/'

    store = shatag.Store(url=args.database, name=args.name)

    pattern = re.compile('([0-9a-f]{64})  (.*)')

    new_rows = 0
    old_rows = store.clear(args.base)

    for entry in fileLineIter(sys.stdin, inputNewline='\0', outputNewline=''):
        match = pattern.match(entry)
        if match is not None:
            (hash, filename) = match.group(1, 2)
            if args.verbose:
                print("{0}  {1}\n".format(hash, filename))
            new_rows += 1
            store.record(args.name, filename, hash)
        else:
            print('Error: incorrectly formatted entry\n', file=sys.stderr)

    if new_rows > 0:
        store.commit()

        print('{0} rows added, {1} rows deleted ({2})'.format(new_rows, old_rows, new_rows - old_rows), file=sys.stderr)

    else:
        store.rollback()
        print('No records received, preserving old database.', file=sys.stderr)
