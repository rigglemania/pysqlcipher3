import os
import shutil
import unittest
import tempfile
import pysqlcipher3.dbapi2 as sqlite


class SqlCipherTests(unittest.TestCase):

    password = 'testing'

    def testCorrectPasswordEntered(self):
        """ Test fetching data after entering the correct password """
        self.createDatabase()
        self.assertSuccessfulQuery(self.password)

    def testNoPasswordEntered(self):
        """ Test for database exception when entering no password """
        self.createDatabase()
        self.assertDatabaseError(None)

    def testWrongPasswordEntered(self):
        """ Test for database exception when entering wrong password """
        self.createDatabase()
        self.assertDatabaseError("Wrong password")

    def testChangePassword(self):
        """ Test for changing the database password """
        new_password = "New password"
        self.createDatabase()
        self.assertSuccessfulQuery(self.password)
        self.changePassword(self.password, new_password)
        self.assertDatabaseError(self.password)
        self.assertSuccessfulQuery(new_password)

    def testAddPassword(self):
        """ Test for adding a password to a plaintext database """
        self.createDatabase(encrypt=False)
        self.assertSuccessfulQuery(None)

        encrypted_db = os.path.join(self.temp_dir, 'encrypted.db')
        conn = sqlite.connect(self.db)
        conn.executescript("ATTACH DATABASE '" + encrypted_db + "'" +
                           "AS encrypted KEY '" + self.password + "'")
        conn.executescript("SELECT sqlcipher_export('encrypted')")
        conn.executescript("DETACH DATABASE encrypted")
        conn.close()
        if os.path.exists(self.db):
            os.remove(self.db)
        os.rename(encrypted_db, self.db)
        self.assertDatabaseError(None)
        self.assertSuccessfulQuery(self.password)

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = os.path.join(self.temp_dir, 'test.db')

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        del self.temp_dir
        del self.db

    def createDatabase(self, encrypt=True):
        conn = sqlite.connect(self.db)
        if encrypt:
            self.setPassword(conn, self.password)
        conn.execute('create table tbl(col text)')
        conn.execute("insert into tbl values('data')")
        conn.commit()
        conn.close()

    def setPassword(self, conn, password, pragma="key"):
        if password is not None:
            conn.executescript("PRAGMA " + pragma + "='" + password + "'")

    def changePassword(self, old_password, new_password):
        conn = sqlite.connect(self.db)
        self.setPassword(conn, old_password)
        self.setPassword(conn, new_password, "rekey")
        conn.close()

    def queryData(self, conn):
        return conn.execute('select col from tbl').fetchone()[0]

    def assertSuccessfulQuery(self, password):
        conn = sqlite.connect(self.db)
        self.setPassword(conn, password)
        col_value = self.queryData(conn)
        self.assertEqual('data', col_value)
        conn.close()

    def assertDatabaseError(self, password):
        conn = sqlite.connect(self.db)
        self.setPassword(conn, password)
        try:
            col_value = self.queryData(conn)
            self.assertIsNone(col_value)
        except sqlite.DatabaseError as ex:
            self.assertEqual('file is encrypted or is not a database', str(ex))
        finally:
            conn.close()


def suite():
    sqlcipher_suite = unittest.makeSuite(SqlCipherTests, "test")
    return unittest.TestSuite((sqlcipher_suite,))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    test()