pysqlcipher3
============

**Note: this project is no longer being actively maintained. Security vulnerabilities may exist in this code. Use at your own risk.**

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
This is the default install option. For production use, you should build 
against ``libsqlcipher``, which must be installed on your system prior to 
installation. Consult your operating system documentation for how to 
install SQL Cipher. You can also manually build SQL Cipher by cloning 
https://github.com/sqlcipher/sqlcipher and following the build instructions.

Build against amalgamation
--------------------------
For convenience during development, you can use a sqlcipher amalgamation
during the install. You will need to obtain the amalgamation from external
sources or build it yourself from https://github.com/sqlcipher/sqlcipher.


To build using the amalgamation, you can do it like this::

  python setup.py build_amalgamation

And then::

  python setup.py install

**32 Bit Windows Setup Instructions (using Visual Studio)**

1. **Install Visual Studio 2015**: if you do not have a paid license, the Community Edition will work fine. Make sure to select all the C++ options during the installation process.

2. **Install OpenSSL**: you can either download the source and build locally or install a prebuilt OpenSSL binary from https://slproweb.com/products/Win32OpenSSL.html (use the latest version)

3. **Confirm that the OPENSSL_CONF environment variable is set properly**: this should not be root OpenSSL path (ex: C:\\openssl-Win32), but instead should be the path to the config file (ex: C:\\openssl-Win32\\bin\\openssl.cfg)

4. **Copy the OpenSSL folder (C:\\openssl-Win32\\include\\openssl) to the VC include directory (ex: C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\include)**: confirm the following path exists (\\VC\\include\\openssl\\aes.h)

5. **Install the latest version of Python 3 (32-bit)**: if you have Python 64-bit installed, you may have to uninstall it before installing Python 32-bit.
  
6. **Use the SQL Cipher 3 amalgamation**: if needed, directions for building SQL Cipher can be found on the following tutorial: http://www.jerryrw.com/howtocompile.ph

7. **Follow the general instructions for building the amalgamation**

**64 Bit Windows Setup Instructions (using Visual Studio)**

Follow the same instructions as above except for the following:

1. **Make sure that you are using OpenSSL-Win64**

2. **Set the PATH to the Win64 environment**

3. **Copy the OpenSSL folder**

4. **Build the amalgamation and install with the latest Python x64**
