#!/usr/bin/env python3
# Copyright 2010 Maxime Augier
# Distributed under the terms of the GNU General Public License

import shatag.base
import sqlite3

from shatag.base import SQLDatabaseIncompatibleError


class LocalStore(shatag.base.SQLStore):
    def __init__(self, url=None, name=None):
        db = sqlite3.connect(url)
        self.db = db

        cursor = self.db.cursor()
        self.cursor = cursor

        super().__init__(url, name)


        try:
            cursor.execute(
                'create table contents(hash text, size integer, name text, path text, primary key(name,path))')
            cursor.execute('create index contents_hash on contents(hash)')
            cursor.execute('pragma user_version = 1')
        except sqlite3.OperationalError as e:
            # Table already created. Check database version.
            try:
                cursor.execute('pragma user_version')
                user_version = cursor.fetchone()[0]
                if user_version == 0:
                    message = """
It seems that you are using an old version of sqlite store. New versions of
shatag changed sqlite database schema.

You have to delete the sqlite file mentioned below, and record all tags again
(e.g. `-pqr`). Alternatively, you can use a new sqlite store, via using a
command line option (`-d`) or editing configuration file (`~/.shatagrc`).

Since we added new meta information (size) of files, we cannot upgrade the
sqlite store automatically. You have to start over.
                    """
                    raise SQLDatabaseIncompatibleError(url, message)
            except SQLDatabaseIncompatibleError as e:
                print(e.message)
                print('Incompatible sqlite store:', e.url)
                import sys
                # As defined in `sysexits.h`:
                #       #define EX_DATAERR      65      /* data format error */
                sys.exit(65)


    def record(self, name, path, size, tag):
        path = path.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
        self.cursor.execute('insert or replace into contents(hash, size, name,path) values (?, ?, ?, ?)', (tag, size, name, path))
