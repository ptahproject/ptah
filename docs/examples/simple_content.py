from paste.httpserver import serve
import sqlalchemy as sqla
import ptah
from ptah import cms


class Hyperlink(cms.Content):
    __tablename__ = 'ptah_cms_hyperlink'
    __type__ = cms.Type('hyperlink', permission=cms.AddContent)
    href = sqla.Column(sqla.Unicode)


if __name__ == '__main__':
    app = ptah.make_wsgi_app({'settings':r'./ptah.ini'})
    # we are initialized after make_wsgi_app
    if not cms.Session.query(Hyperlink).first():
        link = Hyperlink(title='ptah project',
                         href='http://ptahproject.org')
        cms.Session.add(link)
        import transaction; transaction.commit()

    for link in cms.Session.query(Hyperlink).all():
        print 'curl http://localhost:8080/__rest__/cms/content:/%s' % link.__uri__

    serve(app, host='0.0.0.0')
