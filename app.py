#coding:utf-8
__author__ = 'djx'


from bottle import route, run, template, static_file, request ,response,Bottle


import mysqlplubin

import bottle

import pymysql

import json



app = Bottle()

plugin = mysqlplubin.MyPlugin(host='127.0.0.1', port=3306, user='root', passwd='mysql', db='sss')

app.install(plugin)



@app.route('/')

def index():
    if request.get_cookie("visited"):
        response.set_header("Cache-Control", "no-cache")
        response.set_header("Pragma", "no-cache")
        return static_file("index.html", root='./static')
    else:
        response.set_header("Cache-Control", "no-cache")
        response.set_header("Pragma", "no-cache")
        return static_file("login.html", root='./static')



@app.route('/api/login')

def login(db):
    username=bottle.request.query.username
    password=bottle.request.query.password

    db.execute('select username,admin from user where user.isdel=0 and user.username=%s and user.password=%s', (username,password,))

    result = db.fetchall()

    if result!=():
        return {"number":1,"result":result}
    else:
        return {"number":0,"result":result}


@app.route('/api/getusers')

def getusers(db):
    start=bottle.request.query.start
    pagesize=bottle.request.query.pagesize

    db.execute('select user.id, user.username, user.password from user where isdel=0 limit %s, %s '%(start, pagesize))

    result = db.fetchall()

    return {"data":result}


@app.route('/api/addusers',method='POST')

def create(db):

    form = request.POST.decode('utf-8')

    username = form.get('username')

    password=form.get('password')

    db.execute('select * from user where isdel=0 and username=%s' , (username,))

    result=db.fetchall()

    if result:
        return {"data":"该用户已存在！"}
    else:
        db.execute("insert into user (username,password,isdel,admin) values(%s,%s,0,0)" , (username,password,))

        data=db.fetchall()

        print (data)
        return {"data":"添加成功！"}


@app.route('/api/deluser')

def deluser(db):
    id=request.query.id;
    print(id)
    if id != '1':
        print(1)
        db.execute('update user set isdel = 1 where id=%s' % (id,))

        return {"data":'删除成功'}
    else:
        print(2)
        return {"data":'该用户不允许删除'}




@app.route('/api/getall')

def getall(db):
    dname=bottle.request.query.dname
    if dname=='全部城区' or dname=='':
        db.execute('select region.id, region.DISTRICTFULLNAME, region.PNAME,xyregion.NUMINDEX,xyregion.X,xyregion.Y , region.Price from region ,xyregion where region.ID = xyregion.REGIONID', ())
    else:
        db.execute('select region.id, region.DISTRICTFULLNAME, region.PNAME,xyregion.NUMINDEX,xyregion.X,xyregion.Y , region.Price from region ,xyregion where region.ID = xyregion.REGIONID and region.DISTRICTFULLNAME=%s', (dname,))

    result = db.fetchall()
    data ={}
    i=0
    for row in result:
        if row[0] in data:
            tdic = { "x":row[4],"y":row[5],"index":row[3]}
            data[row[0]]["data"].append(tdic)
        else:
            i+=1
            data[row[0]] = {}
            tdic = { "x":row[4],"y":row[5],"index":row[3] }
            data[row[0]]["name"] = row[2]
            data[row[0]]["dname"] = row[1]
            data[row[0]]["id"] = row[0]
            data[row[0]]["price"] = row[6]
            data[row[0]]["data"] = []
            data[row[0]]["data"].append( tdic )

    return {"data":data,"count":i}


@app.route('/api/getproject')

def getproject(db):
    pname=bottle.request.query.pname
    # print(pname)
    if pname=='':
        db.execute('select shiyanproject.ID, shiyanproject.DistrictFullName, shiyanproject.Pname,shiyanproject.XLongitude,shiyanproject.YLatitude,shiyanproject.HouseCount,shiyanproject.Price  from shiyanproject ', ())
    else:
        db.execute('select shiyanproject.ID, shiyanproject.DistrictFullName, shiyanproject.Pname,shiyanproject.XLongitude,shiyanproject.YLatitude,shiyanproject.HouseCount,shiyanproject.Price  from shiyanproject where shiyanproject.DistrictFullName=%s', (pname,))

    result = db.fetchall()
    data ={}
    i=0
    for row in result:
            i+=1
            data[row[0]] = {}
            data[row[0]]["Pname"] = row[2]
            data[row[0]]["dname"] = row[1]
            data[row[0]]["id"] = row[0]
            data[row[0]]["XLongitude"] = row[3]
            data[row[0]]["YLatitude"] = row[4]
            data[row[0]]["HouseCount"] = row[5]
            data[row[0]]["Price"] = row[6]

    return {"data":data,"count":i}


@app.route('/api/create',method='POST')

def create(db):

    form = request.POST.decode('utf-8')

    name = form.get('name')

    dname=form.get('dname')

    price=form.get('price')

    pois=form.get('data')

    db.execute('select * from region where PNAME=%s' , (name,))

    result=db.fetchall()

    if not result:
        db.execute("insert into region (DISTRICTFULLNAME,PNAME,DistrictAlias,Price) values(%s,%s,%s,%s)" , (dname,name,dname,price,))
        data=db.fetchall()
        db.execute('select * from region where PNAME=%s' , (name,))
        res = db.fetchall()
        id = res[0][0]
        jsondata =json.loads(pois)
        i=0
        for row in jsondata:
            db.execute("insert into xyregion (X,Y,NUMINDEX,MAPTYPE,REGIONID) VALUES(%s,%s,%s,%s,%s)" , (row["lng"],row["lat"],i,"百度",id,))
            db.fetchall()
            i+=1

    return {"data":data}


@app.route('/api/delete')

def delete(db):
    id=request.query.id;

    result=db.execute('delete from region where id=%s' % (id,))
    db.execute('delete from xyregion where REGIONID=%s' % (id,))
    return {"data":result}



@app.route('/api/update')

def update(db):

    form = request.POST.decode('utf-8')

    name = form.get('name')

    dname=form.get('dname')

    price=form.get('price')

    pois=form.get('data')

    db.execute('select * from region where PNAME=%s' , (name,))

    result=db.fetchall()



    return {}



@app.route('/static/<filepath:path>')

def server_static(filepath):

        return static_file(filepath, root='./static')


app.run(host='0.0.0.0', port=8090,debug="True")