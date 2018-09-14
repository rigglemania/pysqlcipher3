#-*- coding: iso-8859-1 -*-
# pysqlite2/test/dbapi.py: tests for DB-API compliance
#
# Copyright (C) 2004-2010 Gerhard H�ring <gh@ghaering.de>
#
# This file is part of pysqlite.
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
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import unittest
import pysqlcipher3.dbapi2 as sqlite
try:
    import threading
except ImportError:
    threading = None

from test.support import TESTFN, unlink


class ModuleTests(unittest.TestCase):
    def testAPILevel(self):
        self.assertEqual(sqlite.apilevel, "2.0",
                         "apilevel is %s, should be 2.0" % sqlite.apilevel)

    def testThreadSafety(self):
        self.assertEqual(sqlite.threadsafety, 1,
                         "threadsafety is %d, should be 1" % sqlite.threadsafety)

    def testParamStyle(self):
        self.assertEqual(sqlite.paramstyle, "qmark",
                         "paramstyle is '%s', should be 'qmark'" %
                         sqlite.paramstyle)

    def testWarning(self):
        self.assertTrue(issubclass(sqlite.Warning, Exception),
                     "Warning is not a subclass of Exception")

    def testError(self):
        self.assertTrue(issubclass(sqlite.Error, Exception),
                        "Error is not a subclass of Exception")

    def testInterfaceError(self):
        self.assertTrue(issubclass(sqlite.InterfaceError, sqlite.Error),
                        "InterfaceError is not a subclass of Error")

    def testDatabaseError(self):
        self.assertTrue(issubclass(sqlite.DatabaseError, sqlite.Error),
                        "DatabaseError is not a subclass of Error")

    def testDataError(self):
        self.assertTrue(issubclass(sqlite.DataError, sqlite.DatabaseError),
                        "DataError is not a subclass of DatabaseError")

    def testOperationalError(self):
        self.assertTrue(issubclass(sqlite.OperationalError, sqlite.DatabaseError),
                        "OperationalError is not a subclass of DatabaseError")

    def testIntegrityError(self):
        self.assertTrue(issubclass(sqlite.IntegrityError, sqlite.DatabaseError),
                        "IntegrityError is not a subclass of DatabaseError")

    def testInternalError(self):
        self.assertTrue(issubclass(sqlite.InternalError, sqlite.DatabaseError),
                        "InternalError is not a subclass of DatabaseError")

    def testProgrammingError(self):
        self.assertTrue(issubclass(sqlite.ProgrammingError, sqlite.DatabaseError),
                        "ProgrammingError is not a subclass of DatabaseError")

    def testNotSupportedError(self):
        self.assertTrue(issubclass(sqlite.NotSupportedError,
                                   sqlite.DatabaseError),
                        "NotSupportedError is not a subclass of DatabaseError")

