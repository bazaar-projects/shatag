#!/usr/bin/env python3
# Copyright 2010 Maxime Augier
# Distributed under the terms of the GNU General Public License

import shatag
import psycopg2

from shatag.base import SQLDatabaseIncompatibleError


class PgStore(shatag.base.SQLStore):
    """A postgresql store using psycopg2."""
    def __init__(self, url=None, name=None):
        db = psycopg2.connect(url[3:])
        self.db = db

        cursor = db.cursor()
        self.cursor = cursor

        super(PgStore,self).__init__(url, name)

        try:
            cursor.execute(
                'create table contents(hash varchar(64), size bigint, name varchar(50), path varchar(100), primary key (name, path))')
            cursor.execute('create index content_hash on contents(hash)')
            cursor.execute('create table version(user_version bigint)')
            cursor.execute('insert into version(user_version) values(1)')
        except psycopg2.ProgrammingError:
            # Check database version.
            try:
                cursor.execute('select user_version from version')
                user_version = cursor.fetchone()[0]
                if user_version != 1:
                    message = """
It seems that you are using an old version of PostgreSQL store. New versions of
shatag changed PostgreSQL database schema.

You have to clean up the PostgreSQL database mentioned below, and record all
tags again (e.g. `-pqr`). Alternatively, you can use a new PostgreSQL store,
via using a command line option (`-d`) or editing configuration file
(`~/.shatagrc`).

Since we added new meta information (size) of files, we cannot upgrade the
sqlite store automatically. You have to start over.
                    """
                    raise SQLDatabaseIncompatibleError(url, message)
            except SQLDatabaseIncompatibleError as e:
                print(e.message)
                print('Incompatible PostgreSQL store:', e.url)
                import sys
                # As defined in `sysexits.h`:
                #       #define EX_DATAERR    65    /* data format error */
                sys.exit(65)

            db.rollback()


    # reimplementing these because psycopg2 does not handle classic placeholders correctly
    def clear(self, base='/',name=None):
        if name is None:
            name = self.name
        self.cursor.execute('delete from contents where name = %(name)s and substr(path,1,length(%(base)s)) like %(base)s', {'name': name, 'base': base})
        return self.cursor.rowcount


    def record(self, name, path, size, tag):
        d = {'name': name, 'path': path, 'size': size, 'tag':tag }
        self.cursor.execute('delete from contents where name = %(name)s and path = %(path)s', d)
        self.cursor.execute('insert into contents(hash,size,name,path) values(%(tag)s,%(size)s,%(name)s,%(path)s)', d)

    def fetch(self,hash):
        self.cursor.execute('select name,path from contents where hash = %(hash)s', {'hash':hash})
        return self.cursor

