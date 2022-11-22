import sqlite3

# Global variables
DATABASE = "db/detectFiles.db"

# Open database connection
con = sqlite3.connect(DATABASE)
cur = con.cursor()

# Create table
cur.execute("CREATE TABLE previousFiles(fileName VARCHAR PRIMARY KEY,fileHash VARCHAR)")
cur.execute("INSERT INTO previousFiles VALUES(?,?)",("INGV",""))
cur.execute("INSERT INTO previousFiles VALUES(?,?)",("ROB",""))
cur.execute("INSERT INTO previousFiles VALUES(?,?)",("SGO",""))
cur.execute("INSERT INTO previousFiles VALUES(?,?)",("UGA",""))
cur.execute("INSERT INTO previousFiles VALUES(?,?)",("WUT",""))
con.commit()