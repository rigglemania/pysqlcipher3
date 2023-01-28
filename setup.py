# -*- coding: ISO-8859-1 -*-
# setup.py: the distutils script
#
# Copyright (C) 2015 David Riggleman <davidriggleman@gmail.com>
# Copyright (C) 2013 Kali Kaneko <kali@futeisha.org> (sqlcipher support)
# Copyright (C) 2005-2010 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlcipher.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
import os
import setuptools
import sys

from distutils import log
from distutils.command.build_ext import build_ext
from setuptools import Extension

# If you need to change anything, it should be enough to change setup.cfg.

PACKAGE_NAME = "pysqlcipher3"
VERSION = '1.2.0'
LONG_DESCRIPTION = \
"""Python interface to SQLCipher

pysqlcipher3 is an interface to the SQLite 3.x embedded relational
database engine. It is almost fully compliant with the Python database API
version 2.0. At the same time, it also exposes the unique features of
SQLCipher. Prior to installation, libsqlcipher must already be installed
on your system, with the process dependent on your operating system."""

# define sqlite sources
sources = [os.path.join("src", "python" + str(sys.version_info[0]), source)
           for source in ["module.c", "connection.c", "cursor.c", "cache.c",
                          "microprotocols.c", "prepare_protocol.c",
                          "statement.c", "util.c", "row.c"]]

# define packages
packages = [PACKAGE_NAME, PACKAGE_NAME + ".test"]

if sys.version_info[0] < 3:
    packages.append(PACKAGE_NAME + ".test.python2")
    EXTENSION_MODULE_NAME = "._sqlite"
else:
    packages.append(PACKAGE_NAME + ".test.python3")
    EXTENSION_MODULE_NAME = "._sqlite3"

# Work around clang raising hard error for unused arguments
if sys.platform == "darwin":
    os.environ['CFLAGS'] = "-Qunused-arguments"
    log.info("CFLAGS: " + os.environ['CFLAGS'])


def quote_argument(arg):
    quote = '"' if sys.platform != 'win32' else '\\"'
    return quote + arg + quote

define_macros = [('MODULE_NAME', quote_argument(PACKAGE_NAME + '.dbapi2'))]


class SystemLibSQLCipherBuilder(build_ext):
    description = "Builds a C extension linking against libsqlcipher library"

    def build_extension(self, ext):
        log.info(self.description)
        build_ext.build_extension(self, ext)


class AmalgationLibSQLCipherBuilder(build_ext):
    description = "Builds a C extension using a sqlcipher amalgamation"

    amalgamation_root = "amalgamation"
    amalgamation_header = os.path.join(amalgamation_root, 'sqlite3.h')
    amalgamation_source = os.path.join(amalgamation_root, 'sqlite3.c')

    amalgamation_message = \
        """SQL Cipher amalgamation not found. Please download or build the
        amalgamation and make sure the following files are present in the
        amalgamation folder: sqlite3.h, sqlite3.c"""

    def check_amalgamation(self):
        if not os.path.exists(self.amalgamation_root):
            os.mkdir(self.amalgamation_root)

        header_exists = os.path.exists(self.amalgamation_header)
        source_exists = os.path.exists(self.amalgamation_source)
        if not header_exists or not source_exists:
            raise RuntimeError(self.amalgamation_message)

    def build_extension(self, ext):
        log.info(self.description)

        # it is responsibility of user to provide amalgamation
        self.check_amalgamation()

        # build with fulltext search enabled
        ext.define_macros.append(("SQLITE_ENABLE_FTS3", "1"))
        ext.define_macros.append(("SQLITE_ENABLE_RTREE", "1"))

        # SQLCipher options
        ext.define_macros.append(("SQLITE_ENABLE_LOAD_EXTENSION", "1"))
        ext.define_macros.append(("SQLITE_HAS_CODEC", "1"))
        ext.define_macros.append(("SQLITE_TEMP_STORE", "2"))

        ext.include_dirs.append(self.amalgamation_root)
        ext.sources.append(os.path.join(self.amalgamation_root, "sqlite3.c"))

        if sys.platform == "win32":
            # Try to locate openssl
            openssl_conf = os.environ.get('OPENSSL_CONF')
            if not openssl_conf:
                error_message = 'Fatal error: OpenSSL could not be detected!'
                raise RuntimeError(error_message)

            openssl = os.path.dirname(os.path.dirname(openssl_conf))
            openssl_lib_path = os.path.join(openssl, "lib")

            # Configure the compiler
            ext.include_dirs.append(os.path.join(openssl, "include"))
            ext.define_macros.append(("inline", "__inline"))

            # Configure the linker
            ext.extra_link_args.append("libeay32.lib")
            ext.extra_link_args.append('/LIBPATH:' + openssl_lib_path)
        else:
            ext.extra_link_args.append("-lcrypto")

        build_ext.build_extension(self, ext)

    def __setattr__(self, k, v):
        # Make sure we don't link against the SQLite
        # library, no matter what setup.cfg says
        if k == "libraries":
            v = None
        self.__dict__[k] = v


def get_setup_args():
    return dict(
        name=PACKAGE_NAME,
        version=VERSION,
        python_requires=">=3.3",
        description="DB-API 2.0 interface for SQLCIPHER 3.x",
        long_description=LONG_DESCRIPTION,
        author="David Riggleman",
        author_email="davidriggleman@gmail.com",
        license="zlib/libpng",
        platforms="ALL",
        url="https://github.com/rigglemania/pysqlcipher3",
        package_dir={PACKAGE_NAME: "lib"},
        packages=packages,
        ext_modules=[Extension(
            name=PACKAGE_NAME + EXTENSION_MODULE_NAME,
            sources=sources,
            define_macros=define_macros)
        ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: zlib/libpng License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: C",
            "Programming Language :: Python",
            "Topic :: Database :: Database Engines/Servers",
            "Topic :: Software Development :: Libraries :: Python Modules"],
        cmdclass={
            "build_amalgamation": AmalgationLibSQLCipherBuilder,
            "build_ext": SystemLibSQLCipherBuilder
        }
    )


def main():
    try:
        setuptools.setup(**get_setup_args())
    except BaseException as ex:
        log.info(str(ex))

if __name__ == "__main__":
    main()