class ConnectionTests(unittest.TestCase):

    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        cu = self.cx.cursor()
        cu.execute("create table test(id integer primary key, name text)")
        cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cx.close()

    def testCommit(self):
        self.cx.commit()

    def testCommitAfterNoChanges(self):
        """
        A commit should also work when no changes were made to the database.
        """
        self.cx.commit()
        self.cx.commit()

    def testRollback(self):
        self.cx.rollback()

    def testRollbackAfterNoChanges(self):
        """
        A rollback should also work when no changes were made to the database.
        """
        self.cx.rollback()
        self.cx.rollback()

    def testCursor(self):
        cu = self.cx.cursor()

    def testFailedOpen(self):
        YOU_CANNOT_OPEN_THIS = "/foo/bar/bla/23534/mydb.db"
        try:
            con = sqlite.connect(YOU_CANNOT_OPEN_THIS)
        except sqlite.OperationalError:
            return
        self.fail("should have raised an OperationalError")

    def testClose(self):
        self.cx.close()

    def testExceptions(self):
        # Optional DB-API extension.
        self.assertEqual(self.cx.Warning, sqlite.Warning)
        self.assertEqual(self.cx.Error, sqlite.Error)
        self.assertEqual(self.cx.InterfaceError, sqlite.InterfaceError)
        self.assertEqual(self.cx.DatabaseError, sqlite.DatabaseError)
        self.assertEqual(self.cx.DataError, sqlite.DataError)
        self.assertEqual(self.cx.OperationalError, sqlite.OperationalError)
        self.assertEqual(self.cx.IntegrityError, sqlite.IntegrityError)
        self.assertEqual(self.cx.InternalError, sqlite.InternalError)
        self.assertEqual(self.cx.ProgrammingError, sqlite.ProgrammingError)
        self.assertEqual(self.cx.NotSupportedError, sqlite.NotSupportedError)

    def testInTransaction(self):
        # Can't use db from setUp because we want to test initial state.
        cx = sqlite.connect(":memory:")
        cu = cx.cursor()
        self.assertEqual(cx.in_transaction, False)
        cu.execute("create table transactiontest(id integer primary key, name text)")
        self.assertEqual(cx.in_transaction, False)
        cu.execute("insert into transactiontest(name) values (?)", ("foo",))
        self.assertEqual(cx.in_transaction, True)
        cu.execute("select name from transactiontest where name=?", ["foo"])
        row = cu.fetchone()
        self.assertEqual(cx.in_transaction, True)
        cx.commit()
        self.assertEqual(cx.in_transaction, False)
        cu.execute("select name from transactiontest where name=?", ["foo"])
        row = cu.fetchone()
        self.assertEqual(cx.in_transaction, False)

    def testInTransactionRO(self):
        with self.assertRaises(AttributeError):
            self.cx.in_transaction = True

    def testOpenUri(self):
        if sqlite.sqlite_version_info < (3, 7, 7):
            with self.assertRaises(sqlite.NotSupportedError):
                sqlite.connect(':memory:', uri=True)
            return
        self.addCleanup(unlink, TESTFN)
        with sqlite.connect(TESTFN) as cx:
            cx.execute('create table test(id integer)')
        with sqlite.connect('file:' + TESTFN, uri=True) as cx:
            cx.execute('insert into test(id) values(0)')
        with sqlite.connect('file:' + TESTFN + '?mode=ro', uri=True) as cx:
            with self.assertRaises(sqlite.OperationalError):
                cx.execute('insert into test(id) values(1)')


