from django.shortcuts import render
from django.http import JsonResponse
from .decorator import ajax_required
import pymysql as sql
import sys


# Singleton
class DBInfo:
    __instance = None
    __hostname = ''
    __username = ''
    __password = ''
    __port = 3306
    __dbname = ''
    @staticmethod
    def get_instance():
        if DBInfo.__instance is None:
            DBInfo()
        return DBInfo.__instance

    def __init__(self):
        if DBInfo.__instance is None:
            DBInfo.__instance = self

    def set_hostname(self, hostname):
        self.__hostname = hostname

    def set_username(self, username):
        self.__username = username

    def set_password(self, password):
        self.__password = password

    def set_port(self, port):
        self.__port = port

    def set_dbname(self, dbname):
        self.__dbname = dbname

    def get_hostname(self):
        return self.__hostname

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_port(self):
        return self.__port

    def get_dbname(self):
        return self.__dbname

dbinfo = DBInfo()

def home(request):
    # query = Query(hostname=dbinfo.get_hostname(), username=dbinfo.get_username(),
    #               password=dbinfo.get_password(), dbname=dbinfo.get_dbname(), port=dbinfo.get_port())
    # tables = query.get_tables()
    # views = query.get_views()
    # query.close()
    return render(request, 'home.html', {})

@ajax_required
def set_database(request):
    message = ''
    h = request.POST.get('host')
    p = int(request.POST.get('port'))
    u = request.POST.get('username')
    passwd = request.POST.get('password')
    n = request.POST.get('dbname')
    try:
        query = Query(hostname=h, username=u, password=passwd, dbname=n, port=p)
        tables = query.get_tables()
        views = query.get_views()
        dbinfo.set_hostname(h)
        dbinfo.set_dbname(n)
        dbinfo.set_username(u)
        dbinfo.set_password(passwd)
        dbinfo.set_port(p)
        message = 'Operation successful. Now you can use other options'
    except:
        message = str(sys.exc_info())

    return JsonResponse(data={'message': message, 'tables': tables, 'views': views})


@ajax_required
def table(request):
    table_name = request.POST.getlist('table[]')
    query = Query(hostname=dbinfo.get_hostname(), username=dbinfo.get_username(),
                  password=dbinfo.get_password(), dbname=dbinfo.get_dbname(), port=dbinfo.get_port())
    data, columns = query.exec('SELECT * FROM '+table_name[0])
    query.close()
    return JsonResponse(data={'data': data, 'columns': columns})


@ajax_required
def view(request):
    view_name = request.POST.getlist('view[]')
    query = Query(hostname=dbinfo.get_hostname(), username=dbinfo.get_username(),
                  password=dbinfo.get_password(), dbname=dbinfo.get_dbname(), port=dbinfo.get_port())
    data, columns = query.exec('SELECT * FROM '+view_name[0])
    query.close()
    return JsonResponse(data={'data': data, 'columns': columns})


@ajax_required
def query_execute(request):
    q = request.POST.get('query')
    qu = Query(hostname=dbinfo.get_hostname(), username=dbinfo.get_username(),
                  password=dbinfo.get_password(), dbname=dbinfo.get_dbname(), port=dbinfo.get_port())
    message = ''
    data = []
    columns = []
    try:
        data, columns = qu.exec(q)
    except:
        message = str(sys.exc_info())
    finally:
        qu.close()
    return JsonResponse(data={'data': data, 'columns': columns, 'message': message})


class Query:
    def __init__(self, hostname, username, password, dbname, port=3306):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.database = dbname
        self.conn = sql.connect(host=self.hostname, port=self.port, user=self.username, passwd=self.password, db=self.database)
        self.cur = self.conn.cursor()
        self.tables = []
        self.cur.execute("select TABLE_NAME from information_schema.tables where TABLE_SCHEMA like '{}' and TABLE_TYPE like 'BASE TABLE'".format(self.database))
        for r in self.cur:
            self.tables.append(r[0])
        self.v = []
        self.cur.execute("select TABLE_NAME from information_schema.tables where TABLE_SCHEMA like '{}' and TABLE_TYPE like 'VIEW'".format(self.database))
        for r in self.cur:
            self.v.append(r[0])

    def get_tables(self):
        return self.tables

    def get_views(self):
        return self.v

    def get_columns(self, table):
        columns = []
        self.cur.execute('select * from ' + table)
        for r in self.cur.description:
            columns.append(r[0])
        return columns

    def close(self):
        self.cur.close()

    def exec(self, q):
        data = []
        columns = []
        self.cur.execute(q)
        for r in self.cur:
            data.append(r)
        for d in self.cur.description:
            columns.append(d[0])
        return data, columns
