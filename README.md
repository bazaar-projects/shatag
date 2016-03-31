
# Overview

  Shatag is a tool for computing and caching file checksums, and do
remote duplicate detection. Files are compared on their SHA-256 hash
to find duplicates, and will use filesystem extended attributes to cache
the checksum values.

# Requirements

 - Python 3
 - argparse
 - pyxattr or xattr (until other backends become available)
 - If you want to use a database store: sqlite3 or psycopg2
 - If you want to use an http remote store: requests
 - If you want to use the http store server: the Bottle framework

# Quickstart

  Before you attempt to use shatag, make sure the filesystem you will be working on has
support for user extended attributes. This is typically enabled by adding the `user_xattr`
mount option to the appropriate filesystem in `/etc/fstab`. You can also enable support
without unmounting with:

        sudo mount -o remount,user_xattr /mountpoint

If you want to use a remote database, setup a configuration file ~/.shatagrc with contents like:

        database: "pg: dbname=shatag host=localhost user=shatag password=xxxsecretpasswordxxx"

Next, start tagging some files with: 
  
        shatag -qrt /home/data

By default, shatag will display checksums in a format compatible with the output of `sha256`,
if the timestamps indicate that the file has not changed:

        shatag some file


# Database mode

Shatag can also record hashes to a SQL database, and query it to find duplicate files and their other locations.

Upload the proper tags to the database with:
  
        shatag -qrp /home/data
        
(you could combine the -t and -p flags in one command)

You can start a daemon to automatically recompute tags when needed:

  shatagd -dr /home/data

Check for duplicates in a directory with

  shatag -rl .

# Commands

  shatag(1) is the main tool, and used for computing and displaying file checksums,
as well as reporting duplicate.

  shatagd(1) will monitor directories for file changes and update the checksums automatically.
it requires pyinotify.

  Refer to the man pages of these tools for more information.

# Implementation

Shatag stores a single sha256 checksum in hexadecimal (64 ascii characters) in the "user.shatag.sha256" attribute,
and the modification time of the file at the moment the checksum was computed, as decimal unix time, in "user.shatag.ts".

 The checksum is considered valid if the modification time of the file is still equal to the timestamp stored in the attribute.
With respect to race conditions, shatag will always read the stored timestamp before the checksum, and the checksum before
the actual mtime; it will always write the checksum before the timestamp. In case of accidental parallel operation, shatag
will rather compute unneccesary checksums than consider an old checksum valid.

The local sqlite database contains a single table:
  
        create table contents(hash text, size integer, name text, path text, primary key (hash,name,path));

When querying the database, shatag will lookup the hash and count the matching paths at each location. The file will
be considered a dupe if any location has the file more than once.
