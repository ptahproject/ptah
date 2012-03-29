import transaction
import sqlalchemy as sqla
import ptah
from ptah.testing import PtahTestCase


class TestSqlSession(PtahTestCase):

    def test_transaction(self):
        from ptah.sqlautils import transaction

        class SA(object):

            commited = False
            rollbacked = False

            raise_commit = False

            def commit(self):
                if self.raise_commit:
                    raise RuntimeError()
                self.commited = True

            def rollback(self):
                self.rollbacked = True

        sa = SA()
        trans = transaction(sa)

        with trans:
            pass

        self.assertTrue(sa.commited)

        sa = SA()
        trans = transaction(sa)
        try:
            with trans:
                raise ValueError()
        except:
            pass
        self.assertTrue(sa.rollbacked)

        sa = SA()
        sa.raise_commit = True
        trans = transaction(sa)
        try:
            with trans:
                pass
        except:
            pass
        self.assertTrue(sa.rollbacked)

    def test_sa_session(self):
        with ptah.sa_session() as sa:
            self.assertIs(sa, ptah.get_session())

    def test_sa_session_nested(self):
        err = None

        try:
            with ptah.sa_session() as sa:
                with ptah.sa_session() as sa:
                    pass
        except Exception as e:
            err = e

        self.assertIsNotNone(err)
