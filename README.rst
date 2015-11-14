pysqlcipher3
============

This library is a fork of pysqlcipher targeted for use with Python 3, 
although support for Python 2 is still maintained. It is still in the 
beta state, although this library contains minimal new code and 
instead heavily pulls from the core Python sqlite source code while 
linking against libsqlcipher.


Original code (c) 2004-2007 Gerhard Häring

Packaging for SQLCipher (c) 2013-2014 Kali Kaneko

Python 3 packaging for SQLCipher (c) 2015 David Riggleman

Usage
-----
You have to pass the ``PRAGMA key`` before doing any operations::

  from pysqlcipher3 import dbapi2 as sqlite
  conn = sqlite.connect('test.db')
  c = conn.cursor()
  c.execute("PRAGMA key='password'")
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

Build against libsqlcipher
--------------------------
For production use, you should build against ``libsqlcipher``, which must
be installed on your system prior to installation. Consult your operating
system documentation for how to install SQL Cipher. This is the
default install option.

Build against amalgamation
--------------------------
For convenience during development, you can use a sqlcipher amalgamation
during the install. You will need to obtain the amalgamation from external
sources or build it yourself from https://github.com/sqlcipher/sqlcipher

To build using the amalgamation, you can do it like this::

  python setup.py build_amalgamation

And then::

  python setup.py install
  
How to Compile pysqlcipher3 on Windows 
--------------------------------------

1) Installed the free VS 2015 Community Edition 

Note: make sure to select all the GCC options (VC++, C++, etc). If you are unsure select all options.

2) Installed a prebuilt OpenSSL binary (Win32 OpenSSL v1.0.2d or later) from https://slproweb.com/products/Win32OpenSSL.html


3) Confirm that the OPENSSL_CONF environment variable is set properly in evironment variables. See http://www.computerhope.com/issues/ch000549.htm

Note: This should not be root openssl path (ex: C:/openssl-Win32), but instead should be the path to the config file (ex: C:/openssl-Win32/bin/openssl.cfg)


4) Copy the openssl folder in (C:/OpenSSL-Win32/include/openssl) directory to the VC include directory (ex: C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/include)

Note: Confirm the following path exists (../../VC/include/openssl/aes.h)

5) Install Python 3.5 (32 bit). 

Note: If you have python 64 bit installed you may have to uninstall it before installing python 32 bit.

6) Use the SQL Cipher 3 amalgamations or you may compile the latest SQL Cipher amalgamation by following this tutorial http://www.jerryrw.com/howtocompile.php. 

7) Click start, Run, cmd. In the CMD prompt navigate to the folder where you checked out this repository. Run "python setup.py build_amalgamation"

8) Then run "python setup.py install"

9) Test the new library by attempting to decrypt a database.

Note: If the decrypt fails please check that you have the correct amalagamation files.
