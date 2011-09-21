""" sqlalchemy query wrapper """
from sqlalchemy import orm
from threading import local


class QueryFreezer(object):

    def __init__(self, builder):
        self.builder = builder
        self.data = local()

    def reset(self):
        self.data = local()

    def iter(self, **params):
        data = self.data
        if not hasattr(data, 'query'):
            data.query = self.builder()
            data.mapper = data.query._mapper_zero_or_none()
            data.querycontext = data.query._compile_context()
            data.querycontext.statement.use_labels = True
            data.stmt = data.querycontext.statement

        conn = data.query._connection_from_session(
            mapper = data.mapper,
            clause = data.stmt,
            close_with_result=True)

        result = conn.execute(data.stmt, **params)
        return data.query.instances(result, data.querycontext)

    def one(self, **params):
        ret = list(self.iter(**params))
    
        l = len(ret)
        if l == 1:
            return ret[0]
        elif l == 0:
            raise orm.exc.NoResultFound("No row was found for one()")
        else:
            raise orm.exc.MultipleResultsFound(
                "Multiple rows were found for one()")

    def first(self, **params):
        ret = list(self.iter(**params))[0:1]
        if len(ret) > 0:
            return ret[0]
        else:
            return None

    def all(self, **params):
        return list(self.iter(**params))
