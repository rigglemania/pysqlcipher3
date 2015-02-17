pysqlcipher3
============

This library is a fork of pysqlcipher targeted for use with Python 3, 
although support for Python 2 is still maintained. It is still in the 
beta state, although this library contains minimal new code and 
instead heavily pulls from the core Python sqlite source code while 
linking against libsqlcipher.


Original code (c) 2004-2007 Gerhard Häring

Packaging for SQLCipher (c) 2013-2014 Kali Kaneko

Python 3 Packaging for SQLCipher (c) 2015 David Riggleman

Usage
-----
You have to pass the ``PRAGMA key`` before doing any operations::

  from pysqlcipher3 import dbapi2 as sqlite
  conn = sqlite.connect('test.db')
  c = conn.cursor()
  c.execute("PRAGMA key='test'")
  c.execute('''create table stocks (date text, trans text, symbol text, qty real, price real)''')
  c.execute("""insert into stocks values ('2006-01-05','BUY','RHAT',100,35.14)""")
  conn.commit()
  c.close()

You can quickly verify that your database file in indeed encrypted::

  hexdump -C test.db                                                                                                        
  ab 7f 61 7a 33 9d 07 f4  08 68 c9 b0 4f e3 34 60  |..az3....h..O.4`|
  bb 9d 9c 3d 9e ce 69 57  b6 2f 36 c4 fd 13 bd 61  |...=..iW./6....a|
  77 bf e3 1d 65 b5 ea f7  d2 fc 98 31 23 66 a0 1e  |w...e......1#f..|
  a4 4f fa 66 49 36 84 a1  3e 0c 21 98 84 07 eb 07  |.O.fI6..>.!.....|

Build against amalgamation
--------------------------

For production use, you should build against ``libsqlcipher`` installed in your
system. This is default setup install option.

For convenience during development, you can use a sqlcipher amalgamation
during the install. You will need to obtain the amalgamation from external
sources or build it yourself from https://github.com/sqlcipher/sqlcipher

To build using the amalgamation, you can do it like this::

  python setup.py build_amalgamation

And then::

  python setup.py install
