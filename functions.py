#functions

def get_status():
  toolConn.row_factory = sqlite3.Row
  cur = toolConn.cursor()
  cur.execute("select name from status")
  rows = cur.fetchall();
  status=list()
  for row in rows:
    status.append(row["name"])
  return status

def get_owners():
  userConn.row_factory = sqlite3.Row
  cur = userConn.cursor()
  cur.execute("select username from user")
  rows = cur.fetchall();
  owners=list()
  for row in rows:
    owners.append(row["username"])
  return owners

