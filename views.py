from flask import Flask, render_template, request, session
#from flask import g 
import sqlite3
import hashlib
app = Flask(__name__)
app.config['SECRET_KEY']="thisIsATest" #move this to a secret location at some point


#toolConn = sqlite3.connect('db/toolshare.db')
toolConn= sqlite3.connect('db/tool.db')
userConn = sqlite3.connect('db/user.db')
#xactionConn= sqlite3.connect('db/transaction.db')
#conn persists; no need to open elsewhere

#I don't intend to do a lot of joins even tho I sue lots of tables
#What I intend to do is load global arrays on startup, things like status, user, tools, etc
#I'll need a user_tool table too
#user_xaction table, etc  
#print ("Open databases successfully");

def get_status():
  toolConn.row_factory = sqlite3.Row
  cur = toolConn.cursor()
  cur.execute("select name from status")
  rows = cur.fetchall();
  status=list()
  for row in rows:
    status.append(row["name"])
  return status
#app.config['STATUS'] = get_status()
#print(app.config)
#things I learnt here:
#past tense of learn is learnt, not learned
#putting items in app.config is easy; I assume using session will be too.
#functions need to be defined before they can be called

def get_owners():
  userConn.row_factory = sqlite3.Row
  cur = userConn.cursor()
  cur.execute("select username from user")
  rows = cur.fetchall();
  owners=list()
  for row in rows:
    owners.append(row["username"])
  return owners
#app.config['OWNERS'] = get_owners()
#print(app.config)
#things I learnt here:
#session have a scope of inside a request so they don't work to hold the owners info here

@app.route('/')
def root():
  return render_template('appBase.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method=='POST':
    username=request.form['username']
    password=request.form['password'].encode('utf-8')
    hash = hashlib.md5(password).hexdigest()
    return render_template("register.html", username = username, hash = hash)
  else: 
    return render_template("register.html")

@app.route('/goodbye')
def exit():
  #eventually add cleanup here
  return "Goodbye cruel world!"

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method=='POST':
    return render_template('usersList.html')
  else:
    userConn.row_factory = sqlite3.Row
    cur = userConn.cursor()
    cur.execute("select * from user")
    rows = cur.fetchall();
    return render_template('template.html', rows = rows)
 
@app.route('/tools/', methods=['GET','POST'])
def tools():
  if request.method == 'GET':
    toolConn.row_factory = sqlite3.Row
    cur = toolConn.cursor()
    cur.execute("select * from tool")
    rows = cur.fetchall();
    sRows=list()
    for row in rows:
      sRows.append(dict(row))
    session['ROWS']= sRows
    session['STATUS']=get_status()
    session['OWNERS']=get_owners()
    #print(session)
    return render_template('toolsList.html')
  else:
    return render_method('tools.html')
##what I learnt here:
#since we are now within the request scope, we can use a session
#it's easy to manipulate the session data
#no need to pass data to the template explicitly; push it onto the session instead
#seems one may not pass a resultset via the session; errors ensue
#<investigate alternative specs  ;-) >
#WE can convert the resultset to a list of dictionaries my iterating and converting as shown above
#then, the list can be added to the cookie and used easily enough
#<SecureCookieSession {
#  'STATUS': ['in', 'out', 'lost', 'stolen', 'reserved'], 
#  'OWNERS': ['scott', 'brian', 'stan', 'jim', 'stan2', 'dan', 'lyle', 'salt', 'salt256', 'salt5'], 
#  'ROWS': [
#	{'status': 1, 'id': 1, 'location': None, 'name': 'hammer', 'description': 'conventional hammer', 'owner': 1}, 
#	{'status': 2, 'id': 2, 'location': None, 'name': 'mallet', 'description': 'rubber mallet', 'owner': 1}, 
#	{'status': 3, 'id': 3, 'location': None, 'name': 'micrometer', 'description': 'micrometer set', 'owner': 1}, 
#	{'status': 4, 'id': 4, 'location': None, 'name': 'inside micrometer', 'description': 'inside micrometer set', 'owner': 1}, 
#	{'status': 5, 'id': 5, 'location': 'garage', 'name': 'cnc', 'description': 'mpcnc - not mobile', 'owner': 1}, 
#	{'status': 1, 'id': 6, 'location': 'office', 'name': '3d printer', 'description': 'flsun cube', 'owner': 1}
#  ]
#}>

@app.route('/tools/list/')
def toolsList():
  return render_template('toolsList.html')

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

###templates ###
#
#@app.route('/route/goes/here', methods=['GET', 'POST'])
#def replaceMe():
#  if request.method == 'POST':
#    someVar = request.form['someFormField']  #see register() for example
#    return render_template('replaceMe.html', someVar)
#  else:
#    return render_template('replaceMe.html')
#

##########
###todo###
##########
#look on github for a flask template or skeleton
#build a secure version from the skeleton