class CursorTests(unittest.TestCase):
    def setUp(self):
        self.cx = sqlite.connect(":memory:")
        self.cu = self.cx.cursor()
        self.cu.execute("create table test(id integer primary key, name text, income number)")
        self.cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cu.close()
        self.cx.close()

    def testExecuteNoArgs(self):
        self.cu.execute("delete from test")

    def testExecuteIllegalSql(self):
        try:
            self.cu.execute("select asdf")
            self.fail("should have raised an OperationalError")
        except sqlite.OperationalError:
            return
        except:
            self.fail("raised wrong exception")

    def testExecuteTooMuchSql(self):
        try:
            self.cu.execute("select 5+4; select 4+5")
            self.fail("should have raised a Warning")
        except sqlite.Warning:
            return
        except:
            self.fail("raised wrong exception")

    def testExecuteTooMuchSql2(self):
        self.cu.execute("select 5+4; -- foo bar")

    def testExecuteTooMuchSql3(self):
        self.cu.execute("""
            select 5+4;

            /*
            foo
            */
            """)

    def testExecuteWrongSqlArg(self):
        try:
            self.cu.execute(42)
            self.fail("should have raised a ValueError")
        except ValueError:
            return
        except:
            self.fail("raised wrong exception.")

    def testExecuteArgInt(self):
        self.cu.execute("insert into test(id) values (?)", (42,))

    def testExecuteArgFloat(self):
        self.cu.execute("insert into test(income) values (?)", (2500.32,))

    def testExecuteArgString(self):
        self.cu.execute("insert into test(name) values (?)", ("Hugo",))

    def testExecuteArgStringWithZeroByte(self):
        self.cu.execute("insert into test(name) values (?)", ("Hu\x00go",))

        self.cu.execute("select name from test where id=?", (self.cu.lastrowid,))
        row = self.cu.fetchone()
        self.assertEqual(row[0], "Hu\x00go")

    def testExecuteWrongNoOfArgs1(self):
        # too many parameters
        try:
            self.cu.execute("insert into test(id) values (?)", (17, "Egon"))
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def testExecuteWrongNoOfArgs2(self):
        # too little parameters
        try:
            self.cu.execute("insert into test(id) values (?)")
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def testExecuteWrongNoOfArgs3(self):
        # no parameters, parameters are needed
        try:
            self.cu.execute("insert into test(id) values (?)")
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def testExecuteParamList(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=?", ["foo"])
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def testExecuteParamSequence(self):
        class L(object):
            def __len__(self):
                return 1
            def __getitem__(self, x):
                assert x == 0
                return "foo"

        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=?", L())
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def testExecuteDictMapping(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=:name", {"name": "foo"})
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def testExecuteDictMapping_Mapping(self):
        class D(dict):
            def __missing__(self, key):
                return "foo"

        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=:name", D())
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def testExecuteDictMappingTooLittleArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        try:
            self.cu.execute("select name from test where name=:name and id=:id", {"name": "foo"})
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def testExecuteDictMappingNoArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        try:
            self.cu.execute("select name from test where name=:name")
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def testExecuteDictMappingUnnamed(self):
        self.cu.execute("insert into test(name) values ('foo')")
        try:
            self.cu.execute("select name from test where name=?", {"name": "foo"})
            self.fail("should have raised ProgrammingError")
        except sqlite.ProgrammingError:
            pass

    def testClose(self):
        self.cu.close()

    def testRowcountExecute(self):
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("update test set name='bar'")
        self.assertEqual(self.cu.rowcount, 2)

    def testRowcountSelect(self):
        """
        pysqlite does not know the rowcount of SELECT statements, because we
        don't fetch all rows after executing the select statement. The rowcount
        has thus to be -1.
        """
        self.cu.execute("select 5 union select 6")
        self.assertEqual(self.cu.rowcount, -1)

    def testRowcountExecutemany(self):
        self.cu.execute("delete from test")
        self.cu.executemany("insert into test(name) values (?)", [(1,), (2,), (3,)])
        self.assertEqual(self.cu.rowcount, 3)

    def testTotalChanges(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        if self.cx.total_changes < 2:
            self.fail("total changes reported wrong value")

    # Checks for executemany:
    # Sequences are required by the DB-API, iterators
    # enhancements in pysqlite.

    def testExecuteManySequence(self):
        self.cu.executemany("insert into test(income) values (?)", [(x,) for x in range(100, 110)])

    def testExecuteManyIterator(self):
        class MyIter:
            def __init__(self):
                self.value = 5

            def __next__(self):
                if self.value == 10:
                    raise StopIteration
                else:
                    self.value += 1
                    return (self.value,)

        self.cu.executemany("insert into test(income) values (?)", MyIter())

    def testExecuteManyGenerator(self):
        def mygen():
            for i in range(5):
                yield (i,)

        self.cu.executemany("insert into test(income) values (?)", mygen())

    def testExecuteManyWrongSqlArg(self):
        try:
            self.cu.executemany(42, [(3,)])
            self.fail("should have raised a ValueError")
        except ValueError:
            return
        except:
            self.fail("raised wrong exception.")

    def testExecuteManySelect(self):
        try:
            self.cu.executemany("select ?", [(3,)])
            self.fail("should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            return
        except:
            self.fail("raised wrong exception.")

    def testExecuteManyNotIterable(self):
        try:
            self.cu.executemany("insert into test(income) values (?)", 42)
            self.fail("should have raised a TypeError")
        except TypeError:
            return
        except Exception as e:
            print("raised", e.__class__)
            self.fail("raised wrong exception.")

    def testFetchIter(self):
        # Optional DB-API extension.
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(id) values (?)", (5,))
        self.cu.execute("insert into test(id) values (?)", (6,))
        self.cu.execute("select id from test order by id")
        lst = []
        for row in self.cu:
            lst.append(row[0])
        self.assertEqual(lst[0], 5)
        self.assertEqual(lst[1], 6)

    def testFetchone(self):
        self.cu.execute("select name from test")
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")
        row = self.cu.fetchone()
        self.assertEqual(row, None)

    def testFetchoneNoStatement(self):
        cur = self.cx.cursor()
        row = cur.fetchone()
        self.assertEqual(row, None)

    def testArraySize(self):
        # must default ot 1
        self.assertEqual(self.cu.arraysize, 1)

        # now set to 2
        self.cu.arraysize = 2

        # now make the query return 3 rows
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(name) values ('A')")
        self.cu.execute("insert into test(name) values ('B')")
        self.cu.execute("insert into test(name) values ('C')")
        self.cu.execute("select name from test")
        res = self.cu.fetchmany()

        self.assertEqual(len(res), 2)

    def testFetchmany(self):
        self.cu.execute("select name from test")
        res = self.cu.fetchmany(100)
        self.assertEqual(len(res), 1)
        res = self.cu.fetchmany(100)
        self.assertEqual(res, [])

    def testFetchmanyKwArg(self):
        """Checks if fetchmany works with keyword arguments"""
        self.cu.execute("select name from test")
        res = self.cu.fetchmany(size=100)
        self.assertEqual(len(res), 1)

    def testFetchall(self):
        self.cu.execute("select name from test")
        res = self.cu.fetchall()
        self.assertEqual(len(res), 1)
        res = self.cu.fetchall()
        self.assertEqual(res, [])

    def testSetinputsizes(self):
        self.cu.setinputsizes([3, 4, 5])

    def testSetoutputsize(self):
        self.cu.setoutputsize(5, 0)

    def testSetoutputsizeNoColumn(self):
        self.cu.setoutputsize(42)

    def testCursorConnection(self):
        # Optional DB-API extension.
        self.assertEqual(self.cu.connection, self.cx)

    def testWrongCursorCallable(self):
        try:
            def f(): pass
            cur = self.cx.cursor(f)
            self.fail("should have raised a TypeError")
        except TypeError:
            return
        self.fail("should have raised a ValueError")

    def testCursorWrongClass(self):
        class Foo: pass
        foo = Foo()
        try:
            cur = sqlite.Cursor(foo)
            self.fail("should have raised a ValueError")
        except TypeError:
            pass

@unittest.skipUnless(threading, 'This test requires threading.')
class ThreadTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(id integer primary key, name text, bin binary, ratio number, ts timestamp)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def testConCursor(self):
        def run(con, errors):
            try:
                cur = con.cursor()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testConCommit(self):
        def run(con, errors):
            try:
                con.commit()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testConRollback(self):
        def run(con, errors):
            try:
                con.rollback()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testConClose(self):
        def run(con, errors):
            try:
                con.close()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testCurImplicitBegin(self):
        def run(cur, errors):
            try:
                cur.execute("insert into test(name) values ('a')")
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testCurClose(self):
        def run(cur, errors):
            try:
                cur.close()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testCurExecute(self):
        def run(cur, errors):
            try:
                cur.execute("select name from test")
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def testCurIterNext(self):
        def run(cur, errors):
            try:
                row = cur.fetchone()
                errors.append("did not raise ProgrammingError")
                return
            except sqlite.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        self.cur.execute("select name from test")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

class ConstructorTests(unittest.TestCase):
    def testDate(self):
        d = sqlite.Date(2004, 10, 28)

    def testTime(self):
        t = sqlite.Time(12, 39, 35)

    def testTimestamp(self):
        ts = sqlite.Timestamp(2004, 10, 28, 12, 39, 35)

    def testDateFromTicks(self):
        d = sqlite.DateFromTicks(42)

    def testTimeFromTicks(self):
        t = sqlite.TimeFromTicks(42)

    def testTimestampFromTicks(self):
        ts = sqlite.TimestampFromTicks(42)

    def testBinary(self):
        b = sqlite.Binary(b"\0'")

class ExtensionTests(unittest.TestCase):
    def testScriptStringSql(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.executescript("""
            -- bla bla
            /* a stupid comment */
            create table a(i);
            insert into a(i) values (5);
            """)
        cur.execute("select i from a")
        res = cur.fetchone()[0]
        self.assertEqual(res, 5)

    def testScriptSyntaxError(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        raised = False
        try:
            cur.executescript("create table test(x); asdf; create table test2(x)")
        except sqlite.OperationalError:
            raised = True
        self.assertEqual(raised, True, "should have raised an exception")

    def testScriptErrorNormal(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        raised = False
        try:
            cur.executescript("create table test(sadfsadfdsa); select foo from hurz;")
        except sqlite.OperationalError:
            raised = True
        self.assertEqual(raised, True, "should have raised an exception")

    def testConnectionExecute(self):
        con = sqlite.connect(":memory:")
        result = con.execute("select 5").fetchone()[0]
        self.assertEqual(result, 5, "Basic test of Connection.execute")

    def testConnectionExecutemany(self):
        con = sqlite.connect(":memory:")
        con.execute("create table test(foo)")
        con.executemany("insert into test(foo) values (?)", [(3,), (4,)])
        result = con.execute("select foo from test order by foo").fetchall()
        self.assertEqual(result[0][0], 3, "Basic test of Connection.executemany")
        self.assertEqual(result[1][0], 4, "Basic test of Connection.executemany")

    def testConnectionExecutescript(self):
        con = sqlite.connect(":memory:")
        con.executescript("create table test(foo); insert into test(foo) values (5);")
        result = con.execute("select foo from test").fetchone()[0]
        self.assertEqual(result, 5, "Basic test of Connection.executescript")

class ClosedConTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testClosedConCursor(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            cur = con.cursor()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedConCommit(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            con.commit()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedConRollback(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            con.rollback()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedCurExecute(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        con.close()
        try:
            cur.execute("select 4")
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedCreateFunction(self):
        con = sqlite.connect(":memory:")
        con.close()
        def f(x): return 17
        try:
            con.create_function("foo", 1, f)
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedCreateAggregate(self):
        con = sqlite.connect(":memory:")
        con.close()
        class Agg:
            def __init__(self):
                pass
            def step(self, x):
                pass
            def finalize(self):
                return 17
        try:
            con.create_aggregate("foo", 1, Agg)
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedSetAuthorizer(self):
        con = sqlite.connect(":memory:")
        con.close()
        def authorizer(*args):
            return sqlite.DENY
        try:
            con.set_authorizer(authorizer)
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedSetProgressCallback(self):
        con = sqlite.connect(":memory:")
        con.close()
        def progress(): pass
        try:
            con.set_progress_handler(progress, 100)
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

    def testClosedCall(self):
        con = sqlite.connect(":memory:")
        con.close()
        try:
            con()
            self.fail("Should have raised a ProgrammingError")
        except sqlite.ProgrammingError:
            pass
        except:
            self.fail("Should have raised a ProgrammingError")

class ClosedCurTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testClosed(self):
        con = sqlite.connect(":memory:")
        cur = con.cursor()
        cur.close()

        for method_name in ("execute", "executemany", "executescript", "fetchall", "fetchmany", "fetchone"):
            if method_name in ("execute", "executescript"):
                params = ("select 4 union select 5",)
            elif method_name == "executemany":
                params = ("insert into foo(bar) values (?)", [(3,), (4,)])
            else:
                params = []

            try:
                method = getattr(cur, method_name)

                method(*params)
                self.fail("Should have raised a ProgrammingError: method " + method_name)
            except sqlite.ProgrammingError:
                pass
            except:
                self.fail("Should have raised a ProgrammingError: " + method_name)
