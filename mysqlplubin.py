import pymysql
import inspect

class MyPlugin(object):
    ''' This plugin passes an sqlite3 database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis. '''

    name = 'mysql'
    api = 2

    def __init__(self, host='localhost', port=3306, user='root', passwd='', db='mysql',
                 keyword='db'):
         self.host = host
         self.port = port
         self.user = user
         self.passwd = passwd
         self.db = db
         self.keyword = keyword

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, MyPlugin): continue
            if other.keyword == self.keyword:
                raise Exception("Found another sqlite plugin with "\
                "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        # Override global configuration with route-specific values.
        conf = context.config.get('mysql') or {}
        host = conf.get('host', self.host)
        port = conf.get('port', self.port)
        user = conf.get('user', self.user)
        passwd = conf.get('passwd', self.passwd)
        db = conf.get('db', self.db)

        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.getargspec(context.callback)[0]
        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            # Connect to the database
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,charset="utf8")
            db =  conn.cursor()
            # This enables column access by name: row['column_name']

            # Add the connection handle as a keyword argument.
            kwargs[self.keyword] = db

            try:
                rv = callback(*args, **kwargs)
                conn.commit()


            except Exception as e:
                db.rollback()
                raise Exception( "Database Error", e)
            finally:
                db.close()
                conn.close()
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper