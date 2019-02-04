from flask import Flask, render_template, request, session
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY']="thisIsATest" #move this to a secret location at some point
app.config['SALT']=str(hashlib.sha256(app.config['SECRET_KEY'].encode('utf-8')).hexdigest()).encode('utf-8')
toolConn= sqlite3.connect('db/tool.db')
userConn = sqlite3.connect('db/user.db')
#xactionConn= sqlite3.connect('db/xaction.db')
#*Conn persists; no need to open elsewhere

#I don't intend to do a lot of joins even tho I use lots of tables
#What I intend to do instead is to run multiple queries and pass the results via the session 
#NOTE on app.config vs session - 
#  use app.config if you are outside the request scope (like I could list all users here)
#  use the session once you are within request scope

def convert_results(data):
  #convert query results into a list of dictionary per row
  #access rows by index (or iterate on them), fields by column name
  l=[]
  for line in data:
    l.append(dict(line))
  return l

def get_status():
  toolConn.row_factory = sqlite3.Row
  cur = toolConn.cursor()
  cur.execute("select id, name from status")
  rows = cur.fetchall();
  d={}
  for row in rows:
    print(type(row))
    temp=dict(row)
    d[temp['id']]=temp['name']
  return d

#things I learnt here:
#past tense of learn is learnt if you're british, otherwise learned works!
#putting items in app.config is easy; I assume using session will be too.
#functions need to be defined before they can be called - duh!

def get_owners():
  userConn.row_factory = sqlite3.Row
  cur = userConn.cursor()
  cur.execute("select id, username from user")
  rows = cur.fetchall();
  return convert_results(rows)
#things learned here:
#session have a scope of inside a request so they don't work to hold the owners info here

@app.route('/')
def root():
  return render_template('appBase.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method=='POST':
    username=request.form['username']
    password=request.form['password']
    email=request.form['email']
    hash = hashlib.md5(str(password).encode('utf-8')+app.config['SALT']).hexdigest()
    cur = userConn.cursor()
    cur.execute("insert into user (username, password, email) values (?, ?, ?)", [username, hash, email])
    userConn.commit()
    return render_template("register.html")
  else: 
    return render_template("register.html")
#I learned about the query, cursor, params[], execute, commit pattern 
#also, encode before hashing and types must match before concat
#Should update this with a error trap enabled.

@app.route('/goodbye')
def exit():
  #eventually add cleanup here
  return "Goodbye cruel world!"

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method=='POST':
    username=request.form['username']
    password=request.form['password']
    currentHash=hashlib.md5(str(password).encode('utf-8')+app.config['SALT']).hexdigest()
    cur=userConn.cursor()
    cur.execute("Select * from user where username = ? ",[username])
    rows = cur.fetchall()
    row=rows[0]
    if row['password']== currentHash:
      return render_template('login.html') #was userList
    else:
      redirect('/') #check syntax  
  else:
    userConn.row_factory = sqlite3.Row
    cur = userConn.cursor()
    cur.execute("select * from user")
    rows = cur.fetchall();
    return render_template('login.html', rows = rows)
 
@app.route('/tools/', methods=['GET','POST'])
def tools():
  if request.method == 'GET':
    toolConn.row_factory = sqlite3.Row
    cur = toolConn.cursor()
    cur.execute("select * from tool")
    rows = cur.fetchall();
    session['ROWS']=convert_results(rows)
    session['STATUS']=get_status()
    session['OWNERS']=get_owners()
    session['PAGE']="tools list"
    return render_template('toolsList.html')
  else:
    return render_method('tools.html')
#what I learned here:
#since we are now within the request scope, we can use a session
#it's easy to manipulate the session data
#no need to pass data to the template explicitly; push it onto the session instead

@app.route('/tools/mylist/')
def mytools():
  if request.method == 'GET':
    session['CURRENT_USER_ID']=1
    toolConn.row_factory = sqlite3.Row
    cur = toolConn.cursor()
    cur.execute("select * from tool where owner = " + str(session['CURRENT_USER_ID'])+";") #need to replace with currentUser.id or something
    rows = cur.fetchall();
    session['ROWS']=convert_results(rows)
    session['STATUS']=get_status()
    session['OWNERS']=get_owners()
    session['PAGE']="My Tools List"
    return render_template('toolsList.html')
  else:
    return render_method('tools.html')

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

############
##  todo  ##
############
#look on github for a flask template or skeleton
#build a secure version from the skeleton

#0-refactor so password refers to passwords and hashes are hashes
#1-add code to session and/or app.config to represnt the logged-in status of the user
#prolly the user row plus logged-in=TRUE
#2-Expand the data in the register form and clean up the databbase.
#3-move salt toa config file that is secure and outside the scope of the web app
#so it needs to go in the file that runs on boot (in server mode)
#4-make a user edit page
#5-make a tools crud page; this should be "home" once logged in. 
#  list the tools in a table w/ scroll bars (make a user/tool (many-to-many) lookup table) 